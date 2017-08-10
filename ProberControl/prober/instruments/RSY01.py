#import serial
#import visa

import numpy as np

class RSY01(object):
    '''
    This class models Signal Generator, specifically for Model RSY01
    '''

    def __init__(self,res_manager, address='GPIB0::28::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object 
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False
        self.gpib = res_manager.open_resource(address)
        
        self.reset()

        # Constants
        self.max_freq = 1040
        self.min_freq = 0.009

        # Class Globals
        self.startfreq = 0
        self.stopfreq  = 0
        self.stepfreq  = 0
        self.currentfreq = 0

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'RFSource'

    def whatCanI(self):
        ''':returns: instrument attributes'''
        return ''

    def reset(self):
        '''
        Resets the instrument
        '''
        self.gpib.write('PRESET')

    def out_on(self):
        '''
        Turns the level on.
        '''
        self.gpib.write('LEVEL:ON')
        print('Level: ON')

    def out_off(self):
        '''
        Turns the level off.
        '''
        self.gpib.write('LEVEL:OFF')
        print('Level: OFF.')

    def set_freq(self, freq = 10):
        '''
        Set the frequency to specified frequency.

        :param freq: Specified frequency, defaults to 10.
        :type freq: Integer
        '''
        self.gpib.write('RF '+str(freq)+' MHZ')

    def set_power(self,power = 0):
        '''
        Set the power to specified power.

        :param power: Specified power, defaults to 0.
        :type power: Integer
        '''
        self.gpib.write('LEVEL '+str(power)+' V')

    def sweepTriggerSetup(self, start, end, step):
        '''
        Execute a trigger sweep

        :param start: Specified start
        :type start: Float
        :param end: Specified end
        :type end: Float
        :param step: Specified step
        :type step: Float
        '''

        if (
            start < self.min_freq or
            start > self.max_freq or
            end < self.min_freq or
            end > self.max_freq or
            step < 0.001
            ):
                print ('Specified Frequence Out of Range, or Step Too Low')

        else:
            self.startfreq = float(start)
            self.stopfreq = float(end)
            self.stepfreq = float(step)
            self.currentfreq = float(start)
            self.set_freq(start)

    def trigger(self):
        '''
        Execute the trigger for laster
        '''
        if(self.currentfreq < self.stopfreq and self.currentfreq >= self.startfreq):
            self.currentfreq = float(self.currentfreq) + float(self.stepfreq)
            self.set_freq(self.currentfreq)

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'RSY01'


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
