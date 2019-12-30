from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.our_utils.prepare_document import get_prepared_doc
import cv2
import sys
from keras.models import model_from_json
from keras.preprocessing import image
import numpy as np
import os
import matplotlib.pyplot as plt

DATA_PATH = "data/"

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
hebrew_letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י'\
            ,'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',\
           'ך', 'ם', 'ן', 'ף', 'ץ']

def load_and_compile_model():
    json_file = open('models/model99.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    classifier = model_from_json(loaded_model_json)
    classifier.load_weights("models/model99.h5")
    classifier.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    print("Loaded & compiled model from disk")
    return classifier

def save_letters(letters, classifier):
    for letter in letters:
        letter = cv2.resize(letter.image_letter, (28, 28))
        letter = letter.reshape((28, 28, 1))

        test_letter = image.img_to_array(letter)
        test_image = np.expand_dims(test_letter, axis=0)
        result = classifier.predict((test_image/255))
        if max(result[0]) > 0.995:
            selected_letter = hebrew_letters[result[0].tolist().index(max(result[0]))]
            if selected_letter == "ץ": 
                continue
            resized = cv2.resize(letter, (50,50), interpolation = cv2.INTER_AREA)
            cv2.imshow('',resized)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

def print_predictions(preidction):
        for i, v in enumerate(preidction):
            print(str(i)+" " + hebrew_letters[i]+": "+str(float("{0:.2f}".format(v))))
        print("______")

def show_letters(letters, classifier):
    count_good = 0
    count_all = 0
    for letter in letters:
        letter = cv2.resize(letter.image_letter, (28, 28))
        letter = letter.reshape((28, 28, 1))

        test_letter = image.img_to_array(letter)
        test_image = np.expand_dims(test_letter, axis=0)
        result = classifier.predict((test_image/255))
        # print_predictions(result[0])
        if max(result[0]) > 0.995:
            selected_letter = hebrew_letters[result[0].tolist().index(max(result[0]))]
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

def main():
    if(len(sys.argv) < 2):
        print("Usage: python main.py <file_name>")
        sys.exit(1)

    img_name = DATA_PATH + str(sys.argv[1])
    img = get_prepared_doc(img_name)
    lines = get_lines(img, img_name)
    letters = get_letters(lines)
    classifier = load_and_compile_model()
    show_letters(letters, classifier)
    # save_letters(letters, classifier)    

if __name__ == "__main__":
    main()