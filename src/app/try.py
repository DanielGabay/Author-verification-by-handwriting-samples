from tkinter import filedialog
from tkinter import *
from tkinter.filedialog import askopenfile

path1 = ""
path2 = ""

def gui_entry():
	global path1
	global path2
	if (path1 == "" or path2 == ""):
		return
	err, res = _gui_entry(path1, path2, False)
	# return err too?
	return res


def pyGetFilePath():
	
	root = Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	filez = filedialog.askopenfilenames(parent=root,title='Choose 2 Files',filetypes =[('img', '*.tiff'), ('img', '*.tif'), ('img', '*.png')])
	print (root.tk.splitlist(filez))


pyGetFilePath()

