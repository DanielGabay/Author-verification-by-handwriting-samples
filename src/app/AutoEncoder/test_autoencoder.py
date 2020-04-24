from keras.models import load_model
import numpy as np
import os
from keras.models import model_from_json
import cv2
import matplotlib.pyplot as plt
import sys
import csv
import pandas as pd


FEATUERS_FILE ='save_features.csv'

def already_done(doc_name):

	with open(FEATUERS_FILE, "r") as f:
		csvreader = csv.reader(f, delimiter=",")
		for row in csvreader:
			print(row)
			if len(row) > 0 and doc_name in row[0]:
				print('Element exists in Dataframe!')
				return True
	return False
	
	# df = pd.read_csv(FEATUERS_FILE)
			
	# if int(doc_name) in df['file_name'].values.tolist():
	# 	print('Element exists in Dataframe!')
	# 	return True
	# return False

def load_and_compile_ae(name):
	# load json and create model
	json_file = open(name + '.json', 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	classifier = model_from_json(loaded_model_json)

	# load weights into new model
	classifier.load_weights(name + ".h5")
	# print("Loaded model {} from disk".format(name))
	classifier.compile(optimizer='sgd', loss='mse')
	return classifier

def write_vec_to_exel(df_name,file,letter,count,encoded_states):
	
	row = [file,letter,count]
	row.extend(encoded_states)

	with open(df_name, "a", newline='') as fp:
		wr = csv.writer(fp, dialect='excel')
		wr.writerow(row)

def get_letters_ae_features(letters):
	path_weights = 'AutoEncoder/weights'

	encoder = load_and_compile_ae(path_weights+'/encoder_encoder_32')
	autoencoder = load_and_compile_ae(path_weights+'/encoder_encoder_32')

	for letter in letters:
		img = np.asarray(np.array(letter.letter_img))
		img = img.astype('float32') / 255.
		img = np.reshape(img, (1, 28, 28, 1))  # adapt this if using `channels_first` image data format
		letter.ae_features = encoder.predict(img).ravel()

def test(name):
	path = os.path.dirname(os.path.abspath(__file__))
	path_weights = path + '/weights'

	encoder = load_and_compile_ae(path_weights+'/encoder_encoder_full')
	autoencoder = load_and_compile_ae(path_weights+'/encoder_autoencoder_full')
	
	img = cv2.imread(path + name, 0)
	img = np.asarray(np.array(img))
	img = img.astype('float32') / 255.
	img = np.reshape(img, (1, 28, 28, 1))  # adapt this if using `channels_first` image data format


	image_decoder= autoencoder.predict(img)
	encoded_states = encoder.predict(img)
	print('encoder result: {}'.format(encoded_states))
	print(type(encoded_states))
	# cv2.imshow('',image_decoder.reshape(28,28))
	# cv2.waitKey(0)
	
	# plt.imshow(image_decoder.reshape(28,28))
	# plt.show()
	# encoded_states = encoded_states.tolist()
	# print(encoded_states.shape)
	# print(encoded_states.ravel())  # convert to a list
	# print(len(encoded_states.ravel()))
	return encoded_states.ravel()


if __name__ == '__main__':


	print(already_done('1'))
	print('#@@@@')
	path = os.path.dirname(os.path.abspath(__file__))

	x = [1,2,3]
	y = [3,2,3]

	features = test('/dataset/4.jpeg')
	features1 = test('/dataset/5.jpeg')
	# features = (np.subtract(features,features).tolist())
	# features = [abs(number) for number in features]

	write_vec_to_exel("./save_features.csv","1","8",'1',features1)


	sys.exit(0)
	x.append("8")
	print(x)

	print(np.subtract(x,y))
	print(type(np.subtract(x,y)))
	print(type(np.subtract(x,y).tolist()))
	print(np.subtract(x,y).tolist())
