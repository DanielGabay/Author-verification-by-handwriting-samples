import os
import sys
import cv2
import numpy as np
import pandas as pd
from keras.preprocessing import image
from keras.models import model_from_json
import _global
from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.our_utils.prepare_document import \
    get_prepared_doc
import csv

PATH = os.path.dirname(os.path.abspath(__file__))
FEATUERS_PATH = PATH

letters = ['1','2','4','5','8','12','13','15','17','24']


def load_and_compile_ae(name):
	# load json and create model
	json_file = open(name + '.json', 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	classifier = model_from_json(loaded_model_json)

	# load weights into new model
	classifier.load_weights(name + ".h5")
	print("Loaded model from disk")
	classifier.compile(optimizer='sgd', loss='mse')
	return classifier


def write_vec_to_exel(featuers_file,img_name,letter,encoded_states):
	
	row = [img_name,letter]
	row.extend(encoded_states)

	with open(featuers_file, "a", newline='') as fp:
		wr = csv.writer(fp, dialect='excel')
		wr.writerow(row)

def get_features(encoder,img_letter):

		img_letter = np.asarray(np.array(img_letter))
		img_letter = img_letter.astype('float32') / 255.
		img_letter = np.reshape(img_letter, (1, 28, 28, 1))  # adapt this if using `channels_first` image data format

		encoded_states = encoder.predict(img_letter)
		return encoded_states.ravel()

def already_done(featuers_file,doc_name):

	mode = 'r' if os.path.exists(featuers_file) else 'w+'
	with open(featuers_file, mode) as f:
		csvreader = csv.reader(f, delimiter=",")
		for row in csvreader:
			if len(row) > 0 and doc_name in row[0]:
				# print('Element exists in Dataframe!')
				return True
	return False


def get_encoders():
	encoders = {}
	for letter in letters:
		encoders.update({letter : load_and_compile_ae(PATH+'/weights/encoder_32_{}'.format(letter))})
	return encoders

def main():

	encoders = get_encoders()
	PATH_TO_DATA = PATH + '/letters'
	
	for dir_, _, files in os.walk(PATH_TO_DATA):
		for file_name in files:
			rel_dir = os.path.relpath(dir_, PATH_TO_DATA)
			rel_file = os.path.join(rel_dir, file_name)
			
			doc_name = file_name.split('.')[0]
			featuers_file = "{}/save_featuers_{}.csv".format(FEATUERS_PATH,rel_dir)
			# print(doc_name)
			if already_done(featuers_file,doc_name):
				continue
			encoder = encoders[rel_dir]
			img = cv2.imread("{}/{}".format(PATH_TO_DATA,rel_file), 0)
			features = get_features(encoder,img)
			write_vec_to_exel(featuers_file,doc_name,rel_dir,features)
			
if __name__ == "__main__":

	main()