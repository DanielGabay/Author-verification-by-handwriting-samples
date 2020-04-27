import cv2
import numpy as np
import os


w, h = 120, 80

# path for the dirs contains the words to be resized.
path = "cropped/sorted_cropped_words"
# path for saved resized words.
new_path = "cropped/sorted_cropped_words_resized"
if not os.path.exists(new_path):
    os.mkdir(new_path)
# dir names is 1-11
inner_path = [i for i in range(1,12)]
for inner_dir in inner_path:
    if not os.path.exists(new_path+"/"+str(inner_dir)):
        os.mkdir(new_path+"/"+str(inner_dir))
    curr_dir = path+"/"+str(inner_dir)
    for dirs, _, files in os.walk(curr_dir):
        print(curr_dir)
        for file_name in files:
            image_path_name = "{}/{}/{}".format(path, inner_dir, file_name)
            im = cv2.imread(image_path_name)
            im = cv2.resize(im, dsize=(w, h))
            image_write_path = "{}/{}/{}".format(new_path, inner_dir, file_name)
            cv2.imwrite(image_write_path,im)