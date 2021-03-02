#! /usr/bin/env python
#
# GUI module generated by PAGE version 4.9
# In conjunction with Tcl version 8.6
#    Dec 13, 2017 02:19:07 PM
import sys

try:
    from tkinter import *
except ImportError:
    from tkinter import *

try:
    import tkinter.ttk
    py3 = 0
except ImportError:
    import tkinter.ttk as ttk
    py3 = 1

import ScriptBuilder

def vp_start_gui(Maitre):
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = Tk()
    ScriptBuilder.set_Tk_var()
    top = ScriptBuilderGUI(root, Maitre)
    ScriptBuilder.init(root, top, Maitre)
    root.mainloop()

w = None
def create_ScriptBuilder(w_new, Maitre, *args, **kwargs):
    '''Starting point when module is imported by another program.'''
    global w
    w = w_new
    ScriptBuilder.set_Tk_var()
    top = ScriptBuilderGUI (w, Maitre)
    ScriptBuilder.init(w, top, Maitre)
    return (w, top)

def destroy_ScriptBuilder():
    global w
    w.destroy()
    w = None


class ScriptBuilderGUI:
    def __init__(self, top=None, Maitre=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''

        self.Maitre = Maitre

        _bgcolor = '#000000'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#d9d9d9' # X11 color: 'gray85'
        self.style = tkinter.ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("1000x600+459+11")
        top.title("Script Builder")

        #TEXTBOX
        self.Scrolledtext1 = ScrolledText(top)
        self.Scrolledtext1.place(relx=0.55, rely=0.03, relheight=0.8
                , relwidth=0.43)
        self.Scrolledtext1.configure(font="TkTextFont")
        self.Scrolledtext1.configure(width=10)
        self.Scrolledtext1.configure(wrap=NONE)

        self.menubar = Menu(top,font="TkMenuFont")
        top.configure(menu = self.menubar)

        self.file = Menu(top,tearoff=0)
        self.menubar.add_cascade(menu=self.file,
                label="File")
        self.file.add_command(
                command=ScriptBuilder.loadScript,
                label="Load Script")
        self.file.add_command(
                command=ScriptBuilder.saveScript,
                label="Save Script")
        self.file.add_command(
                command=ScriptBuilder.destroy_window,
                label="Exit")

        self.edit = Menu(top,tearoff=0)
        self.menubar.add_cascade(menu=self.edit,
                label="Edit")
        self.edit.add_command(
                command=ScriptBuilder.searchAndReplace,
                label="Search and Replace")

        self.AddMeasFrame = LabelFrame(top)
        self.AddMeasFrame.place(relx=0.03, rely=0.04, relheight=0.9
                , relwidth=0.5)
        self.AddMeasFrame.configure(relief=GROOVE)
        self.AddMeasFrame.configure(text='''Add Measurement''')
        self.AddMeasFrame.configure(width=590)

        self.MeasNameEntry = Entry(self.AddMeasFrame)
        self.MeasNameEntry.place(relx=0.02, rely=0.05, relheight=0.06
                , relwidth=0.72)
        self.MeasNameEntry.configure(font="TkFixedFont")
        self.MeasNameEntry.configure(textvariable=ScriptBuilder.MeasNameVar)
        self.MeasNameEntry.configure(width=424)

        self.ProcBox = OptionMenu(self.AddMeasFrame,
        ScriptBuilder.ProcBoxVar,
        *self.Maitre.get_all_modules(),
        command = ScriptBuilder.ProcBoxChange
        )
        self.ProcBox.place(relx=0.02, rely=0.35, relheight=0.06, relwidth=0.72)
        self.ProcBox.configure(width=423)
        self.ProcBox.configure(takefocus="")

        self.StructEntry = Entry(self.AddMeasFrame)
        self.StructEntry.place(relx=0.02, rely=0.20, relheight=0.06
                , relwidth=0.72)
        self.StructEntry.configure(font="TkFixedFont")
        self.StructEntry.configure(textvariable=ScriptBuilder.StructNameVar)
        self.StructEntry.configure(width=424)

        self.MeasNameLabel = Label(self.AddMeasFrame)
        self.MeasNameLabel.place(relx=0.02, rely=0.00, height=21, width=114)
        self.MeasNameLabel.configure(text='''Measurement Name''')

        self.StructLabel = Label(self.AddMeasFrame)
        self.StructLabel.place(relx=0.02, rely=0.15, height=21, width=86)
        self.StructLabel.configure(text='''StructureName''')

        self.ProcLabel = Label(self.AddMeasFrame)
        self.ProcLabel.place(relx=0.02, rely=0.30, height=20, width=81)
        self.ProcLabel.configure(text='''Procedure File''')

        self.FuncLabel = Label(self.AddMeasFrame)
        self.FuncLabel.place(relx=0.02, rely=0.45, height=21, width=142)
        self.FuncLabel.configure(text='''Function to be performed''')

        self.FuncBox = OptionMenu(self.AddMeasFrame,
        ScriptBuilder.FuncBoxVar,
        *self.Maitre.get_func_name(0),
        command = ScriptBuilder.FuncBoxChange
        )
        self.FuncBox.place(relx=0.02, rely=0.50, relheight=0.06, relwidth=0.72)
        self.FuncBox.configure(width=423)
        self.FuncBox.configure(takefocus="")

        self.ArgLabel = Label(self.AddMeasFrame)
        self.ArgLabel.place(relx=0.02, rely=0.60, height=21, width=65)
        self.ArgLabel.configure(text='''Arguments''')

        self.ArgEntry = Entry(self.AddMeasFrame)
        self.ArgEntry.place(relx=0.02, rely=0.75, relheight=0.06, relwidth=0.72)
        self.ArgEntry.configure(font="TkFixedFont")
        self.ArgEntry.configure(textvariable=ScriptBuilder.ArgEntryVar)
        self.ArgEntry.configure(width=424)

        self.ArgShowEntry = Entry(self.AddMeasFrame)
        self.ArgShowEntry.place(relx=0.02, rely=0.65, relheight=0.06
                , relwidth=0.72)
        self.ArgShowEntry.configure(font="TkFixedFont")
        self.ArgShowEntry.configure(state=DISABLED)
        self.ArgShowEntry.configure(textvariable=ScriptBuilder.ArgShowEntryVar)
        self.ArgShowEntry.configure(width=424)

        self.AddMeasButton = Button(self.AddMeasFrame)
        self.AddMeasButton.place(relx=0.02, rely=0.9, height=24, width=147)
        self.AddMeasButton.configure(command=ScriptBuilder.addMeasurement)
        self.AddMeasButton.configure(pady="0")
        self.AddMeasButton.configure(text='''AddMeasurement''')
        self.AddMeasButton.configure(width=147)




# The following code is added to facilitate the Scrolled widgets you specified.
class AutoScroll(object):
    '''Configure the scrollbars for a widget.'''

    def __init__(self, master):
        #  Rozen. Added the try-except clauses so that this class
        #  could be used for scrolled entry widget for which vertical
        #  scrolling is not supported. 5/7/14.
        try:
            vsb = tkinter.ttk.Scrollbar(master, orient='vertical', command=self.yview)
        except:
            pass
        hsb = tkinter.ttk.Scrollbar(master, orient='horizontal', command=self.xview)

        #self.configure(yscrollcommand=_autoscroll(vsb),
        #    xscrollcommand=_autoscroll(hsb))
        try:
            self.configure(yscrollcommand=self._autoscroll(vsb))
        except:
            pass
        self.configure(xscrollcommand=self._autoscroll(hsb))

        self.grid(column=0, row=0, sticky='nsew')
        try:
            vsb.grid(column=1, row=0, sticky='ns')
        except:
            pass
        hsb.grid(column=0, row=1, sticky='ew')

        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        # Copy geometry methods of master  (taken from ScrolledText.py)
        if py3:
            methods = list(Pack.__dict__.keys()) | list(Grid.__dict__.keys()) \
                  | list(Place.__dict__.keys())
        else:
            methods = list(Pack.__dict__.keys()) + list(Grid.__dict__.keys()) \
                  + list(Place.__dict__.keys())

        for meth in methods:
            if meth[0] != '_' and meth not in ('config', 'configure'):
                setattr(self, meth, getattr(master, meth))

    @staticmethod
    def _autoscroll(sbar):
        '''Hide and show scrollbar as needed.'''
        def wrapped(first, last):
            first, last = float(first), float(last)
            if first <= 0 and last >= 1:
                sbar.grid_remove()
            else:
                sbar.grid()
            sbar.set(first, last)
        return wrapped

    def __str__(self):
        return str(self.master)

def _create_container(func):
    '''Creates a ttk Frame with a given master, and use this new frame to
    place the scrollbars and the widget.'''
    def wrapped(cls, master, **kw):
        container = tkinter.ttk.Frame(master)
        return func(cls, container, **kw)
    return wrapped

class ScrolledText(AutoScroll, Text):
    '''A standard Tkinter Text widget with scrollbars that will
    automatically show/hide as needed.'''
    @_create_container
    def __init__(self, master, **kw):
        Text.__init__(self, master, **kw)
        AutoScroll.__init__(self, master)

if __name__ == '__main__':
    vp_start_gui()
