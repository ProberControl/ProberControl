import socket
import os
import threading
from time import sleep

# def receiveGeneralData(sock):
#     '''built initially for recieving directory listings'''

#     data = sock.recv(1024)
#     print("Received from {}".format(sock.getsockname()))

#     if data.split(' ')[0] == 'SINGLE':
#         print("\r'{}'".format(data[7:]))
#     else:
#         i = 0
#         for item in data.split(' '):
#             print("{}. {:15}".format(i, item))
#             i += 1

# # Function for recieving data
# def receiveFile(fileName, sock):
#     f = open('new_'+fileName, 'wb')

#     fileSize = long(sock.recv(1024))

#     data = sock.recv(1024)
#     totalReceived = len(data)
#     f.write(data)
#     while totalReceived < fileSize:
#         data = sock.recv(1024)
#         totalReceived += len(data)
#         f.write(data)

#     print("Download Complete\nreceived: {}".format(fileName))
#     f.close()
#     sock.close()

# Function for sending files
# def sendFile(fileName, sock):
#     if os.path.isfile(fileName):
#         with open(fileName, 'rb') as f: # read as binary
#             fileSize = os.path.getsize(fileName)

#             sock.send(str(fileSize))
#             sleep(.02)
#             bytesToSend = f.read(1024) # read only 1024 bytes at a time
#             sock.send(bytesToSend) # send over the socket
   
#             # finish reading the file
#             while bytesToSend:
#                 bytesToSend = f.read(1024)
#                 sock.send(bytesToSend)
#         print("\n{} sent to {}".format(fileName, sock.getsockname()))
#     else:
#         print("Error loading: {}".format(fileName))
    
#     sock.close()

# def parseCommand(command):
#     '''Looks pointless now, but will come in handy later... probably'''
#     command = command.split(' ')

#     if len(command) == 1:
#         return command
#     elif len(command) == 2:
#         return command

# def _chooseThread(sock, command):

#     if len(command) == 1:
#         function = EXECUTABLE[command[0]](sock)
#         t = threading.Thread(target=function)
#         t.start()
#     elif len(command) == 2:
#         t = threading.Thread(target=EXECUTABLE[command[0]], args=(command[1], sock))
#         t.start()
#     elif len(command) == 3:
#         t = threading.Thread(
#             target=functions[command[0]],
#             args=(command[1], command[2], sock)
#         )
#         t.start()

# def commandMode(sock):
#     break_commands = ['q', 'shutdown']
#     message = ''
#     server = sock.getsockname()
#     boot = False

#     while message not in break_commands:
#         if boot:
#             sock = connect()

#         # Wait for command
#         message = raw_input("\n{}-> ".format(server))

#         if message.split(' ')[0] in EXECUTABLE.keys():

#             # Send and wait for ACK
#             sock.send(message)
#             receiveGeneralData(sock)

#             # Execute the message
#             command = parseCommand(message)
#             _chooseThread(sock, command)
#             boot = True
#             # if len(command) > 1:
#             #     EXECUTABLE[command[0]](command[1], sock)
#             # else:
#             #     # Right now only calls receiveGeneralData()
#             #     EXECUTABLE[command[0]](sock)

#         elif message not in break_commands:
#             print("Error: No recognizable command.")

#     sock.send(message)
#     return False

# EXECUTABLE = {
#     'send': sendFile,
#     'receive': receiveFile,
#     'ls': receiveGeneralData,
#     'execute': receiveGeneralData
# }

#host = '128.59.87.139' # Host to the lab station
HOST = '127.0.0.1' # lookback host
PORT = 5000

def connect():
    sock = socket.socket()
    sock.connect((HOST,PORT))
    return sock

def Main():

    # Establish connection
    try:
        sock = connect()
        interaction = True
        while interaction:
            interaction = commandMode(sock)

        sock.close()
    except Exception as e:
        print("Error: {}".format(e))

if __name__ == '__main__':
    Main()