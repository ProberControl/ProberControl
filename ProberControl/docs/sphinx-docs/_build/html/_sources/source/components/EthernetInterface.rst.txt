Ethernet Interface
======

The ethernet interface allows ProberControl to act as a measurement server. It grants access to the Stages dictionary and the Maitre. The server can be configured and switched on from the GUI using the Network menu. Be adviced that no precautions have been taken to harden the software against attacks. Therefore, please make sure that if you start the server the network access to this server is controlled by other means.

The network communication is pure socket communication.

The commands that can be send to the server are ``(send_Stages,send_Maitre,execute_Stages(),execute_Maitre(),quit)``. All commands directly call the corresponding functions in the Ethernet Interface Object located in classes/EthernetInterface.py .

* ``send_Stages``: Returns a dictionary containing all available stages and their functions. The list corresponds to the information in the GUI.
* ``send_Maitre``: Returns a list of all modules in the procedure folders and their functions. The list corresponds to the information in the GUI.
* ``execute_Stages()``: Allows a client to execute a function on all tools in the dictionary. A full command should look like: execute_Stages(MLaser.setwavelength(1550)). The function's return value is send back to the client. If the tool is currently locked in the global measurement handler an error message is returned to the client.
* ``execute_Maitre()``: Allows a client to execute a function on all modules loaded in the Maitre. A full command should look like: execute_Stages(Measure.get_power(1550)). Note that Stages and Maitre arguments do not need to be send, as the DataIO class will include them as needed. The function's return value is send back to the client.
* ``quit``: Quit ends the communication to the client and frees the socket.

Example usage:
1) Open ProberControl, go to Network -> Network Config, choose a Port and Start the Server.
2) Use a network tool such as Putty to connect to ProberControl, in Putty use connection type 'raw'.
3) Send the commands in ASCI e.g. type in putty:send_Stages and ProberControl will reply with the contents of the Stages Dictionary.
4) Close the connection by sending 'quit'.

All data returned to the client are serialized using json.dumps(data). If the client is programmed in python the JSON library allows easy reconstruction of the objects.

The ethernet interface is not a free running thread. Its update() function is called periodically from the GUI.
