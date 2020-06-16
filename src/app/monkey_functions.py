import os

import cv2
import joblib
import numpy as np
from keras.preprocessing import image
from extractComparisonFeatures.detectLetters import get_letters

import _global
from classes import CompareDocuments, Document, IdLetter, IdWord

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
		count_list[letter.letter_index]+=1
	length = len(found_letters)
	counter_list_precent = [i * (100/length) for i in count_list]
	return counter_list_precent

def get_identified_letters(letters):
	return _get_identified_letters(letters)
	
def _get_identified_letters(letters):
	# for main use only:
	Id_Letters = []
	count = 0
	letter_index_improved = 0
	for letter in letters:
		letter = cv2.resize(letter, (_global.LETTERS_SIZE, _global.LETTERS_SIZE))
		letter = letter.reshape((_global.LETTERS_SIZE, _global.LETTERS_SIZE, 1))
		test_letter = image.img_to_array(letter)
		test_image = np.expand_dims(test_letter, axis=0)
		result = _global.lettersClassifier.predict((test_image/255))
		if max(result[0]) > 0.995:
			letter_index = result[0].tolist().index(max(result[0]))
			selected_letter = _global.lang_letters.get(letter_index)
			if selected_letter == "ץ":
				continue
			if selected_letter in _global.ae_trained_letters.values():
				improved_result = _global.lettersImprovedClassifier.predict((test_image/255))
				letter_index_improved = improved_result[0].tolist().index(max(improved_result[0]))
				if max(improved_result[0]) < 0.8:
					pass
					# save_name = "filtered_letters/{}_{}_{:.2f}.jpeg".format(letter_index_improved, count, max(improved_result[0]))
					# cv2.imwrite(save_name,letter)
				else:
					# save_name = "filtered_letters/good/{}_{}_{:.2f}.jpeg".format(letter_index_improved, count, max(improved_result[0]))
					# cv2.imwrite(save_name,letter)
					if letter_index_improved != 30:
						Id_Letters.append(IdLetter(letter,selected_letter, letter_index))
						count += 1
			else:
				count += 1
				Id_Letters.append(IdLetter(letter,selected_letter, letter_index))
		
	return Id_Letters

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
	diff_vector = None
	diff_vector = create_diff_vector(feature_vec1,feature_vec2)
	if 'Sum' in _global.MONKEY_MODEL:
		diff_vector = sum(create_diff_vector(feature_vec1,feature_vec2))
	return prediction_monkey(diff_vector)


def prediction_monkey(diff_vec, alpha = 0, print_pred=True):
	diff_vec = np.asarray(diff_vec)
	result = _global.monkeyClassifier.predict_proba(diff_vec.reshape(1,-1))
	if print_pred:
		print("\nMonkey Result:")
	if result[0][0] > 0.5 + alpha:
		if print_pred:
			print("<Different Authors> [Confident: {0:.2f}%]".format(result[0][0]*100))
		return False, result[0][0]
	else:
		if print_pred:
			print("<Same Author> [confident: {0:.2f}%]".format(result[0][1]*100))
		return True, result[0][1]
			
#print_verbose('{} {}'.format(_global.monkeyClassifier.predict_proba(diff_vec.reshape(1,-1)),_global.monkeyClassifier.predict(diff_vec.reshape(1,-1))))

def get_compared_docs_monkey_results(compare_docs):
	monkey_res, monkey_precent = get_monkey_result(compare_docs.doc1.monkey_features,\
												   compare_docs.doc2.monkey_features)
	compare_docs.monkey_results = {'result': 'Same' if monkey_res is True else 'Different',\
								   'precent' : monkey_precent}


# divide every file to 2 diffrent 'persons'.
def get_pair_letters(lines):
	letters = get_letters(lines)
	size = len(letters)//2
	letters_1 = letters[:size]
	letters_2 = letters[size:]
	identified_letters_1 = get_identified_letters(letters_1)
	identified_letters_2 = get_identified_letters(letters_2)

	return identified_letters_1,identified_letters_2

#TODO: remove in future
# use this to filter letters for Auto-encoder
# def get_identified_letters2(letters, from_main=False):
# 	# for main use only:
# 	if from_main:
# 		Id_Letters = []
# 	found_letters = []
# 	count = 0
# 	count_filterd_letters = 0
# 	for letter in letters:
# 		letter = cv2.resize(letter, (_global.LETTERS_SIZE, _global.LETTERS_SIZE))
# 		letter = letter.reshape((_global.LETTERS_SIZE, _global.LETTERS_SIZE, 1))
# 		test_letter = image.img_to_array(letter)
# 		test_image = np.expand_dims(test_letter, axis=0)
# 		result = _global.lettersClassifier.predict((test_image/255))
# 		if max(result[0]) > 0.995:
# 			letter_index = result[0].tolist().index(max(result[0]))
# 			selected_letter = _global.lang_letters.get(result[0].tolist().index(max(result[0])))
# 			if selected_letter == "ץ":
# 				continue
# 			save_letter = False
# 			if selected_letter in _global.ae_trained_letters.values():
# 				print(selected_letter)
# 				while(1):
# 					cv2.imshow('', letter)
# 					k = cv2.waitKey(0)
# 					if k==27:    # Esc key to stop
# 						save_letter = True
# 						break
# 					else:
# 						save_letter = False # else 
# 						count_filterd_letters += 1
# 						break
# 			count += 1
# 			found_letters.append({'image_letter': letter , 'letter_index': letter_index, 'letter_name': selected_letter})
# 			if from_main and save_letter:
# 				print("saved")
# 				Id_Letters.append(IdLetter(letter,selected_letter))
# 	if from_main:
# 		print("filterd: {}".format(count_filterd_letters))
# 		return found_letters, Id_Letters
# 	return found_letters
