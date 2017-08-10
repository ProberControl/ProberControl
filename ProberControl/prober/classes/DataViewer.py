import numpy as np
import math
import Tkinter as tk
import tkFileDialog
import matplotlib
matplotlib.use('GtkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

class DataViewer(tk.Frame):
    def __init__(self, master=None):
        # Initialise GUI
        tk.Frame.__init__(self, master)
        self.master.title("Data Viewer")
        self.grid()

        # Initialize Standard Values for GUI
        self.FileText     = tk.StringVar()
        self.Meas_Path    = ''
        self.TestText     = tk.StringVar()
        self.test_counter = 0
        self.BoxVar       = tk.StringVar()
        self.ActiveTest   = ''
    
        # Bind Key Strokes To Function
        #self.bind('<KeyRelease-Left>', self.leftKey)
        #self.bind('<KeyRelease-Right>', self.rightKey)

        self.createWidgets()

    # Setup Element on GUI
    def createWidgets(self):
        # Set Measurement file path
        self.FileLabel = tk.Label(self,text='Measurement File')
        self.FileLabel.grid(column=0,row=1,columnspan = 1)
        self.FileEntry = tk.Entry(self,textvariable=self.FileText)
        self.FileEntry.grid(column=2,row=1,columnspan = 2)
        self.FileButton = tk.Button(self, text='Load  File',command=self.FileLoad)
        self.FileButton.grid(column=4,row=1)
        self.BrowseButton = tk.Button(self, text='Browse  File',command=self.FileBrowse)
        self.BrowseButton.grid(column=5,row=1)

        # Show current Test_name
        self.FileLabel = tk.Label(self,textvariable=self.TestText)
        self.FileLabel.grid(column=6,row=1,columnspan = 1)

        # Jump back to recent Test
        self.FileButton = tk.Button(self, text='Back',command=self.BackLoad)
        self.FileButton.grid(column=7,row=1)

        # Jump to next Test
        self.FileButton = tk.Button(self, text='Next',command=self.NextLoad)
        self.FileButton.grid(column=8,row=1)

        # Create Figure and Canvas for MatPlotLib
        self.f = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.f, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1,row=3,columnspan = 5,rowspan=20)

        # Create Toolbar for Matplotlib Canvas
        toolbar_frame = tk.Frame(self)
        toolbar_frame.grid(column=1,row=23,columnspan = 5)
        toolbar = NavigationToolbar2TkAgg( self.canvas, toolbar_frame )

        # Create OptionMenu to choose displayed Test        
        ##Label
        self.MenuLabel = tk.Label(self,text='Test to load')
        self.MenuLabel.grid(column=0,row=2,columnspan = 1)
        ## Menu
        self.TestNameBox = tk.OptionMenu(self,self.BoxVar,[])
        self.TestNameBox.grid(column=2,row=2,columnspan = 2)
            ## Load Button
        self.ProcButton = tk.Button(self, text='Load Test',command=self.NameLoad)
        self.ProcButton.grid(column=4,row=2)

            #Create Button to clear canvas
        self.ClearButton = tk.Button(self, text='Clear Canvas',command=self.ClearCanvas)
        self.ClearButton.grid(column=5,row=2)


    # GUI triggered functions
    def FileBrowse(self):
        try:
            inputFiles = tkFileDialog.askopenfilenames()
            self.FileText.set(self.master.tk.splitlist(inputFiles)[0])
            self.FileLoad()
        except IndexError:
            pass # No file selected, no reason to report error
        except Exception as e:
            print("Error: {}".format(e.stack))

    def ClearCanvas(self):
        self.f.clf()
        self.f.canvas.draw()

    def TestNameBoxChange(self,value):
        self.ActiveTest = value
        self.BoxVar.set(value)

    def NameLoad(self):
        if  self.ActiveTest != '':
            self.TestText.set(self.ActiveTest)
            self.update_canvas(self.Meas_Path, self.ActiveTest,False)

    def BackLoad(self):
        if self.test_counter > 0:
            self.test_counter -= 1
            self.TestText.set(self.test_names[self.test_counter])
            self.update_canvas(self.Meas_Path,self.test_names[self.test_counter])

    def NextLoad(self):
        if self.test_counter < len(self.test_names)-1:
            self.test_counter += 1
            self.TestText.set(self.test_names[self.test_counter])
            self.update_canvas(self.Meas_Path,self.test_names[self.test_counter])

    def FileLoad(self):
        self.Meas_Path = self.FileText.get()

        #get_test_names and fill up option_menu
        self.test_names = self.get_test_names(self.Meas_Path)
        self.TestNameBox["menu"].delete(0, "end")
        for entry in self.test_names:
            self.TestNameBox["menu"].add_command(label=entry,command=lambda value=entry: self.TestNameBoxChange(value))
            #show_first_data
            self.test_counter = 0
            self.TestText.set(self.test_names[0])
            self.update_canvas(self.Meas_Path,self.test_names[0])


    def _quit():
        root.quit()     # stops mainloop
        root.destroy()

    #
    # FUNCTIONAL Functions ###############################
    #

    def update_canvas(self,path,test_name,clear=True):
        data = self.get_test_data(path, test_name)
        
        if clear:
            self.f.clf()

        a = self.f.add_subplot(111)

        try:
            a.plot(zip(*data)[0],zip(*data)[1],'b')
            self.f.canvas.draw()
            
        except IndexError:
            print("Dataset '{}' only has 1 dimension, not able to plot.".format(test_name))
            self.f.clf()

    def get_test_names(self,path):

        NameList=[]

        try:
            with open(path,'r') as MeasFile:
                if MeasFile is None:
                    print 'Problem reading Measurement file.'
                    exit()
            
                for line in MeasFile:
                    if(any(x.isupper() for x in line) or any(x.islower() for x in line)) :
                        NameList.append(line[0:-3])
        except IOError:
            pass # No file was selected, no reason to report an error
        except Exception as e:
            print("Error: {}".format(e))

        if NameList==[]:
            return ['NoName']
        return NameList

    def get_test_data(self, path, test_name):

        Data=[]

        with open(path, 'r') as MeasFile:
            if MeasFile is None:
                print 'Problem reading Measurement file.'
                exit()


            in_block = False
            for line in MeasFile:
          
                if (in_block and line[0:-1] != ''):
                    SubList = line[0:-1].split('\t')
                    CleanSubList = []
                    for elem in SubList:
                        if elem != '':
                            CleanSubList.append(float(elem))
                
                    Data.append(CleanSubList)

                if in_block and line[0:-1] == '':
                    return Data

                if line[0:-3] == test_name or (test_name == 'NoName' and in_block == False):
                    in_block = True

        if in_block == True:
            return Data
        
        print 'Reading Data from File failed'
        return False


if __name__ == "__main__":
    root = tk.Tk()
    main = DataViewer(root)
    main.pack(side="top", fill="both", expand=True)
    root.mainloop()


'''
Copyright (C) 2017  Robert Polster
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
