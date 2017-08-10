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
        _runScript
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

    def set_host(self, host):
        '''Sets the host ip address, throws Exception if IP is invalid'''
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
        '''
        Accept state will continue until Client.py sends 'shutdown' command

        returns boolean for outside while loop running in main()
        '''
        accept = True
        while accept:
            # Waiting for connection from Client.py
            self.clientSock, addr = self.servSock.accept()
            print("{}: Connection Opened-> {}".format(datetime.datetime.today(), addr))
            accept = self._commandMode()

        return accept

    def _accept(self):
        self.clientSock, addr = self.servSock.accept()

    def _commandMode(self):
        '''
        Command mode will continue until user sends either 'shutdown' or 'q'
        '''
        # Client address
        addr = self.clientSock.getsockname()
        boot = False
        message = ''
        while message not in Server.break_commands:
            # Sleep for 2 seconds to avoid collisions of data between threads
            sleep(2)
            if boot:
                self._accept()

            # Wait for next command
            message = self.clientSock.recv(1024)

            # Validate the command, then send ACK to the Client.py 
            if message.split(' ')[0] in self.EXECUTABLE.keys():
                print("{}: Executing: {}".format(datetime.datetime.today(), message))
                self.clientSock.send("SINGLE Executing Command...")

                # Execute the message
                command = self._parseCommand(message)
                self._chooseThread(command)
            else:
                self.clientSock.send("SINGLE Error: No recognizable command.")

            # Reboot the connection after every execution
            boot = True

        if message == 'shutdown':
            return False
        else:
            print("{}: Connection Closed-> {}".format(datetime.datetime.today(), addr))
            return True

    def _chooseThread(self, command):
        '''Divvies up the arguments '''
        if len(command) == 1:
            t = threading.Thread(target=self.EXECUTABLE[command[0]])

        elif len(command) == 2:
            t = threading.Thread(target=self.EXECUTABLE[command[0]],
                kwargs={'filename': command[1]})
        
        t.start()

    def _parseCommand(self, command):
        '''Looks pointless now, but will come in handy later... probably'''
        command = command.split(' ')

        if len(command) == 1:
            return command
        elif len(command) == 2:
            return command

    def _sendFile(self,  filename):
        '''Sends a file to a '''
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
        '''Function that receives files from the Client.py _sendFile function'''
        with open('new_'+filename, 'wb') as f:
            fileSize = long(self.clientSock.recv(1024))
            totalRecieved = 0
            
            # Get the file in 1024 blocks
            while totalRecieved < fileSize:
                data = self.clientSock.recv(1024)
                totalRecieved += len(data)
                f.write(data)

            if fileSize != 0:
                print("Download Complete\nRecieved: {}".format(filename))
            self.clientSock.close()

    def _runScript(self, filename):
        self._executeFile(filename = 'RunScript.py', args=[filename])

    def _listAll(self):
        '''Packages the contents of the server's directory, then sends it to client'''
        package = os.path.abspath('.')+' '
        package += ' '.join([i for i in os.listdir('.')])
        self.clientSock.send(package)

    def _executeFile(self, filename='', args=()):
        '''Function for executing a python file'''
        try:
            script = __import__(filename[:-3])
            t = threading.Thread(target=script.main, args=args)
            t.start()
            self.clientSock.send("SINGLE Successful execution, thread started.")
        except Exception as e:
            print("Error: {}".format(e))
            self.clientSock.send(str(e))

    def __str__(self):
        return "Host: {}\nPort: {}".format(self.host, self.port)

if __name__ == '__main__':

    serving = True;

    while serving:
        try:
            # Add your desired IP address here, 5000 will designate the next available port
            server = Server('127.0.0.1', 5000)
            server.bind_server()
            serving = server.accept_state()
        except Exception as e:
            print("Server crashed, rebooting\n{}".format(e))

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
