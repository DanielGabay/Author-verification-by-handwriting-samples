
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