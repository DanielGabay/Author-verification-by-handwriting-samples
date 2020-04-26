import os
import sys

import cv2
import joblib
import numpy as np

import _global
from ae_letters_functions import (get_compared_docs_ae_letters_results,
                                  prediction_ae_letters)
from AutoEncoder.test_autoencoder import get_letters_ae_features
from classes import CompareDocuments, Document, IdLetter, IdWord
from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.detectWords import get_words
from extractComparisonFeatures.our_utils.prepare_document import \
    get_prepared_doc
from models.letterClassifier import load_and_compile_letters_model
from monkey_functions import (get_compared_docs_monkey_results,
                              get_identified_letters, get_monkey_features)

import warnings
warnings.simplefilter("ignore", UserWarning)


def test_all_same():
	b_files = []
	for _, _, files in os.walk('data2/'):
		b_files = [x for x in files if 'b' in x]	
	for i in range(len(b_files)):
		TEST_FILE_1 = b_files[i]
		# uncomment if comparing *.tiff and *b.png files
		# TEST_FILE_2 = b_files[i].replace('b','').replace('png','tiff')
		TEST_FILE_2 = b_files[i].replace('b','')
		print("\n---------------------")
		print("Test: {} {}".format(TEST_FILE_1, TEST_FILE_2))
		main(TEST_FILE_1, TEST_FILE_2)

def init_doc(doc):
	#TODO: think about the path of document for future use in GUI
	path = _global.DATA_PATH
	doc.doc_img = get_prepared_doc(path+doc.name)
	# ---> Detection Phase
	detected_lines = get_lines(doc.doc_img, doc.name)
	# detected_words = get_words(detected_lines)
	detected_letters = get_letters(detected_lines)

	# ---> Identification Phase
	# we keep monkey letters in a different way for monkey use
	# than our new IdLetter class. for now keep it that way.
	id_letters_for_monkey, doc.id_letters = get_identified_letters(detected_letters, from_main=True)
	doc.monkey_features = get_monkey_features(id_letters_for_monkey)
	get_letters_ae_features(doc.id_letters)



def main(doc_name1, doc_name2):
	doc1, doc2 = Document(doc_name1), Document(doc_name2)
	# prepare Documents
	# ---> Detection Phase
	init_doc(doc1)
	init_doc(doc2)
		
	# ---> Verification Phase
	compare_docs = CompareDocuments(doc1, doc2)

	get_compared_docs_monkey_results(compare_docs)
	get_compared_docs_ae_letters_results(compare_docs)
	
	print("Monkey Result:{}\nAE result: {}".format(compare_docs.monkey_results,\
												   compare_docs.letters_ae_results))

	# call autoencoder with letters & words
	# summaraize all results into one result

def test_all_pairs():
	all_files = []
	count_vectors = []
	all_docs = []
	for _, _, files in os.walk(_global.DATA_PATH):
		b_files = [x for x in files if 'b' in x]
		a_files = [x.replace('b', '') for x in b_files]
		all_files = a_files + b_files
	
	for file_name in all_files:
		print("Get Document obj for: {}".format(file_name))
		doc = Document(file_name)
		init_doc(doc)
		all_docs.append(doc)
	
	tp, fp, tn, fn = 0, 0, 0, 0
	ae_tp, ae_fp, ae_tn, ae_fn = 0, 0, 0, 0
	conflict, conflict_while_same, conflict_while_diff = 0, 0, 0
	tp_prec, fp_prec, tn_prec, fn_prec = [], [], [], []
	mark_as = ""
	for i in range(len(all_docs)):
		for j in range(i+1,len(all_docs)):
			doc1, doc2 = all_docs[i], all_docs[j]
			if doc1.name == doc2.name:
				continue
			print("\n---------------------")
			print("Test: {} {}".format(doc1.name, doc2.name))

			same_author = False
			if doc1.name.replace('b','') == doc2.name or doc2.name.replace('b','') == doc1.name:
				same_author = True

			compare_docs = CompareDocuments(doc1, doc2)
			get_compared_docs_monkey_results(compare_docs)
			get_compared_docs_ae_letters_results(compare_docs)
			result_monkey = True if compare_docs.monkey_results['result'] == 'Same' else False
			precent_monkey = compare_docs.monkey_results['precent'] * 100
			result_letters_ae = True if compare_docs.letters_ae_results['result'] == 'Same' else False
			if result_monkey and result_letters_ae and same_author:
				# all results 'Same author'
				tp += 1
				tp_prec.append(precent_monkey)
				mark_as = "Mark: Same"
			elif not result_monkey and not result_letters_ae and same_author:
				# both monkey and ae call 'diff' while same
				fn += 1
				fn_prec.append(precent_monkey)
				mark_as = "Mark: Different while Same"
			elif not result_monkey and not result_letters_ae and not same_author:
				# all results 'Different author'
				tn += 1
				tn_prec.append(precent_monkey)
				mark_as = "Mark: Different"
			elif result_monkey and result_letters_ae and not same_author:
				# both monkey and ae call 'same' while diff
				fp += 1
				fp_prec.append(precent_monkey)
				mark_as = "Mark: Same while Different"
			else:
				conflict += 1
				if same_author:
					conflict_while_same += 1
				else:
					conflict_while_diff += 1
				mark_as = "Conflict/Mistake"

			
			if result_letters_ae and same_author:
				ae_tp += 1
			elif not result_letters_ae and same_author:
				ae_fn += 1
			elif not result_letters_ae and not same_author:
				ae_tn += 1
			elif result_letters_ae and not same_author:
				ae_fp += 1

			print("Letters AE Result:\n<{} Authors>\ncount_same: {}\ncount_diff: {}"\
				 .format(compare_docs.letters_ae_results['result'],\
					 	 compare_docs.letters_ae_results['count_same'],\
			     		 compare_docs.letters_ae_results['count_diff']))
			# FOR EASY NAVIGATION IN FILE
			print("Real: {}\n{}".format(same_author, mark_as))

	print("\n------------------")
	len_b = len(b_files)
	len_all_pairs = ((len_b*2)*(len_b*2-1))/2
	print("Number of same pairs checked:{}".format(len_b))
	print("Sum of al pairs checked: {}".format(len_all_pairs))
	print("\n------------------")
	print_conf_matrix("Monkey & letter AE Conf Matrix:", tn, tp, fn, fp)
	print("Model accuracy: {0:.2f}% (*NOTE: not includes Undecided results!)".format((tn+tp)/(tn+tp+fn+fp)*100))
	print("Undecided Results:\n->conflict:{}\n-->conflict_while_same:{}\n-->conflict_while_diff:{}"\
		.format(conflict, conflict_while_same,conflict_while_diff))
	print("\n------------------")
	print_conf_matrix("Only letter AE Conf Matrix:", ae_tn, ae_tp, ae_fn, ae_fp)
	print("Model accuracy: {0:.2f}%".format((ae_tn+ae_tp)/(ae_tn+ae_tp+ae_fn+ae_fp)*100))
	print("\n------------------")
	print("Monkey precents")
	print("True-Negative-Precent: mean:{0:.2f} std:{0:.2f}".format(np.mean(tn_prec,axis=0),np.std(tn_prec,axis=0)))
	print("False-Negative-Precent: mean:{0:.2f} std:{0:.2f}".format(np.mean(fn_prec,axis=0),np.std(fn_prec,axis=0)))
	print("False-Positive-Precent: mean:{0:.2f} std:{0:.2f}".format(np.mean(fp_prec,axis=0),np.std(fp_prec,axis=0)))
	print("True-Positive-Precent: mean:{0:.2f} std:{0:.2f}".format(np.mean(tp_prec,axis=0),np.std(tp_prec,axis=0)))

def print_conf_matrix(title, tn, tp, fn, fp):
	print(title)
	print("True-Negative: {}\tFalse-Negative: {}".format(tn, fn))
	print("False-Positive: {}\tTrue-Positive: {}".format(fp, tp))

if __name__ == "__main__":
	# if(len(sys.argv) < 2):
	# 	print("Usage: python main.py <[save_all]/[file_name]> ")
	# 	sys.exit(1)
	#TODO: think how to determine monkey algo by_sum/by_vectors
	_global.init('hebrew')
	load_and_compile_letters_model(_global.LETTERS_MODEL)
	# test_all_same()
	# test_all_pairs()
	main('1.tiff', '2.tiff')
	# if(sys.argv[1] == 'save_all'):
	# 	main_save_all()
	# else: 
	# 	doc_name = str(sys.argv[1])
	# 	main(doc_name)
