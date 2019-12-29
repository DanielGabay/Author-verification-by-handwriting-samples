from extractComparisonFeatures.detectLines import get_lines
from extractComparisonFeatures.detectLetters import get_letters
from extractComparisonFeatures.our_utils.prepare_document import get_prepared_doc
import cv2
import sys
from keras.models import model_from_json
from keras.preprocessing import image
import numpy as np


os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
hebrew_letters = ['א', 'ב', 'ג', 'ד', 'ה', 'ו', 'ז', 'ח', 'ט', 'י'\
            ,'כ', 'ל', 'מ', 'נ', 'ס', 'ע', 'פ', 'צ', 'ק', 'ר', 'ש', 'ת',\
           'ך', 'ם', 'ן', 'ף', 'ץ']

def main():
    if(len(sys.argv) < 2):
        print("Usage: python detectLines.py <file_name>")
        sys.exit(1)



    img_name = "data/" + str(sys.argv[1])
    img = get_prepared_doc(img_name)
    lines = get_lines(img, img_name)
    letters = get_letters(lines)


    num_of_classes = 27
    image_size = 28  # 28X28 pixels
    batch_Size = 128
    # load json and create model
    json_file = open('model99.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    classifier = model_from_json(loaded_model_json)
    classifier.load_weights("model99.h5")
    print("Loaded model from disk")
    classifier.compile(optimizer='adam',  loss='categorical_crossentropy', metrics=['accuracy'])
    for letter in letters:
        test_letter = image.img_to_array(letter.image_letter)
        test_image = np.expand_dims(test_image, axis=0)
        result = classifier.predict((test_image/255)*0.1)
        for i, v in enumerate(result[0]):
            print(str(i)+" " + hebrew_letters[i]+": "+str(float("{0:.2f}".format(v))))
        # cv2.imshow('letter', letter.image_letter)
        # cv2.waitKey(0)

    # print(lines)
    # for line in lines:
    #     cv2.imshow('line', line)
    #     cv2.waitKey(0)

if __name__ == "__main__":
    main()