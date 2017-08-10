import socket

host = '10.0.75.1' # This is the lookback address
port = 5000

s = socket.socket()
s.bind((host, port))

s.listen(1) #Takes the number of connections
c, addr = s.accept() #c is channel
print("connection from: {}".format(str(addr)))

while True:
    data = c.recv(1024)
    if data:
        print("From connected user: {}".format(data))
        data = str(data.decode('utf-8')).upper()
        print("Sending: {}".format(data))
        c.send(data.encode('utf-8'))

c.close()