import time
import visa

class GenPhotPCD104(object):
    '''
    This class models the General Photonics Polarization Scrambler

    .. note:: When using any laser command, remember to send shut-off-laser command at the end of each sweep command set.
        For Trigger Sweep, send shut-off-laser command after sweep ends (sweep end condition noted in TriggerSweepSetup function)
    '''

    def __init__(self, res_manager, address='GPIB0::5::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: string
        '''
        self.active = False
        self.gpib = res_manager.open_resource(address)
        self.gpib.write ('*IDN?')
        info = self.gpib.read()
        print ('Connection Successful: %s' % info)

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'PolScramb'

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True
 
    def getWavelength(self):
        '''Get current Wavelength'''
        self.gpib.write('*WAV?')
        info = self.gpib.read()
        return info

    def enable(self):
        '''Enable Scrambling'''
        self.gpib.write('*ENA#')

    def disable(self):
        '''Disable Scrambling'''
        self.gpib.write('*DIS#')

    def setWavelength(self, wavelength):
        '''
        Set Wavelength of Operation
        '''		
        if wavelength != 980 and wavelength != 1060 and wavelength != 1310 and wavelength != 1480 and wavelength != 1550 and wavelength != 1600:
            return "Invalid wavelength. Please try again."
        else:
            self.gpib.write('*WAV ' + str(int(wavelength))+ '#')
            return "Success"

		
#if __name__ == "__main__":

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
