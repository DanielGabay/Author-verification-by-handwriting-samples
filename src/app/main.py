import os
import random
import sys
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
warnings.filterwarnings("ignore")

import _global
from classes import CompareDocuments, Document, IdLetter, IdWord, Stats
from prepare_document import get_prepared_doc
from monkey_functions import get_compared_docs_monkey_results

#Recognition Phase
from recognition_functions import (get_identified_letters,
                                   get_letter_ae_features, get_monkey_features)
#Detection Phase
from detection_functions import detect_lines, get_letters


def init_doc(doc, only_save_letters=False):
	'''
	Detection Phase
	'''
	doc.doc_img = get_prepared_doc(_global.DATA_PATH + doc.name) if _global.TEST_MODE else get_prepared_doc(doc.name)
	detected_lines = detect_lines(doc.doc_img)
	detected_letters = get_letters(detected_lines)

	'''
	Recognition Phase
	'''
	doc.id_letters = get_identified_letters(detected_letters)
	doc.monkey_features = get_monkey_features(doc.id_letters)
	get_letter_ae_features(doc.id_letters)

	return doc

'''
entry point for GUI
'''
def _main_app(doc_name1, doc_name2, queue=None, test_mode=False):
	try:
		main_app(doc_name1, doc_name2, queue, test_mode)
	except:
		print("error")
		queue.put('Error occured')

def main_app(doc_name1, doc_name2, queue=None, test_mode=False):
	_global.init('hebrew', test_mode=test_mode)
	output = ""
	gui_output = ""

	'''
	Prepare Documents, Detection & Recognition Phases
	'''
	doc1 = init_doc(Document(doc_name1))
	doc2 = init_doc(Document(doc_name2))

	'''
	Verification Phase
	'''
	compare_docs = CompareDocuments(doc1, doc2)
	compare_docs.monkey_results()
	compare_docs.letters_autoencoder_results()

	output = output + "Monkey Result:{}\nAE result: {}".format(\
												   compare_docs.monkey_results,\
												   compare_docs.letters_ae_results)
	
	gui_output += "Algo1: Monkey Result:\n\t<{0}> [Confident: {1:.2f}%]\n".format(compare_docs.monkey_results['result'],\
														 						  compare_docs.monkey_results['precent']*100)
	gui_output += "Algo2: AutoEncoder Letters Result:\n\t<{}> [Confident: {:.2f}%]\n\tResult By Predictions:\n\t<{}> [Confident: {:.2f}%]\n".format(\
														compare_docs.letters_ae_results['result'],\
														compare_docs.letters_ae_results['precent']*100,
														compare_docs.letters_ae_results['result_by_predictions'],\
														compare_docs.letters_ae_results['precent_by_predictions']*100)
	gui_output += "\n\nFinal Result:\n\t<"
	conclusion = compare_docs.monkey_results['result'] + ">" if\
				  compare_docs.monkey_results['result'] == compare_docs.letters_ae_results['result']\
				  else "Conflict>"

	gui_output += conclusion

	conclusion2 = "\n\tWith AE by predictions:\n\t<"
	conclusion2 += compare_docs.monkey_results['result'] + ">" if\
				  compare_docs.monkey_results['result'] == compare_docs.letters_ae_results['result_by_predictions']\
				  else "Conflict>" 

	gui_output += conclusion2
	if queue is not None:
		queue.put(gui_output)

	print(output)

def print_conf_matrix(title, tn, tp, fn, fp):
	print(title)
	print("True-Positive: {}\tFalse-Negative: {}".format(tp, fn))
	print("False-Positive: {}\tTrue-Negative: {}".format(fp, tn))
	recall = tp/(tp+fn)
	precision = tp/(tp+fp)
	f1_score = (2)/((1/recall)+(1/precision))
	print("Recall: {0:.2f}%\nPrecision: {1:.2f}%\nF1-Score: {2:.2f}%".format(recall*100,precision*100, f1_score*100))


def calc_stats(s, result_monkey, result_letters_ae):
	if result_monkey and result_letters_ae and s.same_author:
		# all results 'Same author'
		s.tp += 1
		s.mark_as = "Mark: Same"
	elif not result_monkey and not result_letters_ae and s.same_author:
		# both monkey and ae call 'diff' while same
		s.fn += 1
		s.mark_as = "Mark: Different while Same"
	elif not result_monkey and not result_letters_ae and not s.same_author:
		# all results 'Different author'
		s.tn += 1
		s.mark_as = "Mark: Different"
	elif result_monkey and result_letters_ae and not s.same_author:
		# both monkey and ae call 'same' while diff
		s.fp += 1
		s.mark_as = "Mark: Same while Different"
	else:
		s.conflict += 1
		if s.same_author:
			s.conflict_while_same += 1
		else:
			s.conflict_while_diff += 1
		s.mark_as = "Conflict/Mistake"

	if result_letters_ae and s.same_author:
		s.ae_tp += 1
	elif not result_letters_ae and s.same_author:
		s.ae_fn += 1
	elif not result_letters_ae and not s.same_author:
		s.ae_tn += 1
	elif result_letters_ae and not s.same_author:
		s.ae_fp += 1

	if result_monkey and s.same_author:
		s.monkey_tp += 1
	elif not result_monkey and s.same_author:
		s.monkey_fn += 1
	elif not result_monkey and not s.same_author:
		s.monkey_tn += 1
	elif result_monkey and not s.same_author:
		s.monkey_fp += 1

def get_ae_monkey_results(s, compare_docs):
	compare_docs.monkey_results()
	compare_docs.letters_autoencoder_results()
	result_monkey = True if compare_docs.monkey_results['result'] == 'Same' else False
	precent_monkey = compare_docs.monkey_results['precent'] * 100
	
	# result_letters_ae = True if compare_docs.letters_ae_results['result'] == 'Same' else False
	result_letters_ae = True if compare_docs.letters_ae_results['result_by_predictions'] == 'Same' else False
	
	calc_stats(s, result_monkey, result_letters_ae)
	print("Monkey Result:\n\t<{0}> [Confident: {1:.2f}%]\n".format(compare_docs.monkey_results['result'],\
														 		   compare_docs.monkey_results['precent']*100))
	print("Letters AE Result:\n<{} Author>\nsum_predictions:{}\nprecent_by_predictions:{}\ncount_same: {}\ncount_diff: {}"\
		.format(compare_docs.letters_ae_results['result_by_predictions'],\
				compare_docs.letters_ae_results['sum_predictions'],\
				compare_docs.letters_ae_results['precent_by_predictions'],\
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
	print_conf_matrix("Only Monkey Conf Matrix:", s.monkey_tn, s.monkey_tp, s.monkey_fn, s.monkey_fp)
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
			if doc1.name.replace('b','') == doc2.name or doc2.name.replace('b','') == doc1.name\
				or doc1.name == doc2.name:
				continue
			s.same_author = False
			print("\n---------------------")
			print("Test: {} {}".format(doc1.name, doc2.name))
			compare_docs = CompareDocuments(doc1, doc2)
			get_ae_monkey_results(s, compare_docs)
			s.count_num_of_tests += 1

	print_ae_monkey_results(s, len(b_files))

if __name__ == "__main__":
	# if(len(sys.argv) < 2):
	# 	print("Usage: python main.py <[save_all]/[file_name]> ")
	# 	sys.exit(1)
	#TODO: think how to determine monkey algo by_sum/by_vectors
	_global.init('hebrew')
	test_all_same(106)
	# test_all_pairs()
	# save_all_pairs_docs_letters()
	# main_app('1.tiff', '2.tiff', test_mode=True)
