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

DATA_PATH = "data/"

MODEL_SAVE_AS = "monkey_model.sav"

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
hebrew_letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י'\
			,'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',\
		   'ך', 'ם', 'ן', 'ף', 'ץ']


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



def append_to_vectors(vectors, lines, classifier, half_lines=False):
	if half_lines:
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


if __name__ == "__main__":

	if(len(sys.argv) < 2):
		print("Usage: python train_monkey.py by_vectors / by_sum")
		sys.exit(1)
	if(sys.argv[1] == 'by_vectors'):
		train_model(True)
	else: 
		train_model(False)

