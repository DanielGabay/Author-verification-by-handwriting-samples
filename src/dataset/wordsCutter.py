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
   # print(len(sorted_ctrs))
   
   if DATA_PATH == 'data2/':
      folder_counter = 8
   else:
      folder_counter = 1
   word_counter = 1
   name_num = 0
   for ctr in sorted_ctrs:
      # Get bounding box

      x, y, w, h = cv2.boundingRect(ctr)
      if h>=60 and w>=60:
         # Getting ROI--each word image
         roi = gray[y:y+h, x:x+w]
         # creating a rectangle for each word
         cv2.rectangle(gray,(x,y),( x + w, y + h ),(90,255,0),2)

         H = int(h*0.1)   # remove each frame
         W = int(w*0.05)

         word = roi[H:h - H , W:w - W]
         # word = cv2.erode(word, kernel, iterations=1)

         #we want each image to be 28x28 size so we use resize
         word = cv2.resize(word, (150,150))  # was 100X100

         #write each image to the right folder
         path = os.getcwd() + "\\out\\" + str(folder_counter)+ "\\"
         if not os.path.exists(path):
            os.makedirs(path)
      
         cv2.imwrite(path+str(file_name)+'_'+str(word_counter)+'.png', word)
         word_counter += 1
         if(word_counter == NUM_OF_SQUARS+1):
            folder_counter += 1
            word_counter = 1

   cv2.imwrite("out/page.png", image)


def read_images():

   for filename in os.listdir(DATA_PATH):
      image = cv2.imread(os.path.join(DATA_PATH,filename))
      if image is not None:
         file_name = filename.rsplit('.', 1)[0] # take file name without the format
         arrange(image,file_name)
         
if __name__ == "__main__":
   read_images()