import numpy as np
import _global
import joblib
from monkey_functions import create_diff_vector
from classes import CompareDocuments, Document, IdLetter, IdWord

def prediction_ae_letters(diff_vec):
	diff_vec = np.asarray(diff_vec)
	result = _global.aeLettersClassifier.predict_proba(diff_vec.reshape(1,-1))
	if result[0][0] > 0.5:
		# print("<Different Authors> [Confident: {0:.2f}%]".format(result[0][0]*100))
		# return False, result[0][0]
		return False, result[0][1]
	else:
		# print("<Same Author> [confident: {0:.2f}%]".format(result[0][1]*100))
		return True, result[0][1]

def get_compared_docs_ae_letters_results(compare_docs):
	count_same, count_diff = 0, 0
	sum_predictions = 0
	for letter1 in compare_docs.doc1.id_letters:
		for letter2 in compare_docs.doc2.id_letters:
			if letter1.letter_name == letter2.letter_name and\
				letter1.letter_name in _global.ae_trained_letters.values():
					diff_vector = create_diff_vector(letter1.ae_features, letter2.ae_features)
					is_same, predict_prec = prediction_ae_letters(diff_vector)
					if(is_same):
						count_same += 1
					else:
						count_diff += 1
					sum_predictions += predict_prec

	precent = 0
	result = 'Same' if count_same > count_diff else 'Different'
	if result is 'Same' and (count_same + count_same != 0):
		precent = count_same / (count_same + count_diff)
	elif result is 'Different' and (count_same + count_same != 0):
		precent = count_diff / (count_same + count_diff)

	precent_by_predictions = sum_predictions/(count_same+count_diff)
	result_by_predictions = 'Same' if precent_by_predictions > _global.AE_SUM_PRED_THRESH else 'Diff'	
	compare_docs.letters_ae_results = {'result': result,\
								       'precent': precent,\
									   'count_same': count_same,\
									   'count_diff': count_diff,\
									   'sum_predictions': sum_predictions,
									   'precent_by_predictions': precent_by_predictions,
									   'result_by_predictions': result_by_predictions}