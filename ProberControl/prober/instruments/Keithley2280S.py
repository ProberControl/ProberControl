import socket
import sys
import time

class Keithley2280S(object):
    '''
    This class models a DC Source Meter 2280S from Keithley.
    '''

    CURRENT_CHANNEL = 1
    def __init__(self,res_manager,address='169.254.115.242',channel=1):

        self.active = False
        self.__channel = channel

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:

            self.sock.connect((address, 5025))
            self.sock.sendall('*IDN?\n')
            print(self.sock.recv(1024))
            self.sock.sendall(':DATA:CLE:AUTO 1\n')
            self.sock.sendall(':TRAC:FEED:CONT ALW\n')
            self.sock.sendall(':TRAC:POIN 2\n')

        except Exception:

            print("Error in Connection")

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'DCSource'

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def get_voltage(self, channel = 1):
        self.sock.sendall(':SENS' + str(channel) + ':FUNC "VOLT"' + '\n')
        self.sock.sendall(':TRAC:CLE\n')
        time.sleep(0.3)
        self.sock.sendall(':DATA' + str(channel) + ':DATA? "READ,UNIT"' + '\n')
        output = self.sock.recv(1024).split(',')
        return float(output[0][:-1])

    def get_current(self, channel = 1):
        self.sock.sendall(':SENS' + str(channel) + ':FUNC "CURR"' + '\n')
        self.sock.sendall(':TRAC:CLE\n')
        time.sleep(0.3)
        self.sock.sendall(':DATA' + str(channel) + ':DATA? "READ,UNIT"' + '\n')
        output = self.sock.recv(1024).split(',')
        return float(output[0][:-1])

    def setvoltage(self, value = 0, channel = 1):
        data = ':SOUR' + str(channel) + ':VOLT ' + str(value) + '\n'
        self.sock.sendall(data)

    def setcurrent(self, value = 0, channel = 1):
        self.sock.sendall(':SOUR' + str(channel) + ':CURR ' + str(value) + '\n')

    def setovervoltage(self, value = 0, channel = 1):
        self.sock.sendall(':SOUR' + str(channel) + ':VOLT:PROT ' + str(value) + '\n')

    def setovercurrent(self, value = 0, channel = 1):
        self.sock.sendall(':SOUR' + str(channel) + ':CURR:PROT ' + str(value) + '\n')

    def setOCSwitch(self, value = 0, channel = 1):
       # self.sock.sendall('OCP '+str(channel)+','+str(value))
       return 1

    def setOutputSwitch(self, value = 0, channel = 'CH1'):
        self.sock.sendall('OUTP '+str(value)+','+str(channel) + '\n')

    def getsetvoltage(self, channel = 1):
        self.sock.sendall(':SOUR' + str(channel) + ':VOLT?' + '\n')
        return self.sock.recv(1024)

    def getsetcurrent(self, channel = 1):
        self.sock.sendall(':SOUR' + str(channel) + ':CURR?' + '\n')
        return self.sock.recv(1024)

    def getoutvoltage(self, channel = 1):
        self.get_voltage()

    def getoutcurrent(self, channel = 1):
        self.current()

    def getOCswitch(self, channel = 1):
        #self.sock.sendall('OCP? '+str(channel))
        return '1'

    def getoutswitch(self, channel = 1):
        self.sock.sendall('OUTP?' + '\n')
        return self.sock.recv(1024)

    def save_state(self, mem=1):
         self.sock.sendall('*SAV '+str(mem) + '\n')

    def recall_state(self, mem=1):
         self.sock.sendall('*RCL '+str(mem) + '\n')

    def close_connection(self):
        self.sock.close()







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
