################################################################################
###### This is a template for a multimeter class. The Methods in this class ####
###### are mandatory, as other methods are expecting them. #####################
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
    This class models a ...
    '''

    def __init__(self,res_manager,address='Address here'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False
        self.gpib = res_manager.open_resource(address) #call vis

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'PowerMeter'

    def change_state(self):
        ''' Toggles the self.active parameter'''
        if self.active == True:
            self.active = False
        else:
            self.active = True

    def get_power(self):
        '''
        Query the powermeter reading after setting correct wavelength

        :returns: Float
        '''
