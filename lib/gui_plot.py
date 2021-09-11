# -*- coding: utf-8 -*-
"""
Created on Thu Jan 21 12:13:42 2021

@author: Michael
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 09:54:11 2021

@author: Michael
"""

import tkinter as tk

from tkinter.filedialog import askopenfilename



class Interface(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.create_widgets()
        self.filename = None
        self.do_parser = None
        
    def create_widgets(self):
        self.title('Parse NMEA messages')
        self.geometry("500x250") 
        self.configure(background='white')
        
        self.frame1 = tk.LabelFrame(self, text='Select .nmea file or a folder to parse',
                                    bg='white',padx=30, pady=10)
        self.button = tk.Button(self.frame1, text='Browse File',width=25,
                                command=lambda:self.open_file())
           
        self.var =tk.IntVar()
        self.var.set(0)

       
        self.frame1.pack(pady=10)
        self.button.pack()


    def open_file(self):
        self.filename = askopenfilename(initialdir="C:/SwisstopoMobility/analysis/DataBase/2021",
                               filetypes =(("Text File", "*.nmea"),("All Files","*.*")),
                               title = "Choose a file."
                               )
        self.destroy()


    
    def output(self):
        return self.filename