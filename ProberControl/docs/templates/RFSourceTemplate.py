################################################################################
###### This is a template for an RF-Source class. There are ####################
###### some mandatory methods that are expected to be implemented. #############
################################################################################

# Note: it is a good practice to indicate what packages the instrument utilizes
#        even if the package is passed as a parameter. In that case, you can just
#        leave it commented out.
#
#import serial
#import visa

class ClassNameHere(object):
    '''Purpose of this class here'''
    
    def __init__(self,res_manager, address='YourAddressHere'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object 
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False
        self.gpib = res_manager.open_resource(address)

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'RFSource'

    def whatCanI(self):
        ''':returns: instrument attributes'''
        return ''

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'ClassNameHere'

    def change_state(self):
        ''' Toggles the self.active parameter'''
        if self.active == True:
            self.active = False
        else:
            self.active = True

################################################################################
#################### All methods below are suggested: ##########################
################################################################################

    def out_on(self):
        '''Turns output ON'''    

    def out_off(self):
        '''Turns output OFF'''    

    def set_freq1(self, freq = 10):
        '''
        Sets the first frequency to specified value.

        :param freq: Frequency to spcify; defaults to 10.
        :type freq: Integer
        '''

    def set_freq2(self, freq = 10):
        '''
        Sets the second frequency to specified value.

        :param freq: Frequency to spcify; defaults to 10.
        :type freq: Integer
        '''

    def sweep_f1f2(self):
        '''Execute a sweep of the two frequencies'''    

    def single_trigger_mode(self):
        '''Enter single trigger mode.'''

    def auto_trigger_mode(self):
        '''Enter auto trigger mode'''

    def set_CW_mode(self):
        '''Enter CW mode'''

    def set_deltasweep_mode(self):
        '''Enter delta sweep mode'''
        
    def set_sweep_delta(self,delta = 5):
        '''
        Set delta sweep value

        :param delta: Specified delta value; defaults to 5
        :type delta: Integer
        '''

    def decrement(self):
        '''Execute decrement'''

    def increment(self):
        '''Execute increment'''

    def full_range_sweep(self):
        '''Execute full range sweep'''

    def set_power(self,power = 0):
        '''
        Set the power to specified value.

        :param power: Specified power value; defaults to 0
        :type power: Integer
        '''

    def set_stepsweep_time(self,time = 100):
        '''
        Sets the step sweep time

        :param time: Specified time value; defaults to 100
        :type time: Integer
        '''

    def set_stepsweep_steps(self, steps = 1000):
        '''
        Set the number of steps

        :param steps: Specified step value; defaults to 1000
        :type steps: Integer
        '''

    def set_stepsweep_mode(self):
        '''Enter step-sweep mode'''

    def set_analogsweep_mode(self):
        '''Enter analog-sweep mode'''

    def set_analogsweep_time(self, time = 1000):
        '''
        Set analog-sweep time

        :param time: Specify time value; defaults to 1000
        :type time: Integer
        '''
    
    def set_stepsweep_stepsize(self, step = 500):
        '''
        Set the stepsize of step-sweep mode

        :param step: Specify the step size; defaults to 500.
        :type step: Integer
        '''


    def trigger_sweep(self):
        '''Execute trigger sweep'''
