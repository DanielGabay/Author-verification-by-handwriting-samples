import cv2
import matplotlib.pyplot as plt
import numpy as np
import os


# read image
image = cv2.imread('tables/1.jpg')    

# this variable is used for changing the img letter name.
table_name = 1 

kernel = np.ones((5, 5),  np.uint8)

# cv2.imshow('table_orig', image)
# cv2.waitKey(0)

# setting the image to gray
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
   (ctrs, _) = cv2.findContours(thresh.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


# sort the contours to get the first line of the letter "א" and so on
sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[1])

folders = list() # creating a list of folders names
counter = 0
name_num = 0
curr_folder = 1
# for i, ctr in enumerate(sorted_ctrs):
for ctr in sorted_ctrs:
   # Get bounding box
   x, y, w, h = cv2.boundingRect(ctr)
   if h>=60 and w>=60:

      # Getting ROI--each letter image
      roi = gray[y:y+h, x:x+w]

      # show ROI
      # cv2.imshow('segment no:'+str(i),roi)
      # creating a rectangle for each letter
      cv2.rectangle(gray,(x,y),( x + w, y + h ),(90,255,0),2)
      # cv2.waitKey(0)
      H = int(h*0.15)
      W = int(w*0.13)

      # remove each frame
      letter = roi[H:h - H , W:w - W]
      letter = cv2.erode(letter, kernel, iterations=1)

      #we want each image to be 28x28 size so we use resize
      letter = cv2.resize(letter, (28,28))
      num_of_squars = 10
      if curr_folder != counter//10 + 1:
         name_num = 0

      #write each image to the right folder
      path = os.getcwd() + "\\out\\" + str(counter//num_of_squars+1)+ "\\"
      if not os.path.exists(path):
         os.makedirs(path)
      cv2.imwrite(path+str(name_num)+'_'+str(table_name)+'.jpg', letter)
      curr_folder = counter//10 +1
      name_num+=1
      counter+=1

cv2.imwrite("out/page.png", image)
