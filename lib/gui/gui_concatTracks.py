# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 14:29:28 2021

@author: Michael
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 09:54:11 2021

@author: Michael
"""




import tkinter as tk
from tkinter.filedialog import askdirectory, Radiobutton
import sys
class Interface(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.create_widgets()
        self.filename = None
        self.receiver = None

    def create_widgets(self):
        self.title('Get statistics about a GNSS trajeckts')
        self.geometry("500x500")
        self.configure(background='white')

        # Frame 1
        self.frame1 = tk.LabelFrame(self, text='Select .the foldeter to concate',
                                    bg='white', padx=40, pady=60)

        # Frame 1: Buttons
        self.button2 = tk.Button(self.frame1, text='Browse Folder', width=25,
                                 command=lambda: self.open_folder())

        # Subframe: frame2
        self.frame2 = tk.LabelFrame(self, text='Choose The receiver to evaluate',
                                    bg='white', padx=30, pady=10)

        # Set frame 2 defeault radiobuttons values
        self.var = tk.IntVar()
        self.var.set(0)

        # Set frame2 radiobuttons
        self.radio1 = Radiobutton(self.frame2, text="u-blox Sapcorda", variable=self.var, value=0,
                                  command=self.selection, bg='white')
        self.radio2 = Radiobutton(self.frame2, text="u-blox swipos", variable=self.var, value=1,
                                  bg='white', command=self.selection)
        self.radio3 = Radiobutton(self.frame2, text="NetR9 swipos", variable=self.var, value=2,
                                  bg='white', command=self.selection)

        # Pack Frames
        self.frame1.pack(pady=10)
        self.frame2.pack(pady=10)

        # Pack Buttons
        self.button2.pack()
        self.radio1.pack()
        self.radio2.pack()
        self.radio3.pack()

    def open_folder(self):
        self.filename = askdirectory(initialdir="./DataBase",
                                     title="Choose a folder."
                                     )
        self.destroy()

    def selection(self):
        print(self.var.get())
        if self.var.get() == 0:
            self.receiver = 'sapcorda'
            # return True
        elif self.var.get() == 1:
            self.receiver = 'ublox'
            # return False
        elif self.var.get() == 2:
            self.receiver = 'NetR9'
        else:
            sys.exit("Missing input")

    def output(self):
        if self.var.get() == 0:
            self.receiver = 'sapcorda'

        return self.filename, self.receiver
        return self.filename, self.receiver
