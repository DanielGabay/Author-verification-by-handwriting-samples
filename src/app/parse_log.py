import random
import sys
from collections import Counter

import numpy as np
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt

'''
test log example:

idx0: Test: 10b.tiff 10.tiff
idx1:
idx2: Monkey Result:
idx3: <Same Author> [confident: 83.99%]
idx4: Letters AE Result:
idx5: <Same Author>
idx6: count_same: 8881
idx7: count_diff: 5418
idx8: Real: True
idx9: Mark: Same
'''

# [monkey_res, letters_ae_res, same/diff {1/0}]
def parse_log(filename):
	data = []
	data_idx = 0
	with open(filename) as fp:
		lines = fp.readlines()
		for line_idx in range(len(lines)):
			if 'Test' in lines[line_idx]:
				test_data = get_test_data(lines, line_idx, data_idx)
				data.append(test_data)
				data_idx += 1
	return data

def get_test_data(lines, line_idx, data_idx):
	test_data = []
	test_data.append(get_monkey_data(lines,line_idx+3))
	test_data.append(get_letters_ae_data(lines, line_idx+6))
	test_data.append(get_real_data(lines, line_idx+8))
	return test_data

def get_monkey_data(lines, line_idx):
	s = lines[line_idx].split(':')[1]
	res = s.replace('\n', '').replace(' ', '').replace(']','').replace('%','')
	res = float(res) / 100
	if 'Same' in lines[line_idx]:
		return res
	return 1 - res

def get_letters_ae_data(lines, line_idx):
	cnt_same = int(lines[line_idx].split(':')[1])
	cnt_diff = int(lines[line_idx+1].split(':')[1])
	res = (cnt_same) / (cnt_same+cnt_diff)
	return res

def get_real_data(lines, line_idx):
	s = lines[line_idx].split(':')[1]
	if 'True' in s:
		return 1
	return 0

def filter_only_conflicts(data, max_same, max_diff):
	filterd_data = []
	for d in data:
		if (d[0] > 0.5 and d[1] < 0.5) or \
			(d[1] > 0.5 and d[0] < 0.5):
			if d[2] == 1 and max_same > 0:
				filterd_data.append(d)
				max_same -= 1
			if d[2] == 0 and max_diff > 0:
				filterd_data.append(d)
				max_diff -= 1
	return filterd_data

def getXY(data):
	data = np.array(data)
	X = data[:,[0,1]]
	y = data[:,[2]].ravel()
	return X, y
	

def train_nn(data):
	X, y = getXY(data)
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=3)
	# lr = LogisticRegression()
	# lr.fit(X_train,y_train)
	mlp = MLPClassifier()
	mlp.fit(X_train, y_train)
	# _print_scores(lr, 'Basic Logistic-Regression', X_train, y_train, X_test, y_test)
	# _print_test_proba(lr, 'Basic Logistic-Regression', X_test, y_test)
	_print_scores(mlp, 'Basic Nueral-Network', X_train, y_train, X_test, y_test)
	_print_test_proba(mlp, 'Basic Nueral-Network', X_test, y_test)

def _print_test_proba(model, model_name, X_test, y_test):
	correct_same = 0
	correct_diff = 0
	for i in range(len(X_test)):
		predict = model.predict(X_test[i].reshape(1,-1))[0]
		if predict == 1 and y_test[i] == 1:
			correct_same += 1
			print("[{0:.2f}, {1:.2f}] -> real: {2}, predicted: 1".format(X_test[i][0], X_test[i][1], y_test[i]))
		elif predict == 0 and y_test[i] == 0:
			print("[{0:.2f}, {1:.2f}] -> real: {2}, predicted: 0".format(X_test[i][0], X_test[i][1], y_test[i]))
			correct_diff += 1
		else:
			print("[{0:.2f}, {1:.2f}] -> real: {2}, predicted: conflict".format(X_test[i][0], X_test[i][1], y_test[i]))

		# print("predict: {}".format(model.predict(X_test[i].reshape(1,-1))))
		# print("predict proba: {}".format(model.predict_proba(X_test[i].reshape(1,-1))))
		print("______")
	print("correct_same: {} correct_diff:{}".format(correct_same, correct_diff))
	c = Counter(y_test)
	print("test_same: {} test_diff: {}".format(c[1], c[0]))

def _print_scores(model, model_name, X_train, y_train, X_test, y_test):
	print(model_name)
	print('train score: {0:.4f}%'.format(model.score(X_train, y_train)*100))
	print('test score: {0:.4f}%'.format(model.score(X_test, y_test)*100))
	conf_mat_y_train = metrics.confusion_matrix(y_train, model.predict(X_train))
	conf_mat_y_test = metrics.confusion_matrix(y_test, model.predict(X_test))


def plot_features(data):
	colors = ['r', 'g']
	fig, ax = plt.subplots()
	for i in range(2):
		points = np.array([[data[j][0], data[j][1]] for j in range(len(data)) if data[j][2] == i])
		if i == 1:
			ax.scatter(points[:, 0], points[:, 1], s=100, c=colors[i], marker='*', label='Same')
		else:
			ax.scatter(points[:, 0], points[:, 1], s=7, c=colors[i], label='Different')
	plt.title('Conflict Plot: AutoEncoder(letters) - Monkey',loc='center')
	plt.legend(loc="lower left")
	plt.xlabel('Monkey')
	plt.ylabel('Auto-Encoder')
	plt.show()

if __name__ == "__main__":
	# filename = 'ae_no_0.4__monkey_log.txt'
	filename = 'ae_monkey-bySum_106_diff_same_pairs_no_alef_results.txt'
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	data = parse_log(filename)
	filterd_data = filter_only_conflicts(data, 50, 1000)
	# random.shuffle(filterd_data)
	plot_features(filterd_data)
	# train_nn(filterd_data)
	# train_nn(data)
