import os
import sys
import cv2
import joblib
import numpy as np
import pandas as pd
from keras.preprocessing import image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler

import _global
from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.our_utils.prepare_document import \
    get_prepared_doc
from main import save_letters
from models.letterClassifier import load_and_compile_letters_model
from monkey_collect_data import counter_list, create_diff_vector


BY_VECTORS = False
BY_HALF = False
PRINT_VERBOSE = False

def print_verbose(str):
	if PRINT_VERBOSE:
		print(str)

def get_identified_letters(letters):
	found_letters = []
	count = 0
	for letter in letters:
		letter = cv2.resize(letter.image_letter, (28, 28))
		letter = letter.reshape((28, 28, 1))
		test_letter = image.img_to_array(letter)
		test_image = np.expand_dims(test_letter, axis=0)
		result = _global.lettersClassifier.predict((test_image/255))
		if max(result[0]) > 0.995:
			letter_index = result[0].tolist().index(max(result[0]))
			selected_letter = _global.lang_letters[result[0].tolist().index(max(result[0]))]
			if selected_letter == "ץ": 
				continue
			count += 1
			found_letters.append({'image_letter': letter , 'letter_index': letter_index, 'letter_name': selected_letter})
	return found_letters

# divide every file to 2 different 'persons'.
def get_pair_letters(lines):
	letters = get_letters(lines)
	size = len(letters)//2
	letters_1 = letters[:size]
	letters_2 = letters[size:]
	identified_letters_1 = get_identified_letters(letters_1)
	identified_letters_2 = get_identified_letters(letters_2)
	return identified_letters_1,identified_letters_2

def rescale(data):
	# built in function to rescale data
	scaler = StandardScaler()
	return scaler.fit_transform(data)

def append_to_vectors(vectors, lines, doc_name):
	if BY_HALF:
		letters_1,letters_2 = get_pair_letters(lines)
		count_list_1 = counter_list(letters_1)  
		count_list_2 = counter_list(letters_2)
		vectors.append(count_list_1)
		vectors.append(count_list_2)
	else:
		letters = get_letters(lines)
		print_verbose("	>>> Identify Detected Letters")
		identified_letters = get_identified_letters(letters)  
		# identified_letters = save_letters(letters, doc_name) # save letter
		count_list = counter_list(identified_letters)
		vectors.append(count_list)

def load_models():
	loaded_model = joblib.load(_global.MONKEY_MODEL)
	load_and_compile_letters_model(_global.LETTERS_MODEL)
	return loaded_model

def test_model(TEST_FILE_1, TEST_FILE_2, loaded_model):
	files = [TEST_FILE_1,TEST_FILE_2]
	vectors = []
	for file in files:
		doc_name = file.split('.')[0]
		print_verbose("> Prepare Document {}".format(file))
		img_name = _global.DATA_PATH + file
		img = get_prepared_doc(img_name)
		print_verbose("	>>> Detecting Lines")
		lines = get_lines(img, img_name)
		print_verbose("	>>> Detecting Letters")
		append_to_vectors(vectors, lines, doc_name)
	print_verbose("> Comparing Documents by Monkey Algoritem")
	get_result(vectors, loaded_model)


def get_result(vectors, loaded_model):
	diff_vec1 = None
	if BY_VECTORS:
		diff_vec1 = create_diff_vector(vectors[0],vectors[1])
	else:
		diff_vec1 = sum(create_diff_vector(vectors[0],vectors[1]))
		print("Sum: {}".format(diff_vec1))
	return prediction_monkey(loaded_model, diff_vec1) 

def prediction_monkey(loaded_model, diff_vec):
	diff_vec = np.asarray(diff_vec)
	result = loaded_model.predict_proba(diff_vec.reshape(1,-1))
	print("\nMonkey Result:")
	if result[0][0] > 0.5:
		print("<Different Authors> [Confident: {0:.2f}%]".format(result[0][0]*100))
		return False, result[0][0]
	else:
		print("<Same Author> [confident: {0:.2f}%]".format(result[0][1]*100))
		return True, result[0][1]
		
	#print_verbose('{} {}'.format(loaded_model.predict_proba(diff_vec.reshape(1,-1)),loaded_model.predict(diff_vec.reshape(1,-1))))

def test_all_same(loaded_model):
	b_files = []
	for root, dirs, files in os.walk(_global.DATA_PATH):
		b_files = [x for x in files if 'b' in x]	
	for i in range(len(b_files)):
		TEST_FILE_1 = b_files[i]
		# uncomment if comparing *.tiff and *b.png files
		# TEST_FILE_2 = b_files[i].replace('b','').replace('png','tiff')
		TEST_FILE_2 = b_files[i].replace('b','')
		print("\n---------------------")
		print("Test: {} {}".format(TEST_FILE_1, TEST_FILE_2))
		test_model(TEST_FILE_1, TEST_FILE_2, loaded_model)

def get_count_list(file):
	doc_name = file.split('.')[0]
	img_name = _global.DATA_PATH + file
	img = get_prepared_doc(img_name)
	lines = get_lines(img, img_name)
	letters = get_letters(lines)
	identified_letters = get_identified_letters(letters)
	count_list = counter_list(identified_letters)
	return count_list

def test_conf_matrix(loaded_model):
	all_files = []
	count_vectors = []
	tp, fp, tn, fn = 0, 0, 0, 0
	tp_prec, fp_prec, tn_prec, fn_prec = 0, 0, 0, 0
	for root, dirs, files in os.walk(_global.DATA_PATH):
		b_files = [x for x in files if 'b' in x]
		a_files = [x.replace('b', '') for x in b_files]
		all_files = a_files + b_files
	
	for file in all_files:
		print("Get count list of {}".format(file))
		count_list = get_count_list(file)
		count_vectors.append([file, count_list])
	
	for i in range(len(count_vectors)):
		for j in range(i+1,len(count_vectors)):
			test1, test2 = count_vectors[i][0], count_vectors[j][0]
			if test1 == test2:
				continue
			same_author = False
			if test1.replace('b','') == test2 or test2.replace('b','') == test1:
				same_author = True
			print("\n---------------------")
			print("Test: {} {}".format(test1, test2))
			diff_vectors = []
			diff_vectors.append(count_vectors[i][1])
			diff_vectors.append(count_vectors[j][1])
			result, precent = get_result(diff_vectors, loaded_model) 
			if result and same_author:
				tp += 1
				tp_prec += precent
			elif not result and same_author:
				fn += 1
				fn_prec += precent
			elif not result and not same_author:
				tn += 1
				tn_prec += precent
			elif result and not same_author:
				fp += 1
				fp_prec += precent
			print("True-Negative: {}\tFalse-Negative: {}".format(tn, fn))
			print("False-Positive: {}\tTrue-Positive: {}".format(fp, tp))
	
	print("True-Negative-Precent: {}\tFalse-Negative-Precent: {}".format(tn_prec/tn, fn_prec/fn))
	print("False-Positive-Precent: {}\tTrue-Positive-Precent: {}".format(fp_prec/fp, tp_prec/tp))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if 'by_vectors' in sys.argv:
			BY_VECTORS = True
		_global.init('hebrew', monkey_by_vectors=BY_VECTORS)
		loaded_model = load_models()
		if sys.argv[1] == 'conf_matrix':
			test_conf_matrix(loaded_model)
			sys.exit(0)
		if sys.argv[1] == 'all_same':
			test_all_same(loaded_model)
			sys.exit(0)
		TEST_FILE_1 = sys.argv[1]
		TEST_FILE_2 = sys.argv[2]
		test_model(TEST_FILE_1, TEST_FILE_2, loaded_model)

	else:
		print('Usgae Option1: python test_monkey <file1> <file2> [by_sum/by_vectors]')
		print('Usage Option2: python test_monkey all_same [by_sum/by_vectors]')
	
