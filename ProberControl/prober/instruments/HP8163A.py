#import visa
#import time
#import sys

class HP8163A(object):
    '''
    This class models a Powermeter Agilent 8163A/B Lightwave Multimeter.
    '''
    CURRENT_CHANNEL = 1

    def __init__(self,res_manager,address='GPIB0::14::INSTR', channel=1):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object 
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False
        self.gpib = res_manager.open_resource(address)
        self.__channel = channel
        
        # Set Power Unit to dbm
        self.gpib.write('sens1:pow:unit 0')
        self.gpib.write('sens2:pow:unit 0')

    def _checkChannel(self):

        if CURRENT_CHANNEL != self.__channel:
            _setChannel(self.__channel)

    def _setChannel(self, newChannel):
        '''
        The purpose of this method is to change channels
        The syntax of usage will depend on the particular device.
        '''
        pass

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'PowerMeter'+str(self.__channel)

    def whatCanI(self):
        ''':returns: instrument attributes'''
        return 'OPT'

    def get_power(self,wavelength=1550):
        '''
        Query the powermeter reading after setting correct wavelength

        :returns: Float
        '''

        self.gpib.write('sens'+str(int(self.__channel))+':pow:wav '+str(wavelength)+'nm')
        return float(self.gpib.query('read'+str(int(self.__channel))+':pow?'))

    def close(self):
        '''
        Release resources
        '''
        self.gpib.close()

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'HP8163A'


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
