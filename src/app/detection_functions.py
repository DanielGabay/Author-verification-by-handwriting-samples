
from statistics import median
import numpy as np
from scipy.signal import argrelextrema, savgol_filter
import cv2


def detect_Lines(original):

	_ , thresh = cv2.threshold(original, 127, 255, cv2.THRESH_BINARY_INV)
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

		roi = original[lines_upper[v]:lines_lower[v + 1], 0:width]
		if roi.shape[0] > 0:    
			lines.append(roi)
			
	return lines

def findMedian(points):
	differences = list()
	if len(points) <= 1:
		return 0
	for i in range(len(points)):
		if i > 0:
			differences.append(points[i] - points[i - 1])
	return median(differences)

def union_left_ctr(cur_ctr, next_ctr,canvas):
	"""
		the method main job is to combine 2 conturs to 1.
		some letters in hebrew are consists of two parts, those 2 parts must be together
		so that the network will classify the right word .
		example : "ש"  "ז"
	:param cur_ctr: first part of the word as contur
	:param next_ctr: second part of the word as contur
	:param canvas: the letters locations
	:return: the right action to preform
	"""

	xtemp = cur_ctr.x_start - 3
	ytemp = cur_ctr.y_end - 1

	temp_canvas = canvas.copy()
	ret, temp_canvas = cv2.threshold(temp_canvas, 109, 255, cv2.THRESH_BINARY_INV)
	while temp_canvas[ytemp][xtemp] != 255 and xtemp >= next_ctr.x_start and xtemp > 0:
		xtemp -= 1

	if temp_canvas[ytemp][xtemp] == 255:
			return 0
	else:
			return 1

def find_letters(line_image):
	"""
		this function is the main function in this algorithm,
		the function cut each letter from the word image by using findconturs function
		each contur is part of the line image that contain a letter.
		also the function is handling few cases to get each letter without a noise around.
	:param line_image: the word image
	:return: a list of objects , each object contain the letter image and info about the image
	"""

	if line_image.shape[0] < 40:
		line_image = cv2.resize(line_image, (line_image.shape[1] * 2, line_image.shape[0] * 2))

	#binary
	ret,thresh = cv2.threshold(line_image, 109, 255, cv2.THRESH_BINARY_INV)

	if cv2.__version__.startswith('3.'):
		im2, ctrs, hier = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	else:
		(ctrs, __) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	#sort contours
	sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0], reverse=True)

	#creating objects - so we coult hold a few arguments that connected together in the same variable

	class contur:
		def __init__(self, x, y, w, h):
			self.x_start = x
			self.y_start = y
			self.x_end = x + w
			self.y_end = y + h

	letters_images = list()
	new_ctr = list()

	for j, ctr in enumerate(sorted_ctrs):
		x, y, w, h = cv2.boundingRect(ctr)
		c = contur(x, y, w, h)
		new_ctr.append(c)

	length = len(new_ctr)

	i = 0
	while i < length:
		x, y, w, h = cv2.boundingRect(sorted_ctrs[i])

		if h > 3:
			canvas = np.ones_like(line_image)
			canvas.fill(255)
			cv2.drawContours(canvas, sorted_ctrs, i, (0, 0, 0), 3)

			if i < length - 1 and new_ctr[i].x_start >= new_ctr[i + 1].x_start and new_ctr[i].x_end <= new_ctr[i + 1].x_end:
				Y_end_bigger = max(new_ctr[i].y_end, new_ctr[i + 1].y_end)
				cv2.drawContours(canvas, sorted_ctrs, i + 1, (0, 0, 0), 3)

				if union_left_ctr(new_ctr[i], new_ctr[i+1], canvas) == 0:
					roi = canvas[y:y + h, x:x + w]
					roiriginal = line_image[y:y + h, x:x + w]
				else:
					roi = canvas[new_ctr[i + 1].y_start:Y_end_bigger, new_ctr[i + 1].x_start:new_ctr[i + 1].x_end]
					roiriginal = line_image[new_ctr[i + 1].y_start:Y_end_bigger, new_ctr[i + 1].x_start:new_ctr[i + 1].x_end]
					i += 1
			else:
				roi = canvas[y:y + h, x:x + w]
				roiriginal = line_image[y:y + h, x:x + w]

			letter = np.pad(roiriginal, pad_width=10, mode='constant', constant_values=255)

			letters_images.append(letter)
		i+=1
	return letters_images


def get_letters(lines):
	letters = []
	for line in lines:
		letters.append(find_letters(line))

	letters = [y for x in letters for y in x]
	return letters