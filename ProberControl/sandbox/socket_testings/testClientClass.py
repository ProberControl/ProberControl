from Client import Client
import sys

def Main():

    client = Client('127.0.0.1', 5000)
    client.connect_to_server()
    client.command_mode()

Main()