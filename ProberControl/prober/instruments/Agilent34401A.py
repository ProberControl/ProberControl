#import visa
#import time
#import sys

class Agilent34401A(object):
    '''
    This class models the Agilent 34401A Multimeter.
    '''

    def __init__(self,res_manager,address='GPIB0::22::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object 
        :param address: SCPI address of instrument
        :type address: string
        '''
        self.active = False

        self.gpib = res_manager.open_resource(address)
        print(self.gpib.query('*IDN?'))
        self.gpib.write('*RST')
        self.gpib.write('*CLS')
        self.scalingfactor = 1

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'DCMeter'

    def whatCanI(self):
        ''':returns: instrument attributes'''
        return 'DC'

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def get_voltage(self,scaled=False,query_range=10,resolution=0.01):
        '''
        Queries the voltage of multimeter.
        
        :param scaled: Optional scaling
        :type scaled: Boolean
        :param query_range: range for query
        :type query_range: Integer
        :param resolution: resolution for query
        :type resolution: Float
        :returns: current voltage reading as float
        '''

        val = float(self.gpib.query('MEAS:VOLT:DC? '+str(query_range)+','+str(resolution)))
        
        if scaled==True:
            val = val*self.scalingfactor
        
        return val

    def get_current(self,query_range=1,resolution=0.000001):
        '''
        Queries the current reading of the multimeter

        :param query_range: range for query
        :type query_range: Integer
        :param resolution: resolution for query
        :type resolution: Float       
        :returns: current reading as float
        '''
        return float(self.gpib.query('MEAS:CURR:DC? '+str(query_range)+','+str(resolution)))

    def set_scaling(self,factor=1):
        '''
        Sets the scaling factor of the multimeter instrument.

        :param factor: Desired factor
        :type factor: Float or Integer
        '''

        self.scalingfactor = factor

    def get_scaling(self):
        '''
        Gets the scaling factor.

        :returns: Scaling factor as Int or Float
        '''

        return self.scalingfactor
        

    def close(self):
        '''
        Release resource.
        '''

        self.gpib.close()

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'Agilent34401A'
