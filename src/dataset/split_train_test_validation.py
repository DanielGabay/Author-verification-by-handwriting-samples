import cv2
import numpy as np
import random, os, shutil

dataset = "dataset/"
train_path = dataset + "train/"
test_path = dataset + "test/"
validation_path = dataset + "validation/"

def create_sub_dirs(path):
    sub_dirs = [i for i in range(1,12)]
    for sub_dir in sub_dirs:
        if not os.path.exists(path+str(sub_dir)):
            os.mkdir(path+str(sub_dir))

def create_train_test_validation_dirs():
    if not os.path.exists(dataset):
        os.mkdir(dataset)

    if not os.path.exists(train_path):
        os.mkdir(train_path)
    create_sub_dirs(train_path)

    if not os.path.exists(test_path):
        os.mkdir(test_path)
    create_sub_dirs(test_path)

    if not os.path.exists(validation_path):
        os.mkdir(validation_path)
    create_sub_dirs(validation_path)

def split_train_test_validation(test_size, validation_size):
    path = "cropped/sorted_cropped_words_resized/"
    sub_dirs = [i for i in range(1,12)]
    for sub_dir in sub_dirs:
        curr_dirr = path + str(sub_dir) + "/"
        files = os.listdir(curr_dirr)
        random.shuffle(files)
        validation = files[0:validation_size]
        test = files[validation_size:validation_size+test_size]
        train = files[validation_size+test_size:]
        move_files_to_dest(train, curr_dirr, train_path+str(sub_dir))
        move_files_to_dest(test, curr_dirr, test_path+str(sub_dir))
        move_files_to_dest(validation, curr_dirr, validation_path+str(sub_dir))

def move_files_to_dest(files, source, dest):
    for f in files:
        shutil.move(source+f, dest)

def move_output_dir():
    '''
    move all output dir that created during
    augmantaion to the parent folder
    '''
    path = "cropped/sorted_cropped_words_resized"
    sub_dirs = [i for i in range(1,12)]
    for sub_dir in sub_dirs:
        source = "{}/{}/output/".format(path, sub_dir) 
        dest = "{}/{}/".format(path, sub_dir)
        move_all_src_to_dest(source, dest)
        shutil.rmtree(source)

def move_all_src_to_dest(source, dest):
    '''
    move all files in source to dest
    '''
    files = os.listdir(source)
    for f in files:
        shutil.move(source+f, dest)


if __name__ == "__main__":
    create_train_test_validation_dirs()
    move_output_dir()
    split_train_test_validation(3000,1000)
