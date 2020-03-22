from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras import backend as K
import os
import cv2
import sys
from keras.datasets import mnist
import numpy as np
import matplotlib.pyplot as plt



def save_model(model, name=""):
		path = os.path.dirname(os.path.abspath(__file__))
		path += "/weights/"
		if not os.path.exists(path):
			os.mkdir(path)

		# save train to Json
		encoder_json = model.to_json()
		with open(path + "encoder_" + name +".json" ,"w") as json_file:
			json_file.write(encoder_json)
		# serialize weights to HDF5
		model.save_weights(path + "encoder_" + name + ".h5")


def read_dataset(path):
	data = []
	path = os.path.dirname(os.path.abspath(__file__)) + path
	for root, dirs, files in os.walk(path):
		for file in files:
			img = cv2.imread(path + "/" + file, 0)
			data.append(np.array(img))
	print (len(data))
	return np.asarray(data) , np.asarray(data)


input_img = Input(shape=(28, 28, 1))  # adapt this if using `channels_first` image data format

x = Conv2D(16, (3, 3), activation='relu', padding='same')(input_img)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
x = MaxPooling2D((2, 2), padding='same')(x)
x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
encoded = MaxPooling2D((2, 2), padding='same')(x)



# at this point the representation is (4, 4, 8) i.e. 128-dimensional

x = Conv2D(8, (3, 3), activation='relu', padding='same')(encoded)
x = UpSampling2D((2, 2))(x)
x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
x = UpSampling2D((2, 2))(x)
x = Conv2D(16, (3, 3), activation='relu')(x)
x = UpSampling2D((2, 2))(x)
decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)

autoencoder = Model(input_img, decoded)
autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')


x_train,x_test = read_dataset('/dataset/5')
x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.
x_train = np.reshape(x_train, (len(x_train), 28, 28, 1))  # adapt this if using `channels_first` image data format
x_test = np.reshape(x_test, (len(x_test), 28, 28, 1))  # adapt this if using `channels_first` image data format

autoencoder.fit(x_train, x_train,epochs=5,batch_size=128,
				shuffle=True,
				validation_data=(x_test, x_test))


save_model(autoencoder)

decoded_imgs = autoencoder.predict(x_test)

n = 10
plt.figure(figsize=(20, 4))
for i in range(n):
	# display original
	ax = plt.subplot(2, n, i+1)
	plt.imshow(x_test[i].reshape(28, 28))
	plt.gray()
	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)

	# display reconstruction
	ax = plt.subplot(2, n, i +1 + n)
	plt.imshow(decoded_imgs[i].reshape(28, 28))
	plt.gray()
	ax.get_xaxis().set_visible(False)
	ax.get_yaxis().set_visible(False)
plt.show()

