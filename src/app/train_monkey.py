import os
import sys

import cv2
import joblib
import numpy as np
import pandas as pd
from keras.preprocessing import image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler

import _global
from monkey_collect_data import create_diff_vector
from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.our_utils.prepare_document import \
    get_prepared_doc
from models.letterClassifier import load_and_compile_model

MODEL_SAVE_AS = "monkey_model.sav"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def split_train_test(X, y, train_percent=0.75):
	size = int(len(X) * train_percent)
	X_train = X[:size]
	X_test = X[size:]
	y_train = y[:size]
	y_test = y[size:]
	return (X_train, X_test, y_train, y_test)

def get_xy_by_vectors(equal_file, count_vec_file):
	df_euqal = pd.read_csv(equal_file)
	X_equal = np.asarray(df_euqal.drop('Vector',1))
	X_diff = get_diff_x(count_vec_file)
	X = np.concatenate((X_equal, X_diff), axis=0)
	np.random.shuffle(X)
	y = X[:,-1]
	X = np.delete(X, -1, 1)
	# X = rescale(X)
	return (X, y)

def get_x_by_sums(X, y_val):
	x_sums = []
	for x in X:
		# sum all vector without the last element (the y={0,1})
		element = [sum(x[:-1]), y_val]
		x_sums.append(element)
	return np.asarray(x_sums)


def get_xy_by_sums(equal_file, count_vec_file):
	df_euqal = pd.read_csv(equal_file)
	X_equal = get_x_by_sums(np.asarray(df_euqal.drop('Vector',1)), 1)
	X_diff = get_x_by_sums(get_diff_x(count_vec_file), 0)
	data = np.concatenate((X_equal, X_diff), axis=0)
	np.random.shuffle(data)
	y = data[:,-1]
	X = np.delete(data, -1, 1)
	# X = rescale(X)
	return (X, y)

def get_x_by_sums(X, y_val):
	x_sums = []
	for x in X:
		# sum all vector without the last element (the y={0,1})
		element = [sum(x[:-1]), y_val]
		x_sums.append(element)
	return np.asarray(x_sums)

def get_diff_x(filename):
	df_diff = pd.read_csv(filename)
	df_diff = df_diff.drop('Vector',1)
	data_len = len(df_diff)
	rand1 ,rand2 = -1, -1
	rows = []
	for i in range(500):
		# check that the random numbers are not equal and not successors
		while rand1 == rand2 or rand1 + 1 == rand2 or rand2 + 1 == rand1:
			rand1, rand2 = np.random.randint(data_len), np.random.randint(data_len)
		diff_vector = create_diff_vector(list(df_diff.iloc[rand1]), list(df_diff.iloc[rand2]))
		diff_vector.append(0) # for the y vector (sign that this vector is diff vectors)
		rows.append(diff_vector)
		rand1 ,rand2 = -1, -1
	return np.asarray(rows)

def train_model(by_vectors):
	if by_vectors:
		X, y = get_xy_by_vectors('equal2.csv', 'count_vectors2.csv')
	else:
		X, y = get_xy_by_sums('equal2.csv', 'count_vectors2.csv')
	X_train, X_test, y_train, y_test = split_train_test(X,y,0.85)
	clf = LogisticRegression(random_state=0).fit(X_train, y_train)
	# save train model
	joblib.dump(clf, _global.MONKEY_MODEL)
	# print(y_test[0])
	# print(clf.predict(X_test[0].reshape(1,-1)))
	print(clf.score(X_test, y_test))
	print(clf.score(X_train, y_train))
	print(confusion_matrix(y_test, clf.predict(X_test)))
	# print(clf.coef_)

def get_identified_letters(letters, classifier):
	found_letters = []
	count = 0
	for letter in letters:
		letter = cv2.resize(letter.image_letter, (28, 28))
		letter = letter.reshape((28, 28, 1))
		test_letter = image.img_to_array(letter)
		test_image = np.expand_dims(test_letter, axis=0)
		result = classifier.predict((test_image/255))
		if max(result[0]) > 0.995:
			letter_index = result[0].tolist().index(max(result[0]))
			selected_letter = _global.lang_letters[result[0].tolist().index(max(result[0]))]
			if selected_letter == "ץ": 
				continue
			count += 1
			found_letters.append({'image_letter': letter , 'letter_index': letter_index, 'letter_name': selected_letter})
	return found_letters

# divide every file to 2 diffrent 'persons'.
def get_pair_letters(lines,classifier):
	letters = get_letters(lines)
	size = len(letters)//2
	letters_1 = letters[:size]
	letters_2 = letters[size:]
	identified_letters_1 = get_identified_letters(letters_1,classifier)
	identified_letters_2 = get_identified_letters(letters_2,classifier)

	return identified_letters_1,identified_letters_2


def rescale(data):
	# built in function to rescale data
	scaler = StandardScaler()
	return scaler.fit_transform(data)


def append_to_vectors(vectors, lines, classifier, half_lines=False):
	if half_lines:
		letters_1,letters_2 = get_pair_letters(lines,classifier)
		count_list_1 = counter_list(letters_1)  
		count_list_2 = counter_list(letters_2)
		vectors.append(count_list_1)
		vectors.append(count_list_2)
	else:
		letters = get_letters(lines)
		identified_letters = get_identified_letters(letters,classifier)
		count_list = counter_list(identified_letters)
		vectors.append(count_list)


if __name__ == "__main__":
	if(len(sys.argv) < 2):
		print("Usage: python train_monkey.py <by_vectors/by_sum>")
		sys.exit(1)
	if(sys.argv[1] == 'by_vectors'):
		_global.init(monkey_by_vectors=True)
		train_model(True)
	else: 
		# by_sum
		_global.init(monkey_by_vectors=False)
		train_model(False)
