import os

import cv2
import joblib
import numpy as np
from keras.preprocessing import image

import _global
from classes import CompareDocuments, Document, IdLetter, IdWord
from main_functions import createOutputDirs, save_letters


def get_monkey_features(found_letters):
	'''
	function just for convinent read in main.py
	'''
	return counter_list(found_letters)

def counter_list(found_letters):
	'''
	returns the 'feature vector' for a given found_letters
	'''
	count_list = [0] * 27
	for letter in found_letters:
		count_list[(letter['letter_index'])]+=1
	length = len(found_letters)
	counter_list_precent = [i * (100/length) for i in count_list]
	return counter_list_precent

def get_identified_letters(letters, from_main=False):
	# for main use only:
	if from_main:
		Id_Letters = []
	found_letters = []
	count = 0
	for letter in letters:
		letter = cv2.resize(letter, (_global.LETTERS_SIZE, _global.LETTERS_SIZE))
		letter = letter.reshape((_global.LETTERS_SIZE, _global.LETTERS_SIZE, 1))
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
			if from_main:
				Id_Letters.append(IdLetter(letter,selected_letter,letter_index + 1))
	if from_main:
		return found_letters, Id_Letters
	return found_letters

def create_diff_vector(list_1,list_2):
	diff_vector = [0] * len(list_1)
	for i in range (0,len(list_1)):
		diff_vector[i] =  abs(list_1[i] - list_2[i])
	return diff_vector


def get_monkey_result(feature_vec1, feature_vec2):
	'''
	use this function for main in order to get result
	of monkey algorithem by sending 2 feature vectors
	'''
	#loads the right monkey model
	monkey_model = joblib.load(_global.MODELS_PATH + _global.MONKEY_MODEL)
	_global.monkeyClassifier = monkey_model

	diff_vector = None
	diff_vector = create_diff_vector(feature_vec1,feature_vec2)
	if 'by_sum' in _global.MONKEY_MODEL:
		diff_vector = sum(create_diff_vector(feature_vec1,feature_vec2))
	return prediction_monkey(diff_vector)


def prediction_monkey(diff_vec, alpha = 0):
	diff_vec = np.asarray(diff_vec)
	result = _global.monkeyClassifier.predict_proba(diff_vec.reshape(1,-1))
	print("\nMonkey Result:")
	if result[0][0] > 0.5 + alpha:
		print("<Different Authors> [Confident: {0:.2f}%]".format(result[0][0]*100))
		return False, result[0][0]
	else:
		print("<Same Author> [confident: {0:.2f}%]".format(result[0][1]*100))
		return True, result[0][1]
			
#print_verbose('{} {}'.format(_global.monkeyClassifier.predict_proba(diff_vec.reshape(1,-1)),_global.monkeyClassifier.predict(diff_vec.reshape(1,-1))))

def get_compared_docs_monkey_results(compare_docs):
	monkey_res, monkey_precent = get_monkey_result(compare_docs.doc1.monkey_features,\
												   compare_docs.doc2.monkey_features)
	compare_docs.monkey_results = {'result': 'Same' if monkey_res is True else 'Different',\
								   'precent' : monkey_precent}
