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
from monkey_functions import (counter_list, create_diff_vector,
                              get_identified_letters, get_pair_letters,
                              prediction_monkey)

BY_VECTORS = False
BY_HALF = False
PRINT_VERBOSE = True

def print_verbose(str):
	if PRINT_VERBOSE:
		print(str)

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

def test_model(TEST_FILE_1, TEST_FILE_2):
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
	get_result(vectors)

def get_result(vectors, alpha = 0):
	diff_vec1 = None
	if BY_VECTORS:
		diff_vec1 = create_diff_vector(vectors[0],vectors[1])
	else:
		diff_vec1 = sum(create_diff_vector(vectors[0],vectors[1]))
		print_verbose("Sum: {}".format(diff_vec1))
	return prediction_monkey(diff_vec1, alpha) 

def test_all_same():
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
		test_model(TEST_FILE_1, TEST_FILE_2)

def get_count_list(file):
	doc_name = file.split('.')[0]
	img_name = _global.DATA_PATH + file
	img = get_prepared_doc(img_name)
	lines = get_lines(img, img_name)
	letters = get_letters(lines)
	identified_letters = get_identified_letters(letters)
	count_list = counter_list(identified_letters)
	return count_list

def test_conf_matrix():
	all_files = []
	count_vectors = []
	for root, dirs, files in os.walk(_global.DATA_PATH):
		b_files = [x for x in files if 'b' in x]
		a_files = [x.replace('b', '') for x in b_files]
		all_files = a_files + b_files
	
	for file in all_files:
		print("Get count list of {}".format(file))
		count_list = get_count_list(file)
		count_vectors.append([file, count_list])
	for alpha in range(-50,50,5):
		tp, fp, tn, fn = 0, 0, 0, 0
		tp_prec, fp_prec, tn_prec, fn_prec = [], [], [], []
		for i in range(len(count_vectors)):
			for j in range(i+1,len(count_vectors)):
				test1, test2 = count_vectors[i][0], count_vectors[j][0]
				if test1 == test2:
					continue
				same_author = False
				if test1.replace('b','') == test2 or test2.replace('b','') == test1:
					same_author = True
				# print("\n---------------------")
				# print("Test: {} {}".format(test1, test2))
				diff_vectors = []
				diff_vectors.append(count_vectors[i][1])
				diff_vectors.append(count_vectors[j][1])
				result, precent = get_result(diff_vectors, alpha/100) 
				precent *= 100
				if result and same_author:
					tp += 1
					tp_prec.append(precent)
				elif not result and same_author:
					fn += 1
					fn_prec.append(precent)
				elif not result and not same_author:
					tn += 1
					tn_prec.append(precent)
				elif result and not same_author:
					fp += 1
					fp_prec.append(precent)
		print("\n------------------")
		print("bigger than threshold={0:.2f} is different person".format(alpha/100+0.5))
		print("Model accuracy: {0:.2f}%".format((tn+tp)/(tn+tp+fn+fp)*100))
		print("Confusion Matrix:")
		print("True-Negative: {0:.2f}\tFalse-Negative: {0:.2f}".format(tn, fn))
		print("False-Positive: {0:.2f}\tTrue-Positive: {0:.2f}".format(fp, tp))
		print("")
		print("True-Negative-Precent: mean:{0:.2f} std:{0:.2f}".format(np.mean(tn_prec,axis=0),np.std(tn_prec,axis=0)))
		print("False-Negative-Precent: mean:{0:.2f} std:{0:.2f}".format(np.mean(fn_prec,axis=0),np.std(fn_prec,axis=0)))
		print("False-Positive-Precent: mean:{0:.2f} std:{0:.2f}".format(np.mean(fp_prec,axis=0),np.std(fp_prec,axis=0)))
		print("True-Positive-Precent: mean:{0:.2f} std:{0:.2f}".format(np.mean(tp_prec,axis=0),np.std(tp_prec,axis=0)))

if __name__ == "__main__":
	if len(sys.argv) > 1:
		if 'by_vectors' in sys.argv:
			BY_VECTORS = True
		_global.init('hebrew', monkey_by_vectors=BY_VECTORS)
		if sys.argv[1] == 'conf_matrix':
			test_conf_matrix()
			sys.exit(0)
		if sys.argv[1] == 'all_same':
			test_all_same()
			sys.exit(0)
		TEST_FILE_1 = sys.argv[1]
		TEST_FILE_2 = sys.argv[2]
		test_model(TEST_FILE_1, TEST_FILE_2)

	else:
		print('Usgae Option1: python test_monkey <file1> <file2> [by_sum/by_vectors]')
		print('Usage Option2: python test_monkey all_same [by_sum/by_vectors]')
