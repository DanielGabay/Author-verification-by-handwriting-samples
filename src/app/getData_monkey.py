import os
import sys

import cv2
import numpy as np
import pandas as pd
from keras.preprocessing import image

from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.our_utils.prepare_document import \
	get_prepared_doc
from models.letterClassifier import load_and_compile_model

"""
the main goal of this file is to collect data in order to train a logistic regression model.
every file of essay , we divide to two.To each part we calculate the counter_vector.
1.equal.csv - each line is an subtraction of the counter_vectors of an equal author.
2.count_vectors.csv - each line is the counter_vector of a part.
"""

DATA_PATH = "data/"
MODEL = 'model99'
EQUAL_FILE = 'equal.csv'
COUNT_VEC_FILE = "count_vectors.csv"


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
hebrew_letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י'\
			,'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',\
		   'ך', 'ם', 'ן', 'ף', 'ץ']

class DividedDoc:
	def __init__(self,letter_vec1, letter_vec2):
		self._letter_vec1 = letter_vec1
		self._letter_vec2 = letter_vec2

def calculate_diff(list_1,list_2):
	count = 0
	for i in range (0,len(list_1)):
		count+= abs(list_1[i] - list_2[i])
	return count


"""
function to check if the Monkey algoritem can be useful.we check the mean & std to see if there is a diffrent between
counter_vectors subtraction of eual author to counter_vectors subtraction of diffrent author. 
"""
def sum_diff(list_of_pairs):
	sumEqual = []
	sumDiff = []
	for i in range(len(list_of_pairs)):
		sumEqual.append(calculate_diff(list_of_pairs[i]._letter_vec1,list_of_pairs[i]._letter_vec2))
		print(list_of_pairs[i]._letter_vec1)
		print(list_of_pairs[i]._letter_vec2)
		
		for j in range(i+1,len(list_of_pairs)):
			sumDiff.append(calculate_diff(list_of_pairs[i]._letter_vec1,list_of_pairs[j]._letter_vec1))
			sumDiff.append(calculate_diff(list_of_pairs[i]._letter_vec1,list_of_pairs[j]._letter_vec2))
			sumDiff.append(calculate_diff(list_of_pairs[i]._letter_vec2,list_of_pairs[j]._letter_vec1))
			sumDiff.append(calculate_diff(list_of_pairs[i]._letter_vec2,list_of_pairs[j]._letter_vec2))
		
	print("Equal mean: {}".format(np.mean(np.asarray(sumEqual))))
	print("Equal std: {}".format(np.std(np.asarray(sumEqual))))
	print("Diff mean: {}".format(np.mean(np.asarray(sumDiff))))
	print("Diff std: {}".format(np.std(np.asarray(sumDiff))))

def create_diff_vector(list_1,list_2):
	diff_vector = [0] * len(list_1)
	for i in range (0,len(list_1)):
		diff_vector[i] =  abs(list_1[i] - list_2[i])
	return diff_vector

def counter_list(found_letters):
	count_list = [0] * 27
	for letter in found_letters:
		count_list[(letter['letter_index'])]+=1
	precent = [i * (100/len(found_letters)) for i in count_list]
	return precent

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

def write_to_csv(dfName,vecName,vector):
	#write a new line to the dfName.
	df = pd.read_csv(dfName)
	vector.insert(0,vecName)  # add the vecName 
	modDfObj = df.append(pd.Series(vector, index=df.columns ), ignore_index=True)
	modDfObj.to_csv(dfName, mode='w',index = False)
	

def already_done(doc_name):
	df = pd.read_csv(EQUAL_FILE)
			
	if int(doc_name) in df['Vector'].values.tolist():
		print('Element exists in Dataframe!')
		return True
	return False

def main():
	classifier = load_and_compile_model(MODEL)  # load the letter model
	divided_docs = []
	for root, dirs, files in os.walk(DATA_PATH):
		for file in files:
			doc_name = file.split('.')[0]
			print(doc_name)

			if already_done(doc_name):
				continue
			
			img_name = DATA_PATH + file
			img = get_prepared_doc(img_name)
			lines = get_lines(img, img_name)
			letters_1,letters_2 = get_pair_letters(lines,classifier)
			
			count_list_1 = counter_list(letters_1)  
			count_list_2 = counter_list(letters_2)

			diff_vec = create_diff_vector(count_list_1,count_list_2)
			write_to_csv(EQUAL_FILE,doc_name,diff_vec)
			write_to_csv(COUNT_VEC_FILE,doc_name+'_1',count_list_1)
			write_to_csv(COUNT_VEC_FILE,doc_name+'_2',count_list_2)
			



if __name__ == "__main__":
	main()

