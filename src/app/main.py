import os
import sys

import cv2
import matplotlib.pyplot as plt
import numpy as np
from keras.preprocessing import image

import _global
from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.our_utils.prepare_document import \
    get_prepared_doc
from models.letterClassifier import load_and_compile_letters_model


def save_letters(letters, doc_name):
	found_letters = []
	out_path = createOutputDirs(doc_name)
	count = 0
	for letter in letters:
		letter = cv2.resize(letter.image_letter, (28, 28))
		letter = letter.reshape((28, 28, 1))

		test_letter = image.img_to_array(letter)
		test_image = np.expand_dims(test_letter, axis=0)
		result = _global.lettersClassifier.predict((test_image/255))
		if max(result[0]) > 0.995:
			letter_index = result[0].tolist().index(max(result[0]))
			selected_letter = _global.lang_letters[result[0].tolist().index(max(result[0]))]
			if selected_letter == "ץ": 
				continue
			inner_folder = "{}/{}".format(out_path,letter_index+1)
			if not os.path.exists(inner_folder):   # create folder to contain the line's img
				os.mkdir(inner_folder)
			save_name = "{}/{}.jpeg".format(inner_folder,count)
			print(save_name)
			cv2.imwrite(save_name,letter)
			count += 1
			found_letters.append({'image_letter': letter , 'letter_index': letter_index, 'selected_letter': selected_letter})
	return found_letters

def print_predictions(preidction):
		for i, v in enumerate(preidction):
			print(str(i)+" " + _global.lang_letters[i]+": "+str(float("{0:.2f}".format(v))))
		print("______")

def createOutputDirs(doc_name):
	out_main_folder = "out"
	if not os.path.exists(out_main_folder):   # create folder to contain the line's img
		os.mkdir(out_main_folder)
	out_path = "{}/{}".format(out_main_folder, doc_name)
	if not os.path.exists(out_path):   
		os.mkdir(out_path)
	return out_path

def show_letters(letters):
	count_good = 0
	count_all = 0
	for letter in letters:
		letter = cv2.resize(letter.image_letter, (28, 28))
		letter = letter.reshape((28, 28, 1))

		test_letter = image.img_to_array(letter)
		test_image = np.expand_dims(test_letter, axis=0)
		result = _global.lettersClassifier.predict((test_image/255))
		# print_predictions(result[0])
		if max(result[0]) > 0.995:
			selected_letter = _global.lang_letters[result[0].tolist().index(max(result[0]))]
			if selected_letter == "ץ": 
				continue
			count_all += 1
			print(selected_letter)
			cv2.imshow('',letter)
			k = cv2.waitKey(0)
			if k == 27:
				cv2.destroyAllWindows()
			else:
				count_good +=1
				cv2.destroyAllWindows()
			if count_all == 100:
				break
			plt.close('all')
	print("{} {} {}".format(count_good, count_all, count_good/count_all))

def main(doc_name):
	img_name = _global.DATA_PATH + doc_name
	img = get_prepared_doc(img_name)
	lines = get_lines(img, img_name)
	letters = get_letters(lines)

	# show_letters(letters)


def main_save_all():
	print("###")
	for root, dirs, files in os.walk(_global.DATA_PATH):
		print("###")
		for file in files:
			doc_name = file.split('.')[0]
			check_path_exist = "out/{}".format(doc_name)
			if os.path.exists(check_path_exist):   
				print("{}.tiff already done".format(file))
				continue
			img_name = _global.DATA_PATH + file
			img = get_prepared_doc(img_name)
			lines = get_lines(img, img_name)
			letters = get_letters(lines)
			found_letters = save_letters(letters, doc_name)


if __name__ == "__main__":
	if(len(sys.argv) < 2):
		print("Usage: python main.py <[save_all]/[file_name]> ")
		sys.exit(1)
	_global.init('hebrew')
	load_and_compile_letters_model(_global.LETTERS_MODEL)
	if(sys.argv[1] == 'save_all'):
		main_save_all()
	else: 
		doc_name = str(sys.argv[1])
		main(doc_name)
