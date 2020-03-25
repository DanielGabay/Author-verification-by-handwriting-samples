import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
import shutil
import sys

def cut_width(page, page_num, is_png=False):
    '''
    Cut uncessery scanned page from left and right
    Note: there is a difference between pages
    '''
    width, height = page.size
    bottom = height
    top = 0
    right = width
    left = 0
    if is_png:
        left = 95
        bottom = bottom - 300
    elif page_num == 1:
        left = 104
    else:
        right = width - 104
        bottom = bottom - 622
    cropped = page.crop((left, top, right, bottom))
    # cropped.show()
    return cropped

def png_to_jpeg(png):
    cropped = cut_width(png, 0, True)
    # cropped.show()
    png.save('tiff_as_one_img.jpeg')
    

def tiff_to_jpeg(tiff):
    page_count = 0
    if not os.path.exists('temp'):
        os.mkdir('temp')
    while 1:
        try:
            save_name = 'page' + str(page_count) + ".jpeg"
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
                concat.save('tiff_as_one_img.jpeg')
            else:
                # doc has 1 page
                page1.save('tiff_as_one_img.jpeg')
            return


def get_concat_vertical(im1,im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0,0))
    dst.paste(im2, (0, im1.height))
    return dst

def get_prepared_doc(name='data/500.tiff'):
    extantion = name.split('.')[1]
    try:
        img = Image.open(name)
    except FileNotFoundError:
            print("ERROR: {}: file not found".format(name))
            sys.exit(1)
    if extantion == 'tiff':
        tiff_to_jpeg(img)
        shutil.rmtree('./temp/')
    if extantion == 'png':
        png_to_jpeg(img)
    return cv2.imread('tiff_as_one_img.jpeg',0)