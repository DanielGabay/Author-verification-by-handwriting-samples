from keras.models import model_from_json
import _global

def load_and_compile_letters_model(model):
	'''
	Load the model .h5 and .json files and compile it.
	add lettersClassifier into _globals
	'''
	json_file = open('{}{}.json'.format(_global.MODELS_PATH, model), 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	classifier = model_from_json(loaded_model_json)
	classifier.load_weights("{}{}.h5".format(_global.MODELS_PATH, model))
	classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
	_global.lettersClassifier = classifier
	print("Loaded & compiled model from disk")



