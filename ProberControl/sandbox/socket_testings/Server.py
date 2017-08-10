from socket import socket
import os
import threading
import datetime
from time import sleep

class Server(object):
    '''
    This class is designed to model a server that
    can send, receive, and execute files and data

    Methods:
        _sendFile
        _receiveFile
        _executeFile
        _listAll
    '''
    break_commands = ['q', 'shutdown']

    def __init__(self, host='', port=''):
        self.host = host
        self.port = port
        self.servSock = socket()
        self.EXECUTABLE = {
            'receive': self._sendFile,
            'send': self._receiveFile,
            'execute': self._executeFile,
            'ls' : self._listAll,
            'run': self._runScript
        }

    def __str__(self):
        return "Host: {}\nPort: {}".format(self.host, self.port)

    def set_host(self, host):
        '''
        :param host: Desired host to serve from i.e. 127.0.0.1
        :type host: String
        :raises: Exception
        '''
        if len(host.split('.')) != 4:
            raise Exception("Invalid Host")
        else:
            self.host = host

    def set_port(self, port):
        self.port = port

    def bind_server(self):
        '''Binds the server to the host/port combo'''
        try:
            self.servSock.bind((self.host,self.port))
            self.servSock.listen(5)
            print("{}: Server Running".format(datetime.datetime.today()))
        except Exception as e:
            print("Error: {}".format(e))

    def accept_state(self):
        accept = True
        while accept:
            # Waiting for connection
            self.clientSock, addr = self.servSock.accept()
            print("{}: Connection Opened-> {}".format(datetime.datetime.today(), addr))
            accept = self._commandMode()

    def _accept(self):
        self.clientSock, addr = self.servSock.accept()

    def _commandMode(self):

        # Client address
        addr = self.clientSock.getsockname()
        boot = False
        message = ''
        while message not in Server.break_commands:
            sleep(2)
            if boot:
                self._accept()

            # Wait for next command
            message = self.clientSock.recv(1024)

            if message.split(' ')[0] in self.EXECUTABLE.keys():
                print("{}: Executing: {}".format(datetime.datetime.today(), message))
                self.clientSock.send("SINGLE Executing Command...")

                #execute the message
                command = self._parseCommand(message)
                self._chooseThread(command)
            else:
                self.clientSock.send("SINGLE Error: No recognizable command.")
            boot = True

        if message == 'shutdown':
            return False
        else:
            print("{}: Connection Closed-> {}".format(datetime.datetime.today(), addr))
            return True

    def _chooseThread(self, command):

        if len(command) == 1:
            t = threading.Thread(target=self.EXECUTABLE[command[0]])

        elif len(command) == 2:
            t = threading.Thread(target=self.EXECUTABLE[command[0]],
                kwargs={'filename': command[1]})

        # elif len(command) == 3:
        #     t = threading.Thread(target=functions[command[0]],
        #         args=(command[1], command[2]))
        
        t.start()

    def _parseCommand(self, command):
        '''Looks pointless now, but will come in handy later... probably'''
        command = command.split(' ')

        if len(command) == 1:
            return command
        elif len(command) == 2:
            return command

    def _sendFile(self,  filename):
        if os.path.isfile(filename):
            with open(filename, 'rb') as f: # read as binary
                fileSize = os.path.getsize(filename)
                self.clientSock.send(str(fileSize))
                sleep(.1)
                bytesToSend = f.read(1024) # read only 1024 bytes at a time
                self.clientSock.send(bytesToSend) # send over the socket
       
                # finish reading the file
                while bytesToSend:
                    bytesToSend = f.read(1024)
                    self.clientSock.send(bytesToSend)
            print("{} sent to {}".format(filename, self.clientSock.getsockname()))
        else:
            print("Error loading: {}".format(filename))


    def _receiveFile(self, filename=''):

        with open('new_'+filename, 'wb') as f:
            fileSize = long(self.clientSock.recv(1024))
            totalRecieved = 0
            
            while totalRecieved < fileSize:
                data = self.clientSock.recv(1024)
                totalRecieved += len(data)
                f.write(data)

            if fileSize != 0:
                print("Download Complete\nRecieved: {}".format(filename))
            self.clientSock.close()

    def _runScript(self, filename):
        self._executeFile(filename = 'RunScript.py', args=filename)

    def _listAll(self):
        '''Packages the contents of the server's directory, then sends it to client'''
        package = os.path.abspath('.')+' '
        package += ' '.join([i for i in os.listdir('.')])
        self.clientSock.send(package)

    def _executeFile(self, filename='', args=()):
        try:
            script = __import__(filename[:-3])
            t = threading.Thread(target=script.main, args=args)
            t.start()
            self.clientSock.send("SINGLE Successful execution, thread started.")
        except Exception as e:
            print("Error: {}".format(e))
            self.clientSock.send(str(e))