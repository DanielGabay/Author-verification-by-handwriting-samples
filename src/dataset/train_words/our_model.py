import numpy as np
import os
import cv2
import random
import pickle
import pathlib

DATADIR = 'normal_dataset'
CATEGORIES = [i for i in range(0,11)]
IMG_SIZE = 64

training_data = []

def improve_images(img):

	toDelete = []
	kernel = np.ones((3,3),np.uint8)
	
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
			
	except ValueError:
		print("error!!!")

	return img

def create_training_data():
	for category in CATEGORIES:
		path = os.path.join(pathlib.Path().absolute(), DATADIR, str(category+1))
		print(path)
		for img in os.listdir(path):
			try:
				img_array = cv2.imread(os.path.join(path,img), 0)
				img_array = improve_images(img)
				new_array = img_array #cv2.resize(img_array, (IMG_SIZE,IMG_SIZE))
				training_data.append([new_array, category])
			except Exception as e:
				pass

create_training_data()
random.shuffle(training_data)

X = []
y = []

for features, label in training_data:
	X.append(features)
	y.append(label)

X = np.array(X).reshape(-1, IMG_SIZE, IMG_SIZE, 1)

pickle_out = open("X_zoom_11.pickle", "wb")
pickle.dump(X, pickle_out)
pickle_out.close()

pickle_out = open("y_zoom_11.pickle", "wb")
pickle.dump(y, pickle_out)
pickle_out.close()