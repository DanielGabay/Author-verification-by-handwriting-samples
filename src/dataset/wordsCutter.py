import cv2 as cv2
import matplotlib.pyplot as plt
import numpy as np
import os


DATA_PATH = "data1/"
NUM_OF_SQUARS = 12


def arrange(image,file_name):

   kernel = np.ones((5, 5), np.uint8)
   gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY) 
   # cv2.imshow('gray',gray)
   # cv2.waitKey(0)

   # choosing the best threshold that we wish
   ret,thresh = cv2.threshold(gray, 109, 255, cv2.THRESH_BINARY_INV) 
   # cv2.imshow('thresh',thresh)
   # cv2.waitKey(0)

   # we are using "findContours" function to locate all the squares that contain the letters
   # im2, ctrs= cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   if cv2.__version__.startswith('3.'):
      (_, ctrs, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
   else:
      (ctrs, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

   # sort the contours to get the first line of the letter "א" and so on
   sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[1])
   #cv2.drawContours(image,sorted_ctrs,-1,(0,255,0),3) 
   # print(len(sorted_ctrs))
   
   if DATA_PATH == 'data2/':
      folder_counter = 8
   else:
      folder_counter = 1
   word_counter = 1
   y_first = 0
   name_num = 0
   print(len(sorted_ctrs))
   for ctr in sorted_ctrs:
      # Get bounding box
      # print(ctr)
      area = cv2.contourArea(ctr)
      #print(area)
      # return
      #print(area)
      if area < 35000 or area > 70000:
         continue
      
      x, y, w, h = cv2.boundingRect(ctr)
      

      if word_counter == 1:
         y_first = y
      #if h>=60 and w>=60:
      # Getting ROI--each word image
      roi = gray[y:y+h, x:x+w]
      # creating a rectangle for each word
      cv2.rectangle(gray,(x,y),( x + w, y + h ),(90,255,0),2)
      H = int(h*0.1)   # remove each frame
      W = int(w*0.05)

      word = roi[H:h - H , W:w - W]
      # word = cv2.erode(word, kernel, iterations=1)

      word = cv2.resize(word, (100,100))  # was 100X100
      # cv2.imshow('',word)
      # cv2.waitKey(0)
      #write each image to the right folder

      # to know when we move to the next folder --> mean the next word to in the page
      if(y - y_first > 300):
         y_first = y
         folder_counter += 1
         word_counter = 1

      path = os.getcwd() + "\\out\\" + str(folder_counter)+ "\\"
      if not os.path.exists(path):
         os.makedirs(path)

      cv2.imwrite(path+str(file_name)+'_'+str(word_counter)+'.png', word)
      print(word_counter)
      word_counter += 1

   cv2.imwrite("out/page.png", image)


def read_images():

   for filename in os.listdir(DATA_PATH):
      image = cv2.imread(os.path.join(DATA_PATH,filename))
      if image is not None:
         file_name = filename.rsplit('.', 1)[0] # take file name without the format
         arrange(image,file_name)
         
if __name__ == "__main__":
   read_images()