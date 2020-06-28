# import pkg_resources.py2_warn # import just as workaround for pyinstaller error
import eel
from main import _gui_entry,get_pair_list
from tkinter import filedialog
from tkinter import *
from tkinter.filedialog import askopenfile

path1 = ""
path2 = ""
folder= ""

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
def gui_entry_folder():
	global folder
	if (folder == ""):
		return
	pair_list = get_pair_list(folder)

	for pair in pair_list:
		err, res = _gui_entry(pair[0], pair[1], False)
		# TODO: res is a tuple? cant append
		res.append([pair[0].split("/")[-1], pair[1].index.split("/")[-1]])
		eel.print_from_py(res)()

		break

def get_input_files(title):
	root = Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	f = filedialog.askopenfilenames(parent=root,title=title,filetypes =[('img', '*.tiff'), ('img', '*.tif'), ('img', '*.png')])
	return (root.tk.splitlist(f))

def get_input_folder():
	root = Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	root.directory = filedialog.askdirectory(parent=root)
	return root.directory
	

@eel.expose
def pyGetFolderPath():
	global folder
	folder = get_input_folder()
	
	if folder is "":
		print("E")
		return 'E'
	print(folder.split("/")[-1])
	return folder.split("/")[-1]



@eel.expose
def pyGetFilePath():
	global path1
	global path2
	
	files = get_input_files('Choose 2 Files')
	if len(files) > 1:
		path1 = files[0]
		path2 = files[1]	

	elif len(files) == 1:
		path1 = files[0]
	#	eel.popup_second_file()()
		files = get_input_files('Choose a file')
		if len(files)< 1:
			return "E"
		path2 = files[0]	
	else:
		return "E"
	return [path1.split("/")[-1],path2.split("/")[-1]]


eel.start('index.html', size=(1000, 600))
