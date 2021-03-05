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

import ScriptBuilder

w = None
def create_Debug(w_new, Maitre, Stages, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w
    w = w_new
    #ScriptBuilder.set_Tk_var()
    top = DebugGUI(w, Maitre, Stages)
    #ScriptBuilder.init(w, top, Maitre)
    return (w, top)

def destroy_Debug():
    global w
    w.destroy()
    w = None


class DebugGUI:
    # Function for creating Debug Window
    def __init__(self, top, Maitre, stages):
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

        self.Maitre = Maitre
        top.title("Debug Window")
        top.grid()

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


        # COMMAND TO EXEC
        self.CommandLabel = tk.Label(top,text='Command to Exec')
        self.CommandLabel.grid(column=0,row=5,columnspan = 2)
        self.CommandEntry = tk.Entry(top,textvariable=self.CommandText,width = 55)
        self.CommandEntry.grid(column=2,row=5,columnspan = 2)
        self.CommandButton = tk.Button(top, text='Execute',command=self.CommandButton)
        self.CommandButton.grid(column=4,row=5)

        # Procedure OptionMenu for Procedure selection
        ##Label
        self.CommandLabel = tk.Label(top,text='Procedure Function to Exec')
        self.CommandLabel.grid(column=0,row=20,columnspan = 2)
        ##Module
        self.ModBox = tk.OptionMenu(top,self.ProcMod,*self.Maitre.get_all_modules(),command=self.ModBoxChange)
        self.ModBox.config(width = 20)
        self.ModBox.grid(column=2,row=20,columnspan = 1)
        ##Function
        self.FuncBox = tk.OptionMenu(top,self.ProcFunc,*self.Maitre.get_func_name(0),command=self.FuncBoxChange)
        self.FuncBox.config(width = 20)
        self.FuncBox.grid(column=3,row=20,columnspan = 1)
        ## Argument Display Field
        self.CommandDisplay = tk.Entry(top,textvariable=self.ArgDispText, width = 60,state = 'disabled')
        self.CommandDisplay.grid(column=4,row=19,columnspan = 2)
        ## Argument Entry Field
        self.CommandEntry = tk.Entry(top,textvariable=self.ArgText, width = 60)
        self.CommandEntry.grid(column=4,row=20,columnspan = 2)
        ## Execute Button
        self.ProcButton = tk.Button(top, text='Execute',command=self.ProcButton)
        self.ProcButton.grid(column=6,row=20)

        # STAGE FUNC TO EXEC

        # Hidden features on GUI
        if self.Stages != {}:
            ##Label
            self.StageCommandLabel = tk.Label(top,text='Stage Function to Exec')
            self.StageCommandLabel.grid(column=0,row=4,columnspan = 2)
            ##Stage-Class
            self.StageModBox = tk.OptionMenu(top,self.StageMod,*list(self.Stages.keys()),command=self.StageClassChange)
            self.StageModBox.config(width = 20)
            self.StageModBox.grid(column=2,row=4,columnspan = 1)
            ##Function
            self.StageFuncBox = tk.OptionMenu(top,self.StageFunc,[],command=self.StageFuncChange)
            self.StageFuncBox.config(width = 20)
            self.StageFuncBox.grid(column=3,row=4,columnspan = 1)
            ## Argument Display Field
            self.StageCommandEntry = tk.Entry(top,textvariable=self.StageArgDispText, width = 60,state = 'disabled')
            self.StageCommandEntry.grid(column=4,row=3,columnspan = 2)
            ## Argument Entry Field
            self.StageCommandEntry = tk.Entry(top,textvariable=self.StageArgText, width = 60)
            self.StageCommandEntry.grid(column=4,row=4,columnspan = 2)
            ## Execute Button
            self.StageProcButton = tk.Button(top, text='Execute',command=self.StageClassButton)
            self.StageProcButton.grid(column=6,row=4)

        # Auto Generate Fields for Connected Stages
        self.StageButtonI = 0
        self.StageButtons = {}
        for k,v in list(self.Stages.items()):
            if 'O' == k[0]:
                self.StageButtons[k]=tk.Button(top, text=k ,command= partial(self.SetActiveStage,k))
                self.StageButtons[k].grid(column=self.StageButtonI,row=7)
                self.StageButtonI +=  1
            if 'C' == k[0]:
                self.StageButtons[k]=tk.Button(top, text=k ,command= partial(self.SetActiveStage,k))
                self.StageButtons[k].grid(column=self.StageButtonI,row=7)
                self.StageButtonI +=  1
            if 'E' == k[0]:
                self.StageButtons[k]=tk.Button(top, text=k ,command= partial(self.SetActiveStage,k))
                self.StageButtons[k].grid(column=self.StageButtonI,row=7)
                self.StageButtonI +=  1

        # Set Stepsize in either mm or deg
        if self.StageButtonI != 0:
            self.StatusLabel = tk.Label(top,text='Step Size in deg')
            if self.Stages != {}:
                if 'O' in self.ActiveStage or 'E' in self.ActiveStage:
                    self.StatusLabel = tk.Label(top,text='Step Size in mm')
                if 'C' in self.ActiveStage:
                    self.StatusLabel = tk.Label(top,text='Step Size in deg')
            self.StatusLabel.grid(column=0,row=8,columnspan = 1)
            self.StepEntry = tk.Entry(top,textvariable=self.StepText)
            self.StepEntry.grid(column=2,row=8,columnspan = 2)
            self.StepButton = tk.Button(top, text='Set Step',command=self.StepSetButton)
            self.StepButton.grid(column=4,row=8)

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
        else:
            print(bounded_method(*ArgList))


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

if __name__ == '__main__':
    vp_start_gui()
