#!/usr/bin/env python
import Tkinter as tk
import threading
import inspect
import operator
import logging
from time import sleep
from functools import partial
from maitre import Maitre
from DataViewer import DataViewer
import Initializer as i
import tkFileDialog
import ScriptController
from plotter import NBPlot
from Global_MeasureHandler import Global_MeasureHandler as g


####### Define Window
# Widgets define Buttons etc
# binding spawn events, now reacting on arrow keys

class Application(tk.Frame):
    def __init__(self, master=None, stages={}):
        # Initialise GUI
        tk.Frame.__init__(self, master)
        self.master.title("Prober Control")
        self.grid()

        # Get instance of Global_MeasureHandler; Do not change this!
        self.gh = g()

        # Get Dictionaries of Handles of Stages
        self.Stages = stages
        # Set Active Stage to first Stage in Dictionary
        self.ActiveStage = '-1'
        if self.Stages != {}:
            dev_names = sorted(self.Stages.keys())
            for st in dev_names:
                if st[0] == 'O' or st[0] == 'E':
                    self.ActiveStage = st
                    break
            #print 'Active Stage: ' + self.ActiveStage # why are we printing this?

        # Initialize Procedure Handler
        self.Maitre = Maitre()

        #Gain access to Initializer singleton
        self.init = i.Initializer()

        # Initialize Standard Values for GUI
        self.stickyPlotter  = tk.BooleanVar()
        self.CommandText    = tk.StringVar()
        self.StepText       = tk.StringVar()
        self.ProcMod        = tk.StringVar()
        self.ProcFunc       = tk.StringVar()
        self.ArgText        = tk.StringVar()
        self.ArgDispText    = tk.StringVar()
        self.StageMod       = tk.StringVar()
        self.StageFunc      = tk.StringVar()
        self.StageArgText   = tk.StringVar()
        self.StageArgDispText = tk.StringVar()
        self.Script_Path      = ''
        self.FileText         = tk.StringVar()

        if self.ActiveStage != '-1':
            self.StepText.set(self.Stages[self.ActiveStage].stepsize)
        self.createWidgets()

        # Bind Key Strokes To Function
        self.bind('<KeyRelease-Left>', self.leftKey)
        self.bind('<KeyRelease-Right>', self.rightKey)
        self.bind('<KeyRelease-Up>', self.forwardKey)
        self.bind('<KeyRelease-Down>', self.backwardKey)
        self.bind('<Shift-KeyRelease-Up>',self.upKey)
        self.bind('<Shift-KeyRelease-Down>',self.downKey)

    # Setup Element on GUI
    def createWidgets(self):
        # Create Menu
        MenuBar = tk.Menu(self.master)
        self.master.config(menu=MenuBar)

        # Create Refreshing Cascade
        RefreshMenu = tk.Menu(MenuBar, tearoff=False)
        RefreshMenu.add_command(label='Refresh Stages',command=self.refresh)
        RefreshMenu.add_command(label='Refresh Procedures',command=self.Maitre.refresh)
        RefreshMenu.add_command(label='Print GPIB Bus',command=self.init.printGPIB)
        MenuBar.add_cascade(label='Refresh',menu = RefreshMenu)

        # Create Data Cascade
        DataMenu = tk.Menu(MenuBar, tearoff=False)
        DataMenu.add_command(label='DataViewer',command = self.StartData)
        DataMenu.add_checkbutton(label='Sticky Data in Plotter',onvalue = 1, offvalue = 0, variable=self.stickyPlotter,command = self.ToggleStickyPlotter)
        MenuBar.add_cascade(label='Data',menu = DataMenu)



        # Procedure OptionMenu for Procedure selection
        ##Label
        self.CommandLabel = tk.Label(self,text='Procedure Function to Exec')
        self.CommandLabel.grid(column=0,row=2,columnspan = 2)
        ##Module
        self.ModBox = tk.OptionMenu(self,self.ProcMod,*self.Maitre.get_all_modules(),command=self.ModBoxChange)
        self.ModBox.config(width = 20)
        self.ModBox.grid(column=2,row=2,columnspan = 1)
        ##Function
        self.FuncBox = tk.OptionMenu(self,self.ProcFunc,*self.Maitre.get_func_name(0),command=self.FuncBoxChange)
        self.FuncBox.config(width = 20)
        self.FuncBox.grid(column=3,row=2,columnspan = 1)
        ## Argument Display Field
        self.CommandDisplay = tk.Entry(self,textvariable=self.ArgDispText, width = 60,state = 'disabled')
        self.CommandDisplay.grid(column=4,row=1,columnspan = 2)
        ## Argument Entry Field
        self.CommandEntry = tk.Entry(self,textvariable=self.ArgText, width = 60)
        self.CommandEntry.grid(column=4,row=2,columnspan = 2)
        ## Execute Button
        self.ProcButton = tk.Button(self, text='Execute',command=self.ProcButton)
        self.ProcButton.grid(column=6,row=2)
        # Stages OptionMenu for Function selection
        if self.Stages != {}:
            ##Label
            self.StageCommandLabel = tk.Label(self,text='Stage Function to Exec')
            self.StageCommandLabel.grid(column=0,row=4,columnspan = 2)
            ##Stage-Class
            self.StageModBox = tk.OptionMenu(self,self.StageMod,*list(self.Stages.keys()),command=self.StageClassChange)
            self.StageModBox.config(width = 20)
            self.StageModBox.grid(column=2,row=4,columnspan = 1)
            ##Function
            self.StageFuncBox = tk.OptionMenu(self,self.StageFunc,[],command=self.StageFuncChange)
            self.StageFuncBox.config(width = 20)
            self.StageFuncBox.grid(column=3,row=4,columnspan = 1)
            ## Argument Display Field
            self.StageCommandEntry = tk.Entry(self,textvariable=self.StageArgDispText, width = 60,state = 'disabled')
            self.StageCommandEntry.grid(column=4,row=3,columnspan = 2)
            ## Argument Entry Field
            self.StageCommandEntry = tk.Entry(self,textvariable=self.StageArgText, width = 60)
            self.StageCommandEntry.grid(column=4,row=4,columnspan = 2)
            ## Execute Button
            self.StageProcButton = tk.Button(self, text='Execute',command=self.StageClassButton)
            self.StageProcButton.grid(column=6,row=4)

        # Command Field
        self.CommandLabel = tk.Label(self,text='Command to Exec')
        self.CommandLabel.grid(column=0,row=5,columnspan = 2)
        self.CommandEntry = tk.Entry(self,textvariable=self.CommandText,width = 55)
        self.CommandEntry.grid(column=2,row=5,columnspan = 2)
        self.CommandButton = tk.Button(self, text='Execute',command=self.CommandButton)
        self.CommandButton.grid(column=4,row=5)

        # Scripting Field
        self.ScriptLabel = tk.Label(self,text='Script to Execute')
        self.ScriptLabel.grid(column=0,row=6,columnspan=2)

        self.ScriptEntry = tk.Entry(self,textvariable=self.FileText,width = 55)
        self.ScriptEntry.grid(column=2,row=6,columnspan=2)

        self.ScriptButton = tk.Button(self, text='Execute', command=self.ScriptRun)
        self.ScriptButton.grid(column=4,row=6)

        self.BrowseButton = tk.Button(self, text='Browse',command=self.FileBrowse)
        self.BrowseButton.grid(column=5,row=6)

        # Auto Generate Fields for Connected Stages
        self.StageButtonI = 0
        self.StageButtons = {}
        for k,v in self.Stages.items():
            if 'O' == k[0]:
                self.StageButtons[k]=tk.Button(self, text=k ,command= partial(self.SetActiveStage,k))
                self.StageButtons[k].grid(column=self.StageButtonI,row=7)
                self.StageButtonI +=  1
            if 'C' == k[0]:
                self.StageButtons[k]=tk.Button(self, text=k ,command= partial(self.SetActiveStage,k))
                self.StageButtons[k].grid(column=self.StageButtonI,row=7)
                self.StageButtonI +=  1
            if 'E' == k[0]:
                self.StageButtons[k]=tk.Button(self, text=k ,command= partial(self.SetActiveStage,k))
                self.StageButtons[k].grid(column=self.StageButtonI,row=7)
                self.StageButtonI +=  1

        # Set Stepsize in either mm or deg
        if self.StageButtonI != 0:
            self.StatusLabel = tk.Label(self,text='Step Size in deg')
            if self.Stages != {}:
                if 'O' in self.ActiveStage or 'E' in self.ActiveStage:
                    self.StatusLabel = tk.Label(self,text='Step Size in mm')
                if 'C' in self.ActiveStage:
                    self.StatusLabel = tk.Label(self,text='Step Size in deg')
            self.StatusLabel.grid(column=0,row=8,columnspan = 1)
            self.StepEntry = tk.Entry(self,textvariable=self.StepText)
            self.StepEntry.grid(column=2,row=8,columnspan = 2)
            self.StepButton = tk.Button(self, text='Set Step',command=self.StepSetButton)
            self.StepButton.grid(column=4,row=8)

    ### Functions Triggered by events
    def ToggleStickyPlotter(self):

        if self.stickyPlotter.get:
            pl = NBPlot()
            pl.set_clear(1)
        else:
            pl = NBPlot()
            pl.set_clear(0)

    def FileBrowse(self):
        try:
            inputFiles = tkFileDialog.askopenfilenames()
            self.FileText.set(self.master.tk.splitlist(inputFiles)[0])
        except IndexError:
            pass # No file selected, no reason to report error
        except Exception as e:
            print("Error: {}".format(e))

    def ScriptRun(self):
        path = self.FileText.get()

        try:
            print("Running script {}".format(path))
            name = path.split('/')[-1:][0]

            # Start a thread for the script to run with
            controller = ScriptController.ScriptController(self.Maitre, self.Stages, scriptName=name)
            scriptThread = threading.Thread(target=controller.read_execute)
            scriptThread.start()

            # Start update locking thread
            lockThread = threading.Thread(name='lock thread',target=self.__updateLocked())
            lockThread.start()

            addThread = threading.Thread(name='release thread',target=self.__updateModBox, args=[scriptThread])
            addThread.start()

        except IndexError as e:
            print("Command line error: {}".format(e))
        except IOError as e:
            print("IO Error: {}".format(e))
        except KeyError as e:
            print("Error within the configuration file: {}".format(e))
        except Exception as e:
            print("Error: {}".format(e))

    def __updateLocked(self):
        '''Updates the option menu for Stages after the script is executed'''

        # Wait for the script to get a locked instrument
        # Maybe the better option would be to run this every 2 seconds while the thread is alive

        logging.debug('starting')
        #while self.scriptThread.is_alive():
        sleep(1)
        busy = [item.whoAmI() for i in self.gh.get_locked() for item in i[1]]
        toRemove = [i for i in self.Stages.keys() if i[1:] in busy]

        for item in toRemove:
            try:
                self.StageModBox.children['menu'].delete(item)
            except Exception:
                # Bad Form-- I know. Blame 2.7
                pass
        logging.debug('exiting')

    def __updateModBox(self, thread):
        '''Make unlocked resources available'''
        logging.debug('starting')

        while thread.is_alive():
            pass

        # destroy box
        self.StageModBox.destroy()

        busy = [item.whoAmI() for i in self.gh.get_locked() for item in i[1]]
        toAdd = [i for i in self.Stages.keys() if i[1:] not in busy]
        print busy
        print toAdd
        self.StageModBox = tk.OptionMenu(self,self.StageMod,*list(toAdd),command=self.StageClassChange)
        self.StageModBox.grid(column=2,row=3,columnspan = 1)

        logging.debug('exiting')

    def StartData(self):
        DataWindow=tk.Toplevel(self)
        DataGUI = DataViewer(DataWindow)

    def refresh(self):
        '''Method for refreshing the instruments'''
        self.Stages = self.init.refresh()

    def StageClassButton(self):
        PreArgList=self.StageArgText.get().split(' ')
        ArgList=[]
        # String Interpretation
        for elem in PreArgList:
            if '[' in elem:
                SubList=elem.replace('[','').replace(']','').split(',')
                elem=map(float,SubList)
            if 'Stages' in elem:
                elem = self.Stages
            if 'Maitre' in elem:
                elem = self.Maitre
            if str(elem).isdigit():
                elem=float(elem)
            if elem != '':
                ArgList.append(elem)

                direct_list = inspect.getargspec(self.ActiveStageFuncList[self.ActiveStageFunc])[0]
                insert_list = []

                if "Stages" in direct_list:
                    insert_list.append([direct_list.index("Stages"),self.Stages])

                if "stages" in direct_list:
                    insert_list.append([direct_list.index("stages"),self.Stages])

                if "Maitre" in direct_list:
                    insert_list.append([direct_list.index("Maitre"),self.Maitre])

                if "maitre" in direct_list:
                    insert_list.append([direct_list.index("maitre"),self.Maitre])

                insert_list.sort(key=operator.itemgetter(0))

                if insert_list != []:
                    for x in insert_list:
                        ArgList.insert(x[0],x[1])

        print self.ActiveStageFuncList[self.ActiveStageFunc](*ArgList)

    def StageFuncChange(self,choice):
        self.ActiveStageFunc = self.ActiveStageFuncNames.index(choice)
        self.StageFunc.set(choice)
        argslist = inspect.getargspec(self.ActiveStageFuncList[self.ActiveStageFunc])[0]

        shortlist = []
        for x in argslist:
            if not(x in ["Stages","stages","Maitre","maitre","self"]):
                shortlist.append(x)

        self.StageArgDispText.set(shortlist)

    def StageClassChange(self,choice):

        self.ActiveStageMod = choice

        self.ActiveStageFuncList  = []
        self.ActiveStageFuncNames = []

        for func in inspect.getmembers(self.Stages[self.ActiveStageMod],inspect.ismethod):
            if func[0][0] != '_':
                self.ActiveStageFuncList.append(func[1])
                self.ActiveStageFuncNames.append(func[0])

        self.StageFuncBox["menu"].delete(0, "end")
        for entry in self.ActiveStageFuncNames:
            self.StageFuncBox["menu"].add_command(label=entry, command=lambda value=entry: self.StageFuncChange(value))

    def ProcButton(self):
        PreArgList=self.ArgText.get().split(' ')
        ArgList=[]
        # String Interpretation
        for elem in PreArgList:
            if '[' in elem:
                SubList=elem.replace('[','').replace(']','').split(',')
                elem=map(float,SubList)
            if 'Stages' in elem:
                elem = self.Stages
            if 'Maitre' in elem:
                elem = self.Maitre
            if str(elem).isdigit():
                elem=float(elem)
            if elem == '':
                continue

            ArgList.append(elem)

        direct_list = self.Maitre.get_func_params(self.ActiveMod,self.ActiveFunc)
        insert_list = []

        if "Stages" in direct_list:
            insert_list.append([direct_list.index("Stages"),self.Stages])

        if "stages" in direct_list:
            insert_list.append([direct_list.index("stages"),self.Stages])

        if "Maitre" in direct_list:
            insert_list.append([direct_list.index("Maitre"),self.Maitre])

        if "maitre" in direct_list:
            insert_list.append([direct_list.index("maitre"),self.Maitre])

        insert_list.sort(key=operator.itemgetter(0))

        if insert_list != []:
            for x in insert_list:
                ArgList.insert(x[0],x[1])

        print self.Maitre.execute_func(self.ActiveMod,self.ActiveFunc,ArgList)

    def FuncBoxChange(self,choice):
        self.ActiveFunc = self.Maitre.get_func_name(self.ActiveMod).index(choice)
        self.ProcFunc.set(choice)
        argslist = self.Maitre.get_func_params(self.ActiveMod,self.ActiveFunc)

        shortlist = []
        for x in argslist:
            if not(x in ["Stages","stages","Maitre","maitre","self"]):
                shortlist.append(x)

        self.ArgDispText.set(shortlist)

    def ModBoxChange(self,choice):
        self.ActiveMod = self.Maitre.get_all_modules().index(choice)
        self.FuncBox["menu"].delete(0, "end")
        for entry in self.Maitre.get_func_name(self.ActiveMod):
            self.FuncBox["menu"].add_command(label=entry, command=lambda value=entry: self.FuncBoxChange(value))


    def SetActiveStage(self,Stage):
        print Stage
        self.ActiveStage = Stage
        self.StepText.set(self.Stages[self.ActiveStage].stepsize)
        if 'O' in self.ActiveStage or 'E' in self.ActiveStage:
            self.StatusLabel.config(text='Step Size in mm')
        if 'C' in self.ActiveStage:
            self.StatusLabel.config(text='Step Size in deg')

    def CommandButton(self):
        # Strg in Command Field:
        command = self.CommandText.get()
        print command
        exec(command)
        self.focus_set()

    def StepSetButton(self):
        self.Stages[self.ActiveStage].set_stepsize(float(self.StepText.get()))
        self.focus_set()

    def leftKey(self,event):
        t_y = threading.Thread(target=self.Stages[self.ActiveStage].step, args=('L'))
        t_y.start()

    def rightKey(self,event):
        t_y = threading.Thread(target=self.Stages[self.ActiveStage].step, args=('R'))
        t_y.start()

    def upKey(self,event):
        t_z = threading.Thread(target=self.Stages[self.ActiveStage].step, args=('U'))
        t_z.start()

    def downKey(self,event):
        t_z = threading.Thread(target=self.Stages[self.ActiveStage].step, args=('D'))
        t_z.start()

    def forwardKey(self,event):
        t_x = threading.Thread(target=self.Stages[self.ActiveStage].step, args=('F'))
        t_x.start()

    def backwardKey(self,event):
        t_x = threading.Thread(target=self.Stages[self.ActiveStage].step, args=('B'))
        t_x.start()

if __name__=='__main__':
    ### Create Instance of Window
    app = Application()
    ### Set Focus on windows to catch key strokes
    app.focus_set()
    ### Start Looping and wating for events
    app.mainloop()



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
