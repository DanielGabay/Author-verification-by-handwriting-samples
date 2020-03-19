from keras.models import load_model
import numpy as np
import os


path = os.path.dirname(os.path.abspath(__file__))

encoder = load_model(path + '/encoder_weights.h5')
decoder = load_model(path + '/decoder_weights.h5')

inputs = np.array([[1,2,2]])
x = encoder.predict(inputs)
y = decoder.predict(x)

print('Input: {}'.format(inputs))
print('Encoded: {}'.format(x))
print('Decoded: {}'.format(y))