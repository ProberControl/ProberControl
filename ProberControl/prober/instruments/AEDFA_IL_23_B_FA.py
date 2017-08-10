import serial
from time import sleep

class AEDFA_IL_23_B_FA(object):
    '''
    This class models an Amonics EDFA.

    .. :warning: Baudrate in device needs to be set to 115200
    '''
    def __init__(self,ser):
        '''
        Constructor method for AEDFA instrument

        :param ser: the Serial object corresponding to the EDFAs port
        :type ser: Serial object
        '''
        self.ser = ser
        self.active = False

        # request some info from controller to trigger the reading process
        self.ser.flushInput()
        self.ser.flushOutput()

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'EDFA'
        
    def whatCanI(self):
        ''':returns: instrument attributes'''
        return ''

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def close(self):
        '''
        Closes session with resource.
        '''

        self.ser.close()

    def set_mode(self, mode):
        '''
        Sets the mode for the instrument.

        :param mode: Operating mode for instrument. Possible inputs at -> mode_options()
        :type mode: String
        '''

        self.ser.write(":MODE:SW:CH1 "+mode+" \n")

    def get_mode(self):
        '''
        Query the current mode of instrument.

        :returns: String, current mode.
        '''

        self.ser.write(":MODE:SW:CH1? \n")
        return self._read2cr()

    def mode_options(self):
        '''
        Queries available modes for the instrument.

        :returns: String of available modes
        '''

        self.ser.write(":READ:MODE:NAMES? \n")
        return self._read2cr()

    def set_power(self, power):
        '''
        Set the driving set-point of the specified <mode> for the specified channel

        :param power: specified power
        :type power: Float
        '''
        self.ser.write(":DRIV:APC:CUR:CH1 "+str(power)+" \n")

    def get_set_power(self):
        '''
        Queries the current set power

        :returns: Float
        '''
        if self.get_mode() == "APC":
            self.ser.write(":DRIV:APC:CUR:CH1? \n")
        
            return self._read2cr()
        else:
            return -1

    def set_pump_currents(self,channel,current):
        '''
        Sets the specified current for a particular channel.

        :param channel: Specified channel
        :type channel: Integer
        :param current: Specified current
        :type current: Float
        '''

        self.ser.write(":DRIV:ACC:CUR:CH"+str(channel)+" "+str(current)+" \n")

    
    def get_pump_currents(self,channel):
        '''
        Queries the current for specified channel.

        :returns: Float
        '''

        if self.get_mode() == "ACC":
            self.ser.write(":DRIV:ACC:CUR:CH"+str(channel)+"? \n")

            return self._read2cr()
        else:
            return -1

    def set_status_pumps(self,state=1):
        '''
        Sets the status for pump.

        :param state: specified state
        :type state: Integer
        '''
        if self.get_mode() == "ACC":
            self.ser.write(":DRIV:ACC:STAT:CH1 "+str(state)+" \n")
            sleep(0.01)
            self.ser.write(":DRIV:ACC:STAT:CH2 "+str(state)+" \n")
        elif self.get_mode() == "APC":
            self.ser.write(":DRIV:APC:STAT:CH1 "+str(state)+" \n")
           

    def set_master_out(self,state=1):
        '''
        Sets master control switch

        :param state: 1 means ON and 0 means OFF
        :type state: Integer
        '''

        if state == 1:
            self.ser.write(":DRIV:MCTRL 1 \n")
        else:
            self.ser.write(":DRIV:MCTRL 0 \n")

    def get_master_out(self):
        '''
        Get the master control switch status

        :returns: Integer; 0,1,2 for OFF, ON, BUSY respectively 
        '''
        self.ser.write(":DRIV:MCTRL? \n")

        return self._read2cr()

    def get_out_power(self):
        '''
        Get the existing input power value of the specified channel.

        :returns: Float
        '''
        self.ser.write(":SENS:POW:OUT:CH1? \n")

        return self._read2cr()

    def _read2cr(self):
        '''
        Internal function for reading instrument
        '''
        sleep(0.01)

        response = ''

        letter = self.ser.read()
        while( letter != '\n'):
            response += letter
            letter = self.ser.read()

        return response[0:-1]

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'AEDFA_IL_23_B_FA'


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
