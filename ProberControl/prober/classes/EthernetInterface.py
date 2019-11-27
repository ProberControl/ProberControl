import socket
import select
import json
import os
import threading
import datetime
import inspect
from time import sleep
from .DataIO import DataIO


# Getting an instance of the Global_MeasureHandler singleton object
from ..classes.Global_MeasureHandler import Global_MeasureHandler as g
# Getting Global_MeasureHandler (singleton)instance; Do not change this!
gh = g()

class Eth_Server():
    '''
    The Ethernet Interface presents the Maitre and Stages-Dictionary to the outside.
    Any return value from executed functions are returned to the client.
    '''

    def __init__(self,Stages,Maitre):
        self.Stages = Stages
        self.Maitre = Maitre
        self.port   = 8888
        self.running = False

        self.read_list = []
        self.commands = (self.send_Stages,self.send_Maitre,self.execute_Stages,self.execute_Maitre,self.quit)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind(('', self.port))
        self.server_socket.listen(5)
        self.read_list = [self.server_socket]
        self.running = True
        print("Listening on port "+str(self.port))

    def stop_server(self):
        self.server_socket.close()
        self.running = False
        print("Stopped Server")

    def get_running(self):
        return self.running

    def update(self):
        '''
        Checks whether a client wants to connect and reacts on commands.
        '''
        if(self.running):
            readable, writable, errored = select.select(self.read_list, [], [],0.1)
            for s in readable:
                if s is self.server_socket:
                    client_socket, address = self.server_socket.accept()
                    self.read_list.append(client_socket)
                    print("Connection from", address)

                else:
                    data = s.recv(1024)

                    if data:
                        for func in self.commands:
                            if func.__name__ in data:
                                func(s,data)
                                break
                    else:
                        s.close()
                        self.read_list.remove(s)


    def set_port(self,port):
        self.port = int(port)

    def get_port(self):
        return self.port

    def quit(self,s,data):
        '''
        Closes Client Communication Socket
        '''
        s.close()
        self.read_list.remove(s)

    def send_Maitre(self,s,data):
        proc_book = {}

        for i,elem in enumerate(self.Maitre.get_all_modules()):
            func_names = []
            for func in self.Maitre.get_func_name(i):
                if func[0] != '_':
                    func_names.append(func)
            proc_book[elem] = func_names

        json_book = json.dumps(proc_book)
        s.send(json_book)

    def send_Stages(self,s,data):
        stage_book = {}
        for k,v in self.Stages.items():
            func_names = []
            for func in inspect.getmembers(self.Stages[k],inspect.ismethod):
                if func[0][0] != '_':
                    func_names.append(func[0])
            stage_book[k] = func_names

        json_book = json.dumps(stage_book)
        s.send(json_book)

    def execute_Maitre(self,s,data):
        (module_name,func_name,arg_string) = self.split_data(data)

        try:
            Mod_Index  = self.Maitre.get_all_modules().index(module_name)
        except:
            s.send("ERROR: Invalid Procedure Module")

        Func_Index = -1
        for i,elem in enumerate(self.Maitre.get_func_name(Mod_Index)):
            if elem == func_name:
                Func_Index = i
                break

        if Func_Index == -1:
            s.send("Function could not be found")
            return

        ArgList = DataIO.parameter_prep(Stages = self.Stages, Maitre = self.Maitre,arg_string = arg_string, func_parameter_list = self.Maitre.get_func_params(Mod_Index,Func_Index))

        data =  self.Maitre.execute_func(Mod_Index,Func_Index,ArgList)

        json_book = json.dumps(data)
        s.send(json_book)

    def execute_Stages(self,s,data):

        (stage,func_name,arg_string) = self.split_data(data)

        func_handle = ''
        for func in inspect.getmembers(self.Stages[stage],inspect.ismethod):
            if func[0] == func_name:
                func_handle = func[1]
                break

        if func_handle == '':
            s.send("Function could not be found")
            return


        ArgList = DataIO.parameter_prep(Stages = self.Stages, Maitre = self.Maitre,arg_string = arg_string, func_parameter_list = inspect.getargspec(func_handle)[0])

        # check if instrument has been locked
        bounded_method = func_handle
        if g().is_locked(bounded_method.__self__):
            s.send('Cannot execute method {} : instrument locked by running script.'.format(bounded_method))
        else:
            json_book = json.dumps(bounded_method(*ArgList))
            s.send(json_book)

    def split_data(self,data):
        func_string = data[data.find('(')+1:data.rfind(')')]

        stage = func_string[:func_string.find('.')]
        func_name = func_string[func_string.find('.')+1:func_string.find('(')]
        arg_string = func_string[func_string.find('(')+1:func_string.rfind(')')]

        return (stage,func_name,arg_string)

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

class Eth_GUI():
    def __init__(self, top=None, eth_interface = None):

        self.top = top

        # Store Ethernet interface locally
        self.eth_interface = eth_interface

        # Preparing GUI variables
        self.RunningVar      = BooleanVar()
        self.PortEntryVar    = StringVar()

        # Setting up Window
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
        self.style.map('.',background=[('selected', _compcolor), ('active',_ana2color)])

        top.geometry("482x212+593+264")
        top.title("Ethernet Interface")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")



        self.style.configure('TNotebook.Tab', background=_bgcolor)
        self.style.configure('TNotebook.Tab', foreground=_fgcolor)
        self.style.map('TNotebook.Tab', background=[('selected', _compcolor), ('active',_ana2color)])
        self.RiderTab = tkinter.ttk.Notebook(top)
        self.RiderTab.place(relx=0.02, rely=0.05, relheight=0.78, relwidth=0.94)
        self.RiderTab.configure(width=454)
        self.RiderTab.configure(takefocus="")
        self.RiderTab_t1 = tkinter.ttk.Frame(self.RiderTab)
        self.RiderTab.add(self.RiderTab_t1, padding=3)
        self.RiderTab.tab(0, text="Server",underline="-1",)

        self.PortLabel = Label(self.RiderTab_t1)
        self.PortLabel.place(relx=0.04, rely=0.14, height=21, width=28)
        self.PortLabel.configure(activebackground="#f9f9f9")
        self.PortLabel.configure(activeforeground="black")
        self.PortLabel.configure(background="#d9d9d9")
        self.PortLabel.configure(disabledforeground="#a3a3a3")
        self.PortLabel.configure(foreground="#000000")
        self.PortLabel.configure(highlightbackground="#d9d9d9")
        self.PortLabel.configure(highlightcolor="black")
        self.PortLabel.configure(text='''Port''')

        self.PortEntry = Entry(self.RiderTab_t1)
        self.PortEntry.place(relx=0.22, rely=0.14, relheight=0.14, relwidth=0.72)

        self.PortEntry.configure(background="white")
        self.PortEntry.configure(disabledforeground="#a3a3a3")
        self.PortEntry.configure(font="TkFixedFont")
        self.PortEntry.configure(foreground="#000000")
        self.PortEntry.configure(highlightbackground="#d9d9d9")
        self.PortEntry.configure(highlightcolor="black")
        self.PortEntry.configure(insertbackground="black")
        self.PortEntry.configure(selectbackground="#c4c4c4")
        self.PortEntry.configure(selectforeground="black")
        self.PortEntry.configure(textvariable=self.PortEntryVar)
        self.PortEntry.configure(width=324)

        self.StartButton = Button(self.RiderTab_t1)
        self.StartButton.place(relx=0.22, rely=0.71, height=24, width=70)
        self.StartButton.configure(activebackground="#d9d9d9")
        self.StartButton.configure(activeforeground="#000000")
        self.StartButton.configure(background="#d9d9d9")
        self.StartButton.configure(command=self.start_server)
        self.StartButton.configure(disabledforeground="#a3a3a3")
        self.StartButton.configure(foreground="#000000")
        self.StartButton.configure(highlightbackground="#d9d9d9")
        self.StartButton.configure(highlightcolor="black")
        self.StartButton.configure(pady="0")
        self.StartButton.configure(text='''Start Server''')

        self.StopButton = Button(self.RiderTab_t1)
        self.StopButton.place(relx=0.42, rely=0.71, height=24, width=67)
        self.StopButton.configure(activebackground="#d9d9d9")
        self.StopButton.configure(activeforeground="#000000")
        self.StopButton.configure(background="#d9d9d9")
        self.StopButton.configure(command=self.stop_server)
        self.StopButton.configure(disabledforeground="#a3a3a3")
        self.StopButton.configure(foreground="#000000")
        self.StopButton.configure(highlightbackground="#d9d9d9")
        self.StopButton.configure(highlightcolor="black")
        self.StopButton.configure(pady="0")
        self.StopButton.configure(text='''Stop Server''')

        self.RunningLabel = Label(self.RiderTab_t1)
        self.RunningLabel.place(relx=0.04, rely=0.43, height=21, width=51)
        self.RunningLabel.configure(background="#d9d9d9")
        self.RunningLabel.configure(disabledforeground="#a3a3a3")
        self.RunningLabel.configure(foreground="#000000")
        self.RunningLabel.configure(text='''Running''')

        self.RunningCheck = Checkbutton(self.RiderTab_t1)
        self.RunningCheck.place(relx=0.22, rely=0.43, relheight=0.18, relwidth=0.06)
        self.RunningCheck.configure(activebackground="#d9d9d9")
        self.RunningCheck.configure(activeforeground="#000000")
        self.RunningCheck.configure(background="#d9d9d9")
        self.RunningCheck.configure(disabledforeground="#a3a3a3")
        self.RunningCheck.configure(foreground="#000000")
        self.RunningCheck.configure(highlightbackground="#d9d9d9")
        self.RunningCheck.configure(highlightcolor="black")
        self.RunningCheck.configure(justify=LEFT)
        self.RunningCheck.configure(state=DISABLED)
        self.RunningCheck.configure(variable=self.RunningVar)

        self.ExitButton = Button(top)
        self.ExitButton.place(relx=0.83, rely=0.85, height=24, width=57)
        self.ExitButton.configure(activebackground="#d9d9d9")
        self.ExitButton.configure(activeforeground="#000000")
        self.ExitButton.configure(background="#d9d9d9")
        self.ExitButton.configure(command=self.exit_window)
        self.ExitButton.configure(disabledforeground="#a3a3a3")
        self.ExitButton.configure(foreground="#000000")
        self.ExitButton.configure(highlightbackground="#d9d9d9")
        self.ExitButton.configure(highlightcolor="black")
        self.ExitButton.configure(pady="0")
        self.ExitButton.configure(text='''Exit''')
        self.ExitButton.configure(width=57)

        self.get_status()

    def get_status(self):
        self.RunningVar.set(self.eth_interface.get_running())
        self.PortEntryVar.set(self.eth_interface.get_port())

    def start_server(self):
        self.eth_interface.set_port(self.PortEntryVar.get())
        self.eth_interface.start_server()
        self.get_status()

    def stop_server(self):
        self.eth_interface.stop_server()
        self.get_status()

    def exit_window(self):
        self.top.destroy()
