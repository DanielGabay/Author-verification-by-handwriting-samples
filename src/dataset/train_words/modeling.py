# Importing the Keras Libraries and packages
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Sequential
from keras.layers import Convolution2D
from keras.layers import MaxPooling2D
from keras.layers import Flatten
from keras.layers import Dense
from keras.layers import Dropout
from keras.layers import Conv2D
from keras.layers import Activation
from our_model import New_model
from keras import backend as K
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"

# Part 2

# predictions


def run_model(num_of_epochs, train_size, validation_size, batch_Size, filters, dropout, kernel, model_name):

	img_width, img_height = 120, 120

	train_data_dir = 'dataset/train'
	test_data_dir = 'dataset/test'
	validation_data_dir = 'dataset/validation'

	model = New_model(11,img_width, img_height)

	train_datagen = ImageDataGenerator(rescale=1. / 255 )

	test_datagen = ImageDataGenerator(rescale=1. / 255)

	training_set = train_datagen.flow_from_directory(train_data_dir,target_size=(img_width, img_height),color_mode="grayscale",batch_size=batch_Size,shuffle=True)

	test_set = test_datagen.flow_from_directory(test_data_dir, target_size=(img_width, img_height), color_mode="grayscale", batch_size=batch_Size,shuffle=True)

	validation_set=test_datagen.flow_from_directory(validation_data_dir,target_size=(img_width, img_height),color_mode="grayscale",batch_size=batch_Size,shuffle=True)

	model.fit_generator(training_set,
						epochs=num_of_epochs, validation_data=validation_set,
						steps_per_epoch=train_size // batch_Size,
						validation_steps=validation_size // batch_Size,shuffle=True)

	# save train to Json
	model_json=model.to_json()
	with open(model_name + ".json", "w") as json_file:
		json_file.write(model_json)
	# serialize weights to HDF5
	model.save_weights(model_name+ '.h5')
