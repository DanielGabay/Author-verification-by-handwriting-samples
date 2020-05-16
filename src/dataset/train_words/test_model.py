# Import Json model
from keras.models import model_from_json
import os
import cv2
from keras.preprocessing.image import ImageDataGenerator
import numpy as np
from keras.preprocessing import image
import matplotlib.pyplot as plt
import sys

# import the necessary packages



letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י', 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת','ך', 'ם', 'ן', 'ף', 'ץ']

#to avoid errors
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


num_of_classes = 11
batch_Size = 128

width, height = 120, 120
############################################################## load the model jason file

# load json and create model
model_name = 'words_shuffle_model_resized_80_120'
json_file = open("{}.json".format(model_name), 'r')
loaded_model_json = json_file.read()
json_file.close()
classifier = model_from_json(loaded_model_json)

# load weights into new model
classifier.load_weights("{}.h5".format(model_name))
# weights, biases = classifier.layers[0].get_weights()
# print(weights)
print("Loaded model from disk")
# classifier.compile(optimizer='adam',  loss='categorical_crossentropy', metrics=['accuracy'])

# print("$$$$$$$$$$$$$$")
# test_datagen = ImageDataGenerator(rescale=1. / 255)
# test_set = test_datagen.flow_from_directory('dataset/test', target_size=(width, height), batch_size=batch_Size,
# 											 class_mode='categorical')
# ##############################################################




############################################################# this part is for testing an entire folder with the same letter

# letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י'
#             , 'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',
#            'ך', 'ם', 'ן', 'ף', 'ץ']

# letter = '0'
# test_set.reset()
#images = []
id_words = [i for i in range(1,12)]
for id_word in id_words:
	images = []
	for filename in os.listdir("dataset/test/" + str(id_word)):
		img = cv2.imread(os.path.join("dataset/test/" + str(id_word), filename),0)
		# print(os.path.join("dataset/test/" + str(id_word), filename))
		if img is not None:
			images.append(img)
	print(" len is :{}".format(len(images)))
	print(id_word)
	count = 0
	for img in images:
		# img = cv2.resize(img, (120, 80)) ######## this we addedddddddddddddddddd
		# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)######## this we addedddddddddddddddddd
		img = img.reshape((120, 120,1))######## this we addedddddddddddddddddd
		#test_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		test_image = image.img_to_array(img)
		test_image = np.expand_dims(test_image, axis=0)
		result = classifier.predict((test_image/255))
		max_result = max(result[0])
		word_index = result[0].tolist().index(max_result)+1
		#print(result[0])
		print(word_index)
		# input()
		if(word_index == id_word):
			count += 1
	print("test word: {}, recognize: {}, precent: {}".format(id_word, count, count/len(images)))

############################################################


# images = []
# for filename in os.listdir("4"):
# 	img = cv2.imread(os.path.join("4/{}".format(filename)))
# 	if img is not None:
# 		images.append(img)
# print(" len is :{}".format(len(images)))
# count = 0
# for img in images:
# 	# img = cv2.resize(img, (120, 80)) ######## this we addedddddddddddddddddd
# 	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)######## this we addedddddddddddddddddd
# 	img = img.reshape((120, 80,1))######## this we addedddddddddddddddddd
# 	#test_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 	test_image = image.img_to_array(img)
# 	test_image = np.expand_dims(test_image, axis=0)
# 	result = classifier.predict((test_image/255))
# 	max_result = max(result[0])
# 	print(result[0])
# 	sys.exit(1)
# 	word_index = result[0].tolist().index(max_result)+1
# 	print(word_index)
# 	print("_____")
# 	# print(result[0])
# 	# print(word_index)
# 	# input()
# 	if(word_index == 4):
# 		count += 1
# print("test word: {}, recognize: {}, precent: {}".format(4, count, count/len(images)))





############################################################ # this part is to view the accuracy on the test set

# loss, acc = classifier.evaluate_generator(test_set,steps=batch_Size)
# print("loss:"+ str(loss)+"  ,acc: "+str(acc))

###########################################################

# read the image and define the stepSize and window size
# (width,height)
# image = cv2.imread("16.png") # your image path
# tmp = image # for drawing a rectangle
# stepSize = 1
# (w_width, w_height) = (50, image.shape[0]-1) # window size
# for x in range(0, image.shape[1] - w_width , 5):
#     for y in range(0, image.shape[0] - w_height, stepSize):
#         window = image[y:y + w_height, x:x + w_width, :]
#         cv2.rectangle(tmp, (x, y), (x + w_width, y + w_height), (255, 0, 0), 2) # draw rectangle on image
#         plt.imshow(np.array(tmp).astype('uint8'))

#         img = cv2.resize(window, (28, 28)) ######## this we addedddddddddddddddddd
#         img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)######## this we addedddddddddddddddddd
#         img = img.reshape((28, 28,1))######## this we addedddddddddddddddddd
#         test_image = img
#         test_image = np.expand_dims(test_image, axis=0)
#         result = classifier.predict((test_image/255)*0.1)
#         #maxx = max(result[0][1])
#         maxx = max(result[0])
#         if maxx > 0.6:
#             for i, v in enumerate(result[0]):
#                 print(str(i)+" " + letters[i]+ ": "+str(float("{0:.2f}".format(v))))
#             print("#####################")
#             cv2.imshow('',img)
#             cv2.waitKey(0)
#         # draw window on image


# # show all windows
# plt.show()

# import sys
# sys.exit(1)

############################################################ this part is for testing a single image

# img =cv2.imread('4/131400001_46.png',0)

# img = cv2.resize(img, (120, 80)) ######## this we addedddddddddddddddddd
# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)######## this we addedddddddddddddddddd
# img = img.reshape((120, 80,1))######## this we addedddddddddddddddddd

# cv2.imshow('kkk', img)
# cv2.waitKey(0)
# img = cv2.resize(img, (120, 120))
# test_image = img
# test_image = image.img_to_array(test_image)
# test_image = np.expand_dims(test_image, axis=0)
# result = classifier.predict((test_image/255))
# print(result[0])
# for i, predict in enumerate(result[0]):
#     if predict == 1:
#         prediction = i
#         break
# else:
#     prediction = 'none'
#
# print("------------------")
# if prediction != 'none':
#     print(letters[prediction])

# ############################################################

# # this 2 lines is to view the probability vector
# for i, v in enumerate(result[0]):
# 	print(str(i+1)+ ": "+str(float("{0:.2f}".format(v))))

