################################################################################
################# This template models a multi-channel laser ###################
################################################################################

class InstrumentNameHere(object):
    '''
    This class is a template for a multi-channel laser. The idea is that when there are several objects that refer to the same instrument, we need a way of ensuring that the channel you're intending to send traffic to, is in fact the channel that the device is set to. For this, we can use a class variable CURRENT_CHANNEL which will change based on whatever object used it last. In all of the method definitions, you have to call _checkChannel() before to confirm that you're infact on the right channel.
    '''
    CURRENT_CHANNEL = 1

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

    def _checkChannel(self):

        if CURRENT_CHANNEL != self.__channel:
            _setChannel(self.__channel)

    def _setChannel(self, newChannel):
        '''
        The purpose of this method is to change channels
        The syntax of usage will depend on the particular device.
        '''

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'Device' + str(self.__channel)

    def whatCanI(self):
        ''':returns: instrument attributes'''
        return ''

    def setwavelength(self, wavelength):
        '''
        Loads a single wavelength and sets output high

        :param waveLength: Specified wavelength
        :type waveLength: Integer
        '''

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'InstrumentNameHere'    