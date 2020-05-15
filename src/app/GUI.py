# importing tkinter and tkinter.ttk 
# and all their functions and classes 
from tkinter import * 
from tkinter.ttk import *
from main import main
  
# importing askopenfile function 
# from class filedialog 
from tkinter.filedialog import askopenfile 
  
root = Tk() 
root.geometry('200x100') 

f1, f2 = None, None
# This function will be used to open 
# file in read mode and only Python files 
# will be opened 
def open_file(): 
    file = askopenfile(mode ='r', filetypes =[('img', '*.tiff')])
    global f1
    global f2
    if file is not None: 
        if f1 is None:
            f1 = file.name
            printOutput(f1.split('/')[-1])
        else:
            f2 = file.name
            printOutput(f2.split('/')[-1])

def run_test():
    global f1
    global f2
    output = main(f1, f2)
    printOutput(output)
    f1, f2 = None, None

def printOutput(output):
    # if you want the button to disappear:
    # button.destroy() or button.pack_forget()
    label = Label(root, text=output)
    #this creates a new label to the GUI
    label.pack() 

btn = Button(root, text ='Open', command = lambda:open_file()) 
btn2 = Button(root, text ='Run', command = lambda:run_test()) 
btn.pack(side = TOP, pady = 10)
btn2.pack(side = TOP, pady = 10)

  
mainloop() 