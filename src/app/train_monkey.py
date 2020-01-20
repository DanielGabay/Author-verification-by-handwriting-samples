import os
import sys

import cv2
import numpy as np
import pandas as pd
from keras.preprocessing import image
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
import joblib

from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.our_utils.prepare_document import \
	get_prepared_doc
from models.letterClassifier import load_and_compile_model

DATA_PATH = "data/"


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
hebrew_letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י'\
			,'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',\
		   'ך', 'ם', 'ן', 'ף', 'ץ']

class DividedDoc:
	def __init__(self,letter_vec1, letter_vec2):
		self._letter_vec1 = letter_vec1
		self._letter_vec2 = letter_vec2

def calculate_diff(list_1,list_2):
	count = 0
	for i in range (0,len(list_1)):
		count+= abs(list_1[i] - list_2[i])
	return count


def sum_diff(list_of_pairs):
	sumEqual = []
	sumDiff = []
	for i in range(len(list_of_pairs)):
		sumEqual.append(calculate_diff(list_of_pairs[i]._letter_vec1,list_of_pairs[i]._letter_vec2))
		print(list_of_pairs[i]._letter_vec1)
		print(list_of_pairs[i]._letter_vec2)
		
		for j in range(i+1,len(list_of_pairs)):
			sumDiff.append(calculate_diff(list_of_pairs[i]._letter_vec1,list_of_pairs[j]._letter_vec1))
			sumDiff.append(calculate_diff(list_of_pairs[i]._letter_vec1,list_of_pairs[j]._letter_vec2))
			sumDiff.append(calculate_diff(list_of_pairs[i]._letter_vec2,list_of_pairs[j]._letter_vec1))
			sumDiff.append(calculate_diff(list_of_pairs[i]._letter_vec2,list_of_pairs[j]._letter_vec2))
		
	print("Equal mean: {}".format(np.mean(np.asarray(sumEqual))))
	print("Equal std: {}".format(np.std(np.asarray(sumEqual))))
	print("Diff mean: {}".format(np.mean(np.asarray(sumDiff))))
	print("Diff std: {}".format(np.std(np.asarray(sumDiff))))



def create_diff_vector(list_1,list_2):
	diff_vector = [0] * len(list_1)
	for i in range (0,len(list_1)):
		diff_vector[i] =  abs(list_1[i] - list_2[i])
	return diff_vector


def counter_list(found_letters):
	count_list = [0] * 27
	for letter in found_letters:
		#print(letter['letter_index'])
		count_list[(letter['letter_index'])]+=1
	precent = [i * (100/len(found_letters)) for i in count_list]
	return precent

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
			selected_letter = hebrew_letters[result[0].tolist().index(max(result[0]))]
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

def main():
	classifier = load_and_compile_model('model99')
	divided_docs = []
	for root, dirs, files in os.walk(DATA_PATH):
		for file in files:
			doc_name = file.split('.')[0]
			print(doc_name)

			df = pd.read_csv('equal2.csv')
			
			if int(doc_name) in df['Vector'].values.tolist():
				print('Element exists in Dataframe!')
				continue
			
			img_name = DATA_PATH + file
			img = get_prepared_doc(img_name)
			lines = get_lines(img, img_name)
		
			letters_1,letters_2 = get_pair_letters(lines,classifier)
			
			count_list_1 = counter_list(letters_1)  
			count_list_2 = counter_list(letters_2)
			diff_vec = create_diff_vector(count_list_1,count_list_2)
			write_to_csv("equal2.csv",doc_name,diff_vec)
			write_to_csv("count_vectors2.csv",doc_name+'_1',count_list_1)
			write_to_csv("count_vectors2.csv",doc_name+'_2',count_list_2)
			

			# divided_docs.append(DividedDoc(count_list_1,count_list_2))

	#sum_diff(divided_docs)

def write_to_csv(dfName,vecName,vector):
	
	df = pd.read_csv(dfName)
	# df.rename(columns=df.iloc[0])
	if vecName in df['Vector'].values.tolist():
		print('Element exists in Dataframe')
		return
	vector.insert(0,vecName)  # add the vecName 
	modDfObj = df.append(pd.Series(vector, index=df.columns ), ignore_index=True)
	modDfObj.to_csv(dfName, mode='w',index = False)
	

def create_diff_csv(dfName):
	
	df = pd.read_csv(dfName)

	for i ,row in enumerate(np.asarray(df)):
		row =list(row)
		doc_name = row.pop(0)
		print(row)
		print(len(row))
		print(i)
		break

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

def rescale(data):
	# built in function to rescale data
	scaler = StandardScaler()
	return scaler.fit_transform(data)

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



def train_model():
	X, y = get_xy_by_vectors('equal2.csv', 'count_vectors2.csv')
	# X, y = get_xy_by_sums('equal2.csv', 'count_vectors2.csv')
	X_train, X_test, y_train, y_test = split_train_test(X,y,0.8)
	clf = LogisticRegression(random_state=0).fit(X_train, y_train)
	# save train model
	joblib.dump(clf, "monkey_model.sav")
	# print(y_test[0])
	# print(clf.predict(X_test[0].reshape(1,-1)))
	print(clf.score(X_test, y_test))
	print(clf.score(X_train, y_train))
	print(confusion_matrix(y_test, clf.predict(X_test)))
	print(clf.coef_)

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

def test_model():
	loaded_model = joblib.load('monkey_model.sav')
	classifier = load_and_compile_model('model99')
	vectors = []
	for root, dirs, files in os.walk(DATA_PATH):
		for file in files:
			if file != 'd.tiff' and  file != 's.tiff':
				continue
			doc_name = file.split('.')[0]
			print(doc_name)
			
			img_name = DATA_PATH + file
			img = get_prepared_doc(img_name)
			lines = get_lines(img, img_name)
			letters = get_letters(lines)
			append_to_vectors(vectors, lines, classifier, True)
	# diff_vec1 = sum(create_diff_vector(vectors[0],vectors[1]))
	# diff_vec2 = sum(create_diff_vector(vectors[0],vectors[2]))
	# diff_vec3 = sum(create_diff_vector(vectors[0],vectors[3]))
	# diff_vec4 = sum(create_diff_vector(vectors[1],vectors[2]))
	# diff_vec5 = sum(create_diff_vector(vectors[1],vectors[3]))
	# diff_vec6 = sum(create_diff_vector(vectors[2],vectors[3]))
	# print(diff_vec1)
	# print(diff_vec6)
	# print(diff_vec2)
	# print(diff_vec3)
	# print(diff_vec4)
	# print(diff_vec5)
	diff_vec1 = create_diff_vector(vectors[0],vectors[1])
	diff_vec2 = create_diff_vector(vectors[0],vectors[2])
	diff_vec3 = create_diff_vector(vectors[0],vectors[3])
	diff_vec4 = create_diff_vector(vectors[1],vectors[2])
	diff_vec5 = create_diff_vector(vectors[1],vectors[3])
	diff_vec6 = create_diff_vector(vectors[2],vectors[3])
	print(sum(diff_vec1))
	print(sum(diff_vec6))
	print(sum(diff_vec2))
	print(sum(diff_vec3))
	print(sum(diff_vec4))
	print(sum(diff_vec5))
	prediction_monkey(loaded_model,diff_vec1) # '1')
	prediction_monkey(loaded_model,diff_vec6) # '1')
	prediction_monkey(loaded_model,diff_vec2) # '0')
	prediction_monkey(loaded_model,diff_vec3) # '0')
	prediction_monkey(loaded_model,diff_vec4) # '0')
	prediction_monkey(loaded_model,diff_vec5) # '0')
		

def prediction_monkey(loaded_model, diff_vec):
	diff_vec = np.asarray(diff_vec)
	# diff_vec = rescale(diff_vec.reshape(-1,1))
	print('{} {}'.format(loaded_model.predict_proba(diff_vec.reshape(1,-1)),loaded_model.predict(diff_vec.reshape(1,-1))))

if __name__ == "__main__":
	# create_diff_csv('equal.csv')
	# sys.exit(1)
	# main()

	train_model()
	# test_model()
