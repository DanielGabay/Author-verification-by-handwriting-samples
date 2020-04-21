import cv2
import numpy as np
import os

'''
not so smart resize words to SIZExSIZE.
just get it done :)
'''

SIZE = 64
'''
this is the path for the dirs contains the words.
the words images is overwritten!
'''
path = "cropped/sorted_cropped_words_resized"

# dir names is 1-11
inner_path = [i for i in range(1,12)]
for inner_dir in inner_path:
    curr_dir = path+"/"+str(inner_dir)
    for dirs, _, files in os.walk(curr_dir):
        print(curr_dir)
        for file_name in files:
            image_path_name = curr_dir + "/" + file_name
            im = cv2.imread(image_path_name)
            im = cv2.resize(im, dsize=(SIZE, SIZE))

            cv2.imwrite(image_path_name,im)