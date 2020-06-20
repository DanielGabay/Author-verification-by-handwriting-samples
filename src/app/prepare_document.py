import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
import shutil
import sys
import _global

def cut_width(page, page_num, is_png=False):
	'''
	Cut uncessery scanned page from left and right
	Note: there is a difference between pages
	'''
	width, height = page.size
	bottom = height
	right = width
	top = 0
	left = 0
	if page_num == 1:
		if is_png:
			left = 37
		else: # is tiff
			left = 100
	elif page_num == 2:
		if is_png:
			right = width - 80
			bottom = bottom - 300
		else: # is tiff
			right = width - 100
			bottom = bottom - 622
	cropped = page.crop((left, top, right, bottom))
	# cropped.show()
	return cropped

def image_to_png(png):
	width, height = png.size
	page1, page2 = png.crop((0, 0, width, height/2)), png.crop((0,height/2, width, height))
	page1, page2 = cut_width(page1, 1, True), cut_width(page2, 2, True)
	concat = get_concat_vertical(page1, page2)
	concat.save(_global.CONCAT_AS_ONE_IMAGE)
	#concat.show()
	

def tiff_to_jpeg(tiff):
	page_count = 0
	if not os.path.exists('temp'):
		os.mkdir('temp')
	while 1:
		try:
			save_name = 'page' + str(page_count) + ".jpeg"
			try:
				tiff.save('temp/'+save_name)
			except OSError:
				'''
				Deal with OSError by saving tiff as jpeg
				'''
				tiff = tiff.convert("RGB")
				tiff.save('temp/'+save_name)
			page_count = page_count+1
			tiff.seek(page_count)
		except EOFError:
			page1 = Image.open('temp/page0.jpeg')
			page1 = cut_width(page1, 1)
			if page_count > 1:
				# doc has 2 pages
				page2 = Image.open('temp/page1.jpeg')
				page2 = cut_width(page2, 2)
				concat = get_concat_vertical(page1, page2)
				concat.save(_global.CONCAT_AS_ONE_IMAGE)
			else:
				# doc has 1 page
				page1.save(_global.CONCAT_AS_ONE_IMAGE)
			return


def get_concat_vertical(im1,im2):
	dst = Image.new('RGB', (im1.width, im1.height + im2.height))
	dst.paste(im1, (0,0))
	dst.paste(im2, (0, im1.height))
	return dst

def get_prepared_doc(name='data/500.tiff'):
	extantion = name.split('.')[-1]
	try:
		img = Image.open(name)
	except FileNotFoundError:
			print("ERROR: {}: file not found".format(name))
			sys.exit(1)
	if extantion == 'tiff' or extantion == 'tif':
		tiff_to_jpeg(img)
		shutil.rmtree('./temp/')
	if extantion == 'png' or extantion == 'jpeg':
		image_to_png(img)
	img = cv2.imread(_global.CONCAT_AS_ONE_IMAGE,0)
	os.remove(_global.CONCAT_AS_ONE_IMAGE)
	return img