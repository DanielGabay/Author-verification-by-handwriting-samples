import os
import joblib
from keras.models import model_from_json

def init(language='hebrew', monkey_by_vectors=False,\
		test_mode=True, default_letters_ae=True):
	'''
	@param: language:
		Current version has the ability to process only hebrew docs.
		In the future we'll support in more languages
	@param: monkey_by_vectors
		Load the right monkey model by the wanted method
		True: by_vectors
		False: by_sum
	'''
	os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
	global lang_letters
	global lang_words
	global ae_letters
	global DATA_PATH
	global MODELS_PATH
	global LETTERS_MODEL
	global LETTERS_IMPROVED_MODEL
	global WORDS_MODEL
	global MONKEY_MODEL
	global LETTERS_SIZE
	global WORDS_SIZE
	global AE_LETTERS_MODEL
	global ae_trained_letters
	global TEST_MODE
	global monkeyClassifier
	global aeLettersClassifier
	global lettersClassifier
	global lettersImprovedClassifier
	global wordsClassifier
	global DEFAULT_LETTERS_AE
	global CONCAT_AS_ONE_IMAGE
	global AE_LETTERS_RESULT_BY_PRECENT
	global AE_SUM_PRED_THRESH


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

	
	DATA_PATH = 'data/'
	MODELS_PATH = 'models/'

	LETTERS_SIZE = 28
	WORDS_SIZE = 64
	CONCAT_AS_ONE_IMAGE = 'tiff_as_one_img.png'
	
	TEST_MODE = test_mode # True if we want to use DATA_PATH to load docs
	DEFAULT_LETTERS_AE = default_letters_ae # True if we use 1 AutoEncoder for all letters
	AE_LETTERS_RESULT_BY_PRECENT = True # True if we want to sum precents instead of counting same/diff letters
	AE_SUM_PRED_THRESH = 0.5 # threshold to determine Same/Diff by sum predictions

	lang_letters = {}
	lang_words = {}
	ae_trained_letters = {}
	if language == 'hebrew':
		LETTERS_MODEL = 'hebLettersModel'
		LETTERS_IMPROVED_MODEL = 'hebLettersImprovedModel'
		WORDS_MODEL = 'hebWordsModel'
		AE_LETTERS_MODEL = 'hebAutoEncoderDiffVecModel.sav'
		if monkey_by_vectors:
			MONKEY_MODEL = 'hebMonkeyLettersByVectors.sav'
		else:
			MONKEY_MODEL = 'hebMonkeyLettersBySum.sav'
		lang_letters = get_lang_letters_dict(language)
		lang_words = get_lang_words_ditc(language)
		ae_trained_letters = get_ae_trained_letters(language)
	
		#TODO: add trained words model to Model diractory

		aeLettersClassifier = joblib.load(MODELS_PATH + AE_LETTERS_MODEL)
		lettersClassifier = load_and_compile_model(LETTERS_MODEL, MODELS_PATH)
		lettersImprovedClassifier = load_and_compile_model(LETTERS_IMPROVED_MODEL, MODELS_PATH) 
		wordsClassifier = load_and_compile_model(WORDS_MODEL, MODELS_PATH)
		monkeyClassifier = joblib.load(MODELS_PATH + MONKEY_MODEL)

def load_and_compile_model(model, models_path):
	'''
	Load the model .h5 and .json files and compile it.
	add lettersClassifier into _globals
	'''
	json_file = open('{}{}.json'.format(models_path, model), 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	classifier = model_from_json(loaded_model_json)
	classifier.load_weights("{}{}.h5".format(models_path, model))
	classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
	print("Loaded & compiled model from disk")
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
					23: 'ם'
					}
	return lang_dict

def get_lang_words_ditc(lang):
	lang_dict = {}
	if lang is 'hebrew':
		lang_dict = {
					0: 'של',\
					1: 'לא',\
					2: 'את',\
					3: 'גם',\
					4: 'לסיכום',\
					5: 'כי',\
					6: 'זה',\
					7: 'זו',\
					8: 'יש',\
					9: 'לדעתי',\
					10: 'אני',\
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
					26: 'ץ'
					}
	return lang_dict