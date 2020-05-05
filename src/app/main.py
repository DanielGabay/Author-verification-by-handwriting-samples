import os
import sys

import cv2
import joblib
import numpy as np
import random

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
from main_functions import save_object, load_object
import warnings
warnings.simplefilter("ignore", UserWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0,1,2,3"

class Stats():
	def __init__(self):
		self.tp = 0
		self.fp = 0
		self.tn = 0
		self.fn = 0
		self.ae_tp = 0
		self.ae_fp = 0
		self.ae_tn = 0
		self.ae_fn = 0
		self.monkey_tp = 0
		self.monkey_fp = 0
		self.monkey_tn = 0
		self.monkey_fn = 0
		self.conflict = 0
		self.conflict_while_same = 0
		self.conflict_while_diff = 0
		self.mark_as = ""
		self.same_author = None
		self.count_num_of_tests = 0

def calc_stats(s, result_monkey, result_letters_ae, same_author):
	if result_monkey and result_letters_ae and same_author:
		# all results 'Same author'
		s.tp += 1
		s.mark_as = "Mark: Same"
	elif not result_monkey and not result_letters_ae and same_author:
		# both monkey and ae call 'diff' while same
		s.fn += 1
		s.mark_as = "Mark: Different while Same"
	elif not result_monkey and not result_letters_ae and not same_author:
		# all results 'Different author'
		s.tn += 1
		s.mark_as = "Mark: Different"
	elif result_monkey and result_letters_ae and not same_author:
		# both monkey and ae call 'same' while diff
		s.fp += 1
		s.mark_as = "Mark: Same while Different"
	else:
		s.conflict += 1
		if same_author:
			s.conflict_while_same += 1
		else:
			s.conflict_while_diff += 1
		s.mark_as = "Conflict/Mistake"

			
	if result_letters_ae and same_author:
		s.ae_tp += 1
	elif not result_letters_ae and same_author:
		s.ae_fn += 1
	elif not result_letters_ae and not same_author:
		s.ae_tn += 1
	elif result_letters_ae and not same_author:
		s.ae_fp += 1

	if result_monkey and same_author:
		s.monkey_tp += 1
	elif not result_monkey and same_author:
		s.monkey_fn += 1
	elif not result_monkey and not same_author:
		s.monkey_tn += 1
	elif result_monkey and not same_author:
		s.monkey_fp += 1

def get_ae_monkey_results(s, compare_docs):
	get_compared_docs_monkey_results(compare_docs)
	get_compared_docs_ae_letters_results(compare_docs)
	result_monkey = True if compare_docs.monkey_results['result'] == 'Same' else False
	precent_monkey = compare_docs.monkey_results['precent'] * 100
	result_letters_ae = True if compare_docs.letters_ae_results['result'] == 'Same' else False
	
	calc_stats(s, result_monkey, result_letters_ae, s.same_author)
	print("Letters AE Result:\n<{} Author>\ncount_same: {}\ncount_diff: {}"\
		.format(compare_docs.letters_ae_results['result'],\
				compare_docs.letters_ae_results['count_same'],\
				compare_docs.letters_ae_results['count_diff']))
	print("Real: {}\n{}".format(s.same_author, s.mark_as)) 	# FOR EASY NAVIGATION IN FILE

def print_ae_monkey_results(s, len_b):
	print("\n------------------")
	print("Number of same pairs checked:{}".format(len_b))
	print("Sum of al pairs checked: {}".format(s.count_num_of_tests))
	print("\n------------------")
	print_conf_matrix("Monkey & letter AE Conf Matrix:", s.tn, s.tp, s.fn, s.fp)
	print("Model accuracy: {0:.2f}% (*NOTE: not includes Undecided results!)".format((s.tn+s.tp)/(s.tn+s.tp+s.fn+s.fp)*100))
	print("Undecided Results:\n->conflict:{}\n-->conflict_while_same:{}\n-->conflict_while_diff:{}"\
		.format(s.conflict, s.conflict_while_same,s.conflict_while_diff))
	print("\n------------------")
	print_conf_matrix("Only letter AE Conf Matrix:", s.ae_tn,s.ae_tp, s.ae_fn, s.ae_fp)
	print("Model accuracy: {0:.2f}%".format((s.ae_tn+s.ae_tp)/(s.ae_tn+s.ae_tp+s.ae_fn+s.ae_fp)*100))
	print("\n------------------")
	print_conf_matrix("Only Monkey Conf Matrix:", s.monkey_tp, s.monkey_fp, s.monkey_tn, s.monkey_fn)
	print("Model accuracy: {0:.2f}%".format((s.monkey_tn+s.monkey_tp)/(s.monkey_tn+s.monkey_tp+s.monkey_fn+s.monkey_fp)*100))

def get_doc_by_name(all_docs, file_name):
	for doc in all_docs:
		if doc.name == file_name:
			return doc

def test_all_same(test_random_different=0):
	b_files = []
	s = Stats()
	all_docs = []

	for _, _, files in os.walk(_global.DATA_PATH):
		b_files = [x for x in files if 'b' in x]
	for _, _, files in os.walk(_global.DATA_PATH):
		b_files = [x for x in files if 'b' in x]
		a_files = [x.replace('b', '') for x in b_files]
		all_files = a_files + b_files
	
	for file_name in all_files:
		print("Get Document obj for: {}".format(file_name))
		doc = Document(file_name)
		doc = init_doc(doc)
		all_docs.append(doc)
		
	for file_name in b_files:
		doc1 = get_doc_by_name(all_docs, file_name)
		doc2 = get_doc_by_name(all_docs, file_name.replace('b',''))
		print("\n---------------------")
		print("Test: {} {}".format(doc1.name, doc2.name))
		s.same_author = True
		compare_docs = CompareDocuments(doc1, doc2)
		get_ae_monkey_results(s, compare_docs)
		s.count_num_of_tests += 1


	if test_random_different != 0:
		for i in range(test_random_different):
			sampled_list = random.sample(all_files, 2)
			doc1 = get_doc_by_name(all_docs, sampled_list[0])
			doc2 = get_doc_by_name(all_docs, sampled_list[1])
			if doc1.name.replace('b','') == doc2.name or doc2.name.replace('b','') == doc1.name:
				continue
			s.same_author = False
			print("\n---------------------")
			print("Test: {} {}".format(doc1.name, doc2.name))
			compare_docs = CompareDocuments(doc1, doc2)
			get_ae_monkey_results(s, compare_docs)
			s.count_num_of_tests += 1

	print_ae_monkey_results(s, len(b_files))
	
def init_doc(doc, only_for_save_obj=False):
	#TODO: think about the path of document for future use in GUI
	# obj_name = doc.name.split('.')[0]
	# if os.path.exists(_global.OBJ_PATH + obj_name):
	# 	doc = load_object(obj_name)
	# else:
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
	# save_object(doc, obj_name)
	# if not only_for_save_obj:
	get_letters_ae_features(doc.id_letters)
	return doc

def main(doc_name1, doc_name2, test_all_same=False):
	doc1, doc2 = Document(doc_name1), Document(doc_name2)
	# prepare Documents
	# ---> Detection Phase
	doc1 = init_doc(doc1)
	doc2 = init_doc(doc2)
		
	# ---> Verification Phase
	compare_docs = CompareDocuments(doc1, doc2)

	get_compared_docs_monkey_results(compare_docs)
	get_compared_docs_ae_letters_results(compare_docs)
	if test_all_same:
		return compare_docs
	# print("Monkey Result:{}\nAE result: {}".format(compare_docs.monkey_results,\
	# 											   compare_docs.letters_ae_results))

	# call autoencoder with letters & words
	# summaraize all results into one result

def test_all_pairs():
	count_pairs = 0
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
		doc = init_doc(doc)
		all_docs.append(doc)
	
	tp, fp, tn, fn = 0, 0, 0, 0
	ae_tp, ae_fp, ae_tn, ae_fn = 0, 0, 0, 0
	monkey_tp, monkey_fp, monkey_tn, monkey_fn = 0, 0, 0, 0
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

			if result_monkey and same_author:
				monkey_tp += 1
			elif not result_monkey and same_author:
				monkey_fn += 1
			elif not result_monkey and not same_author:
				monkey_tn += 1
			elif result_monkey and not same_author:
				monkey_fp += 1
			
			print("Letters AE Result:\n<{} Author>\ncount_same: {}\ncount_diff: {}"\
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
	print_conf_matrix("Only Monkey Conf Matrix:", monkey_tp, monkey_fp, monkey_tn, monkey_fn)
	print("Model accuracy: {0:.2f}%".format((monkey_tn+monkey_tp)/(monkey_tn+monkey_tp+monkey_fn+monkey_fp)*100))


def print_conf_matrix(title, tn, tp, fn, fp):
	print(title)
	print("True-Negative: {}\tFalse-Negative: {}".format(tn, fn))
	print("False-Positive: {}\tTrue-Positive: {}".format(fp, tp))

def save_all_docs_obj_as_files():
	for _, _, files in os.walk(_global.DATA_PATH):
		for file in files:
			print(file)
			doc = Document(file)
			doc = init_doc(doc, only_for_save_obj=True)

if __name__ == "__main__":
	# if(len(sys.argv) < 2):
	# 	print("Usage: python main.py <[save_all]/[file_name]> ")
	# 	sys.exit(1)
	#TODO: think how to determine monkey algo by_sum/by_vectors
	_global.init('hebrew')
	load_and_compile_letters_model(_global.LETTERS_MODEL)
	# save_all_docs_obj_as_files()
	test_all_same(5000)
	# test_all_pairs()
	# main('1.tiff', '2.tiff')
	# if(sys.argv[1] == 'save_all'):
	# 	main_save_all()
	# else: 
	# 	doc_name = str(sys.argv[1])
	# 	main(doc_name)
