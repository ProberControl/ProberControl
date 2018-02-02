################################################################################
###### This is a template for a laser class. You'll see that some methods ######
###### are designated as mandatory, while some others are merely suggested. ####
###### There are certain methods that are expected in other parts of the #######
###### program. If you have any experience with Java interfaces, it is a #######
###### similiar concept; you are implementing some AutoProber interfaces. ######
################################################################################

# Note: it is a good practice to indicate what packages the instrument utilizes
#        even if the package is passed as a parameter. In that case, you can just
#        leave it commented out.
#
#import visa

class InstrumentNameHere(object):
    '''
    This class models the YOURLASERHERE laser.

    .. note:: If you want to make a note, fill this out.

    '''

    def __init__(self, res_manager, address='adress of laser'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: string
        '''
        self.active = False
        self.max_wavelength =
        self.min_wavelength =
        self.gpib = res_manager.open_resource(address) #call vis

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'Laser'

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

    def getwavelength(self):
        '''
        Queries wavelength of the laser

        :returns: Float
        '''

    def setpower(self,power = 0 ):
        '''
        Sets power in dbm

        :param power: Specified power to set the laser to in dbm
        :type power: Integer
        '''

    def getpower(self):
        '''
        Gets output power in dbm

        :returns: Float
        '''

    def sweepWavelengthsTriggerSetup (self, start, end, step):
        '''
        Have to keep track of Triggers in main command, use Stop Sweep Command to end sweep.
        Extra triggers do not make the laser sweep outside of specified end wavelength.
        Remeber to shut off laser after sweep ends

        :param start: Specified wavelength
        :type start: Integer
        :param end: Specified wavelength
        :type end: Integer
        :param time: Specified time
        :type time: Float
        '''

    def trigger(self):
        '''
        Triggers laser
        '''

################################################################################
#################### All methods below are suggested: ##########################
################################################################################

    def get_max_wavelength(self):
        '''
        Queries the maximum allowed wavelength

        :returns: Integer
        '''
        return self.max_wavelength

    def get_min_wavelength(self):
        '''
        Queries the minimum allowed wavelength

        :returns: Integer
        '''
        return self.min_wavelength

    def sweepWavelengthsStep (self, start, end, step):
        '''
        Executes a sweep with respect to a specified step

        :param start: Specified wavelength
        :type start: Integer
        :param end: Specified wavelength
        :type end: Integer
        :param step: Specified step must be greater or equal to than 0.001
        :type step: Float
        '''

    def sweepWavelengthsContinuous (self, start, end, time):
        '''
        Executes a sweep with respect to a specified time

        :param start: Specified wavelength
        :type start: Integer
        :param end: Specified wavelength
        :type end: Integer
        :param time: Specified time
        :type time: Float
        '''

    def checkStatus(self):
        '''
        Checks the status of the laser. Handles timeout exception

        :returns: Boolean
        '''

    def manualStep(self, step):
        '''
        Use if want to manually step by a particular size, in conjuction with Send Single Wavelength

        :param step: specified step increment, but be greater than or equal to 0.001
        :type step: Float
        '''


    def stopSweep(self):
        '''Stop sweep'''

    def pauseSweep(self):
        '''Suspend sweep'''

    def resumeSweep(self):
        '''
        Use after pause to resume, still have to call trigger() for next data point if using with trigger sweep
        '''

    def outputOFF(self):
        '''
        Turns output of laser source OFF

        .. note:: Output occasionally doesn't turn off unless turned ON beforehand
        '''
