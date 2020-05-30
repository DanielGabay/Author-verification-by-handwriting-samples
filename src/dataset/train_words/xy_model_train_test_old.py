from keras import backend as K
import os
import pickle
import warnings
# ignore warnings prints
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

from keras.models import Sequential
#from keras.layers import Dense, Dropout, Flatten, BatchNormalization, Activation
from keras.layers import BatchNormalization
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.constraints import maxnorm
from keras.utils import np_utils
from keras.layers import Conv2D, Bidirectional, LSTM
from tensorflow import keras
from keras import backend as K
import cv2
from keras.models import model_from_json
import numpy as np
import sys
from keras.utils.np_utils import to_categorical
import matplotlib.pyplot as plt

from keras.layers.core import Dense, Dropout, Flatten,Activation
from keras.layers.convolutional import Conv2D, MaxPooling2D, SeparableConv2D

def showImages(template,image, str = ''):
	plt.subplot(121), plt.imshow(template.squeeze(),cmap='gray')
	plt.subplot(122), plt.imshow(image.squeeze(),cmap='gray')
	plt.show()



IMG_SIZE = 64
N_CLASS = 11
model_name = "xy_11_improved_trained_model_64_64"

def split_train_test(X, y, train_precent=0.7):
	train_size = int(train_precent * len(X))
	X_train = X[:train_size]
	X_test = X[train_size:]
	y_train = y[:train_size]
	y_test = y[train_size:]
	return (X_train, y_train, X_test, y_test)

def train_model(X_train, y_train, class_num):
	model = get_model(2, X_train.shape[1:],class_num)
	model.fit(X_train, y_train, batch_size=64, epochs=10, validation_split=0.1)
	# save train to Json
	model_json=model.to_json()
	with open(model_name + ".json", "w") as json_file:
		json_file.write(model_json)
	# serialize weights to HDF5
	model.save_weights(model_name+ '.h5')

def improve_images(X):
	kernel = np.ones((2,2),np.uint8)
	for idx, img in enumerate(X):
		retval, thresh_for_large = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)
		opening = cv2.morphologyEx(thresh_for_large, cv2.MORPH_OPEN, kernel)
		opening = np.expand_dims(opening, axis=0)
		opening = opening.transpose((1, 2, 0)) 
		X[idx] = np.expand_dims(opening, axis=0)

	return X


def test_model(X_test, y_test):
	json_file = open(model_name + '.json', 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	classifier = model_from_json(loaded_model_json)

	# load weights into new model
	classifier.load_weights(model_name+'.h5')
	print("Loaded model from disk")
	#classifier.compile(optimizer='adam',  loss='categorical_crossentropy', metrics=['accuracy'])

	# scores = classifier.evaluate(X_test, y_test, verbose=0)
	# print("Accuracy: %.2f%%" % (scores[1]*100))
	count_correct = 0
	for i, test_image in enumerate(X_test):
		test_image = np.expand_dims(test_image, axis=0)
		result = classifier.predict(test_image)
		max_result = max(result[0])
		result = result[0].tolist().index(max_result)
		y_real = y_test[i].tolist().index(1)
		print("predicted: {} Real: {} ".format(result, y_real))
		print(max_result)
		print("----------------")
		if result == y_real:
			count_correct += 1
	print("correct: {} acc: {:.2f}".format(count_correct, count_correct/len(X_test)))

def get_model(num, shape, class_num):
	if num == 1:
		model = Sequential()

		model.add(Conv2D(64, (3, 3), input_shape=shape))
		model.add(Activation('relu'))
		model.add(MaxPooling2D(pool_size=(2, 2)))


		model.add(Conv2D(64, (3, 3), padding='same'))
		model.add(Activation('relu'))
		model.add(MaxPooling2D(pool_size=(2, 2)))

		model.add(Flatten())
		model.add(Dense(64))
		model.add(Dense(N_CLASS))
		model.add(Activation('softmax'))

		model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
		return model

	elif num == 2:
		model = Sequential()

		model.add(Conv2D(32, (3, 3), input_shape=shape, padding='same'))
		model.add(Activation('relu'))

		model.add(Dropout(0.2))

		model.add(BatchNormalization())

		model.add(Conv2D(64, (3, 3), padding='same'))
		model.add(Activation('relu'))


		model.add(MaxPooling2D(pool_size=(2, 2)))
		model.add(Dropout(0.2))
		model.add(BatchNormalization())

		model.add(Conv2D(64, (3, 3), padding='same'))
		model.add(Activation('relu'))
		model.add(MaxPooling2D(pool_size=(2, 2)))
		model.add(Dropout(0.2))
		model.add(BatchNormalization())

		model.add(Conv2D(128, (3, 3), padding='same'))
		model.add(Activation('relu'))
		model.add(Dropout(0.2))
		model.add(BatchNormalization())

		model.add(Flatten())
		model.add(Dropout(0.2))

		model.add(Dense(256, kernel_constraint=maxnorm(3)))
		model.add(Activation('relu'))
		model.add(Dropout(0.2))
		model.add(BatchNormalization())

		model.add(Dense(128, kernel_constraint=maxnorm(3)))
		model.add(Activation('relu'))
		model.add(Dropout(0.2))
		model.add(BatchNormalization())

		model.add(Dense(class_num))
		model.add(Activation('softmax'))
		
		model.compile(loss='categorical_crossentropy', optimizer= 'adam', metrics=['accuracy'])

		return model

if __name__ == '__main__':
	# if len(sys.argv) < 2:
	# 	print('python xy_model.py <train/test>')
	# 	sys.exit(1)
	X = pickle.load(open('X_improved_11_64_64.pickle', "rb"))
	y = pickle.load(open('y_improved_11_64_64.pickle', "rb"))
	
	X = improve_images(X)
	
	X = X.astype('float32')
	X = X / 255

	X_train, y_train, X_test, y_test = split_train_test(X, y)
	y_train = np_utils.to_categorical(y_train)
	y_test = np_utils.to_categorical(y_test)
	class_num = y_test.shape[1]
	if sys.argv[1] == 'train':
		train_model(X_train, y_train, class_num)
	if sys.argv[1] == 'test':
		test_model(X_test, y_test)