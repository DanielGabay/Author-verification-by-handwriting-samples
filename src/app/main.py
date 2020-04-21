import os
import sys

import cv2
import matplotlib.pyplot as plt
import numpy as np
from keras.preprocessing import image

import _global
from classes import Document, IdLetter, IdWord, CompareDocuments
from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.detectWords import get_words
from extractComparisonFeatures.our_utils.prepare_document import \
    get_prepared_doc
from models.letterClassifier import load_and_compile_letters_model

#TODO: move functions to some helper function file instead of
#getting them from the monkey_collect_data & test_monkey
from monkey_collect_data import get_identified_letters, get_monkey_features
from test_monkey import get_monkey_result, save_letters

def main(doc_name1, doc_name2):
	#TODO: think about the path of document for future use in GUI
	path = _global.DATA_PATH
	docs = [Document(doc_name1), Document(doc_name2)]

	# prepare Documents
	for doc in docs:
		doc.doc_img = get_prepared_doc(path+doc.name)
		# ---> Detection Phase
		lines = get_lines(doc.doc_img, doc.name)
		words = get_words(lines)
		letters = get_letters(lines)

		# ---> Identification Phase
		# we keep monkey letters in a different way for monkey use
		# than our new IdLetter class. for now keep it that way.
		id_letters_for_monkey, doc.id_letters = get_identified_letters(letters)
		doc.monkey_features = get_monkey_features(id_letters_for_monkey)

	compare_docs = CompareDocuments(docs[0], docs[1])
	# ---> Verification Phase
	monkey_res, monkey_precent = get_monkey_result(compare_docs.doc1.monkey_features,\
												   compare_docs.doc2.monkey_features)

	compare_docs.monkey_results = {'result': 'Same' if monkey_res is True else 'Different',\
								   'precent' : monkey_precent}
					   
	# print(compare_docs.monkey_results)

	# call autoencoder with letters & words
	# summaraize all results into one result

if __name__ == "__main__":
	# if(len(sys.argv) < 2):
	# 	print("Usage: python main.py <[save_all]/[file_name]> ")
	# 	sys.exit(1)
	#TODO: think how to determine monkey algo by_sum/by_vectors
	_global.init('hebrew')
	load_and_compile_letters_model(_global.LETTERS_MODEL)
	main('10.tiff', '100.tiff')
	# if(sys.argv[1] == 'save_all'):
	# 	main_save_all()
	# else: 
	# 	doc_name = str(sys.argv[1])
	# 	main(doc_name)

#TODO: move next functions to other file
#      no need in main file

def main_save_all():
	for root, dirs, files in os.walk(_global.DATA_PATH):
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
		letter = cv2.resize(letter, (_global.LETTERS_SIZE, _global.LETTERS_SIZE))
		letter = letter.reshape((_global.LETTERS_SIZE, _global.LETTERS_SIZE, 1))

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
