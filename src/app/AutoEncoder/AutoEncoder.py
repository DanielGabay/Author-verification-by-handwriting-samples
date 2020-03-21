import os
import sys

import cv2
import joblib
import keras
import numpy as np
import tensorflow as tf
from keras import backend as K
from keras.callbacks import TensorBoard
from keras.layers import Conv2D, Dense, Input, MaxPooling2D, UpSampling2D
from keras.models import Model


os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="1" #model will be trained on GPU 1

class AutoEncoder:
	def __init__(self, encoding_dim=32):
		self.encoding_dim = encoding_dim
		
	def _encoder(self):
		inputs = Input(shape=(784,))
		encoded = Dense(self.encoding_dim, activation='relu')(inputs)
		model = Model(inputs, encoded)
		self.encoder = model
		return model

	def _decoder(self):
		inputs = Input(shape=(784,))
		decoded = Dense(784)(inputs)
		model = Model(inputs, decoded)
		self.decoder = model
		return model

	# def encoder_decoder(self):
	# 	input_img = Input(shape=(28, 28, 1))

	# 	x = Conv2D(16, (3, 3), activation='relu', padding='same')(input_img)
	# 	x = MaxPooling2D((2, 2), padding='same')(x)
	# 	x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
	# 	x = MaxPooling2D((2, 2), padding='same')(x)
	# 	x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
	# 	encoded = MaxPooling2D((2, 2), padding='same')(x)
	# 	self.encoder = Model(input_img, encoded)
	# 	# at this point the representation is (4, 4, 8) i.e. 128-dimensional

	# 	x = Conv2D(8, (3, 3), activation='relu', padding='same')(encoded)
	# 	x = UpSampling2D((2, 2))(x)
	# 	x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
	# 	x = UpSampling2D((2, 2))(x)
	# 	x = Conv2D(16, (3, 3), activation='relu')(x)
	# 	x = UpSampling2D((2, 2))(x)
	# 	decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)
	# 	self.decoder = Model(input_img, decoded)
	# 	self.model = self.decoder
	# 	return self.model

	def encoder_decoder(self):
		ec = self._encoder()
		dc = self._decoder()
		print(self.X[0].shape)
		inputs = Input(shape=(28, 28, 784))
		ec_out = ec(inputs)
		dc_out = dc(ec_out)
		model = Model(inputs, dc_out)

		self.model = model
		return model

	def fit(self, batch_size=10, epochs=10):
		self.model.compile(optimizer='sgd', loss='mse')
		self.model.fit(self.X, self.X,
						epochs=epochs,
						batch_size=batch_size)

	def read_dataset(self, path):
		data = []
		if not hasattr(self, 'X'):
			self.X = None

		for root, dirs, files in os.walk(path):
			for file in files:
				img = cv2.imread(path + "/" + file, 0)
				data.append(np.array(img))
		self.X = np.asarray(data)
		print(len(self.X))
		# self.X = np.reshape(self.X, (len(self.X), 28, 28, 1))

	def save(self, name=""):
		path = os.path.dirname(os.path.abspath(__file__))
		path += "/weights/"
		if not os.path.exists(path):
			os.mkdir(path)

		# save train to Json
		encoder_json = self.encoder.to_json()
		with open(path + "encoder_" + name +".json" ,"w") as json_file:
			json_file.write(encoder_json)
		# serialize weights to HDF5
		self.encoder.save_weights(path + "encoder_" + name + ".h5")

		decoder_json = self.decoder.to_json()
		with open(path + "decoder_" + name +".json" ,"w") as json_file:
			json_file.write(decoder_json)
		# serialize weights to HDF5
		self.decoder.save_weights(path + "decoder_" + name + ".h5")

		ae_json = self.model.to_json()
		with open(path + "ae_" + name + ".json" ,"w") as json_file:
			json_file.write(decoder_json)
		# serialize weights to HDF5
		self.model.save_weights(path + "ae_" + name + ".h5")


if __name__ == '__main__':
	path = os.path.dirname(os.path.abspath(__file__))
	path += '/dataset/5'
	ae = AutoEncoder()
	ae.read_dataset(path)
	ae.encoder_decoder()
	ae.fit(batch_size=50, epochs=2)
	ae.save("4")
