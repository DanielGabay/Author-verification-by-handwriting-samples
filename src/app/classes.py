import _global
import numpy as np
import cv2
from keras.preprocessing import image
import matplotlib.pyplot as plt
from skimage import measure

class IdWord():
	'''
	Identified word
	'''
	def __init__(self, word_img, word_name, word_index):
		self.word_img = word_img
		self.word_name = word_name # identified word name
		self.word_index = word_index # index in dictionary

class IdLetter():
	'''
	Identified letter.
	'''
	def __init__(self, letter_img, letter_name,letter_index, img_resized):
		self.letter_img = letter_img
		self.letter_name = letter_name # identified letter name
		self.letter_index = letter_index # index in dictionary
		self.img_resized = img_resized
	'''
	at run time we'll add the following:
	@ae_features -> holds the vector of auto-encoder features for this letter
	'''

class Document():
	'''
	This class will hold all the needed data for our document object
	'''
	# @name: document name.
	def __init__(self, name):
		self.name = name

	'''
	at run time we'll add the following:
	@doc_img: save prepared document
	@id_words: list of all identified words. -> [IdWord objects]
	@id_letters: list of all identified letters.  ->[IdLetter objects]
	@monkey_features: list of features that were found at the monkey algorithem.
	'''

class LetterImgPredict():
	def __init__(self, classifier):
		self.classifier = classifier

	def predict(self, letter_img):
		letter_img, letter_resized = self.predictable_img(letter_img)
		result = self.classifier.predict(letter_img)
		max_result = max(result[0])
		letter_index = result[0].tolist().index(max_result)
		selected_letter = _global.lang_letters.get(letter_index)
		return max_result, IdLetter(letter_img ,selected_letter, letter_index, letter_resized)
	
	def predictable_img(self, img):
		img_resized = cv2.resize(img, ( _global.LETTERS_SIZE, _global.LETTERS_SIZE))
		_img = img_resized.reshape((_global.LETTERS_SIZE, _global.LETTERS_SIZE, 1))
		_img = image.img_to_array(_img)
		_img = np.expand_dims(_img, axis=0)
		return _img / 255, img_resized
	

class AlgoPredict():
	'''
	This class handle predict process
	'''
	def __init__(self, algo_classifier):
		self.classifier = algo_classifier

	def create_diff_vector(self, vec1, vec2, by_sum):
		vectors_len = len(vec1)
		diff_vector = [0] * vectors_len
		for i in range (vectors_len):
			diff_vector[i] =  abs(vec1[i] - vec2[i])
		diff_vector = diff_vector if not by_sum else sum(diff_vector)
		return np.asarray(diff_vector)

	def predict(self, vec1, vec2, by_sum=False, is_monkey=False, threshold=0.5):
		diff_vector = self.create_diff_vector(vec1, vec2, by_sum)
		result = self.classifier.predict_proba(diff_vector.reshape(1,-1))
		if result[0][0] > threshold: # different authors
			res = result[0][0] if is_monkey else result[0][1]
			return False, res
		else:  # same authors
			return True, result[0][1]
			# print("<Same Author> [confident: {0:.2f}%]".format(result[0][1]*100))

class CompareDocuments():
	'''
	This class hold pair of documents that we are currently comparing.
	at run time we'll add the following fields:
	self.monkey_results -> dict: {<result>: <value1>, <precent>: <value2>}/
								*	value1: String -> 'Same'/'Different'
						  		* 	value2: algo result, number between (0-1)
	self.letters_ae_results -> dict: same as above
	self.words_ae_results -> dict: same as above
	self.final_result -> dict: same as above, after summarize all algos results
	'''

	# @doc1 -> Document object representing the first doc
	# @doc2 -> Document object representing the second doc
	# @monkey -> handle prediction for monkey algorithm
	# @ae_letters -> handle prediction for AutoEncoder letters algorithm
	def __init__(self, doc1, doc2):
		self.doc1 = doc1
		self.doc2 = doc2
		self.monkey = AlgoPredict(_global.monkeyClassifier)
		self.ae_letters = AlgoPredict(_global.aeLettersClassifier)
		self.ssim_count = 0
		self.ssim_total = 0

	def monkey_results(self):
		by_sum = True if 'Sum' in _global.MONKEY_MODEL else False
		is_same, is_same_precent = self.monkey.predict(self.doc1.monkey_features,\
													   self.doc2.monkey_features,\
													   by_sum=by_sum,\
													   is_monkey=True)
		self.monkey_results = {'result': 'Same' if is_same is True else 'Different',\
								   'precent' : is_same_precent}

	def filter_ae_trained_letters(self, letters):
		return [x for x in letters if x.letter_name in _global.ae_trained_letters.values()]


	def showImages(self, img1,img2, prec):
		plt.subplot(121), plt.imshow(img1,cmap='gray')
		plt.subplot(122), plt.imshow(img2,cmap='gray')
		plt.title('prediction: {}'.format(prec)) 
		plt.show()


	def _ssim(self, letter1, letter2):
		s = measure.compare_ssim(cv2.resize(letter1, (28,28)), cv2.resize(letter2, (28,28)))
		self.showImages(letter1, letter2, s)

	
	def letters_autoencoder_results(self):
		count_same, count_diff, total_count = 0, 0, 0
		sum_predictions, precent, precent_by_predictions = 0, 0, 0
		doc1_letters = self.filter_ae_trained_letters(self.doc1.id_letters)
		doc2_letters = self.filter_ae_trained_letters(self.doc2.id_letters)
		for letter1 in doc1_letters:
			for letter2 in doc2_letters:
				if letter1.letter_name == letter2.letter_name:
					self.ssim_count += measure.compare_ssim(letter1.img_resized, letter2.img_resized)
					self.ssim_total += 1
					is_same, predict_prec = self.ae_letters.predict(letter1.ae_features, letter2.ae_features, by_sum=False)
					if is_same:
						count_same += 1
					else:
						count_diff += 1
					sum_predictions += predict_prec

					# self.showImages(letter1.img, letter2.img, predict_prec)
		total_count = count_same + count_diff
		result = 'Same' if count_same > count_diff else 'Different'

		if total_count != 0:
			precent_by_predictions = sum_predictions / total_count
			if result is 'Same':
				precent = count_same / total_count
			elif result is 'Different':
				precent = count_diff / total_count
		
		result_by_predictions = 'Same' if precent_by_predictions > _global.AE_SUM_PRED_THRESH else 'Different'	
		self.letters_ae_results = {	'result': result,\
								  	'precent': precent,\
							        'count_same': count_same,\
									'count_diff': count_diff,\
									'sum_predictions': sum_predictions,\
									'precent_by_predictions': precent_by_predictions,\
									'result_by_predictions': result_by_predictions
									}
class Stats():
	def __init__(self):
		self.tp = 0
		self.fp = 0
		self.tn = 0
		self.fn = 0
		self.ae_tp = 0
		self.ae_fp = 0
		self.ae_tn = 0
		self.ae_fn = 0
		self.monkey_tp = 0
		self.monkey_fp = 0
		self.monkey_tn = 0
		self.monkey_fn = 0
		self.ssim_tp = 0
		self.ssim_fp = 0
		self.ssim_tn = 0
		self.ssim_fn = 0
		self.conflict = 0
		self.conflict_while_same = 0
		self.conflict_while_diff = 0
		self.mark_as = ""
		self.same_author = None
		self.count_num_of_tests = 0