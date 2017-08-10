#import visa
#import time
#import sys

class Keithley2400(object):
    '''
    This class models the Keithley Model 2400 Series SourceMeter DC-Source
    '''
    def __init__(self,res_manager,address='GPIB0::21::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object 
        :param address: SCPI address of instrument
        :type address: String
        '''

        self.active = False

        self.gpib = res_manager.open_resource(address) #call visa
        print(self.gpib.query('*IDN?'))
        self.gpib.write('*RST')
        self.gpib.write('*CLS')

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

    def get_voltage(self, query_range=10,resolution=0.01):
        '''
        Get the voltage

        :param query_range: Specified range value, defaults to 10
        :type query_range: Integer
        :param resolution: Specified resoultion to query, defaults to 0.01
        :type resolution: Float
        :returns: Float
        ''' 
        return float(self.gpib.query(':MEAS:VOLT:DC? '+str(query_range)+','+str(resolution)))

    def get_current(self,query_range=1,resolution=0.000001):
        '''
        Get the current

        :param query_range: Specified range value, defaults to 10
        :type query_range: Integer
        :param resolution: Specified resoultion to query, defaults to 0.000001
        :type resolution: Float
        :returns: Float
        ''' 
        return float(self.gpib.query(':MEAS:CURR:DC? '+str(query_range)+','+str(resolution)))

    def close(self):
        '''Release resources'''
        self.gpib.close()

    def setvoltage(self, value = 0):
        '''
        Set the voltage

        :param value: Specified voltage value, defaults to 0
        :type value: Integer
        ''' 
        self.gpib.write(':SOUR:FUNC VOLT')
        self.gpib.write(':SOUR:VOLT '+str(value))

    def setcurrent(self, value = 0):
        '''
        Set the current

        :param value: Specified voltage value, defaults to 0
        :type value: Integer
        '''    
        self.gpib.write(':SOUR:FUNC CURR')
        self.gpib.write(':SOUR:CURR '+str(value))

    def setovervoltage(self, value = 0):
        '''
        Set the over voltage

        :param value: Specified voltage value, defaults to 0
        :type value: Integer
        ''' 
        self.gpib.write(':SENS:VOLT:PROT '+str(value))

    def setovercurrent(self, value = 0):
        '''
        Set the over current

        :param value: Specified current value, defaults to 0
        :type value: Integer
        '''    
        self.gpib.write(':SENS:CURR:PROT '+str(value))
      
    def setOutputSwitch(self, value = 0):
        '''
        Set the output switch to 1 -> ON or 0 -> OFF

        :param value: Specified state, defaults to 0 for OFF, 1 for ON
        :type value: Integer
        '''
        if value == 0:
            self.gpib.write(':OUTP OFF')
        if value == 1:
            self.gpib.write(':OUTP ON')

    def getsetvoltage(self):
        '''
        Queries the current voltage
        
        :returns: String
        '''
        self.gpib.write(':SOUR:VOLT?')
        return self.gpib.read()

    def getsetcurrent(self):
        '''
        Queries the current
        
        :returns: String
        '''
        self.gpib.write(':SOUR:CURR?')
        return self.gpib.read()

    def getoutvoltage(self):
        '''
        Queries the current out-voltage
        
        :returns: Float
        '''
        return float(self.gpib.query(':MEAS:VOLT:DC? '+str(Range)+','+str(Resolution)))     

    def getoutcurrent(self):
        '''
        Queries the current out-current
        
        :returns: Float
        '''
        return float(self.gpib.query(':MEAS:CURR:DC? '+str(Range)+','+str(Resolution)))

    def getoutswitch(self):
        '''
        Queries the current out-switch
        
        :returns: String
        '''
        self.gpib.write(':OUTP?')
        return self.gpib.read()

    def save_state(self,mem=1):
        '''
        Stores state within non-volatile memory

        :param mem: Specified space to write to
        :type mem: Integer
        '''
        self.gpib.write('*SAV '+str(mem))

    def recall_state(self,mem=1):
        '''
        Loads stored state from specified memory location

        :param mem: Specified space to query
        :type mem: Integer
        '''
        self.gpib.write('*RCL '+str(mem))

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'Keithley2400'
