# import pkg_resources.py2_warn # import just as workaround for pyinstaller error
import eel
from main import _gui_entry
from tkinter import filedialog
from tkinter import *
from tkinter.filedialog import askopenfile

path1 = ""
path2 = ""

eel.init('GUI')
@eel.expose
def gui_entry():
	global path1
	global path2
	if (path1 == "" or path2 == ""):
		return
	err, res = _gui_entry(path1, path2, False)
	# return err too?
	return res

@eel.expose
def pyGetFilePath(file_num):
	global path1
	global path2
	root = Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	f = askopenfile(mode ='r', filetypes =[('img', '*.tiff')])
	if f is None:
		return ""
	if file_num == 1:
		path1 = f.name
		print("1: {}".format(path1))
	elif file_num == 2:
		path2 = f.name
		print("2: {}".format(path2))
	return f.name.split("/")[-1]

eel.start('index.html', size=(1000, 600))
