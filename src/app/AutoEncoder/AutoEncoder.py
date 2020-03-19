import keras
from keras.layers import Input, Dense
from keras.models import Model
from keras.callbacks import TensorBoard
import numpy as np 
import os
import joblib
import tensorflow as tf

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="1" #model will be trained on GPU 1

class AutoEncoder:
	def __init__(self, encoding_dim=3):
		self.encoding_dim = encoding_dim
		r = lambda: np.random.randint(1, 3)
		self.x = np.array([[r(),r(),r()] for _ in range(1000)])
		print(self.x)

	def _encoder(self):
		inputs = Input(shape=(self.x[0].shape))
		encoded = Dense(self.encoding_dim, activation='relu')(inputs)
		model = Model(inputs, encoded)
		self.encoder = model
		return model

	def _decoder(self):
		inputs = Input(shape=(self.encoding_dim,))
		decoded = Dense(3)(inputs)
		model = Model(inputs, decoded)
		self.decoder = model
		return model

	def encoder_decoder(self):
		ec = self._encoder()
		dc = self._decoder()
		
		inputs = Input(shape=self.x[0].shape)
		ec_out = ec(inputs)
		dc_out = dc(ec_out)
		model = Model(inputs, dc_out)
		
		self.model = model
		return model

	def fit(self, batch_size=10, epochs=300):
		self.model.compile(optimizer='sgd', loss='mse')
		self.model.fit(self.x, self.x,
						epochs=epochs,
						batch_size=batch_size)

	def save(self):
		path = os.path.dirname(os.path.abspath(__file__))
		print(path)
		# joblib.dump(self.encoder, path +'/encoder_weights.h5')
		# joblib.dump(self.decoder, path + '/decoder_weights.h5')
		# joblib.dump(self.model, path + '/ae_weights.h5')
		self.encoder.save(path + '/encoder_weights.h5')
		self.decoder.save(path + '/decoder_weights.h5')
		self.model.save(path+ '/ae_weights.h5')
		
if __name__ == '__main__':
	ae = AutoEncoder(encoding_dim=2)
	ae.encoder_decoder()
	ae.fit(batch_size=50, epochs=300)
	ae.save()