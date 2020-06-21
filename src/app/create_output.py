
def generate_output(compare_docs):

	output =  "Monkey Result: {}\nAE result: {}\nSSIM Result: {}".format(\
												   compare_docs.monkey_results,\
												   compare_docs.letters_ae_results,\
												   compare_docs.ssim_results)
	return output


def generate_gui_output(compare_docs): 

	gui_output = "Algo1: Monkey Result:\n\t<{0}> [Confident: {1:.2f}%]\n".format(compare_docs.monkey_results['result'],\
														 						  compare_docs.monkey_results['precent']*100)
	gui_output += "Algo2: AutoEncoder Letters Result:\n\t<{}> [Confident: {:.2f}%]\n\tResult By Predictions:\n\t<{}> [Confident: {:.2f}%]\n".format(\
														compare_docs.letters_ae_results['result'],\
														compare_docs.letters_ae_results['precent']*100,
														compare_docs.letters_ae_results['result_by_predictions'],\
														compare_docs.letters_ae_results['precent_by_predictions']*100)
	gui_output += "\n\nFinal Result:\n\t<"
	
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