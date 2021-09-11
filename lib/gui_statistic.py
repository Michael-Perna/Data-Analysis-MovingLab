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
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory


class Interface(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.create_widgets()
        self.filename = None
        self.do_parser = None

    def create_widgets(self):
        self.title('Get statistics about a GNSS trajeckts')
        self.geometry("500x250") 
        self.configure(background='white')
        
        # Frame 1
        self.frame1 = tk.LabelFrame(self, text='Select .result file to evaluate',
                                    bg='white',padx=40, pady=60)

        # Frame 1: Buttons
        self.button = tk.Button(self.frame1, text='Browse File',width=25,
                                command=lambda:self.open_file())
        self.button2 = tk.Button(self.frame1, text='Browse Folder',width=25,
                                command=lambda:self.open_folder())
           
        # Pack Frames 
        self.frame1.pack(pady=10)
        
        # Pack Buttons
        self.button.pack()
        self.button2.pack()

    def open_file(self):
        self.filename = askopenfilename(initialdir="./DataBase",
                               filetypes =(('RESULT file', '*.result'),("All Files","*.*")),
                               title = "Choose a file."
                               )
        self.destroy()

    def open_folder(self):
        self.filename = askdirectory(initialdir="./DataBase",
                               title = "Choose a folder."
                               )
        self.destroy()

    def output(self):
        return self.filename