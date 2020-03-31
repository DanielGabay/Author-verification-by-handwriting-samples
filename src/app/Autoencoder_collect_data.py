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
from models.letterClassifier import load_and_compile_letters_model
import csv

PATH = os.path.dirname(os.path.abspath(__file__))
FEATUERS_FILE = PATH +'/Autoencoder/save_features.csv'

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


def write_vec_to_exel(img_name,letter,encoded_states):
	
	row = [img_name,letter]
	row.extend(encoded_states)

	with open(FEATUERS_FILE, "a", newline='') as fp:
		wr = csv.writer(fp, dialect='excel')
		wr.writerow(row)

def get_features(encoder,img_letter):

		img_letter = np.asarray(np.array(img_letter))
		img_letter = img_letter.astype('float32') / 255.
		img_letter = np.reshape(img_letter, (1, 28, 28, 1))  # adapt this if using `channels_first` image data format

		encoded_states = encoder.predict(img_letter)
		return encoded_states.ravel()

def already_done(doc_name):

	with open(FEATUERS_FILE, "r") as f:
		csvreader = csv.reader(f, delimiter=",")
		for row in csvreader:
			if len(row) > 0 and doc_name in row[0]:
				print('Element exists in Dataframe!')
				return True
	return False

def main():
	encoder = load_and_compile_ae(PATH+'/AutoEncoder/weights/encoder_encoder_full')
	PATH_TO_DATA = PATH + '/Autoencoder/dataset/try1'

	for dir_, _, files in os.walk(PATH_TO_DATA):
		for file_name in files:
			rel_dir = os.path.relpath(dir_, PATH_TO_DATA)
			rel_file = os.path.join(rel_dir, file_name)
			
			doc_name = file_name.split('.')[0]
			print(doc_name)
			if already_done(doc_name):
				continue

			img = cv2.imread("{}/{}".format(PATH_TO_DATA,rel_file), 0)
			features = get_features(encoder,img)
			write_vec_to_exel(doc_name,rel_dir,features)
			
if __name__ == "__main__":
	main()