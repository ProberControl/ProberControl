#!/usr/bin/env python
import tkinter as tk
from tkinter import scrolledtext
import threading
from queue import Queue
import inspect
import operator
import logging
from time import sleep
from functools import partial
from .maitre import Maitre
from .DataViewer import DataViewer
from . import Initializer as i
import tkinter.filedialog
from . import ScriptController
from .plotter import NBPlot
from .Global_MeasureHandler import Global_MeasureHandler as g
from . import ScriptBuilderGUI
from . import DebugGUI
from .EthernetInterface import Eth_Server
from .EthernetInterface import Eth_GUI
from .DataIO import DataIO

from tkinter import *

import sys
import io

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.see("end")
        self.widget.configure(state="disabled")

####### Define Window
# Widgets define Buttons etc
# binding spawn events, now reacting on arrow keys

class Application(tk.Frame):

    def restartGUI(self, Maitre, stages = {}):
        self.__init__(Maitre, stages)

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

        #Initialise Ethernet Interface
        self.eth = Eth_Server(self.Stages,self.Maitre)
        self.eth_loop()

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
        self.ConsoleText    = tk.StringVar()

        if self.ActiveStage != '-1':
            self.StepText.set(self.Stages[self.ActiveStage].stepsize)
        self.createWidgets()
        sys.stdout = TextRedirector(self.Console, "stdout")
        sys.stderr = TextRedirector(self.Console, "stderr")

        # Bind Key Strokes To Function
        self.bind('<KeyRelease-Left>', self.leftKey)
        self.bind('<KeyRelease-Right>', self.rightKey)
        self.bind('<KeyRelease-Up>', self.forwardKey)
        self.bind('<KeyRelease-Down>', self.backwardKey)
        self.bind('<Shift-KeyRelease-Up>',self.upKey)
        self.bind('<Shift-KeyRelease-Down>',self.downKey)
        self.bind('<Return>', self.hitEnter)

        self.q = Queue()

        # Start Queue Listening event
        self.qLoop()


    def eth_loop(self):
        '''
        Calls repeatedly Eth interface update function. To check for new connections or commands.
        '''
        self.eth.update()
        self.after(100, self.eth_loop)


    def qLoop(self):
        '''
        Pulls every 100 ms from the que and executes funtion f, if a return queue is provided return will be put in provided queue
        '''
        try:
            while True:
                f, a, k, qr = self.q.get_nowait()
                r = f(*a, **k)
                if qr: qr.put(r)
        except:
            pass
        self.after(100, self.qLoop)

    # Setup Element on GUI
    # This is main part that u edit
    # TODO: run loop that continually refreshes/reinitializes all these features for debuggin purposes, remove that code before pushing.

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

        # Create Debug Cascade, with Func to Exec window
        DebugMenu = tk.Menu(MenuBar, tearoff=False)
        DebugMenu.add_command(label='Debug',command = self.startDebugGUI)
        MenuBar.add_cascade(label='Debug',menu = DebugMenu)

        # Create Network Cascade
        NetworkMenu = tk.Menu(MenuBar, tearoff=False)
        NetworkMenu.add_command(label='Network Config',command = self.startEthernetGUI)
        MenuBar.add_cascade(label='Network',menu = NetworkMenu)

        # Parameters for adjusting main buttons on GUI (Browse, Execute, Build)
        self.ScriptLabel = tk.Label(self,text='Script to Execute')
        self.ScriptLabel.grid(column=0,row=0,columnspan=2)

        self.ScriptEntry = tk.Entry(self,textvariable=self.FileText,width = 55)
        self.ScriptEntry.grid(column=2,row=0,columnspan=2)

        self.BrowseButton = tk.Button(self, text='Browse Scripts',command=self.FileBrowse, height = 5, width = 20)
        self.BrowseButton.grid(column=0,row=2,columnspan=2, rowspan = 4, padx=5, pady=5)

        self.BuildButton = tk.Button(self, text='Build Script',command=self.startScriptBuilder, height = 5, width = 20)
        self.BuildButton.grid(column=0,row=10,columnspan=2, rowspan = 4, padx=5, pady=5)

        self.ScriptButton = tk.Button(self, text='Execute Script', command=self.ScriptRun, height = 5, width = 20, bg = "green", fg = "white")
        self.ScriptButton.grid(column=0,row=6,columnspan=2, rowspan = 4, padx=5, pady=5)

        #Console Text Widget
        self.Console = scrolledtext.ScrolledText(self, height=18, width=120, bg='black', fg='white', font='consolas 10')
        self.Console.grid(column=2,row=2,columnspan = 2, rowspan = 30, sticky='ew')
        self.Console.tag_config("stderr", background="black", foreground="red")
        self.Console.tag_config("stdout", background="black", foreground="white")


    # Function for creating Debug Window
    def startDebugGUI(self):
        BuilderWindow=tk.Toplevel(self)
        #DebugGUI.DebugGUI(BuilderWindow, self.Maitre, self.Stages)
        DebugGUI.create_Debug(BuilderWindow, self.Maitre, self.Stages)

    # function for enabling you to hit enter to run script instead of pressing execute
    def hitEnter(self, event):
        self.ScriptRun()

    ### Functions Triggered by events
    def ToggleStickyPlotter(self):

        if self.stickyPlotter.get():
            pl = NBPlot()
            pl.set_clear(0)
        else:
            pl = NBPlot()
            pl.set_clear(1)


    def FileBrowse(self):
        try:
            inputFiles = tkinter.filedialog.askopenfilenames()
            self.FileText.set(self.master.tk.splitlist(inputFiles)[0])
        except IndexError:
            pass # No file selected, no reason to report error
        except Exception as e:
            print(("Error: {}".format(e)))

            self.ConsoleText.set(self.ConsoleText.get() + " \n Error: {}".format(e))


    def ScriptRun(self):
        path = self.FileText.get()

        try:

            name = path.split('/')[-1:][0]

            # Start a thread for the script to run with
            controller = ScriptController.ScriptController(self.Maitre, self.Stages, scriptName=name,queue = self.q)

            scriptThread = threading.Thread(target=controller.read_execute)
            scriptThread.start()

        except IndexError as e:
            print(("Command line error: {}".format(e)))

            self.ConsoleText.set(self.ConsoleText.get() + "\n Command line error: {}".format(e))

        except IOError as e:
            print(("IO Error: {}".format(e)))
            self.ConsoleText.set(self.ConsoleText.get() +  "\n Command line error: {}".format(e))

        except KeyError as e:
            print(("Error within the configuration file: {}".format(e)))
            self.ConsoleText.set(self.ConsoleText.get() +  "\n Error within the configuration file: {}".format(e))
        except Exception as e:
            print(("Error: {}".format(e)))
            self.ConsoleText.set(self.ConsoleText.get() +  "\n Error: {}".format(e))

    def startEthernetGUI(self):
        BuilderWindow=tk.Toplevel(self)
        Eth_GUI(BuilderWindow,self.eth)


    def startScriptBuilder(self):
        BuilderWindow=tk.Toplevel(self)
        ScriptBuilderGUI.create_ScriptBuilder(BuilderWindow, self.Maitre )

    def StartData(self):
        DataWindow=tk.Toplevel(self)
        DataGUI = DataViewer(DataWindow)

    def refresh(self):
        '''Method for refreshing the instruments'''
        self.Stages = self.init.refresh()

    def StageClassButton(self):
        ArgList = DataIO.parameter_prep(Stages = self.Stages, Maitre = self.Maitre,arg_string = self.StageArgText.get(),func_parameter_list = inspect.getargspec(self.ActiveStageFuncList[self.ActiveStageFunc])[0])

        # check if instrument has been locked
        bounded_method = self.ActiveStageFuncList[self.ActiveStageFunc]
        if g().is_locked(bounded_method.__self__):

            print('Cannot execute method {} : instrument locked by running script.'.format(bounded_method))
            self.ConsoleText.set(self.ConsoleText.get() +  '\n Cannot execute method {} : instrument locked by running script.'.format(bounded_method))
        else:
            print(bounded_method(*ArgList))
            self.ConsoleText.set(self.ConsoleText.get() + bounded_method(*ArgList))


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

        ArgList = DataIO.parameter_prep(Stages = self.Stages, Maitre = self.Maitre,arg_string = self.ArgText.get(),func_parameter_list = self.Maitre.get_func_params(self.ActiveMod,self.ActiveFunc))

        print(self.Maitre.execute_func(self.ActiveMod,self.ActiveFunc,ArgList))
        self.gh.release_current_user_instruments()


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
        print(Stage)
        self.ActiveStage = Stage
        self.StepText.set(self.Stages[self.ActiveStage].stepsize)
        if 'O' in self.ActiveStage or 'E' in self.ActiveStage:
            self.StatusLabel.config(text='Step Size in mm')
        if 'C' in self.ActiveStage:
            self.StatusLabel.config(text='Step Size in deg')

    def CommandButton(self):
        # Strg in Command Field:
        command = self.CommandText.get()
        print(command)
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

    #while True:
        #if userpushbutton call reload() function
        #reload() will reinitialize components of gui
    '''
    import imp
    import time
    while True:
        mod = imp.load_source("GUI", "./GUI.py")
        mod.function()
        time.sleep(1)
    '''
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
