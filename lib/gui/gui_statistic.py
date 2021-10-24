# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 14:29:28 2021.

@author: Michael
"""

from tkinter.filedialog import askdirectory
from tkinter.filedialog import Radiobutton
import tkinter as tk
import sys


class Interface(tk.Tk):
    """User Interface."""

    def __init__(self):
        """Init."""
        tk.Tk.__init__(self)
        self.create_widgets()
        self.filename = None
        self.zone = None
        self.save_csv = None

    def create_widgets(self):
        """Create widget."""
        self.title('Get statistics about a GNSS trajeckts')
        self.geometry("500x500")
        self.configure(background='white')

        # Frame 1
        self.frame1 = tk.LabelFrame(self,
                                    text='Select .the foldeter to concate',
                                    bg='white', padx=40, pady=60)

        # Frame 1: Buttons
        self.button2 = tk.Button(self.frame1, text='Browse Folder', width=25,
                                 command=lambda: self.open_folder())

        # Subframe: frame2
        self.frame2 = tk.LabelFrame(self,
                                    text='Choose the area to analyse',
                                    bg='white', padx=30, pady=10)

        # Set frame 2 defeault radiobuttons values
        self.var = tk.IntVar()
        self.var.set(0)

        # Set frame2 radiobuttons
        self.radio0 = Radiobutton(self.frame2,
                                  text="The whole track", variable=self.var,
                                  value=0,
                                  command=self.selection, bg='white')
        self.radio1 = Radiobutton(self.frame2,
                                  text="open_sky", variable=self.var,
                                  value=1,
                                  command=self.selection, bg='white')
        self.radio2 = Radiobutton(self.frame2,
                                  text="city_NS",
                                  variable=self.var, value=2,
                                  bg='white', command=self.selection)
        self.radio3 = Radiobutton(self.frame2,
                                  text="city_EW",
                                  variable=self.var, value=3,
                                  bg='white', command=self.selection)
        self.radio4 = Radiobutton(self.frame2,
                                  text="old_city",
                                  variable=self.var, value=4,
                                  bg='white', command=self.selection)
        self.radio5 = Radiobutton(self.frame2,
                                  text="peripheric",
                                  variable=self.var, value=5,
                                  bg='white', command=self.selection)

        # Subframe: frame3
        self.frame3 = tk.LabelFrame(self,
                                    text='Save the dataframe as csv?',
                                    bg='white', padx=30, pady=10)

        # Set frame 3 defeault radiobuttons values
        self.var_2 = tk.IntVar()
        self.var_2.set(0)

        # Set frame3 radiobuttons
        self.radio_6 = Radiobutton(self.frame3,
                                   text="No", variable=self.var_2,
                                   value=0,
                                   command=self.selectionB, bg='white')
        self.radio_7 = Radiobutton(self.frame3,
                                   text="Yes", variable=self.var_2,
                                   value=1,
                                   command=self.selectionB, bg='white')

        # Pack Frames
        self.frame1.pack(pady=10)
        self.frame2.pack(pady=10)
        self.frame3.pack(pady=10)

        # Pack Buttons
        self.button2.pack()
        self.radio0.pack()
        self.radio1.pack()
        self.radio2.pack()
        self.radio3.pack()
        self.radio4.pack()
        self.radio5.pack()
        self.radio_6.pack()
        self.radio_7.pack()

    def open_folder(self):
        self.filename = askdirectory(initialdir="./DataBase",
                                     title="Choose a folder."
                                     )
        self.destroy()

    def selection(self):
        if self.var.get() == 0:
            self.zone = ''
        elif self.var.get() == 1:
            self.zone = 'open_sky'
        elif self.var.get() == 2:
            self.zone = 'city_NS'
        elif self.var.get() == 3:
            self.zone = 'city_EW'
        elif self.var.get() == 4:
            self.zone = 'old_city'
        elif self.var.get() == 5:
            self.zone = 'peripheric'
        else:
            sys.exit("Missing input")

    def selectionB(self):
        if self.var_2.get() == 1:
            self.save_csv = True
        elif self.var_2.get() == 0:
            self.save_csv = False
        else:
            sys.exit("Missing input")

    def output(self):
        if self.var.get() == 0:
            self.zone = ''
        if self.var_2.get() == 0:
            self.save_csv = False

        return self.filename, self.zone, self.save_csv
