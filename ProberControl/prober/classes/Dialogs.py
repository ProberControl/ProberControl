'''
Module Contains Dialogs for User Interaction
'''

import sys
import math

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

class Search_and_Replace(Toplevel):
        def __init__(self, parent, textWidget):
            self.text = textWidget

            Toplevel.__init__(self, parent)
            self.transient(parent)

            self.SearchEntryVar = StringVar()
            self.ReplaceEntryVar = StringVar()

            '''This class configures and populates the toplevel window.
               top is the toplevel containing window.'''
            _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
            _fgcolor = '#000000'  # X11 color: 'black'
            _compcolor = '#d9d9d9' # X11 color: 'gray85'
            _ana1color = '#d9d9d9' # X11 color: 'gray85'
            _ana2color = '#d9d9d9' # X11 color: 'gray85'
            self.style = tkinter.ttk.Style()
            if sys.platform == "win32":
                self.style.theme_use('winnative')
            self.style.configure('.',background=_bgcolor)
            self.style.configure('.',foreground=_fgcolor)
            self.style.configure('.',font="TkDefaultFont")
            self.style.map('.',background=
                [('selected', _compcolor), ('active',_ana2color)])

            self.geometry("482x188+694+307")
            self.title("Search and Replace")
            self.configure(background="#d9d9d9")



            self.style.configure('TNotebook.Tab', background=_bgcolor)
            self.style.configure('TNotebook.Tab', foreground=_fgcolor)
            self.style.map('TNotebook.Tab', background=
                [('selected', _compcolor), ('active',_ana2color)])
            self.RiderTab = tkinter.ttk.Notebook(self)
            self.RiderTab.place(relx=0.02, rely=0.05, relheight=0.88, relwidth=0.94)
            self.RiderTab.configure(width=454)
            self.RiderTab.configure(takefocus="")
            self.RiderTab_t1 = tkinter.ttk.Frame(self.RiderTab)
            self.RiderTab.add(self.RiderTab_t1, padding=3)
            self.RiderTab.tab(0, text="Replace",underline="-1",)

            self.SearchLabel = Label(self.RiderTab_t1)
            self.SearchLabel.place(relx=0.04, rely=0.14, height=21, width=47)
            self.SearchLabel.configure(background="#d9d9d9")
            self.SearchLabel.configure(disabledforeground="#a3a3a3")
            self.SearchLabel.configure(foreground="#000000")
            self.SearchLabel.configure(text='''Search''')

            self.ReplaceLabel = Label(self.RiderTab_t1)
            self.ReplaceLabel.place(relx=0.04, rely=0.43, height=21, width=47)
            self.ReplaceLabel.configure(background="#d9d9d9")
            self.ReplaceLabel.configure(disabledforeground="#a3a3a3")
            self.ReplaceLabel.configure(foreground="#000000")
            self.ReplaceLabel.configure(text='''Replace''')

            self.SearchEntry = Entry(self.RiderTab_t1)
            self.SearchEntry.place(relx=0.22, rely=0.14, relheight=0.14
                    , relwidth=0.72)
            self.SearchEntry.configure(background="white")
            self.SearchEntry.configure(disabledforeground="#a3a3a3")
            self.SearchEntry.configure(font="TkFixedFont")
            self.SearchEntry.configure(foreground="#000000")
            self.SearchEntry.configure(insertbackground="black")
            self.SearchEntry.configure(textvariable=self.SearchEntryVar)
            self.SearchEntry.configure(width=324)

            self.ReplaceEntry = Entry(self.RiderTab_t1)
            self.ReplaceEntry.place(relx=0.22, rely=0.43, relheight=0.14
                    , relwidth=0.72)
            self.ReplaceEntry.configure(background="white")
            self.ReplaceEntry.configure(disabledforeground="#a3a3a3")
            self.ReplaceEntry.configure(font="TkFixedFont")
            self.ReplaceEntry.configure(foreground="#000000")
            self.ReplaceEntry.configure(insertbackground="black")
            self.ReplaceEntry.configure(textvariable=self.ReplaceEntryVar)
            self.ReplaceEntry.configure(width=324)

            self.SearchAllButton = Button(self.RiderTab_t1)
            self.SearchAllButton.place(relx=0.22, rely=0.61, height=24, width=69)
            self.SearchAllButton.configure(activebackground="#d9d9d9")
            self.SearchAllButton.configure(activeforeground="#000000")
            self.SearchAllButton.configure(background="#d9d9d9")
            self.SearchAllButton.configure(command=self.searchAll)
            self.SearchAllButton.configure(disabledforeground="#a3a3a3")
            self.SearchAllButton.configure(foreground="#000000")
            self.SearchAllButton.configure(highlightbackground="#d9d9d9")
            self.SearchAllButton.configure(highlightcolor="black")
            self.SearchAllButton.configure(pady="0")
            self.SearchAllButton.configure(text='''Search All''')

            self.ReplaceAllButton = Button(self.RiderTab_t1)
            self.ReplaceAllButton.place(relx=0.42, rely=0.61, height=24, width=69)
            self.ReplaceAllButton.configure(activebackground="#d9d9d9")
            self.ReplaceAllButton.configure(activeforeground="#000000")
            self.ReplaceAllButton.configure(background="#d9d9d9")
            self.ReplaceAllButton.configure(command=self.replaceAll)
            self.ReplaceAllButton.configure(disabledforeground="#a3a3a3")
            self.ReplaceAllButton.configure(foreground="#000000")
            self.ReplaceAllButton.configure(highlightbackground="#d9d9d9")
            self.ReplaceAllButton.configure(highlightcolor="black")
            self.ReplaceAllButton.configure(pady="0")
            self.ReplaceAllButton.configure(text='''Replace All''')

            self.SearchNextButton = Button(self.RiderTab_t1)
            self.SearchNextButton.place(relx=0.22, rely=0.83, height=24, width=69)
            self.SearchNextButton.configure(activebackground="#d9d9d9")
            self.SearchNextButton.configure(activeforeground="#000000")
            self.SearchNextButton.configure(background="#d9d9d9")
            self.SearchNextButton.configure(command=self.searchNext)
            self.SearchNextButton.configure(disabledforeground="#a3a3a3")
            self.SearchNextButton.configure(foreground="#000000")
            self.SearchNextButton.configure(highlightbackground="#d9d9d9")
            self.SearchNextButton.configure(highlightcolor="black")
            self.SearchNextButton.configure(pady="0")
            self.SearchNextButton.configure(text='''Search Next''')

            self.ReplaceNextButton = Button(self.RiderTab_t1)
            self.ReplaceNextButton.place(relx=0.42, rely=0.83, height=24, width=69)
            self.ReplaceNextButton.configure(activebackground="#d9d9d9")
            self.ReplaceNextButton.configure(activeforeground="#000000")
            self.ReplaceNextButton.configure(background="#d9d9d9")
            self.ReplaceNextButton.configure(command=self.replaceNext)
            self.ReplaceNextButton.configure(disabledforeground="#a3a3a3")
            self.ReplaceNextButton.configure(foreground="#000000")
            self.ReplaceNextButton.configure(highlightbackground="#d9d9d9")
            self.ReplaceNextButton.configure(highlightcolor="black")
            self.ReplaceNextButton.configure(pady="0")
            self.ReplaceNextButton.configure(text='''Replace Next''')

            self.Button2 = Button(self.RiderTab_t1)
            self.Button2.place(relx=0.62, rely=0.61, height=24, width=67)
            self.Button2.configure(activebackground="#d9d9d9")
            self.Button2.configure(activeforeground="#000000")
            self.Button2.configure(background="#d9d9d9")
            self.Button2.configure(command=self.exit)
            self.Button2.configure(disabledforeground="#a3a3a3")
            self.Button2.configure(foreground="#000000")
            self.Button2.configure(highlightbackground="#d9d9d9")
            self.Button2.configure(highlightcolor="black")
            self.Button2.configure(pady="0")
            self.Button2.configure(text='''Cancel''')
            self.Button2.configure(width=67)

        def replaceNext(self):
            if not( 'search' in self.text.tag_names() ):
                (pos,countVar) = self.searchNext()

            if 'search' in self.text.tag_names():
                start = self.text.tag_ranges('search')[0]
                stop = self.text.tag_ranges('search')[1]

                self.text.delete(start,stop)
                self.text.insert(start,self.ReplaceEntryVar.get())

        def searchNext(self):
            # Restart on top if  cursor is on the bottom
            if math.floor(float(self.text.index(END)))-1 == math.floor(float(self.text.index(INSERT))):
                self.text.mark_set(INSERT, '1.0')

            # Delete all tags
            for tag in self.text.tag_names():
                self.text.tag_delete(tag)

            #Prepare search variable + create marker
            countVar = StringVar()
            self.text.tag_configure("search", background="green")

            # Search
            pos = self.text.search( self.SearchEntryVar.get(), INSERT , stopindex="end", count=countVar)
            if not pos:
                    return

            # Highlight
            self.text.tag_add("search", pos, "%s + %sc" % (pos, countVar.get()))

            # Set cursor behind found instance
            self.text.mark_set(INSERT, "%s + %sc" % (pos, countVar.get()))

            return (pos,countVar)

        def searchAll(self):
            countVar = StringVar()
            self.text.tag_configure("search", background="green")

            pos = "1.0"
            while(True):
                pos = self.text.search( self.SearchEntryVar.get(), pos , stopindex="end", count=countVar)
                if not pos:
                    break

                self.text.tag_add("search", pos, "%s + %sc" % (pos, countVar.get()))
                pos =  "%s + %sc" % (pos, countVar.get())

        def replaceAll(self):
            script = self.text.get(1.0 , END)

            script = script.replace(self.SearchEntryVar.get(),self.ReplaceEntryVar.get())

            self.text.delete(1.0, END)
            self.text.insert(1.0,script)
            self.text.see(END)

        def exit(self):
            for tag in self.text.tag_names():
                self.text.tag_delete(tag)

            self.destroy()
