import os
import threading
from time import sleep
from socket import socket

class Client(object):
    '''
    This class is designed to model a client to interact with Server.py
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
        self.EXECUTABLE = {
            'send': self.sendFile,
            'receive': self.receiveFile,
            'ls': self.receiveGeneralData,
            'execute': self.receiveGeneralData,
            'run': self.receiveGeneralData
        }

    def set_host(self, host):
        self.host = host

    def set_host(self, port):
        self.port = port

    def command_mode(self):
        self._commandMode()

    def connect_to_server(self, host='', port=''):

        self.servSock = socket()

        if (host and port):
            self.host = host
            self.port = port
            self.servSock.connect((host,port))
        elif (self.host and self.port):
            self.servSock.connect((self.host, self.port))
        else:
            raise Exception("No host or port designated.")


    def _commandMode(self):
        message = ''
        server = self.servSock.getsockname()
        boot = False

        while message not in Client.break_commands:
            if boot:
                self.connect_to_server(self.host,self.port)

            # Wait for command
            message = raw_input("\n{}-> ".format(server))
            command = self._parseCommand(message)

            if self.__inExecutables(command[0]):

                # Handshake 
                self.servSock.send(message); self.receiveGeneralData()

                # Execute the message
                command = self._parseCommand(message)
                self._chooseThread(command)
                boot = True

                # Wait 1 for command to send/receive data
                sleep(1)

            elif message not in Client.break_commands:
                print("Error: No recognizable command.")

        self.servSock.send(message)
        return False

    def __inExecutables(self, command):
        return command in self.EXECUTABLE.keys()

    def sendFile(self, fileName):
        '''
        Method for sending data to the connected server
        :param fileName: the specified file to send
        :type fileName: String
        '''
        if os.path.isfile(fileName):
            with open(fileName, 'rb') as f: # read as binary

                # Send the filesize to server
                fileSize = str(os.path.getsize(fileName))
                self.servSock.send(fileSize)

                # Wait 1 to avoid collisions
                sleep(.01)
                
                # finish reading and sending the file
                bytesToSend = f.read(1024)
                while bytesToSend:
                    self.servSock.send(bytesToSend)
                    bytesToSend = f.read(1024)

            # Successful transfer of data
            print("\n{} sent to {}".format(fileName, self.servSock.getsockname()))
        else:
            print("Error loading: {}".format(fileName))
            self.servSock.send(str(0)) # waiting for filesize on the other end
        
        self.servSock.close()

    def _parseCommand(self, command):
        '''Looks pointless now, but will come in handy later... probably'''
        command = command.split(' ')

        if len(command) == 1:
            return command
        elif len(command) == 2:
            return command

    def _chooseThread(self, command):

        if len(command) == 1:
            function = self.EXECUTABLE[command[0]]()
            t = threading.Thread(target=function)
        elif len(command) == 2:
            t = threading.Thread(target=self.EXECUTABLE[command[0]], args=[command[1]])

        t.start()

    def receiveGeneralData(self, information=''):
        '''built initially for recieving directory listings'''

        data = self.servSock.recv(1024)
        print("Received from {}".format(self.servSock.getsockname()))

        if data.split(' ')[0] == 'SINGLE':
            print("\r\r'{}'".format(data[7:]))
        else:
            i = 0
            for item in data.split(' '):
                print("{}. {:15}".format(i, item))
                i += 1

    def receiveFile(self, fileName):
        
        with open('new_'+fileName, 'wb') as f:
            fileSize = long(self.servSock.recv(1024))

            data = self.servSock.recv(1024)
            totalReceived = len(data)
            f.write(data)
            while totalReceived < fileSize:
                data = self.servSock.recv(1024)
                totalReceived += len(data)
                f.write(data)

            print("Download Complete\nreceived: {}".format(fileName))

        self.servSock.close()

    def __str__(self):
        return "Client: {}\nPort: {}".format(self.host, self.port)

if __name__ == '__main__':

    client = Client('127.0.0.1', 5000)
    client.connect_to_server()
    client.command_mode()