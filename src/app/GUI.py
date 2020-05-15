import os
import warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
warnings.filterwarnings("ignore")

import time
from tkinter import *
from tkinter.filedialog import askopenfile
from tkinter.ttk import *
from multiprocessing import Process, Queue

import _global
from main import main_app

class MainApplication(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, root, *args, **kwargs)
		self.root = root
		self.root.geometry('600x250')
		self.btn1 = Button(root, text ='Open File 1', command = lambda:self.open_clicked1()).grid(row=0, column=0)
		self.file_name1_lable = Label(root, text="")
		self.file_name1_lable.grid(row=0, column=1)
		self.btn2 = Button(root, text ='Open File 2', command = lambda:self.open_clicked2()).grid(row=1, column=0)
		self.file_name2_lable = Label(root, text="")
		self.file_name2_lable.grid(row=1, column=1)
		self.btn3 = Button(root, text ='Run', command = lambda:self.run_clicked()).grid(row=2, column=0)
		self.output_result_label = Label(root, text="")
		self.output_result_label.grid(row=3, column=3)
		self.file_name1 = None
		self.file_name2 = None

	def open_clicked1(self): 
		file = askopenfile(mode ='r', filetypes =[('img', '*.tiff')])
		if file is not None: 
			self.file_name1 = file.name
			self.file_name1_lable.config(text=file.name.split('/')[-1])
			if self.output_result_label.cget('text') is not "":
				self.output_result_label.config(text="")

	
	def open_clicked2(self): 
		file = askopenfile(mode ='r', filetypes =[('img', '*.tiff')])
		if file is not None: 
			self.file_name2 = file.name
			self.file_name2_lable.config(text=file.name.split('/')[-1])
			if self.output_result_label.cget('text') is not "":
				self.output_result_label.config(text="")
	
	def run_clicked(self):
		# self.progress()
		# self.prog_bar.start()
		if self.file_name1 is None or self.file_name2 is None:
			self.output_result_label.config(text='Error, 2 files must be loaded')
		output = main_app(self.file_name1, self.file_name2)
		self.output_result_label.config(text=output)


	def progress(self):
		self.prog_bar = Progressbar(
			self.master, orient="horizontal",
			length=200, mode="indeterminate"
			)
		self.prog_bar.pack(side=TOP)



if __name__ == "__main__":
	root = Tk()
	MainApplication(root)
	_global.init(language='hebrew', test_mode=False)
	root.mainloop()
