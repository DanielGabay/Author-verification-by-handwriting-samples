from keras.models import load_model
import numpy as np
import os
from keras.models import model_from_json
import cv2
import matplotlib.pyplot as plt

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

	encoder = load_and_compile_ae(path_weights+'/encoder_encoder')
	autoencoder = load_and_compile_ae(path_weights+'/encoder_autoencoder')
	
	img = cv2.imread(path + name, 0)


	img = np.asarray(np.array(img))
	print(img.shape)
	img = img.astype('float32') / 255.
	print(img.shape)
	img = np.reshape(img, (1, 28, 28, 1))  # adapt this if using `channels_first` image data format


	image_decoder= autoencoder.predict(img)
	encoded_states = encoder.predict(img)
	print('encoder result: {}'.format(encoded_states))
	print(type(encoded_states))
	cv2.imshow('',image_decoder.reshape(28,28))
	cv2.waitKey(0)

	# plt.imshow(image_decoder.reshape(28,28))
	# plt.show()
	

	print(encoded_states.shape)
	


if __name__ == '__main__':
	test('/dataset/sux3.jpeg')