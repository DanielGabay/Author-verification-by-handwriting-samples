
def generate_output(compare_docs):
	output =  "Monkey Result: {}\nAE result: {}\nSSIM Result: {}".format(\
												   compare_docs.monkey_results,\
												   compare_docs.letters_ae_results,\
												   compare_docs.ssim_results)
	return output

def generate_gui_output(compare_docs): 
	monkey_res = compare_docs.monkey_results['result']
	monkey_pred = compare_docs.monkey_results['precent'] * 100
	ae_res = compare_docs.letters_ae_results['result_by_predictions']
	ae_pred = compare_docs.letters_ae_results['precent_by_predictions'] * 100
	ssim_res = compare_docs.ssim_results['result']
	ssim_pred = compare_docs.ssim_results['precent'] * 100
	final_result = compare_docs.final_result['result']
	final_pred = compare_docs.final_result['precent'] * 100
	gui_output = "Algo1: Monkey Result:\n\t{0} [Confident: {1:.2f}%]".format(monkey_res, monkey_pred)
	gui_output += "\nAlgo2: AutoEncoder Letters Result:\n\t{0} [Confident: {1:.2f}%]".format(ae_res, ae_pred)
	gui_output += "\nAlgo3: SSIM Result:\n\t{0} [Confident: {1:.2f}%]".format(ssim_res, ssim_pred)
	gui_output += "\n\nFinal Result:\n\t{0} [Confident: {1:.2f}%]".format(final_result, final_pred)
	
	return gui_output


def generate_conclusion(compare_docs):
	conclusion = compare_docs.monkey_results['result'] + ">" if\
				  compare_docs.monkey_results['result'] == compare_docs.letters_ae_results['result']\
				  else "Conflict>"
	return conclusion

	# conclusion2 = "\n\tWith AE by predictions:\n\t<"
	# conclusion2 += compare_docs.monkey_results['result'] + ">" if\
	# 			  compare_docs.monkey_results['result'] == compare_docs.letters_ae_results['result_by_predictions']\
	# 			  else "Conflict>" 

def print_ae_monkey_results(s, len_b):
	print("\n------------------")
	print("Number of same pairs checked:{}".format(len_b))
	print("Sum of al pairs checked: {}".format(s.count_num_of_tests))
	print("\n------------------")
	print_conf_matrix("Monkey & letter AE Conf & ssim Matrix:", s.tn, s.tp, s.fn, s.fp)
	print("Model accuracy: {0:.2f}%".format(model_acc(s.tn, s.tp, s.fn, s.fp)))
	# print_conf_matrix("Monkey & letter AE Conf Matrix:", s.tn, s.tp, s.fn, s.fp)
	# print("Model accuracy: {0:.2f}% (*NOTE: not includes Undecided results!)".format(model_acc(s.tn, s.tp, s.fn, s.fp)))
	# print("Undecided Results:\n->conflict:{}\n-->conflict_while_same:{}\n-->conflict_while_diff:{}"\
		# .format(s.conflict, s.conflict_while_same,s.conflict_while_diff))
	print("\n------------------")
	print_conf_matrix("Only letter AE Conf Matrix:", s.ae_tn, s.ae_tp, s.ae_fn, s.ae_fp)
	print("Model accuracy: {0:.2f}%".format(model_acc(s.ae_tn, s.ae_tp, s.ae_fn, s.ae_fp)))
	print("\n------------------")
	print_conf_matrix("Only Monkey Conf Matrix:", s.monkey_tn, s.monkey_tp, s.monkey_fn, s.monkey_fp)
	print("Model accuracy: {0:.2f}%".format(model_acc(s.monkey_tn, s.monkey_tp, s.monkey_fn, s.monkey_fp)))
	print("\n------------------")
	print_conf_matrix("Only ssim Conf Matrix:", s.ssim_tn, s.ssim_tp, s.ssim_fn, s.ssim_fp)
	print("Model accuracy: {0:.2f}%".format(model_acc(s.ssim_tn, s.ssim_tp, s.ssim_fn, s.ssim_fp)))

def model_acc(tn, tp, fn, fp):
	total = tn+tp+fn+fp
	if total == 0:
		return 0
	return (tn+tp)/(total) * 100

def print_conf_matrix(title, tn, tp, fn, fp):
	recall, precision, f1_score = 0, 0, 0
	print(title)
	print("True-Positive: {}\tFalse-Negative: {}".format(tp, fn))
	print("False-Positive: {}\tTrue-Negative: {}".format(fp, tn))
	if tp+fn != 0:
		recall = tp/(tp+fn)
		
	if tp+fp != 0:
		precision = tp/(tp+fp)
	if recall != 0 and precision != 0:
		f1_score = (2)/((1/recall)+(1/precision))
	print("Recall: {0:.2f}%\nPrecision: {1:.2f}%\nF1-Score: {2:.2f}%".format(recall*100,precision*100, f1_score*100))