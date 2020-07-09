#import pkg_resources.py2_warn # import just as workaround for pyinstaller error
import eel
from main import _gui_entry, get_folder_pairs_files, _gui_entry_init_global
from tkinter import filedialog
from tkinter import *
from tkinter.filedialog import askopenfile
import pandas as pd
from pandas import ExcelWriter
import time

# globals
PATH1 = ""
PATH2 = ""
EXEL_FILE =""
CURRENT_FOLDER = ""
KEEP_FOLDER_COMPARING = True

# init GUI window (select the GUI folder)
eel.init('GUI')

'''
eel exposed functions to javascript
'''

@eel.expose
def init_py_main_global():
	err = _gui_entry_init_global()
	print(err)
	return err

@eel.expose
def disable_folder_comparing():
	global KEEP_FOLDER_COMPARING
	KEEP_FOLDER_COMPARING = False	

@eel.expose
def gui_entry_files():
	global PATH1
	global PATH2
	if (PATH1 == "" or PATH2 == ""):
		return
	err, res = _gui_entry(PATH1, PATH2, False)
	print(err)
	res.append([PATH1.split("/")[-1], PATH2.split("/")[-1]])
	
	return err, res

@eel.expose
def gui_entry_folder():
	global CURRENT_FOLDER
	global EXEL_FILE
	global KEEP_FOLDER_COMPARING
	KEEP_FOLDER_COMPARING = True
	if CURRENT_FOLDER == "":
		return "FOLER_NOT_SELECTED"
	pair_list = get_folder_pairs_files(CURRENT_FOLDER, EXEL_FILE)
	for pair in pair_list:
		if not KEEP_FOLDER_COMPARING:   #break point from JS
			return
		err, res = _gui_entry(pair[0], pair[1], False)
		eel.set_pair_result(err, res)()

@eel.expose
def pyGetExelFilePath():
	global EXEL_FILE
	root = Tk()
	root.withdraw()
	root.wm_attributes('-topmost', 1)
	f = ""
	f = filedialog.askopenfilename(parent=root,title="rrr")
	if f is not "":
		EXEL_FILE = f
		return f.split("/")[-1]
	else:
		print("fdfdf")


@eel.expose
def pyGetFilePath():
	global PATH1
	global PATH2
	
	files = get_input_files('Choose 2 Files')
	if len(files) > 1:
		PATH1 = files[0]
		PATH2 = files[1]	

	elif len(files) == 1:
		PATH1 = files[0]
		files = get_input_files('Choose a file')
		if len(files)< 1:
			return "E"
		PATH2 = files[0]	
	else:
		return "E"
	return [PATH1.split("/")[-1],PATH2.split("/")[-1]]

@eel.expose
def pyGetFolderPath():
	global CURRENT_FOLDER
	CURRENT_FOLDER = get_input_folder()
	
	if CURRENT_FOLDER is "":
		return 'E'
	return CURRENT_FOLDER.split("/")[-1]

def convert_data_to_xlsx(data):
	return [get_line_from_data(data[i]) for i in range(len(data))]

@eel.expose
def save_result_to_excel(data, folderName = ""):
	timestr = time.strftime("%d-%m-%Y_%H-%M-%S")
	header = ["file1", "file2", "predicted", "confident"]
	data = convert_data_to_xlsx(data)
	df = pd.DataFrame(data, columns=header)
	xlsx_name = "{}_{}.xlsx".format(folderName, timestr)
	with ExcelWriter(xlsx_name) as writer:
		df.to_excel(writer)

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

def get_line_from_data(data):
	if data['error'] is not "":
		return [data['file1'], data['file2'], data['error'], "{}".format("ERROR")]
	precent = 0
	predicted = ""
	diff_prec = data['preds'][0]
	same_prec = data['preds'][1]

	if (same_prec > diff_prec):
		precent = same_prec
		predicted = "Same"
	else:
		precent = diff_prec
		predicted = "Different"
	return [data['file1'], data['file2'], predicted, "{}%".format(precent)]

eel.start('index.html', size=(1000, 600))
