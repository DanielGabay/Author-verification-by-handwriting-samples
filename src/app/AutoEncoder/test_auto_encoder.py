from keras.models import load_model
import numpy as np
import os
from keras.models import model_from_json
import cv2

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

def test(name):
	path = os.path.dirname(os.path.abspath(__file__))
	path_weights = path + '/weights'

	encoder = load_and_compile_ae(path_weights+'/encoder_4')
	decoder = load_and_compile_ae(path_weights+'/decoder_4')

	img = cv2.imread(path + name, 0)
	inputs = np.array(img)
	x = encoder.predict(inputs)
	y = decoder.predict(x)

	print('Input: {}'.format(inputs))
	print('Encoded: {}'.format(x))
	print('Decoded: {}'.format(y))

if __name__ == '__main__':
	test('/dataset/4/1_52.jpeg')