################################################################################
################# This template models a multi-channel laser ###################
################################################################################

class InstrumentNameHere(object):
    '''
    This class is a template for a multi-channel laser.
    '''

    def __init__(self, res_manager, address='YourAddressHere', channel):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: string
        :param channel: Channel that this laser object refers to.
        :type channel: Integer
        '''
        self.__channel = channel
        self.active = False
        self.gpib = res_manager.open_resource(address) #call visa


    def whoAmI(self):
        ''':returns: reference to device'''
        return 'Device'

    def change_state(self):
        ''' Toggles the self.active parameter'''
        if self.active == True:
            self.active = False
        else:
            self.active = True

    def setwavelength(self, wavelength):
        '''
        Loads a single wavelength and sets output high

        :param waveLength: Specified wavelength
        :type waveLength: Integer
        '''
