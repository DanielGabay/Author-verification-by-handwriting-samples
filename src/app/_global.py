import joblib
from keras.models import model_from_json
import os

import sys

def init(language='hebrew', monkey_by_vectors=True,\
		test_mode=True, data_path=None, print_globals=False):
	'''
	@param: language:
		Current version has the ability to process only hebrew docs.
		In the future we'll support in more languages
	@param: monkey_by_vectors
		Load the right monkey model by the wanted method
		True: by_vectors
		False: by_sum
	'''
	global DATA_PATH
	global MODELS_PATH

	global lang_letters
	global ae_letters
	global ae_trained_letters

	global LETTERS_SIZE
	global TEST_MODE

	global AE_LETTERS_RESULT_BY_PRECENT
	global SSIM_THRESHOLD
	global BASIC_LETTER_THESHOLD
	global IMPROVED_LETTER_THESHOLD
	global AE_SUM_PRED_THRESH
	global CONCAT_AS_ONE_IMAGE

	global monkeyClassifier
	global aeLettersClassifier
	global lettersImprovedClassifier
	global lettersClassifier
	global encoder
	global finalResultClassifier

	global AE_LETTERS_MODEL
	global FINAL_RESULT_MODEL
	global LETTERS_MODEL
	global ENCODER_MODEL
	global LETTERS_IMPROVED_MODEL
	global MONKEY_MODEL

	'''
	use this try block to check wether this init function was
	called already.
	at the first time: continue init
	else: return
	'''
	try:
		lettersClassifier
	except NameError:
		pass
	else:
		return

	BASE_DIR = ""
	if getattr(sys, 'frozen', False):
		BASE_DIR = os.path.dirname(sys.executable)
	elif __file__:
		BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	
	MODELS_PATH = os.path.join(BASE_DIR, "models\\")
	DATA_PATH = os.path.join(BASE_DIR, "data\\")

	if data_path is not None:
		DATA_PATH = os.path.join(BASE_DIR, "{}\\".format(data_path))

	LETTERS_SIZE = 28
	CONCAT_AS_ONE_IMAGE = 'concat_img.png'

	TEST_MODE = test_mode # True if we want to use DATA_PATH to load docs
	AE_LETTERS_RESULT_BY_PRECENT = True # True if we want to sum precents instead of counting same/diff letters
	AE_SUM_PRED_THRESH = 0.5 # threshold to determine Same/Diff by sum predictions

	BASIC_LETTER_THESHOLD = 0.995
	IMPROVED_LETTER_THESHOLD = 0.8
	SSIM_THRESHOLD = 0.45
	lang_letters = {}
	ae_trained_letters = {}
	if language == 'hebrew':
		LETTERS_MODEL = 'hebLettersModel'
		ENCODER_MODEL = 'hebLettersEncoder32'
		LETTERS_IMPROVED_MODEL = 'hebLettersImprovedModel'
		AE_LETTERS_MODEL = 'hebAutoEncoderDiffVecModel.sav'
		FINAL_RESULT_MODEL = 'hebFinalResult_mlp.sav'
		if monkey_by_vectors:
			MONKEY_MODEL = 'hebMonkeyLettersByVectors_lr.sav'
			# MONKEY_MODEL = 'hebMonkeyLettersByVectors_mlp.sav'
			# MONKEY_MODEL = 'hebMonkeyLettersByVectors.sav'
		else:
			MONKEY_MODEL = 'hebMonkeyLettersBySum.sav'
		lang_letters = get_lang_letters_dict(language)
		ae_trained_letters = get_ae_trained_letters(language)

		'''
		load all models
		'''
		aeLettersClassifier = joblib.load(MODELS_PATH + AE_LETTERS_MODEL)
		monkeyClassifier = joblib.load(MODELS_PATH + MONKEY_MODEL)
		finalResultClassifier = joblib.load(MODELS_PATH + FINAL_RESULT_MODEL)
		lettersClassifier = load_model(MODELS_PATH, LETTERS_MODEL)
		lettersImprovedClassifier = load_model(MODELS_PATH, LETTERS_IMPROVED_MODEL)
		encoder = load_model(MODELS_PATH, ENCODER_MODEL)
	if print_globals:
		print("Monkey: {}\nAutoEncoder by predictions: {}".format(MONKEY_MODEL, AE_LETTERS_RESULT_BY_PRECENT))
		print("AutoEncoder threshold: {}".format(AE_SUM_PRED_THRESH))

def load_model(models_path, model_name):
	'''
	Load the model .h5 and .json files and compile it.
	add lettersClassifier into _globals
	'''
	json_file = open(os.path.join(models_path, model_name + ".json"), 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	classifier = model_from_json(loaded_model_json)
	classifier.load_weights(os.path.join(models_path, model_name + ".h5"))
	print("Loaded: {} from disk".format(model_name))
	return classifier

def get_ae_trained_letters(lang):
	lang_dict = {}
	if lang is 'hebrew':
		lang_dict = {
					1: 'ב',\
					3: 'ד',\
					4: 'ה',\
					7: 'ח',\
					11: 'ל',\
					12: 'מ',\
					14: 'ס',\
					16: 'פ',\
					23: 'ם',\
					30: 'זבל'
					}
	return lang_dict

def get_lang_letters_dict(lang):
	lang_dict = {}
	if lang is 'hebrew':
		lang_dict = {
					0: 'א',\
					1: 'ב',\
					2: 'ג',\
					3: 'ד',\
					4: 'ה',\
					5: 'ו',\
					6: 'ז',\
					7: 'ח',\
					8: 'ט',\
					9: 'י',\
					10: 'כ',\
					11: 'ל',\
					12: 'מ',\
					13: 'נ',\
					14: 'ס',\
					15: 'ע',\
					16: 'פ',\
					17: 'צ',\
					18: 'ק',\
					29: 'ר',\
					20: 'ש',\
					21: 'ת',\
					22: 'ך',\
					23: 'ם',\
					24: 'ן',\
					25: 'ף',\
					26: 'ץ',\
					30: 'זבל'
					}
	return lang_dict