#import serial
#import visa

class HP6624A(object):
    '''
    This class models a MULTIPLE OUTPUT LINEAR SYSTEM.
    '''
    def __init__(self,res_manager, address='GPIB0::1::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object 
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False

        self.gpib = res_manager.open_resource(address)
        self.setvoltage(0,1)
        self.setvoltage(0,2)
        self.setvoltage(0,3)
        self.setvoltage(0,4)

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'DCSource'

    def whatCanI(self):
        ''':returns: instrument attributes'''
        return 'DC'

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def setvoltage(self, value = 0, channel = 1):    
        '''
        Set the voltage

        :param value: Specified voltage to set channel to
        :type value: Integer
        :param channel: Specified channel to set
        :type channel: Integer
        '''
        self.gpib.write('VSET '+str(channel)+','+str(value))

    def setcurrent(self, value = 0, channel = 1):
        '''
        Set the current

        :param value: Specified current to set channel to
        :type value: Integer
        :param channel: Specified channel to set
        :type channel: Integer
        '''    
        self.gpib.write('ISET '+str(channel)+','+str(value))

    def setovervoltage(self, value = 0, channel = 1):
        '''
        Set the over-voltage

        :param value: Specified over-voltage to set channel to
        :type value: Integer
        :param channel: Specified channel to set
        :type channel: Integer
        ''' 
        self.gpib.write('OVSET '+str(channel)+','+str(value))

    def setOCSwitch(self, value = 0, channel = 1):
        '''
        Set the OC Switch

        :param value: Specified value to set channel to
        :type value: Integer
        :param channel: Specified channel to set
        :type channel: Integer
        ''' 
        self.gpib.write('OCP '+str(channel)+','+str(value))
        
    def setOutputSwitch(self, value = 0, channel = 1):
        '''
        Set the output Switch

        :param value: Specified output value to set channel to
        :type value: Integer
        :param channel: Specified channel to set
        :type channel: Integer
        '''     
        self.gpib.write('OUT '+str(channel)+','+str(value))

    def getsetvoltage(self, channel = 1):
        '''
        Queries the voltage of a specified channel

        :param channel: Specified channel to query
        :type channel: Integer
        :returns: Integer
        '''
        self.gpib.write('VSET? '+str(channel))
        return self.gpib.read()

    def getsetcurrent(self, channel = 1):
        '''
        Queries the current of a specified channel

        :param channel: Specified channel to query
        :type channel: Integer
        :returns: Integer
        '''
        self.gpib.write('ISET? '+str(channel))
        return self.gpib.read()

    def getoutvoltage(self, channel = 1):
        '''
        Queries the voltage of a specified channel

        :param channel: Specified channel to query
        :type channel: Integer
        :returns: Integer
        '''
        self.gpib.write('VOUT? '+str(channel))
        return self.gpib.read()

    def getoutcurrent(self, channel = 1):
        '''
        Queries the out-current of a specified channel

        :param channel: Specified channel to query
        :type channel: Integer
        :returns: Integer
        '''
        self.gpib.write('IOUT? '+str(channel))
        return self.gpib.read()

    def getOCswitch(self, channel = 1):
        '''
        Queries the OC switch of a specified channel

        :param channel: Specified channel to query
        :type channel: Integer
        :returns: Integer
        '''
        self.gpib.write('OCP? '+str(channel))
        return self.gpib.read()

    def getoutswitch(self, channel = 1):
        '''
        Queries the out switch of a specified channel

        :param channel: Specified channel to query
        :type channel: Integer
        :returns: Integer
        '''
        self.gpib.write('OUT? '+str(channel))
        return self.gpib.read()

    def save_state(self, mem=1):
        '''
        Stores state within non-volatile memory

        :param mem: Specified space to write to
        :type mem: Integer
        '''
        self.gpib.write('STO '+str(mem))

    def recall_state(self, mem=1):
        '''
        Loads stored state from specified memory location

        :param mem: Specified space to query
        :type mem: Integer
        '''
        self.gpib.write('RCL '+str(mem))

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'HP6624A'    


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
