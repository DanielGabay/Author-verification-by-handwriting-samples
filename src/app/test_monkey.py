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

#TEST:
TEST_FILE_1 = '12.tiff'
TEST_FILE_2 = '15.tiff'


BY_VECTORS = False
BY_HALF = False
#

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
		print("	>>> Identify Detected Letters")
		identified_letters = get_identified_letters(letters)  
		# identified_letters = save_letters(letters, doc_name) # save letter
		count_list = counter_list(identified_letters)
		vectors.append(count_list)

def test_model():
	files = [TEST_FILE_1,TEST_FILE_2]
	loaded_model = joblib.load(_global.MONKEY_MODEL)
	load_and_compile_letters_model(_global.LETTERS_MODEL)
	vectors = []

	for file in files:
		doc_name = file.split('.')[0]
		print("> Prepare Document {}".format(file))
		img_name = _global.DATA_PATH + file
		img = get_prepared_doc(img_name)
		print("	>>> Detecting Lines")
		lines = get_lines(img, img_name)
		print("	>>> Detecting Letters")
		append_to_vectors(vectors, lines, doc_name) 
	print("> Comparing Documents by Monkey Algoritem")
	get_result(vectors, loaded_model)


def get_result(vectors, loaded_model):
	diff_vec1 = None
	if BY_VECTORS:
		diff_vec1 = create_diff_vector(vectors[0],vectors[1])
	else:
		diff_vec1 = sum(create_diff_vector(vectors[0],vectors[1]))
		print(diff_vec1)
	prediction_monkey(loaded_model, diff_vec1) 

		
def prediction_monkey(loaded_model, diff_vec):
	diff_vec = np.asarray(diff_vec)
	result = loaded_model.predict_proba(diff_vec.reshape(1,-1))
	print("\nMonkey Result:")
	if result[0][0] > 0.5:
		print("<Different Authors> [Confident: {0:.2f}%]".format(result[0][0]*100))
	else:
		print("<Same Author> [confident: {0:.2f}%]".format(result[0][1]*100))
	
	#print('{} {}'.format(loaded_model.predict_proba(diff_vec.reshape(1,-1)),loaded_model.predict(diff_vec.reshape(1,-1))))

if __name__ == "__main__":
	if len(sys.argv) > 2:
		TEST_FILE_1 = sys.argv[1]
		TEST_FILE_2 = sys.argv[2]
		if len(sys.argv) == 4 and sys.argv[3] == 'by_vectors':
			BY_VECTORS = True
	else:
		print('Usgae: python test_monkey <file1> <file2> [by_sum/by_vectors]')
		print('Running default files: {} {}, by_sum'.format(TEST_FILE_1, TEST_FILE_2))

	_global.init('hebrew', monkey_by_vectors=BY_VECTORS)
	test_model()
