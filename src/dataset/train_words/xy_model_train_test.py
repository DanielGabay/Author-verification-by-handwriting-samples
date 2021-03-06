from keras import backend as K
import os
import pickle
import warnings
import math

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

def createKernel(kernelSize, sigma, theta):
	"""create anisotropic filter kernel according to given parameters"""
	assert kernelSize % 2 # must be odd size
	halfSize = kernelSize // 2
	
	kernel = np.zeros([kernelSize, kernelSize])
	sigmaX = sigma
	sigmaY = sigma * theta
	
	for i in range(kernelSize):
		for j in range(kernelSize):
			x = i - halfSize
			y = j - halfSize
			
			expTerm = np.exp(-x**2 / (2 * sigmaX) - y**2 / (2 * sigmaY))
			xTerm = (x**2 - sigmaX**2) / (2 * math.pi * sigmaX**5 * sigmaY)
			yTerm = (y**2 - sigmaY**2) / (2 * math.pi * sigmaY**5 * sigmaX)
			
			kernel[i, j] = (xTerm + yTerm) * expTerm

	kernel = kernel / np.sum(kernel)
	return kernel

def wordSegmentation(img, kernelSize=25, sigma=11, theta=7, minArea=0):
	"""Scale space technique for word segmentation proposed by R. Manmatha: http://ciir.cs.umass.edu/pubfiles/mm-27.pdf
	
	Args:
		img: grayscale uint8 image of the text-line to be segmented.
		kernelSize: size of filter kernel, must be an odd integer.
		sigma: standard deviation of Gaussian function used for filter kernel.
		theta: approximated width/height ratio of words, filter function is distorted by this factor.
		minArea: ignore word candidates smaller than specified area.
		
	Returns:
		List of tuples. Each tuple contains the bounding box and the image of the segmented word.
	"""

	# apply filter kernel
	kernel = createKernel(kernelSize, sigma, theta)
	imgFiltered = cv2.filter2D(img, -1, kernel, borderType=cv2.BORDER_REPLICATE).astype(np.uint8)
	(_, imgThres) = cv2.threshold(imgFiltered, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	imgThres = 255 - imgThres

	# find connected components. OpenCV: return type differs between OpenCV2 and 3
	if cv2.__version__.startswith('3.'):
		(_, components, _) = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	else:
		(components, _) = cv2.findContours(imgThres, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

	# append components to result
	res = []
	for c in components:
		
		# skip small word candidates
		if cv2.contourArea(c) < minArea:
			continue
		# append bounding box and image of word to result list
		currBox = cv2.boundingRect(c) # returns (x, y, w, h)
		(x, y, w, h) = currBox
		currImg = img[y:y+h, x:x+w]
		res.append((currBox, currImg))

	# return list of words, sorted by x-coordinate
	return sorted(res, key=lambda entry:entry[0][0])


def showImages(img,img1, str = ''):
	plt.subplot(121), plt.imshow(img.squeeze(),cmap='gray')
	plt.subplot(122), plt.imshow(img1.squeeze(),cmap='gray')
	plt.show()

#squeeze()

IMG_SIZE = 64
N_CLASS = 11
model_name = "xy_11_trained_zoom_model_64_64"

def split_train_test(X, y, train_precent=0.8):
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

def improve_images(X,y):

	toDelete = []
	kernel = np.ones((3,3),np.uint8)
	for idx, img in enumerate(X):
		
		retval, thresh_for_large = cv2.threshold(img, 220, 255, cv2.THRESH_BINARY)
		opening = cv2.morphologyEx(thresh_for_large, cv2.MORPH_OPEN, kernel)
		opening = np.expand_dims(opening, axis=0)
		opening = opening.transpose((1, 2, 0)) 
		try:
			color_x, color_y = np.where(np.any(opening < 255, axis=2))        # detect only the words without the white background
			x0 = color_x.min()
			x1 = color_x.max()
			y0 = color_y.min()
			y1 = color_y.max()
			cropped_image = opening[x0:x1 + 2, y0:y1 + 2]
			wordImg = cv2.resize(cropped_image, dsize=(IMG_SIZE, IMG_SIZE))
			X[idx] = np.expand_dims(wordImg, axis=0)
			
		except ValueError:
			print("{} error!!!!".format(idx))
			toDelete.append(idx)

	for idx in reversed(toDelete):
		np.delete(X, idx)
		np.delete(y, idx)
	
	return X,y


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
		'''
		print("predicted: {} Real: {} ".format(result, y_real))
		print(max_result)
		print("----------------")
		'''
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
	X = pickle.load(open('X_zoom_11.pickle', "rb"))
	y = pickle.load(open('y_zoom_11.pickle', "rb"))
	print("{} {}".format(len(X), len(y)))
	# X ,y = improve_images(X,y)

	# X = X.reshape(-1, IMG_SIZE, IMG_SIZE, 1)
	
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