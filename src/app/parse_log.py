import random
import sys
from collections import Counter

import numpy as np
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import matplotlib.pyplot as plt
from classes import Stats

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
	

def train_nn(data, filterd_data):
	X, y = getXY(data)
	X1, y1 = getXY(filterd_data)
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=3)
	X1_train, X1_test, y1_train, y1_test = train_test_split(X1, y1, test_size=0.9, random_state=3)
	# lr = LogisticRegression()
	# lr.fit(X_train,y_train)
	mlp = MLPClassifier()
	mlp.fit(X_train, y_train)
	# _print_scores(lr, 'Basic Logistic-Regression', X_train, y_train, X_test, y_test)
	# _print_test_proba(lr, 'Basic Logistic-Regression', X_test, y_test)
	_print_test_proba(mlp, 'Basic Nueral-Network', X1_test, y1_test)
	# _print_scores(mlp, 'Basic Nueral-Network', X_train, y_train, X_test, y_test)

def _print_test_proba(model, model_name, X_test, y_test):
	correct_same = 0
	correct_diff = 0
	for i in range(len(X_test)):
		predict = model.predict(X_test[i].reshape(1,-1))[0]
		predict_proba = model.predict_proba(X_test[i].reshape(1,-1))[0]
		if predict == 1 and y_test[i] == 1:
			correct_same += 1
			# print("[{0:.2f}, {1:.2f}] -> real: {2}, predicted: 1".format(X_test[i][0], X_test[i][1], y_test[i]))
		elif predict == 0 and y_test[i] == 0:
			# print("[{0:.2f}, {1:.2f}] -> real: {2}, predicted: 0".format(X_test[i][0], X_test[i][1], y_test[i]))
			correct_diff += 1
		# else:
		print("Monkey: {0:.2f}\nAE: {1:.2f}\nExcpected: {2}\npredicted: {3}\nproba: {4}".format(\
			X_test[i][0], X_test[i][1], y_test[i], predict, predict_proba))

		# print("predict: {}".format(model.predict(X_test[i].reshape(1,-1))))
		# print("predict proba: {}".format(model.predict_proba(X_test[i].reshape(1,-1))))
		print("______")
	c = Counter(y_test)
	print("correct_same:{}/{} correct_diff:{}/{}".format(correct_same, c[1], correct_diff, c[0]))
	# print("test_same: {} test_diff: {}".format(c[1], c[0]))

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

def monkey_ae_res(test, monkey_threshold=0.5, ae_threshold=0.5):
	monkey_res = True if test[0] > monkey_threshold else False
	ae_res = True if test[1] > ae_threshold else False
	return {'monkey_res': monkey_res, 'ae_res': ae_res}

def update_stats(s, r):
	if r['monkey_res'] and r['ae_res'] and s.same_author:
		# all results 'Same author'
		s.tp += 1
		s.mark_as = "Mark: Same"
	elif not r['monkey_res'] and not r['ae_res'] and s.same_author:
		# both monkey and ae call 'diff' while same
		s.fn += 1
		s.mark_as = "Mark: Different while Same"
	elif not r['monkey_res'] and not r['ae_res'] and not s.same_author:
		# all results 'Different author'
		s.tn += 1
		s.mark_as = "Mark: Different"
	elif r['monkey_res'] and r['ae_res'] and not s.same_author:
		# both monkey and ae call 'same' while diff
		s.fp += 1
		s.mark_as = "Mark: Same while Different"
	else:
		s.conflict += 1
		if s.same_author:
			s.conflict_while_same += 1
		else:
			s.conflict_while_diff += 1
		s.mark_as = "Conflict/Mistake"

	if r['ae_res'] and s.same_author:
		s.ae_tp += 1
	elif not r['ae_res'] and s.same_author:
		s.ae_fn += 1
	elif not r['ae_res'] and not s.same_author:
		s.ae_tn += 1
	elif r['ae_res'] and not s.same_author:
		s.ae_fp += 1

	if r['monkey_res'] and s.same_author:
		s.monkey_tp += 1
	elif not r['monkey_res'] and s.same_author:
		s.monkey_fn += 1
	elif not r['monkey_res'] and not s.same_author:
		s.monkey_tn += 1
	elif r['monkey_res'] and not s.same_author:
		s.monkey_fp += 1

def conf_matrix_by_thresholds(data, monkey_threshold=0.5, ae_threshold=0.5):
	stats = Stats()
	for d in data:
		results = monkey_ae_res(d, monkey_threshold, ae_threshold)
		stats.same_author = True if d[2] == 1 else False
		update_stats(stats, results)
	print_ae_monkey_results(stats, monkey_threshold, ae_threshold)


def print_ae_monkey_results(s, monkey_threshold, ae_threshold):
	print("\n------------------")
	print("Monkey threshold: {0:.2f}\nAE threshold: {1:.2f}".format(monkey_threshold, ae_threshold))
	print("\n------------------")
	print_conf_matrix("Monkey & letter AE Conf Matrix:", s.tn, s.tp, s.fn, s.fp)
	print("Model accuracy: {0:.2f}% (*NOTE: not includes Undecided results!)".format((s.tn+s.tp)/(s.tn+s.tp+s.fn+s.fp)*100))
	print("Undecided Results:\n->conflict:{}\n-->conflict_while_same:{}\n-->conflict_while_diff:{}"\
		.format(s.conflict, s.conflict_while_same,s.conflict_while_diff))
	print("\n------------------")
	print_conf_matrix("Only letter AE Conf Matrix:", s.ae_tn,s.ae_tp, s.ae_fn, s.ae_fp)
	print("Model accuracy: {0:.2f}%".format((s.ae_tn+s.ae_tp)/(s.ae_tn+s.ae_tp+s.ae_fn+s.ae_fp)*100))
	print("\n------------------")
	# print_conf_matrix("Only Monkey Conf Matrix:", s.monkey_tn, s.monkey_tp, s.monkey_fn, s.monkey_fp)
	# print("Model accuracy: {0:.2f}%".format((s.monkey_tn+s.monkey_tp)/(s.monkey_tn+s.monkey_tp+s.monkey_fn+s.monkey_fp)*100))

def print_conf_matrix(title, tn, tp, fn, fp):
	print(title)
	print("True-Positive: {}\tFalse-Negative: {}".format(tp, fn))
	print("False-Positive: {}\tTrue-Negative: {}".format(fp, tn))
	# recall = tp/(tp+fn)
	# precision = tp/(tp+fp)
	# f1_score = (2)/((1/recall)+(1/precision))
	# print("Recall: {0:.2f}%\nPrecision: {1:.2f}%\nF1-Score: {2:.2f}%".format(recall*100,precision*100, f1_score*100))


if __name__ == "__main__":
	# filename = 'ae_no_0.4__monkey_log.txt'
	filename = 'ae_monkey-bySum_106_diff_same_pairs_no_alef_results.txt'
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	data = parse_log(filename)
	random.shuffle(data)
	filterd_data = filter_only_conflicts(data, 50, 1000)
	random.shuffle(filterd_data)
	train_nn(data,filterd_data)
	# conf_matrix_by_thresholds(data, monkey_threshold=0.5, ae_threshold=0.4)
	# print(data)
	# plot_features(data)
	# filterd_data = filter_only_conflicts(data, 50, 1000)
	# random.shuffle(filterd_data)
	# plot_features(filterd_data)
	# train_nn(filterd_data)
	# train_nn(data)
	