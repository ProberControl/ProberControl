#! /usr/bin/env python
#
# Support module partially generated by PAGE version 4.9
# In conjunction with Tcl version 8.6
#    Dec 13, 2017 02:19:12 PM


import sys
import tkFileDialog
import prober.classes.Dialogs as dialogs

try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1

global script
script = ''

def set_Tk_var():
    global MeasNameVar
    MeasNameVar = StringVar()
    global ProcBoxVar
    ProcBoxVar = StringVar()
    global StructNameVar
    StructNameVar = StringVar()
    global FuncBoxVar
    FuncBoxVar = StringVar()
    global ArgEntryVar
    ArgEntryVar = StringVar()
    global ArgShowEntryVar
    ArgShowEntryVar = StringVar()
    global BlockTypeBoxVar
    BlockTypeBoxVar = StringVar()
    global BlockNameVar
    BlockNameVar = StringVar()
    global copyLastMeasBlock
    copyLastMeasBlock = StringVar()
    copyLastMeasBlock.set(0)
    global LocalBinFuncFileBoxVar
    LocalBinFuncFileBoxVar = StringVar()
    global LocalBinFuncFuncBoxVar
    LocalBinFuncFuncBoxVar = StringVar()
    global GroupByBoxVar
    GroupByBoxVar = StringVar()
    global GlobBinFuncFileBoxVar
    GlobBinFuncFileBoxVar = StringVar()
    global GlobBinFuncFuncBoxVar
    GlobBinFuncFuncBoxVar = StringVar()


def searchAndReplace():
    global w, top_level, root, Maitre
    replaceDia = dialogs.Search_and_Replace(root, w.Scrolledtext1)


def addBlock():
    new_block = ''

    if BlockTypeBoxVar.get() != '' and BlockNameVar.get() != '':
        new_block += '> '+BlockTypeBoxVar.get().lower()+'\n'
        new_block += BlockNameVar.get()+'\n'

    if LocalBinFuncFuncBoxVar.get() != '':
        new_block += '> bin \n'
        new_block += LocalBinFuncFileBoxVar.get()+':'+LocalBinFuncFuncBoxVar.get()+'\n'

    scriptPreCursor  = w.Scrolledtext1.get(1.0, INSERT )

    # To copy all the measurements from the previous block
    # 1) Find start of previous block
    # 2) Get name of previous block (next line after block type identifier)
    # 3) copy block and swap every old block name with new block name (e.g. to adapt structure names)
    # 4) append to new_block variable

    header = '> '+BlockTypeBoxVar.get().lower()

    if copyLastMeasBlock.get() == '1':
        blockStartIndex = scriptPreCursor.rfind(header)
        print blockStartIndex
        if blockStartIndex:
            splitScript = scriptPreCursor[blockStartIndex:].splitlines(1)
            old_block_name = splitScript[1].strip(' ').strip('\n')

            print old_block_name

            print ''.join(splitScript[2:]).replace(old_block_name,BlockNameVar.get())

            new_block += ''.join(splitScript[2:]).replace(old_block_name,BlockNameVar.get())



    scriptPostCursor = w.Scrolledtext1.get(INSERT , END)

    script = scriptPreCursor + new_block + scriptPostCursor

    w.Scrolledtext1.delete(1.0, END)
    w.Scrolledtext1.insert(1.0,script)
    w.Scrolledtext1.see(END)

def LocalBinFuncFileBoxChange(choice):
    global w, Maitre
    LocalBinFuncFile = Maitre.get_all_modules().index(choice)
    w.LocalBinFuncFuncBox["menu"].delete(0, "end")
    for entry in ['']+Maitre.get_func_name(LocalBinFuncFile):
        w.LocalBinFuncFuncBox["menu"].add_command(label=entry, command=lambda value=entry: LocalBinFuncFuncBoxVar.set(value))

def GlobalsUpdate():
    global w
    script = w.Scrolledtext1.get(1.0, END)
    splitScript = script.splitlines(1)
    i = 0

    for line in splitScript[0:2]:
        if 'group-by' in line or 'bin-by' in line:
            i+=1

    if GroupByBoxVar.get() != '':
        groupStr = 'group-by:'+GroupByBoxVar.get().lower()+'\n'
    else:
        groupStr = ''

    if GlobBinFuncFuncBoxVar.get() != '':
        binStr = 'bin-by:'+GlobBinFuncFileBoxVar.get()+':'+GlobBinFuncFuncBoxVar.get()+'\n'
    else:
        binStr=''

    splitScript = [groupStr,binStr]+splitScript[i:]

    script = ''.join(splitScript)

    w.Scrolledtext1.delete(1.0, END)
    w.Scrolledtext1.insert(1.0,script)
    w.Scrolledtext1.see(1.0)

def GlobBinFuncFileBoxChange(choice):
    global w, Maitre
    GlobBinFuncFile = Maitre.get_all_modules().index(choice)
    w.GlobBinFuncFuncBox["menu"].delete(0, "end")
    for entry in ['']+Maitre.get_func_name(GlobBinFuncFile):
        w.GlobBinFuncFuncBox["menu"].add_command(label=entry, command=lambda value=entry: GlobBinFuncFuncBoxVar.set(value))

def ProcBoxChange(choice):
    global w, ActiveMod, Maitre
    ActiveMod = Maitre.get_all_modules().index(choice)
    w.FuncBox["menu"].delete(0, "end")
    for entry in Maitre.get_func_name(ActiveMod):
        w.FuncBox["menu"].add_command(label=entry, command=lambda value=entry: FuncBoxChange(value))

def FuncBoxChange(choice):
    global w, ActiveMod, ActiveFunc, Maitre,ArgShowEntryVar
    ActiveFunc = Maitre.get_func_name(ActiveMod).index(choice)
    FuncBoxVar.set(choice)
    argslist = Maitre.get_func_params(ActiveMod, ActiveFunc)

    shortlist = ''
    for x in argslist:
            if not(x in ["Stages","stages","Maitre","maitre","self"]):
                shortlist += x+' '

    ArgShowEntryVar.set(shortlist)

def addMeasurement():
    global script

    new_measurement = ''

    new_measurement += '#Measurement Name \n'
    new_measurement += MeasNameVar.get()
    new_measurement += '\n'

    if StructNameVar.get() != '':
        new_measurement += '#structure \n'
        new_measurement += StructNameVar.get()
        new_measurement += '\n'

    new_measurement += '#procedure \n'
    new_measurement += ProcBoxVar.get()
    new_measurement += '\n'

    new_measurement += '#Function \n'
    new_measurement += FuncBoxVar.get()
    new_measurement += '\n'

    new_measurement += '#Arguments \n'
    new_measurement += ArgEntryVar.get()
    new_measurement += '\n\n'

    scriptPreCursor  = w.Scrolledtext1.get(1.0, INSERT )
    scriptPostCursor = w.Scrolledtext1.get(INSERT , END)

    script = scriptPreCursor + new_measurement + scriptPostCursor

    w.Scrolledtext1.delete(1.0, END)
    w.Scrolledtext1.insert(1.0,script)
    w.Scrolledtext1.see(END)

def destroy_window():
    print('Stopped ScriptBuilder')
    sys.stdout.flush()

def loadScript():
    '''
    Function loads script from file
    and resets script variable and text output to new script
    '''
    global w, script

    inputFile = open(tkFileDialog.askopenfilename(),'r')
    script = inputFile.read()
    inputFile.close()
    w.Scrolledtext1.delete(1.0, END)
    w.Scrolledtext1.insert(1.0,script)

def saveScript():
    '''
    Function updates script variable from text-widget and saves it to file
    '''
    global w, script

    outputFile = open(tkFileDialog.asksaveasfilename(),'w')
    script = w.Scrolledtext1.get(1.0, END)
    outputFile.write(script)
    outputFile.close()


def init(top, gui, maitre, *args, **kwargs):
    global w, top_level, root, Maitre
    Maitre = maitre
    w = gui
    top_level = top
    root = top

def destroy_window():
    # Function which closes the window.
    global top_level
    top_level.destroy()
    top_level = None

if __name__ == '__main__':
    #import prober.classes.ScriptBuilderGUI as ScriptBuilderGUI
    import prober.classes.maitre as maitre

    Maitre = maitre.Maitre()

    #ScriptBuilderGUI.vp_start_gui(Maitre)
    
    import time
    import imp
    
    while True:
        ScriptBuilderGUI = imp.load_source("ScriptBuilderGUI", "./prober/classes/ScriptBuilderGUI.py")
        ScriptBuilderGUI.vp_start_gui(Maitre)
        time.sleep(3)
    
    
