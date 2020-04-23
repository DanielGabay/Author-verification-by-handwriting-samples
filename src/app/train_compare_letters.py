import os
import sys

import cv2
import joblib
import numpy as np
import pandas as pd
import random
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier

import _global
from extractComparisonFeatures.detectLetters import get_letters
from monkey_collect_data import create_diff_vector
import matplotlib.pyplot as plt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def split_train_test(X, y, train_percent=0.75):
	size = int(len(X) * train_percent)
	X_train = X[:size]
	X_test = X[size:]
	y_train = y[:size]
	y_test = y[size:]
	return (X_train, X_test, y_train, y_test)

def get_xy(PATH_TO_CSV , SIZE = 10000):
	isFirst = True
	X = np.asarray(list())
	print(PATH_TO_CSV)
	for dir_, _, files in os.walk(PATH_TO_CSV):
		for file_name in files:
			print("collect data from {}".format(file_name))
			df = pd.read_csv("{}/{}".format(PATH_TO_CSV,file_name) ,header=None) 
			equal_rows = get_same_x(df,SIZE)
			diff_rows = get_diff_x(df,SIZE)
			mix = np.concatenate((equal_rows, diff_rows), axis=0)
			if isFirst == True:
				X  = mix
				isFirst = False
			else:	
				X = np.concatenate((X, mix), axis=0)

	np.random.shuffle(X)
	y = X[:,-1]
	X = np.delete(X, -1, 1)
	#X = rescale(X)
	return (X, y)


def get_same_x(df , SIZE):
	data_len = len(df)
	rows = []
	current_author = df.iloc[0][0].split("_")[0]
	current_author_count = 0
	for i in range(data_len-1):
		for j in range(i+1,data_len):
			if is_same_author(df.iloc[i],df.iloc[j]) == False:
				break
			# print(df.iloc[i][0].split("_")[0] ,df.iloc[j][0].split("_")[0])  # get the autor name )
			row_1 , row_2 = list(df.iloc[i])[2:] , list(df.iloc[j])[2:]  # take only the features.
			diff_vector = create_diff_vector(row_1,row_2)
			diff_vector.append(1) # for the y vector (sign that this vector is same vectors)
			rows.append(diff_vector)

	rows = random.choices(rows, k=SIZE)  # select only K random vectors from the rows list
	return np.asarray(rows)


def get_diff_x(df_diff , SIZE):
	data_len = len(df_diff)
	rand1 ,rand2 = -1, -1
	rows = []
	for i in range(SIZE):
		# check that the random numbers are not equal and not successors
		while rand1 == rand2 or is_same_author(df_diff.iloc[rand1],df_diff.iloc[rand2]) == True:
			rand1, rand2 = np.random.randint(data_len), np.random.randint(data_len)

		row_1 , row_2 = list(df_diff.iloc[rand1])[2:] , list(df_diff.iloc[rand2])[2:]  # take only the features.
		diff_vector = create_diff_vector(row_1,row_2)
		diff_vector.append(0) # for the y vector (sign that this vector is diff vectors)
		rows.append(diff_vector)
		rand1 ,rand2 = -1, -1
	return np.asarray(rows)

def print_result(model,X_test,y_test,X_train,y_train,str = ""):
	print(">>result of {}:".format(str))
	print(">>>X_test-y_test score: {}".format(model.score(X_test, y_test)))
	print(confusion_matrix(y_test, model.predict(X_test)))
	print(">>>X_train-y_train score: {}".format(model.score(X_train, y_train)))
	print(confusion_matrix(y_train, model.predict(X_train)))



def train_model():
	X, y = get_xy("AutoEncoder/features_data",10000)
	X_train, X_test, y_train, y_test = split_train_test(X,y,0.8)
	lr_model = LogisticRegression(random_state=0,max_iter=1000).fit(X_train, y_train)
	mlp_model = MLPClassifier()
	mlp_model.fit(X_train, y_train)
	print_result(mlp_model,X_test,y_test,X_train,y_train,"Logistic")
	print_result(lr_model,X_test,y_test,X_train,y_train,"CNN")
	joblib.dump(lr_model, 'compare_letters_by_vectors.sav') 	# save trained model

def rescale(data):
	# built in function to rescale data
	scaler = StandardScaler()
	return scaler.fit_transform(data)

def is_same_author(row1,row2):
	author1 ,author2 = row1[0].split("_")[0] ,row2[0].split("_")[0]  # get the autor name 
	return True if author1 == author2 else False

	

if __name__ == "__main__":
	train_model()

