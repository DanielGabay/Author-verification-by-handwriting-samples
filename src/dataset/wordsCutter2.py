import cv2
import numpy as np
import sys
import os


DATA_PATH = 'data1/'
# DATA_PATH = 'data2/'
DONE_PATH = "{}/{}_{}.txt".format("cropped","done_with", DATA_PATH.split('/')[0])
OUT_PATH = 'cropped/'

NUM_OF_WORDS = 0
dirs = []

if '1' in DATA_PATH:
    dirs = [i for i in range(1, 8)]
elif '2' in DATA_PATH:
    dirs = [i for i in range(8, 12)]


def arrange(img, filename, done_list):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)

    # ret,thresh = cv2.threshold(gray, 109, 255, cv2.THRESH_BINARY_INV) 

    kernel = np.ones((5,5),np.uint8)
    erosion = cv2.erode(gray,kernel,iterations = 2)
    kernel = np.ones((4,4),np.uint8)
    dilation = cv2.dilate(erosion,kernel,iterations = 2)

    edged = cv2.Canny(dilation, 30, 200)

    (contours, _) = cv2.findContours(edged, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1])

    rects = [cv2.boundingRect(cnt) for cnt in contours]
    # rects = sorted(rects,key=lambda  x:x[1],reverse=True)


    i = -1
    j = 1
    y_old = 5000
    x_old = 5000
    seen_xy = []
    for rect in rects:
        x,y,w,h = rect
        area = w * h

        if area > 47000 and area < 70000:
            # print("y_old: {} y: {} x_old: {} x: {}".format(y_old, y, x_old, x))
            if y_old - y > 200:
                if i + 1 < len(dirs):
                    i += 1
                y_old = y

            if abs(x_old - x) > 300:
                taken_word = False
                for cord in seen_xy:
                    if abs(cord[0]-x) < 30 and abs(cord[1]-y) < 30:
                        taken_word = True
                if taken_word:
                    continue

                if abs(y_old-y) > 250 and x_old > x:
                    if i + 1< len(dirs):
                        i += 1
                    y_old = y
            
                x_old = x
                seen_xy.append([x,y])
                out = img[y+15:y+h-15,x+15:x+w-15]
                out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
                path = os.getcwd() + "\\" + OUT_PATH + str(dirs[i]) + "\\"
                if not os.path.exists(path):
                    os.makedirs(path)
                save_name = path + filename + '_' + str(j) + '.png'
                cv2.imwrite(save_name, out)
                j += 1

def read_done_file():
	with open(DONE_PATH) as f:
		lines = f.read().splitlines()
		return lines

def write_done_file(done_list,doc_name):
	done_list.append(doc_name)
	file = open(DONE_PATH, "a") 
	file.write("{}{}".format(doc_name,"\n")) 
	file.close()

def read_images(done_list):
    for filename in os.listdir(DATA_PATH):
        if filename in done_list:   
            print("{} already done".format(filename))
            continue
        image = cv2.imread(os.path.join(DATA_PATH,filename))
        if image is not None:
            file_name = filename.split("_")[2].split('.')[0]
            arrange(image, file_name ,done_list)
            write_done_file(done_list, filename)
         
if __name__ == "__main__":
    if not os.path.exists(OUT_PATH):
        os.makedirs(OUT_PATH)
    if not os.path.exists(DONE_PATH):   # create folder to contain the done img
        print("create done file")
        file = open(DONE_PATH, "w") 
        file.close()
    done_list = read_done_file()  # read the files we already done with
    read_images(done_list)