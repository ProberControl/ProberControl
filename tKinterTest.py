import tkinter as tk
from tkinter import *

test = Tk()
'''
test.testButton = tk.Button(test, text = 'hi', height = 5, width = 10)
test.testButton.grid(column=0, row = 0, columnspan =3, rowspan = 2, sticky = 'ew')
test.scriptEntry = tk.Entry(test)
test.scriptEntry.grid(column = 0, row = 2, columnspan = 3, rowspan = 3, sticky = 'ew')
'''

test.ScriptLabel = tk.Label(test,text='Script to Execute')
test.ScriptLabel.grid(column=0,row=0,columnspan=2)


test.ScriptEntry = tk.Entry(test) #,width = 55
test.ScriptEntry.grid(column=2,row=0, columnspan = 2, sticky="ew")
test.rowconfigure(0, weight = 2)
test.columnconfigure(2, weight = 1)
#test.ScriptEntry.columnconfigure(3, weight = 0)
#test.ScriptEntry.columnconfigure(4, weight = 0)

test.BrowseButton = tk.Button(test, text='Browse Scripts', height = 5, width = 20)
test.BrowseButton.grid(column=0,row=2,columnspan=2, rowspan = 4, padx=5, pady=5)

test.BuildButton = tk.Button(test, text='Build Script', height = 5, width = 20)
test.BuildButton.grid(column=0,row=6,columnspan=2, rowspan = 4, padx=5, pady=5)

test.ScriptButton = tk.Button(test, text='Execute Script', height = 5, width = 20, bg = "green", fg = "white")
test.ScriptButton.grid(column=0,row=10,columnspan=2, rowspan = 4, padx=5, pady=5)

test.ScriptEntry.columnconfigure(0, weight = 1)
test.ScriptEntry.rowconfigure(0, weight = 1)
#test.columnconfigure(1, weight = 1)
#test.columnconfigure(2, weight = 1)

test.mainloop()
