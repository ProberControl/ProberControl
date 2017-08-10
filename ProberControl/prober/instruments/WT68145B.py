#import serial
#import visa

import numpy as np

class WT68145B(object):
    def __init__(self,res_manager, address='GPIB0::5::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object 
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False

        self.gpib = res_manager.open_resource(address)
        # select power channel L0 and put it to minimal pwoer
        self.set_power(-120)
        # keep rf ouput on when switching freqs
        self.gpib.write('RC1')

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'RFSource'

    def whatCanI(self):
        ''':returns: instrument attributes'''
        return ''

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def out_on(self):
        '''Turns output ON'''    
        self.gpib.write('RF1')

    def out_off(self):
        '''Turns output OFF'''    
        self.gpib.write('RF0')

    def set_freq1(self, freq = 10):
        '''
        Sets the first frequency to specified value.

        :param freq: Frequency to spcify; defaults to 10.
        :type freq: Integer
        '''
        self.gpib.write('F1 '+str(freq)+' GH')

    def set_freq2(self, freq = 10):
        '''
        Sets the second frequency to specified value.

        :param freq: Frequency to spcify; defaults to 10.
        :type freq: Integer
        '''
        self.gpib.write('F2 '+str(freq)+' GH')

    def sweep_f1f2(self):
        '''Execute a sweep of the two frequencies'''    
        self.gpib.write('SF1')

    def single_trigger_mode(self):
        '''Enter single trigger mode.'''
        self.gpib.write('EXT')

    def auto_trigger_mode(self):
        '''Enter auto trigger mode'''
        self.gpib.write('AUT')

    def set_CW_mode(self):
        '''Enter CW mode'''
        self.gpib.write('CF1')

    def set_deltasweep_mode(self):
        '''Enter delta sweep mode'''
        self.gpib.write('DF1')
        
    def set_sweep_delta(self,delta = 5):
        '''
        Set delta sweep value

        :param delta: Specified delta value; defaults to 5
        :type delta: Integer
        '''
        self.gpib.write('DLF '+str(delta)+' GH')

    def decrement(self):
        '''Execute decrement'''
        self.gpib.write('DN')

    def increment(self):
        '''Execute increment'''
        self.gpib.write('UP')

    def full_range_sweep(self):
        '''Execute full range sweep'''
        self.gpib.write('FUL')

    def set_power(self,power = 0):
        '''
        Set the power to specified value.

        :param power: Specified power value; defaults to 0
        :type power: Integer
        '''
        self.gpib.write('XL0 '+str(power)+' DM')
        self.gpib.write('L0')

    def set_stepsweep_time(self,time = 100):
        '''
        Sets the step sweep time

        :param time: Specified time value; defaults to 100
        :type time: Integer
        '''
        self.gpib.write('SDT '+str(time)+' MS')

    def set_stepsweep_steps(self, steps = 1000):
        '''
        Set the number of steps

        :param steps: Specified step value; defaults to 1000
        :type steps: Integer
        '''
        self.gpib.write('SNS '+str(steps)+' SPS')

    def set_stepsweep_mode(self):
        '''Enter step-sweep mode'''
        self.gpib.write('SSP')

    def set_analogsweep_mode(self):
        '''Enter analog-sweep mode'''
        self.gpib.write('SWP')

    def set_analogsweep_time(self, time = 1000):
        '''
        Set analog-sweep time

        :param time: Specify time value; defaults to 1000
        :type time: Integer
        '''
        self.gpib.write('SWT '+str(time)+' MS')
    
    def set_stepsweep_stepsize(self, step = 500):
        '''
        Set the stepsize of step-sweep mode

        :param step: Specify the step size; defaults to 500.
        :type step: Integer
        '''
        self.gpib.write('SYZ '+str(step)+' MH')

    def trigger_sweep(self):
        '''Execute trigger sweep'''
        self.gpib.write('TRG')

    def fill_freq_buffer(self, start, stop,steps):
        '''
        Writes to frequency buffer.

        :param start: Specify starting point.
        :type start: Float
        :param stop: Specify ending point
        :type stop: Float
        :param steps: Specify steps
        :type steps: Float
        '''
        self.gpib.write('ZL000')

        for x in np.arange(float(start),float(stop),(float(stop)-float(start))/float(steps)):
            self.gpib.write(str(x)+' GH,')

        self.gpib.write('ZEL GTF ZS000') 

    def freq_step(self):
        '''Set step frequency.'''
        self.gpib.write('Y')

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'WT68145B'
