
"""
for new_model:
"""

import numpy
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, BatchNormalization, Activation
from keras.layers.convolutional import Conv2D, MaxPooling2D
from keras.constraints import maxnorm
from keras.utils import np_utils
from keras import backend as K 

"""
for geeks model:
"""
# # importing libraries 
# from keras.preprocessing.image import ImageDataGenerator 
# from keras.models import Sequential 
# from keras.layers import Conv2D, MaxPooling2D 
# from keras.layers import Activation, Dropout, Flatten, Dense 
# from keras import backend as K 

def New_model(n_class,img_width, img_height):

	if K.image_data_format() == 'channels_first': 
		shape = (1, img_width, img_height) 
	else: 
		shape = (img_width, img_height, 1) 

	model = Sequential()

	model.add(Conv2D(32, (3, 3), input_shape= shape, padding='same'))
	model.add(Activation('relu'))

	model.add(Dropout(0.2))

	model.add(BatchNormalization())

	model.add(Conv2D(64, (3, 3), padding='same'))
	model.add(Activation('relu'))


	model.add(MaxPooling2D(pool_size=(2, 2)))
	model.add(Dropout(0.2))
	model.add(BatchNormalization())

	model.add(Conv2D(64, (3, 3), padding='same'))
	model.add(Activation('relu'))
	model.add(MaxPooling2D(pool_size=(2, 2)))
	model.add(Dropout(0.2))
	model.add(BatchNormalization())
		
	model.add(Conv2D(128, (3, 3), padding='same'))
	model.add(Activation('relu'))
	model.add(Dropout(0.2))
	model.add(BatchNormalization())

	model.add(Flatten())
	model.add(Dropout(0.2))

	model.add(Dense(256, kernel_constraint=maxnorm(3)))
	model.add(Activation('relu'))
	model.add(Dropout(0.2))
	model.add(BatchNormalization())
		
	model.add(Dense(128, kernel_constraint=maxnorm(3)))
	model.add(Activation('relu'))
	model.add(Dropout(0.2))
	model.add(BatchNormalization())

	model.add(Dense(n_class))
	model.add(Activation('softmax'))

	model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

	return model


def geeksModel(n_class,img_width,img_height):



	if K.image_data_format() == 'channels_first': 
		input_shape = (1, img_width, img_height) 
	else: 
		input_shape = (img_width, img_height, 1) 
	model = Sequential() 
	model.add(Conv2D(32, (2, 2), input_shape =input_shape )) 
	model.add(Activation('relu')) 
	model.add(MaxPooling2D(pool_size =(2, 2))) 
	
	model.add(Conv2D(32, (2, 2))) 
	model.add(Activation('relu')) 
	model.add(MaxPooling2D(pool_size =(2, 2))) 
	
	model.add(Conv2D(64, (2, 2))) 
	model.add(Activation('relu')) 
	model.add(MaxPooling2D(pool_size =(2, 2))) 
	
	model.add(Flatten()) 
	model.add(Dense(64)) 
	model.add(Activation('relu')) 
	model.add(Dropout(0.5)) 
	model.add(Dense(1)) 
	model.add(Activation('sigmoid')) 
	
	model.compile(loss ='binary_crossentropy', 
						optimizer ='rmsprop', 
					metrics =['accuracy']) 




def New_model1(n_class,img_width, img_height):


	classifier = Sequential()

   # Step 1 - Convolution
   # input layer
   classifier.add(Convolution2D(filters=filters, kernel_size=kernel, input_shape=(img_width, img_height, 1), activation='relu'))

   # Step 2 - Pooling
   classifier.add(MaxPooling2D(pool_size=(2, 2)))

   # # To increase Efficiency, add another Convolutional layer
   # classifier.add(Convolution2D(filters=32, kernel_size=3, activation='relu'))
   #
   # classifier.add(MaxPooling2D(pool_size=(2, 2)))

   classifier.add(Dropout(dropout))

   # Step 3 - Flattening
   classifier.add(Flatten())


   # Step 4 - Full Connection
   # add hidden layers


   classifier.add(Dense(units=2048, activation="relu"))
   classifier.add(Dropout(dropout))

   classifier.add(Dense(units=1024, activation="relu"))

   classifier.add(Dense(units=512, activation="relu"))
   classifier.add(Dropout(dropout))

   classifier.add(Dense(units=256, activation="relu"))
   classifier.add(Dropout(dropout))


   # Output layer
   classifier.add(Dense(units=num_of_classes, activation="softmax"))

   ################# Compiling the CNN #################
   """
   we need to compile our model. Compiling the model takes three parameters: optimizer, loss and metrics.
   The optimizer controls the learning rate. We will be using ‘adam’ as our optmizer. Adam is generally a good optimizer to use for many cases.
   The adam optimizer adjusts the learning rate throughout training.
   The learning rate determines how fast the optimal weights for the model are calculated.
   A smaller learning rate may lead to more accurate weights (up to a certain point), but the time it takes to compute the weights will be longer.
   We will use ‘categorical_crossentropy’ for our loss function. This is the most common choice for classification.
   A lower score indicates that the model is performing better.
   To make things even easier to interpret, we will use the ‘accuracy’ metric to see the accuracy score on the validation set when we train the model.
   """
   classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])