
import numpy as np
import _global
from classes import IdLetter, LetterImgPredict


def get_identified_letters(letters):
	id_letters = []
	basic_letters_model = LetterImgPredict(_global.lettersClassifier)
	improved_letters_model = LetterImgPredict(_global.lettersImprovedClassifier)

	for letter in letters:
		basic_result, id_letter = basic_letters_model.predict(letter)
		if basic_result > _global.BASIC_LETTER_THESHOLD:
			if id_letter.letter_name == "ץ":
				continue
			if id_letter.letter_name in _global.ae_trained_letters.values():
				improved_result, id_letter_improved = improved_letters_model.predict(letter)
				if improved_result < _global.IMPROVED_LETTER_THESHOLD:
					continue
				if id_letter_improved.letter_index == 30: # dont save it if its garbage
					continue
			id_letters.append(id_letter)

	return id_letters


def get_monkey_features(found_letters):
	'''
	returns the 'feature vector' for a given found_letters
	'''
	count_list = [0] * 27
	for letter in found_letters:
		count_list[letter.letter_index]+=1
	length = len(found_letters)
	counter_list_precent = [i * (100/length) for i in count_list]
	return counter_list_precent


def get_letter_ae_features(letters):

	for letter in letters:
		if letter.letter_name in _global.ae_trained_letters.values():
			letter.ae_features = _global.encoder.predict(letter.letter_img).ravel()
