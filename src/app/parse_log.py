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
import joblib

import csv
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

'''
new test log example with: AE by predictions & SSIM
idx0: Test: 10b.tiff 10.tiff
idx1: Monkey Result:
idx2: <Same Author> [confident: 83.99%]
idx3: Letters AE Result:
idx4: <Same Author>
idx5: count_same: 8881
idx6: count_diff: 5418
idx7: sum_predictions: 1258
idx8: precent_by_predictions: 0.619
idx9: ssim result:
idx10: <Same>
idx11: pred: 0.477
idx12: Real: True
idx13: Mark: Same
'''

new_log_by_majority = False
new_log_ae_by_pred = True
new_log_mlp = True
new_log_normalize_predictions = False
new_log_ssim_thresh = 0.5
new_log_ae_thresh = 0.5

if new_log_by_majority:
	new_log_ae_thresh = 0.55
	new_log_ssim_thresh = 0.44

# [monkey_res, letters_ae_res, same/diff {1/0}]
def parse_log(filename, old_log=False, to_excel=False):
	data = list()
	test_names = list()
	with open(filename) as fp:
		lines = fp.readlines()
		for line_idx in range(len(lines)):
			if 'Test:' in lines[line_idx]:
				l = lines[line_idx].split(" ") # ["Test:", "A.tiff", "B.tiff"] -> will take only names
				test_names.append([l[1], l[2].replace("\n","")])
				test_data = None
				if not to_excel:
					if old_log:
						test_data = get_old_log_test_data(lines, line_idx)
					else:
						test_data = get_new_log_test_data(lines, line_idx)
				else:
					test_data = get_new_log_test_data_to_excel(lines, line_idx)
				data.append(test_data)
	if to_excel:
		return data, test_names
	return data

def get_old_log_test_data(lines, line_idx):
	test_data = []
	test_data.append(get_monkey_data(lines,line_idx+3))
	test_data.append(get_letters_ae_by_count_data(lines, line_idx+6))
	test_data.append(get_real_data(lines, line_idx+13))
	return test_data

def get_new_log_test_data(lines, line_idx):
	test_data = []
	test_data.append(get_monkey_data(lines,line_idx+2))
	if new_log_ae_by_pred:
		test_data.append(get_letters_ae_by_pred_data(lines, line_idx+8))
	else:
		test_data.append(get_letters_ae_by_count_data(lines, line_idx+5))
	test_data.append(get_ssim_data(lines, line_idx+10))
	test_data.append(get_real_data(lines, line_idx+12))
	return test_data

def predict_data_features(data):
	np_data = np.array(data)
	X = np_data[:3]
	model = joblib.load("models/hebFinalResult_mlp.sav")
	proba = model.predict_proba(X.reshape(1,-1))[0]
	if proba[0] > proba[1]:
		return 0, float('{:.2f}'.format(proba[0])) # predicted diff
	else:
		return 1, float('{:.2f}'.format(proba[1])) # predicted same

def get_new_log_test_data_to_excel(lines, line_idx):
	test_data = []
	test_data.append(get_monkey_data(lines,line_idx+2))
	test_data.append(get_letters_ae_by_pred_data(lines, line_idx+8))
	test_data.append(get_ssim_data(lines, line_idx+10))
	test_data.append(get_real_data(lines, line_idx+12))
	predicted, proba = predict_data_features(test_data)
	test_data.append(predicted)
	test_data.append(proba)
	cnt_same, cnt_diff = get_letters_ae_by_count_data_to_excel(lines, line_idx+5)
	test_data.append(cnt_same)
	test_data.append(cnt_diff)
	return test_data

def get_monkey_data(lines, line_idx):
	s = lines[line_idx].split(':')[1]
	res = s.replace('\n', '').replace(' ', '').replace(']','').replace('%','')
	res = float(res) / 100
	if 'Same' in lines[line_idx]:
		if new_log_by_majority:
			return 1
		return res
	if new_log_by_majority:
		return 0
	return 1 - res

def get_letters_ae_by_count_data(lines, line_idx):
	cnt_same = int(lines[line_idx].split(':')[1])
	cnt_diff = int(lines[line_idx+1].split(':')[1])
	res = (cnt_same) / (cnt_same+cnt_diff)
	if new_log_by_majority:
		return 1 if cnt_same > cnt_diff else 0
	return res

def get_letters_ae_by_count_data_to_excel(lines, line_idx):
	cnt_same = int(lines[line_idx].split(':')[1])
	cnt_diff = int(lines[line_idx+1].split(':')[1])
	return cnt_same, cnt_diff

def get_letters_ae_by_pred_data(lines, line_idx):
	prec = float(lines[line_idx].split(" ")[-1])
	if new_log_normalize_predictions:
		prec = (prec - 0.139)/(0.778 - 0.139)
	if new_log_by_majority:
		return 1 if prec > new_log_ae_thresh else 0
	return prec

def get_ssim_data(lines, line_idx):
	prec = float(lines[line_idx+1].split(" ")[-1]) / 100
	if new_log_normalize_predictions:
		prec = (prec - 0.124)/(0.566-0.124)
	if new_log_by_majority:
		return 1 if prec > new_log_ssim_thresh else 0
	return prec

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

def getXY(data, old_log=True):
	length = len(data[0])
	data = np.array(data)
	features = [0,1] if old_log else [0,1,2] # new log has 3 features (monkey,ae,ssim)
	X = data[:,features]
	y = data[:,[length-1]].ravel()
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
		elif predict == 0 and y_test[i] == 0:
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

def new_log_print_test_proba(model, model_name, X_test, y_test):
	correct_same = 0
	correct_diff = 0
	for i in range(len(X_test)):
		predict = model.predict(X_test[i].reshape(1,-1))[0]
		predict_proba = model.predict_proba(X_test[i].reshape(1,-1))[0]
		if predict == 1 and y_test[i] == 1:
			correct_same += 1
		elif predict == 0 and y_test[i] == 0:
			correct_diff += 1
		print("Monkey: {0:.2f}\nAE: {1:.2f}\nSSIM: {2:.2f}\nExcpected: {3}\npredicted: {4}\nproba: {5}".format(\
			X_test[i][0], X_test[i][1], X_test[i][2], y_test[i], predict, predict_proba))

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

def old_log():
	# filename = 'ae_no_0.4__monkey_log.txt'
	filename = 'ae_monkey-bySum_106_diff_same_pairs_no_alef_results.txt'
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	data = parse_log(filename, old_log=True, to_excel=False)
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

def new_log_train_nn(data):
	X, y = getXY(data, old_log=False)
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=3)
	if new_log_mlp:
		mlp = MLPClassifier(max_iter=1000, shuffle=True)
		mlp.fit(X_train, y_train)
		new_log_print_test_proba(mlp, 'Basic Nueral-Regression', X_test, y_test)
		_print_scores(mlp, 'Basic Nueral-Network', X_train, y_train, X_test, y_test)
		# joblib.dump(mlp, 'hebFinalResult_mlp.sav') # save trained model

	else:
		lr = LogisticRegression()
		lr.fit(X_train,y_train)
		new_log_print_test_proba(lr, 'Basic Logistic-Regression', X_test, y_test)
		_print_scores(lr, 'Basic Logistic-Regression', X_train, y_train, X_test, y_test)

def new_log():
	filename = 'ssim_old_data_106.txt'
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	data = parse_log(filename, old_log=False, to_excel=False)
	random.shuffle(data)
	new_log_train_nn(data)
	# print(data)


def write_to_csv(csv_file, vector):
	#write a new line to the csvfile.
	csvWriter = csv.writer(csv_file,delimiter=',')
	csvWriter.writerow(vector)

def new_log_to_excel(plot=False):
	filename = 'final_result_new_data97'
	# filename = 'ssim_old_data_106'
	if len(sys.argv) > 1:
		filename = sys.argv[1]
	data, test_names = parse_log(filename + '.txt', old_log=False, to_excel=True)
	csv_name = filename + '.csv'
	with open(csv_name, 'w', newline='') as csv_file:
		header = ["File1", "File2", "Monkey", "AE", "SSIM", "Label", "Predicted","Proba", "Count Same", "Count Diff"]
		write_to_csv(csv_file, header)
		for i in range(len(data)):
			vector = test_names[i] + data[i]
			write_to_csv(csv_file, vector)
	if plot:
		plot_final_res(data)


def plot_final_res(data):
	colors = ['r', 'g']
	fig, ax = plt.subplots()
	for i in range(2):
		points = np.array([[data[j][4], data[j][5]] for j in range(len(data)) if data[j][3] == i])
		if i == 1:
			ax.scatter(points[:, 0], points[:, 1], s=12, c=colors[i], marker='*', label='label: Same')
		else:
			ax.scatter(points[:, 0], points[:, 1], s=12, c=colors[i], label='label: Different')
	plt.title('Final result prediction <-> label',loc='center')
	plt.legend(loc="lower center")
	plt.xlabel('Predicted as')
	plt.ylabel('Prediction precent')
	plt.show()


def convet_utf16_utf8(old_name, new_name):
	file_old = open(old_name, mode='r', encoding='utf-16-le')
	file_new = open(new_name, mode='w', encoding='utf-8')
	text = file_old.read()
	file_new.write(text)

if __name__ == "__main__":
	# old_log()
	# new_log()
	new_log_to_excel(plot=False)
