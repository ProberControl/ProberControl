import socket
import os
import threading
import datetime
from time import sleep

# Function for recieving data
def receiveFile(fileName, sock):
    f = open('new_'+fileName, 'wb')
    fileSize = long(sock.recv(1024))
    
    data = sock.recv(1024)
    totalRecieved = len(data)

    f.write(data)
    while totalRecieved < fileSize:
        data = sock.recv(1024)
        totalRecieved += len(data)
        f.write(data)

    print("Download Complete\nRecieved: {}".format(fileName))
    f.close()
    #sock.close()

# Function for sending files
def sendFile(fileName, sock):
    if os.path.isfile(fileName):
        with open(fileName, 'rb') as f: # read as binary
            fileSize = os.path.getsize(fileName)
            sock.send(str(fileSize))
            bytesToSend = f.read(1024) # read only 1024 bytes at a time
            sock.send(bytesToSend) # send over the socket
   
            # finish reading the file
            while bytesToSend:
                bytesToSend = f.read(1024)
                sock.send(bytesToSend)
        print("{} sent to {}".format(fileName, sock.getsockname()))
    else:
        print("Error loading: {}".format(fileName))

    #sock.close()

# Function executes python files
# The files must include a main
def executeFile(fileName, sock, args=()):
    try:
        script = __import__(fileName[:-3])
        t = threading.Thread(target=script.Main, args=args)
        t.start()
        sock.send("SINGLE Successful execution, thread started.")
    except Exception as e:
        print("Error: {}".format(e))
        sock.send(str(e))

# Function sends listing of current directory
def listAll(sock):
    package = os.path.abspath('.')+' '
    package += ' '.join([i for i in os.listdir('.')])
    sock.send(package)

def parseCommand(command):
    '''Looks pointless now, but will come in handy later... probably'''
    command = command.split(' ')

    if len(command) == 1:
        return command
    elif len(command) == 2:
        return command

def commandMode(sock):
    # Client address
    addr = sock.getsockname()

    print("{}: Connection Opened-> {}".format(datetime.datetime.today(), addr))
    message = ''
    break_commands = ['q', 'shutdown']

    while message not in break_commands:
        sleep(1)
        try:
            # Wait for next command
            message = sock.recv(1024)
        except Exception:
            _reboot()

        if message.split(' ')[0] in EXECUTABLE.keys():
            print("{}: Executing: {}".format(datetime.datetime.today(), message))
            sock.send("SINGLE Executing Command...")

            #execute the message
            command = parseCommand(message)
            _chooseThread(sock, command)
        else:
            sock.send("SINGLE Error: No recognizable command.")

    if message == 'shutdown':
        return False
    else:
        #sock.close()
        print("{}: Connection Closed-> {}".format(datetime.datetime.today(), addr))
        return True

# def _reboot():
#     host = '127.0.0.1' # Changed for different machines -> $ ipconfig /all
#     port = 5000 # Arbitrary

#     s = socket.socket()
#     try:
#         s.bind((host,port))
#         s.listen(5)
#     except Exception as e:
#         print("Error: {}".format(e))


def _chooseThread(sock, command):
    if len(command) == 1:
        function = EXECUTABLE[command[0]](sock)
        t = threading.Thread(target=function)
    elif len(command) == 2:
        t = threading.Thread(target=EXECUTABLE[command[0]], args=(command[1], sock))
        t.start()
    elif len(command) == 3:
        t = threading.Thread(
            target=functions[command[0]],
            args=(command[1], command[2], sock)
        )
        t.start()

# Collection of possible functions
EXECUTABLE = {
    'receive': sendFile,
    'send': receiveFile,
    'execute': executeFile,
    'ls' : listAll
}

# Main Method
def Main():

    # Print Successful startup of server
    

    accept = True
    while accept:
        # Waiting for connection
        sock, addr = s.accept()
        accept = commandMode(sock)

    # print("{}: Server Shutdown".format(datetime.datetime.today()))
    s.close()

if __name__ == '__main__':
    Main()