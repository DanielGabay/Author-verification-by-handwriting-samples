import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
import shutil

def cut_width(page, page_nume):
    '''
    Cut uncessery scanned page from left and right
    Note: there is a difference between pages
    '''
    width, height = page.size
    if page_nume == 1:
        left = 104
        right = width
    else:
        left = 0
        right = width-104
    top = 0
    bottom = height
    cropped = page.crop((left, top, right, bottom))
    # cropped.show()
    return cropped

def tiff_to_jpeg(tiff):
    page_count = 0
    if not os.path.exists('temp'):
        os.mkdir('temp')
    while 1:
        try:
            save_name = 'page' + str(page_count) + ".jpeg"
            tiff.save('temp/'+save_name)
            tiff.seek(page_count+1)
            page_count = page_count+1
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

def get_prepared_doc(tiff_name='data/500.tiff'):
    tiff = Image.open(tiff_name)
    tiff_to_jpeg(tiff)
    shutil.rmtree('./temp/')
    return cv2.imread('tiff_as_one_img.jpeg',0)