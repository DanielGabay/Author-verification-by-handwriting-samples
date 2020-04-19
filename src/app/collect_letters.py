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

done_path = "{}/{}".format("letter_collection","done_with.txt")
max_threshold = 0.995
min_threshold = 0.95


def save_letters(letters, doc_name):
	count = 0
	for letter in letters:
		letter = cv2.resize(letter, (28, 28))
		letter = letter.reshape((28, 28, 1))

		test_letter = image.img_to_array(letter)
		test_image = np.expand_dims(test_letter, axis=0)
		result = _global.lettersClassifier.predict((test_image/255))
		max_result = max(result[0])
		threshold = -1
		if max_result >= max_threshold:
			threshold = max_threshold
		elif max_result >= min_threshold:
			threshold = min_threshold
		if threshold != -1:
			letter_index = result[0].tolist().index(max_result)
			inner_folder = "{}/{}/{}/".format("letter_collection",letter_index+1, threshold*100)
			selected_letter = _global.lang_letters[result[0].tolist().index(max_result)]
			if selected_letter == "ץ": 
				continue
			if not os.path.exists(inner_folder):   # create folder to contain the line's img
				os.mkdir(inner_folder)
			save_name = "{}/{}_{}.jpeg".format(inner_folder,doc_name,count)
			cv2.imwrite(save_name,letter)
			count += 1


def print_predictions(preidction):
		for i, v in enumerate(preidction):
			print(str(i)+" " + _global.lang_letters[i]+": "+str(float("{0:.2f}".format(v))))
		print("______")

def createOutputDirs():
	out_main_folder = "letter_collection"
	if not os.path.exists(out_main_folder):   # create folder to contain the line's img
		os.mkdir(out_main_folder)
	count = 1
	while(count < 27):
		out_path = "{}/{}".format(out_main_folder, count)
		if not os.path.exists(out_path):   
			print("make folder {}".format(count))
			os.mkdir(out_path)
		count+=1
	if not os.path.exists(done_path):   # create folder to contain the done img
		print("create done file")
		file = open(done_path, "w") 
		file.close()

def read_done_file():
	with open(done_path) as f:
		lines = f.read().splitlines()
		return lines

def write_done_file(done_list,doc_name):
	done_list.append(doc_name)
	file = open(done_path, "a") 
	file.write("{}{}".format(doc_name,"\n")) 
	file.close()

def main_save_all():
	done_list = read_done_file()  # read the files we already done with

	for root, dirs, files in os.walk(_global.DATA_PATH):
		for file in files:
			doc_name = file.split('.')[0]
			print(doc_name)
			
			if doc_name in done_list:   
				print("{} already done".format(file))
				continue
			img_name = _global.DATA_PATH + file
			img = get_prepared_doc(img_name)
			lines = get_lines(img, img_name)
			letters = get_letters(lines)
			found_letters = save_letters(letters, doc_name)
			write_done_file(done_list,doc_name)
			
	print("done")


if __name__ == "__main__":
	_global.init('hebrew')
	load_and_compile_letters_model(_global.LETTERS_MODEL)
	createOutputDirs() # create the folders to collect the data
	main_save_all()
