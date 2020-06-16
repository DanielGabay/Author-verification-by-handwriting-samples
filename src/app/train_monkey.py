import os
import sys
import cv2
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from monkey_collect_data import create_diff_vector
import matplotlib.pyplot as plt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def print_result(model,X_test,y_test,X_train,y_train,str = ""):
	print(">>result of {}:".format(str))
	print(">>>X_test-y_test score: {}".format(model.score(X_test, y_test)))
	print(confusion_matrix(y_test, model.predict(X_test)))
	print(">>>X_train-y_train score: {}".format(model.score(X_train, y_train)))
	print(confusion_matrix(y_train, model.predict(X_train)))

def split_train_test(X, y, train_percent=0.75):
	size = int(len(X) * train_percent)
	X_train = X[:size]
	X_test = X[size:]
	y_train = y[:size]
	y_test = y[size:]
	return (X_train, X_test, y_train, y_test)

def add_equal_rows_b(X_equal,count_vec_file):
	df = pd.read_csv(count_vec_file)
	data_len = len(df)
	rows = []
	for i in range(data_len-1):
		for j in range(i+1,data_len):
			if is_same_author(df.iloc[i],df.iloc[j]) == False:
				break
			if not author_is_b(df.iloc[i])  and author_is_b(df.iloc[j]):
				row_1, row_2 = list(df.iloc[i])[1:] , list(df.iloc[j])[1:]  # take only the features.
				diff_vector = create_diff_vector(row_1,row_2)
				diff_vector.append(1) # for the y vector (sign that this vector is same vectors)
				rows.append(diff_vector)
	X_equal = np.asarray(X_equal)
	rows = np.asarray(rows)
	equal = np.vstack((X_equal,rows))
	return equal

def get_xy(equal_file, count_vec_file,by_vectors):
	df_euqal = pd.read_csv(equal_file)
	X_equal = np.asarray(add_equal_rows_b(df_euqal.drop('Vector',1),count_vec_file))
	print(X_equal.shape)
	X_diff = get_diff_x(count_vec_file,len(X_equal))
	if not by_vectors :
		X_equal =get_x_by_sums(X_equal,1)
		X_diff = get_x_by_sums(X_diff,0)
		#plot_sums_data(data)
		#print_mean_std(X_equal, X_diff)

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

def plot_sums_data(data):
	fig, ax = plt.subplots()
	colors = ['r', 'g']
	for i in range(2):
		points = np.array([data[j] for j in range(len(data)) if data[j][1] == i])
		ax.scatter(points[:, 0], points[:, 1], s=1, c=colors[i])
	plt.show()

def print_mean_std(X_equal, X_diff):
    print("Equal-> mean: {} std: {}".format(np.mean(X_equal[:,0]), np.std(X_equal[:,0])))
    print("Diff-> mean: {} std: {}".format(np.mean(X_diff[:,0]), np.std(X_diff[:,0])))


def get_diff_x(filename,SIZE):
	df_diff = pd.read_csv(filename)

	df_diff = df_diff.drop('Vector',1)
	data_len = len(df_diff)
	rand1 ,rand2 = -1, -1
	rows = []
	for i in range(SIZE):
		# check that the random numbers are not equal and not successors
		# while rand1 == rand2 or rand1 + 1 == rand2 or rand2 + 1 == rand1: # before we used the 'b' authors
		while abs(rand1-rand2) < 4 : # to select only diffrenet authers
			rand1, rand2 = np.random.randint(data_len), np.random.randint(data_len)
		diff_vector = create_diff_vector(list(df_diff.iloc[rand1]), list(df_diff.iloc[rand2]))
		diff_vector.append(0) # for the y vector (sign that this vector is diff vectors)
		rows.append(diff_vector)
		rand1 ,rand2 = -1, -1
	return np.asarray(rows)

def train_model(by_vectors):
	X, y = get_xy('equal2.csv', 'count_vectors2.csv',by_vectors)
	X_train, X_test, y_train, y_test = split_train_test(X,y,0.80)

	lr_model = LogisticRegression(random_state=0,max_iter=1000).fit(X_train, y_train)
	mlp_model = MLPClassifier(random_state=0,max_iter=1000).fit(X_train, y_train)

	print_result(lr_model,X_test,y_test,X_train,y_train,"Logistic")
	print_result(mlp_model,X_test,y_test,X_train,y_train,"CNN")

	joblib.dump(lr_model, 'hebMonkeyLettersByVectors_lr.sav') 	# save trained model
	joblib.dump(mlp_model, 'hebMonkeyLettersByVectors_mlp.sav') 	# save trained model

def is_same_author(row1,row2):
	author1 ,author2 = row1[0].split("_")[0] ,row2[0].split("_")[0]  # get the autor name 
	return True if author1 == author2 else False
	
def author_is_b(row):
	return row[0].split("_")[1] == 'b' 

def rescale(data):
	# built in function to rescale data
	scaler = StandardScaler()
	return scaler.fit_transform(data)

if __name__ == "__main__":
	train_model(False)
