import os
import sys
from statistics import median

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.signal import argrelextrema, savgol_filter

# import detectWords
from .our_utils.prepare_document import get_prepared_doc
import _global

"""
sumPixles algoritem is taken from https://github.com/moranzargari/Handwriting-detection-recognition
as a part of last year final project by Moran Zargari & Itay Hefetz
"""

def findMedian(points):
    differences = list()
    if len(points) <= 1:
        return 0
    for i in range(len(points)):
        if i > 0:
            differences.append(points[i] - points[i - 1])
    return median(differences)

def detect_Lines(original, thresh, out_folder=None):
    hight, width = thresh.shape[:2]

    # creates a vector that containing the sum of pixels per line
    img_row_sum = np.sum(thresh, axis=1)

    # smoothing the data by Savitzky–Golay filter
    w = savgol_filter(img_row_sum, 19, 1)

    # find maximum points
    c_w_max = argrelextrema(w, np.greater, order=5)

    # find the median of the differences between two adjacent maximum points
    median_prev = findMedian(c_w_max[0])

    # initialize stop conditions
    delta = 1  # threshold of change between iterations
    i = 2 # index of current iteration

    # in each iteration, do smooth until the difference between iterations < delta
    while 1:
        for x in range(i):
            if x == 0:
                w = savgol_filter(w, 11, 1)
            else:
                w = savgol_filter(w, 9, 1)
        c_w_max = argrelextrema(w, np.greater, order=5)
        median_next = findMedian(c_w_max[0])
        if abs(median_next-median_prev) <= delta:
            break
        median_prev = median_next
        i += 1

    # show current status
    # plt.scatter(c_w_max[0], w[c_w_max[0]], linewidth=1.5, s=40, c='black')
    # plt.plot(img_row_sum)
    # plt.plot(w, 'pink')
    # plt.show()

    # after smoothing the graph, now we will find the minimum upper and lower points - Y's values
    max_points = c_w_max[0]
    lines_upper, lines_lower = list(), list()
    min = img_row_sum[0]
    # holds the bounderys of the lower and upper Y's values of the lines
    indexU, indexL = 0, 0
    i, j, k = 0, 0, 0  # indexs of minimum points
    while i < len(img_row_sum) and j < len(max_points):
        while i < max_points[j]:
            if img_row_sum[i] < min:
                min = img_row_sum[i]
                indexL = i
            i += 1
            if img_row_sum[k] <= min:
                min = img_row_sum[k]
                indexU = k
            k += 1
        lines_lower.append(indexL)
        lines_upper.append(indexU)
        min = img_row_sum[max_points[j]]
        j += 1

  
    # finding the last minimum point, so we could find the last lower line.
    last_max_point = max_points[len(max_points)-1]
    last_min_point = img_row_sum[last_max_point]
    index = 0
    for x in range(last_max_point, len(img_row_sum)):
        if img_row_sum[x] < last_min_point:
            index = x
            last_min_point = img_row_sum[x]
    lines_lower.append(index)

    
    # cut's each line
    lines = list()
    min_line_hight = 20
    count_lines_min_hight = 0
    for v in range(len(lines_upper)): 
        if lines_upper[v] > lines_lower[v + 1]:
            continue
        # TODO: return list of [lines_upper:lines_lower] at the end of the function?
        roi = original[lines_upper[v]:lines_lower[v + 1], 0:width]
        if roi.shape[0] > 0:    
            lines.append(roi)
            # uncomment to save_lines
            if out_folder is not None:
                cv2.imwrite(out_folder + "/" + str(v) + ".png", roi)
    return lines

def createOutputDirs(img_name):
    out_main_folder = "detected_lines"
    if not os.path.exists(out_main_folder):   # create folder to contain the line's img
        os.mkdir(out_main_folder)
    inner_folder = img_name[img_name.find("/")+1:img_name.find(".")] # take only the name of the img
    out_path = "{}/{}".format(out_main_folder, inner_folder)
    if not os.path.exists(out_path):   
        os.mkdir(out_path)
    return out_path

def get_lines(img, img_name):
    # uncomment to save lines
    # out_path = createOutputDirs(img_name)
    ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    return detect_Lines(img, thresh)
    # return detect_Lines(img, thresh, out_path)

def main():
    if(len(sys.argv) < 2):
        print("Usage: python detectLines.py <file_name>")
        sys.exit(1)
    
    # reading the image (gray)
    img_name = _global.DATA_PATH + str(sys.argv[1])
    # TODO: get the image from the main app
    img = get_prepared_doc(img_name)
    # TODO: return img from the function correctly..
    # current state: read the saved image to folder
    img = cv2.imread('tiff_as_one_img.jpeg', 0)
    out_path = createOutputDirs(img_name)

    # binary
    ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    lines = detect_Lines(img, thresh, out_path)
   

if __name__ == '__main__':
    main()


####################################################################
# draw upper and lower lines where the minimum points are
# upper-green, lower-blue
# for line in lines_lower:
#     original = cv2.line(original, (0, line), (width, line), (255, 0, 0), 1)
# for line in lines_upper:
#     original = cv2.line(original, (0, line), (width, line), (0, 255, 0), 1)
#
# print(lines_upper)
# print()
# print(lines_lower)

####################################################################
