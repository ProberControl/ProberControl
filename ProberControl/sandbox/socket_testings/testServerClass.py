from Server import Server
import sys

def Main():

    server = Server('127.0.0.1', 5000)
    print(server)

    server.bind_server()
    server.accept_state()

Main()