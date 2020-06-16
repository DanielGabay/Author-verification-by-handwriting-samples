import os
import warnings
# ignore warnings prints
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
warnings.filterwarnings("ignore")

from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askopenfile, asksaveasfilename
from tkinter.ttk import *
from multiprocessing import Process, Queue
from main import _main_app

import _global
import threading

class MainApplication(Frame):
	def __init__(self, parent, *args, **kwargs):
		Frame.__init__(self, root, *args, **kwargs)
		self.root = root
		self.root.title("Author Verification Based On Hand Writing Analysis")
		self.root.geometry('470x250')
		self.open1_btn = Button(root, text ='Open File 1', command = lambda:self.open_clicked1()).grid(row=0, column=0)
		self.file_name1_lable = Label(root, text="")
		self.file_name1_lable.grid(row=0, column=1)
		self.open2_btn = Button(root, text ='Open File 2', command = lambda:self.open_clicked2()).grid(row=1, column=0)
		self.file_name2_lable = Label(root, text="")
		self.file_name2_lable.grid(row=1, column=1)
		self.run_btn = Button(root, text ='Run', command = lambda:self.run_clicked()).grid(row=2, column=0)
		self.save_btn = Button(root, text ='Save', command = lambda:self.save_output()).grid(row=3, column=0)
		self.output_result_label = Label(root, text="")
		self.output_result_label.grid(row=4, column=3)
		self.file_name1 = None
		self.file_name2 = None
		self.is_running = False # used for blocking attemps on load files an run
								# while already running the main_app

	def open_clicked1(self):
		'''
		open a window for choosing the path for file1
		'''
		if self.is_running:
			return
		file = askopenfile(mode ='r', filetypes =[('doc', '*.tiff')])
		if file is not None:
			self.file_name1 = file.name
			self.file_name1_lable.config(text=file.name.split('/')[-1])
			if self.get_output() is not "":
				self.clear_output()
	
	def open_clicked2(self):
		'''
		open a window for choosing the path for file2
		'''
		if self.is_running:
			return
		file = askopenfile(mode ='r', filetypes =[('img', '*.tiff')])
		if file is not None:
			self.file_name2 = file.name
			self.file_name2_lable.config(text=file.name.split('/')[-1])
			if self.get_output() is not "":
				self.clear_output()

	def get_output(self):
		return self.output_result_label.cget('text')
	
	def clear_output(self):
		self.output_result_label.config(text="")

	def worker(self):
		'''
		Thread worker.
		calls the main_app after creating sub-proccess.
		sub-process is created in order to use the trained models
		in the main_app -> workaround to fix keras-tensorflow bug.
		'''
		self.is_running = True

		# creating a queue and pass it to main.
		# the output will be written into the queue.
		queue = Queue(maxsize=1)
		_main_app(self.file_name1, self.file_name2,queue=queue,test_mode= False)
		# p = Process(target=_main_app, args=(self.file_name1, self.file_name2, queue, False))
		# p.start()

		# code is block until the output from main is ready in queue.
		# because its running on another thread, the mainloop window is still running.
		output = queue.get()
		# p.terminate()
		self.prog_bar.destroy()
		self.print_output(output)
		self.is_running = False

	def print_output(self, output):
		if output is not None:
			self.output_result_label.config(text=output)

	def run_clicked(self):
		if self.is_running:
			return
		if self.file_name1 is None or self.file_name2 is None:
			self.print_output('Error, 2 files must be loaded first.')
			return

		self.clear_output()
		self.progress()
		self.prog_bar.start()
		t_worker = threading.Thread(target=self.worker)
		t_worker.start()

	def progress(self):
		self.prog_bar = Progressbar(
			self.master, orient="horizontal",
			length=200, mode="indeterminate"
			)
		self.prog_bar.grid(row=3, column=4)
	
	def save_output(self):
		'''
        this function allow the user to save the output into a txt file
		'''
		if self.get_output() is "":
			return
		file1 = self.file_name1.split('/')[-1]
		file2 = self.file_name2.split('/')[-1]
		name = asksaveasfilename(
			initialdir="C:",
			title="Choose your file",
			initialfile="test_{}_{}".format(file1.split('.')[0],\
									  		file2.split('.')[0]),
			filetypes=[("Text Files", "*.txt")],
			defaultextension='txt'
		)
		try:
			f = open(name, "w")
			f.write("Test: {} {}\n{}".format(file1,file2,self.get_output()))
			f.close()
			# messagebox.showinfo("Saved successfully", "Path:\n" + name)
		except:
			pass

if __name__ == "__main__":
	root = Tk()
	# _global.init(language='hebrew', test_mode=False)
	MainApplication(root)
	root.mainloop()
