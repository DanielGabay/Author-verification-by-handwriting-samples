import os
import sys

import cv2
import numpy as np
import pandas as pd
from keras.preprocessing import image
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
import joblib

from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.our_utils.prepare_document import \
	get_prepared_doc
from models.letterClassifier import load_and_compile_model
from getData_monkey import create_diff_vector
from getData_monkey import counter_list

DATA_PATH = "data/"
MODEL = 'model99'
MODEL_LOAD_FROM = "monkey_model.sav"

#TEST:
TEST_FILE_1 = '1.tiff'
TEST_FILE_2 = '2.tiff'
BY_VECTORS = False
BY_HALF = True
#

hebrew_letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י'\
			,'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',\
		   'ך', 'ם', 'ן', 'ף', 'ץ']





#create the 'diffrent auther' X samples --> sub the counter_vec of diffrent authers



###


def get_identified_letters(letters, classifier):
	found_letters = []
	count = 0
	for letter in letters:
		letter = cv2.resize(letter.image_letter, (28, 28))
		letter = letter.reshape((28, 28, 1))
		test_letter = image.img_to_array(letter)
		test_image = np.expand_dims(test_letter, axis=0)
		result = classifier.predict((test_image/255))
		if max(result[0]) > 0.995:
			letter_index = result[0].tolist().index(max(result[0]))
			selected_letter = hebrew_letters[result[0].tolist().index(max(result[0]))]
			if selected_letter == "ץ": 
				continue
			count += 1
			found_letters.append({'image_letter': letter , 'letter_index': letter_index, 'letter_name': selected_letter})
	return found_letters

# divide every file to 2 diffrent 'persons'.
def get_pair_letters(lines,classifier):
	letters = get_letters(lines)
	size = len(letters)//2
	letters_1 = letters[:size]
	letters_2 = letters[size:]
	identified_letters_1 = get_identified_letters(letters_1,classifier)
	identified_letters_2 = get_identified_letters(letters_2,classifier)

	return identified_letters_1,identified_letters_2


def rescale(data):
	# built in function to rescale data
	scaler = StandardScaler()
	return scaler.fit_transform(data)


def append_to_vectors(vectors, lines, classifier):
	if BY_HALF:
		letters_1,letters_2 = get_pair_letters(lines,classifier)
		count_list_1 = counter_list(letters_1)  
		count_list_2 = counter_list(letters_2)
		
		vectors.append(count_list_1)
		vectors.append(count_list_2)
	else:
		letters = get_letters(lines)
		identified_letters = get_identified_letters(letters,classifier)
		count_list = counter_list(identified_letters)
		vectors.append(count_list)

def test_model():
	loaded_model = joblib.load(MODEL_LOAD_FROM)
	classifier = load_and_compile_model(MODEL)
	vectors = []

	for root, dirs, files in os.walk(DATA_PATH):
		for file in files:
			if file != TEST_FILE_1 and  file != TEST_FILE_2:
				continue
			doc_name = file.split('.')[0]
			print(doc_name)
			img_name = DATA_PATH + file
			img = get_prepared_doc(img_name)
			lines = get_lines(img, img_name)
			letters = get_letters(lines)
			append_to_vectors(vectors, lines, classifier) 
	
	diff_vec1 = sum(create_diff_vector(vectors[0],vectors[1]))
	diff_vec2 = sum(create_diff_vector(vectors[0],vectors[2]))
	diff_vec3 = sum(create_diff_vector(vectors[0],vectors[3]))
	diff_vec4 = sum(create_diff_vector(vectors[1],vectors[2]))
	diff_vec5 = sum(create_diff_vector(vectors[1],vectors[3]))
	diff_vec6 = sum(create_diff_vector(vectors[2],vectors[3]))
	# print(diff_vec1)
	# print(diff_vec6)
	# print(diff_vec2)
	# print(diff_vec3)
	# print(diff_vec4)
	# print(diff_vec5)
	# diff_vec1 = create_diff_vector(vectors[0],vectors[1])
	# diff_vec2 = create_diff_vector(vectors[0],vectors[2])
	# diff_vec3 = create_diff_vector(vectors[0],vectors[3])
	# diff_vec4 = create_diff_vector(vectors[1],vectors[2])
	# diff_vec5 = create_diff_vector(vectors[1],vectors[3])
	# diff_vec6 = create_diff_vector(vectors[2],vectors[3])
	# print(sum(diff_vec1))
	# print(sum(diff_vec6))
	# print(sum(diff_vec2))
	# print(sum(diff_vec3))
	# print(sum(diff_vec4))
	# print(sum(diff_vec5))
	prediction_monkey(loaded_model,diff_vec1) # '1')
	prediction_monkey(loaded_model,diff_vec6) # '1')
	prediction_monkey(loaded_model,diff_vec2) # '0')
	prediction_monkey(loaded_model,diff_vec3) # '0')
	prediction_monkey(loaded_model,diff_vec4) # '0')
	prediction_monkey(loaded_model,diff_vec5) # '0')
		
def prediction_monkey(loaded_model, diff_vec):
	diff_vec = np.asarray(diff_vec)
	# diff_vec = rescale(diff_vec.reshape(-1,1))
	print('{} {}'.format(loaded_model.predict_proba(diff_vec.reshape(1,-1)),loaded_model.predict(diff_vec.reshape(1,-1))))

if __name__ == "__main__":
	if(len(sys.argv) > 3 and sys.argv[1] == 'by_vectors'):
		BY_VECTORS = True
	
	if len(sys.argv) > 4:
		TEST_FILE_1 = sys.argv[2]
		TEST_FILE_2 = sys.argv[3]
	
	test_model()
