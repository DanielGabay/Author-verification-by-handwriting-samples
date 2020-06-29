# import pkg_resources.py2_warn # import just as workaround for pyinstaller error
import eel
from main import _gui_entry,get_pair_list
from tkinter import filedialog
from tkinter import *
from tkinter.filedialog import askopenfile
import csv
import time


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
	
	res.append([path1.split("/")[-1], path2.split("/")[-1]])
	# return err too?
	return res

@eel.expose
def gui_entry_folder():
	global folder
	if (folder == ""):
		return
	pair_list = get_pair_list(folder)
	count = 0
	for pair in pair_list:
		err, res = _gui_entry(pair[0], pair[1], False)
		# TODO: res is a tuple? cant append
		res.append([pair[0].split("\\")[-1], pair[1].split("\\")[-1]])
		eel.print_from_py(res)()
		count+=1
		if count == 2:
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


@eel.expose
def save_result_to_excel(data,folderName = ""):
	timestr = time.strftime("%d-%m-%Y_%H-%M-%S")
	csv_name = "{}_{}.csv".format(folderName,timestr)
	with open(csv_name, 'w', newline='') as csv_file:
		csvWriter = csv.writer(csv_file, delimiter=',')
		header = ["file1", "file2", "predicted", "confident"]
		csvWriter.writerow(header)
		for i in range(len(data)):
			line = get_line_from_data(data[i])
			csvWriter.writerow(line)

def get_line_from_data(data):
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