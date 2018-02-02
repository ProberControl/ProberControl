################################################################################
###### This is a template for a SourceMeter DC-Source Class. There are #########
###### some mandatory methods that are expected to be implemented. #############
################################################################################

# Note: it is a good practice to indicate what packages the instrument utilizes
#        even if the package is passed as a parameter. In that case, you can just
#        leave it commented out.
#
#import visa
#import time
#import sys

class InstrumentNameHere(object):
    '''
    This class models ...
    '''
    def __init__(self,res_manager,address='YourAddressHere'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False
        self.gpib = res_manager.open_resource(address) #call visa

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'DCSource'

    def change_state(self):
        ''' Toggles the self.active parameter'''
        if self.active == True:
            self.active = False
        else:
            self.active = True

    def get_voltage(self):
        '''Get the voltage'''

    def get_current(self):
        '''Get the current'''

    def close(self):
        '''Release resources'''

    def setVoltage(self, value = 0):
        '''
        Set the voltage

        :param value: Specified voltage value, defaults to 0
        :type value: Integer
        '''

    def setCurrent(self, value = 0):
        '''
        Set the current

        :param value: Specified voltage value, defaults to 0
        :type value: Integer
        '''

################################################################################
#################### All methods below are suggested: ##########################
################################################################################

    def setovervoltage(self, value = 0):
        '''
        Set the over voltage

        :param value: Specified voltage value, defaults to 0
        :type value: Integer
        '''

    def setovercurrent(self, value = 0):
        '''
        Set the over current

        :param value: Specified current value, defaults to 0
        :type value: Integer
        '''

    def setOutputSwitch(self, value = 0):
        '''
        Set the output switch to 1 -> ON or 0 -> OFF

        :param value: Specified state, defaults to 0 for OFF, 1 for ON
        :type value: Integer
        '''

    def getsetvoltage(self):
        '''
        Queries the current voltage

        :returns: String
        '''

    def getsetcurrent(self):
        '''
        Queries the current

        :returns: String
        '''

    def getoutvoltage(self):
        '''
        Queries the current out-voltage

        :returns: Float
        '''

    def getoutcurrent(self):
        '''
        Queries the current out-current

        :returns: Float
        '''

    def getoutswitch(self):
        '''
        Queries the current out-switch

        :returns: String
        '''

    def save_state(self,mem=1):
        '''
        Stores state within non-volatile memory

        :param mem: Specified space to write to
        :type mem: Integer
        '''

    def recall_state(self,mem=1):
        '''
        Loads stored state from specified memory location

        :param mem: Specified space to query
        :type mem: Integer
        '''
