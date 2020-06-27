# import pkg_resources.py2_warn # import just as workaround for pyinstaller error
import eel
from main import _gui_entry
from tkinter import filedialog
from tkinter import *
from tkinter.filedialog import askopenfile

path1 = ""
path2 = ""

eel.init('file-upload_new')
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
def pyGetFilePath():
	global path1
	global path2
	root = Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	f = filedialog.askopenfilenames(parent=root,title='Choose 2 Files',filetypes =[('img', '*.tiff'), ('img', '*.tif'), ('img', '*.png')])
	files = (root.tk.splitlist(f))
	if len(files) > 1:
		path1 = files[0]
		path2 = files[1]	

		return [files[0].split("/")[-1],files[1].split("/")[-1]]
	else:
		return "E"

eel.start('index.html', size=(1000, 600))
