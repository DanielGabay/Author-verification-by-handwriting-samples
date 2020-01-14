from keras.models import model_from_json

def load_and_compile_model(model):
	json_file = open('models/{}.json'.format(model), 'r')
	loaded_model_json = json_file.read()
	json_file.close()
	classifier = model_from_json(loaded_model_json)
	classifier.load_weights("models/{}.h5".format(model))
	classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
	print("Loaded & compiled model from disk")
	return classifier



