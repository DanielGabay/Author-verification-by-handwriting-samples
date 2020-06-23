import os
import random
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
warnings.filterwarnings("ignore")
import eel
import _global
from classes import CompareDocuments, Document, Stats
from prepare_document import get_prepared_doc
from create_output import generate_conclusion,generate_gui_output,generate_output,print_ae_monkey_results

#Recognition Phase
from recognition_functions import (get_identified_letters,
                                   get_letter_ae_features, get_monkey_features)
#Detection Phase
from detection_functions import detect_lines, get_letters

py_print_to_gui = False

def print_to_gui(str):
	if py_print_to_gui:
		eel.print_from_py(str)()

def init_doc(doc, only_save_letters=False):
	'''
	Detection Phase
	'''
	path = os.path.join(_global.DATA_PATH, doc.name) if _global.TEST_MODE else doc.name
	print_to_gui(path) # can be removed later
	doc.doc_img = get_prepared_doc(path)
	detected_lines = detect_lines(doc.doc_img)
	detected_letters = get_letters(detected_lines)

	'''
	Recognition Phase
	'''
	print_to_gui("Identify Letters") # can be removed later
	doc.id_letters = get_identified_letters(detected_letters)
	print_to_gui("Getting Monkey Features") # can be removed later
	doc.monkey_features = get_monkey_features(doc.id_letters)
	print_to_gui("Getting AutoEncoder Features") # can be removed later
	get_letter_ae_features(doc.id_letters)

	return doc

def _gui_entry(doc_name1, doc_name2):
	try:
		result = main_app(doc_name1, doc_name2, test_mode=True)
		return result
	except FileNotFoundError:
		return "File not found on data folder"
	except Exception as e:
		print(e)
		return "Error: {}".format(e)


def main_app(doc_name1, doc_name2, test_mode=False):
	"""
	Initialize Variable& Settings
	"""
	_global.init('hebrew', test_mode=test_mode)

	'''
	Prepare Documents, Detection & Recognition Phases
	'''
	doc1 = init_doc(Document(doc_name1))
	doc2 = init_doc(Document(doc_name2))

	print("Comparing: [{}] [{}]".format(doc1.name, doc2.name))
	'''
	Verification Phase
	'''
	compare_docs = CompareDocuments(doc1, doc2)
	print_to_gui("Verifying") # can be removed later
	compare_docs.verify()

	'''
	Create Output
	'''
	output = generate_output(compare_docs)
	
	gui_output = generate_gui_output(compare_docs)
	# gui_output = generate_gui_output(compare_docs) + generate_conclusion(compare_docs)

	print(output)
	print("-----")
	print(gui_output)
	return gui_output, compare_docs.final_result['proba']

def print_conf_matrix(title, tn, tp, fn, fp):
	recall, precision, f1_score = 0, 0, 0
	print(title)
	print("True-Positive: {}\tFalse-Negative: {}".format(tp, fn))
	print("False-Positive: {}\tTrue-Negative: {}".format(fp, tn))
	if tp+fn != 0:
		recall = tp/(tp+fn)
		
	if tp+fp != 0:
		precision = tp/(tp+fp)
	if recall != 0 and precision != 0:
		f1_score = (2)/((1/recall)+(1/precision))
	print("Recall: {0:.2f}%\nPrecision: {1:.2f}%\nF1-Score: {2:.2f}%".format(recall*100,precision*100, f1_score*100))


def calc_stats(s, result_monkey, result_letters_ae, result_ssim, result_final):
	count_algos = 0
	if result_monkey:
		count_algos += 1
	if result_letters_ae:
		count_algos += 1
	if result_ssim:
		count_algos += 1
	
	if count_algos >= 2 and s.same_author:
		s.tp += 1
		s.mark_as = "Mark: Same"
	elif count_algos >= 2 and not s.same_author:
		s.fp += 1
		s.mark_as = "Mark: Same while Different"
	elif count_algos < 2 and s.same_author:
		s.fn += 1
		s.mark_as = "Mark: Different while Same"
	elif count_algos < 2 and not s.same_author:
		s.tn += 1
		s.mark_as = "Mark: Different"

	if result_letters_ae and s.same_author:
		s.ae_tp += 1
	elif not result_letters_ae and s.same_author:
		s.ae_fn += 1
	elif not result_letters_ae and not s.same_author:
		s.ae_tn += 1
	elif result_letters_ae and not s.same_author:
		s.ae_fp += 1
	
	if result_final and s.same_author:
		s.final_tp += 1
	elif not result_final and s.same_author:
		s.final_fn += 1
	elif not result_final and not s.same_author:
		s.final_tn += 1
	elif result_final and not s.same_author:
		s.final_fp += 1

	if result_monkey and s.same_author:
		s.monkey_tp += 1
	elif not result_monkey and s.same_author:
		s.monkey_fn += 1
	elif not result_monkey and not s.same_author:
		s.monkey_tn += 1
	elif result_monkey and not s.same_author:
		s.monkey_fp += 1
	
	if result_ssim and s.same_author:
		s.ssim_tp += 1
	elif not result_ssim and s.same_author:
		s.ssim_fn += 1
	elif not result_ssim and not s.same_author:
		s.ssim_tn += 1
	elif result_ssim and not s.same_author:
		s.ssim_fp += 1

def get_ae_monkey_results(s, compare_docs):
	_, final_res, final_res_pred = compare_docs.verify()

	result_monkey = True if compare_docs.monkey_results['result'] == 'Same' else False
	compare_docs.monkey_results['precent'] * 100
	result_ssim = True if compare_docs.ssim_results['result'] == 'Same' else False
	ssim_pred = compare_docs.ssim_results['precent'] * 100
	if _global.AE_LETTERS_RESULT_BY_PRECENT:
		result_letters_ae = True if compare_docs.letters_ae_results['result_by_predictions'] == 'Same' else False
	else:
		result_letters_ae = True if compare_docs.letters_ae_results['result'] == 'Same' else False
	
	calc_stats(s, result_monkey, result_letters_ae, result_ssim, True if final_res == 'Same' else False)
	print("Monkey Result:\n<{0}> [Confident: {1:.2f}%]".format(compare_docs.monkey_results['result'],\
														 		   compare_docs.monkey_results['precent']*100))
	print("Letters AE Result:\n<{}>\ncount_same: {}\ncount_diff: {}\nsum_predictions: {}\nprecent_by_predictions: {}"\
		.format(compare_docs.letters_ae_results['result_by_predictions'],\
				compare_docs.letters_ae_results['count_same'],\
				compare_docs.letters_ae_results['count_diff'],\
				compare_docs.letters_ae_results['sum_predictions'],\
				compare_docs.letters_ae_results['precent_by_predictions']))
	ssim_print = "Same" if result_ssim else "Different"
	print("ssim result:\n<{}>\npred: {}".format(ssim_print, ssim_pred))
	print("Real: {}\n{}".format(s.same_author, s.mark_as)) 	# FOR EASY NAVIGATION IN FILE
	print("Final Result: {0} [Confident: {1:.2f}]".format(final_res, final_res_pred))

def model_acc(tn, tp, fn, fp):
	total = tn+tp+fn+fp
	if total == 0:
		return 0
	return (tn+tp)/(total) * 100

def print_ae_monkey_results(s, len_b):
	print("\n------------------")
	print("Number of same pairs checked:{}".format(len_b))
	print("Sum of al pairs checked: {}".format(s.count_num_of_tests))
	print("\n------------------")
	print_conf_matrix("Monkey & letter AE Conf & ssim Matrix:", s.tn, s.tp, s.fn, s.fp)
	print("Model accuracy: {0:.2f}%".format(model_acc(s.tn, s.tp, s.fn, s.fp)))
	# print_conf_matrix("Monkey & letter AE Conf Matrix:", s.tn, s.tp, s.fn, s.fp)
	# print("Model accuracy: {0:.2f}% (*NOTE: not includes Undecided results!)".format(model_acc(s.tn, s.tp, s.fn, s.fp)))
	# print("Undecided Results:\n->conflict:{}\n-->conflict_while_same:{}\n-->conflict_while_diff:{}"\
		# .format(s.conflict, s.conflict_while_same,s.conflict_while_diff))
	print("\n------------------")
	print_conf_matrix("Only letter AE Conf Matrix:", s.ae_tn, s.ae_tp, s.ae_fn, s.ae_fp)
	print("Model accuracy: {0:.2f}%".format(model_acc(s.ae_tn, s.ae_tp, s.ae_fn, s.ae_fp)))
	print("\n------------------")
	print_conf_matrix("Only Monkey Conf Matrix:", s.monkey_tn, s.monkey_tp, s.monkey_fn, s.monkey_fp)
	print("Model accuracy: {0:.2f}%".format(model_acc(s.monkey_tn, s.monkey_tp, s.monkey_fn, s.monkey_fp)))
	print("\n------------------")
	print_conf_matrix("Only ssim Conf Matrix:", s.ssim_tn, s.ssim_tp, s.ssim_fn, s.ssim_fp)
	print("Model accuracy: {0:.2f}%".format(model_acc(s.ssim_tn, s.ssim_tp, s.ssim_fn, s.ssim_fp)))
	print("\n------------------")
	print_conf_matrix("Final Result Conf Matrix:", s.final_tn, s.final_tp, s.final_fn, s.final_fp)
	print("Model accuracy: {0:.2f}%".format(model_acc( s.final_tn, s.final_tp, s.final_fn, s.final_fp)))

def get_doc_by_name(all_docs, file_name):
	for doc in all_docs:
		if doc.name == file_name:
			return doc

def test_all_same(test_random_different=0):
	b_files = []
	all_docs = []
	all_files = []
	s = Stats()

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
			s.count_num_of_tests += 1
			get_ae_monkey_results(s, compare_docs)

	print_ae_monkey_results(s, len(b_files))

if __name__ == "__main__":
	_global.init('hebrew',monkey_by_vectors=True, print_globals=True, data_path="newData")
	# test_all_same(1000)
	main_app('9.tiff', '8.tiff', test_mode=True)
