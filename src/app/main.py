import os
import sys
import joblib
import cv2
import matplotlib.pyplot as plt
import numpy as np
from keras.preprocessing import image

import _global
from classes import Document, IdLetter, IdWord, CompareDocuments
from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.detectWords import get_words
from extractComparisonFeatures.our_utils.prepare_document import \
    get_prepared_doc
from models.letterClassifier import load_and_compile_letters_model

#TODO: move functions to some helper function file instead of
#getting them from the monkey_collect_data & test_monkey
from monkey_collect_data import get_identified_letters, get_monkey_features, create_diff_vector
from test_monkey import get_monkey_result, save_letters
from AutoEncoder.test_autoencoder import get_letters_ae_features

def predict_ae(diff_vec, ae_letters_model):
	diff_vec = np.asarray(diff_vec)
	result = ae_letters_model.predict_proba(diff_vec.reshape(1,-1))
	if result[0][0] > 0.5:
		# print("<Different Authors> [Confident: {0:.2f}%]".format(result[0][0]*100))
		return False, result[0][0]
	else:
		# print("<Same Author> [confident: {0:.2f}%]".format(result[0][1]*100))
		return True, result[0][1]

def test_all_same():
	b_files = []
	for root, dirs, files in os.walk('data2/'):
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

def get_compared_docs_ae_letters_results(compare_docs):
	ae_letters_model = joblib.load('models/ae_diff_vectors_letters.sav')
	count_diff = count_same = count_h_same = count_d_same = count_h_diff = count_d_diff = 0
	ae_learned_letters = ['א' ,'פ','ל','ב','ס' ,'ם','מ' ,'ח','ד' ,'ה']

	for letter1 in compare_docs.doc1.id_letters:
		for letter2 in compare_docs.doc2.id_letters:
			if letter1.letter_name == letter2.letter_name and\
				letter1.letter_name in ae_learned_letters:
					diff_vector = create_diff_vector(letter1.ae_features, letter2.ae_features)
					is_same, _ = predict_ae(diff_vector, ae_letters_model)
					if(is_same):
						if(letter1.letter_name == 'ה'):
							count_h_same += 1
						else:
							count_d_same += 1
						count_same += 1
					else:
						if(letter1.letter_name == 'ה'):
							count_h_diff += 1
						else:
							count_d_diff += 1
						count_diff += 1

	compare_docs.letters_ae_results = {'result': 'Same' if count_same >= count_diff else 'Different',\
								   	#    'precent' : ?}
									   'count_same': count_same,\
									   'count_diff': count_diff}
	if count_same >= count_diff:
		return (count_same, count_diff, True) # True -> same auther
	else:
		return (count_same, count_diff, False) # Flase -> diff auther
	# print("results:\nsame letters: {}\ndiff letters: {}".format(count_same, count_diff))
	# print('same_h: {} diff_h: {}\nsame_d: {} diff_d: {}'.format(count_h_same, count_h_diff, count_d_same, count_d_diff))

def get_compared_docs_monkey_results(compare_docs):
	monkey_res, monkey_precent = get_monkey_result(compare_docs.doc1.monkey_features,\
												   compare_docs.doc2.monkey_features)
	compare_docs.monkey_results = {'result': 'Same' if monkey_res is True else 'Different',\
								   'precent' : monkey_precent}

def main(doc_name1, doc_name2):
	doc1, doc2 = Document(doc_name1), Document(doc_name2)

	# prepare Documents
	init_doc(doc1)
	init_doc(doc2)
		
	# ---> Verification Phase
	compare_docs = CompareDocuments(doc1, doc2)

	get_compared_docs_monkey_results(compare_docs)
	# letters_autoencoder_res = get_letters_autoencoder_results(compare_docs.doc1.letters_ae_results,\
															#   compare_docs.doc2.letters_ae_results)

					   
	# print(compare_docs.monkey_results)

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
	test_all_pairs()
	# main('500b.tiff', '500.tiff')
	# if(sys.argv[1] == 'save_all'):
	# 	main_save_all()
	# else: 
	# 	doc_name = str(sys.argv[1])
	# 	main(doc_name)

#TODO: move next functions to other file
#      no need in main file

def main_save_all():
	for root, dirs, files in os.walk(_global.DATA_PATH):
		for file in files:
			doc_name = file.split('.')[0]
			check_path_exist = "out/{}".format(doc_name)
			if os.path.exists(check_path_exist):   
				print("{}.tiff already done".format(file))
				continue
			img_name = _global.DATA_PATH + file
			img = get_prepared_doc(img_name)
			lines = get_lines(img, img_name)
			letters = get_letters(lines)
			found_letters = save_letters(letters, doc_name)


def print_predictions(preidction):
		for i, v in enumerate(preidction):
			print(str(i)+" " + _global.lang_letters[i]+": "+str(float("{0:.2f}".format(v))))
		print("______")

def createOutputDirs(doc_name):
	out_main_folder = "out"
	if not os.path.exists(out_main_folder):   # create folder to contain the line's img
		os.mkdir(out_main_folder)
	out_path = "{}/{}".format(out_main_folder, doc_name)
	if not os.path.exists(out_path):   
		os.mkdir(out_path)
	return out_path

def show_letters(letters):
	count_good = 0
	count_all = 0
	for letter in letters:
		letter = cv2.resize(letter, (_global.LETTERS_SIZE, _global.LETTERS_SIZE))
		letter = letter.reshape((_global.LETTERS_SIZE, _global.LETTERS_SIZE, 1))

		test_letter = image.img_to_array(letter)
		test_image = np.expand_dims(test_letter, axis=0)
		result = _global.lettersClassifier.predict((test_image/255))
		# print_predictions(result[0])
		if max(result[0]) > 0.995:
			selected_letter = _global.lang_letters[result[0].tolist().index(max(result[0]))]
			if selected_letter == "ץ": 
				continue
			count_all += 1
			print(selected_letter)
			cv2.imshow('',letter)
			k = cv2.waitKey(0)
			if k == 27:
				cv2.destroyAllWindows()
			else:
				count_good +=1
				cv2.destroyAllWindows()
			if count_all == 100:
				break
			plt.close('all')
	print("{} {} {}".format(count_good, count_all, count_good/count_all))
