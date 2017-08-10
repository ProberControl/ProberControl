import socket

host = '128.59.87.139' # Address of the server we want to connect to
port = 5000

s = socket.socket()
s.connect((host,port))

message = raw_input("To Send: ")

while message != 'q':
    s.send(message.encode('utf-8'))
    
    data = s.recv(1024) #1024 buffer size
    
    print("Recieved: {}".format(data.decode('utf-8')))
    message = raw_input("To Send: ")
s.close()