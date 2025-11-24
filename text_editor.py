from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import askopenfile, asksaveasfile

filename = None

def new_file():
    global filename
    filename = "untitled"
    text.delete(0.0, END) # line 0 and column 0 within the text file
    
def save_file():
    global filename
    t = text.get(0.0, END)
    f = open(filename, 'w')
    f.write(t)
    f.close()
    
def save_as():
    f = asksaveasfile(mode='w', defaultextension=".txt")
    t = text.get(0.0, END)
    try:
        f.write(t.rstrip())
    except:
        messagebox.ABORTshowerror(title="Error", message="Could not save file")
        
def open_file():
    f = askopenfile(mode='r')
    t = f.read()
    text.delete(0.0, END)
    text.insert(0.0, t)
    
root = Tk()
root.title("MY PYTHON TEXT EDITOR")
root.minsize(width=400, height=400)
root.maxsize(width=400, height=400)

text = Text(root, width=400, height=400)
text.pack()

menubar = Menu(root)
filemenu = Menu(menubar)
filemenu.add_command(label="New", command=new_file)
filemenu.add_command(label="Open", command=open_file)
filemenu.add_command(label="Save", command=save_file)
filemenu.add_command(label="Save As...", command=save_as)
filemenu.add_separator()
filemenu.add_command(label="Quit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

root.config(menu=menubar)
root.mainloop()


