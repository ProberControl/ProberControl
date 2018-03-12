class TL2500(object):
    '''
    This class handles the communication with the fiContec TL2500 system.

    .. note::
    '''

    def __init__(self, interface=None, address=None):
        '''
            Add all code needed to start the communication with the TL2500.

            The interface-handler (interface) object is provided by the framework and will depend whether the system is controlled via gpib,ethernet or serial. All communication can be performed using interface.write() .read() .query().

            Non public functions are defined by leading _ in the function name e.g. _sum()

            The self.active is needed by the framework and should be toggled by the functions whenever they start to perform non atomic code and toggled back to false afterwads
        '''
        self.active = False

    def whoAmI(self):
        ''':returns: instrument attributes'''
        return 'Prober'

    def __changeState(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True


################## TOOL COMMANDS ###############################

    def get_state(self):
        '''
            Returns the state of the prober. Minimal set of returns: error, uncalibrated, ready
        '''
        return 'ready'

    def load_chip(self,reticle_id):
        '''
            Prober loads reticle onto single die probing station. Sets state so that following coupling commands are executed depending whether chip is in waferfor or die form.

            (1) Prober fetches position and state of chip from DB
            (2a)  If die is on already loaded wafer do nothing
            (2b)  If die is on new wafer possibly store current wafer back to foup
            (2c)  If die is in chip state and measurement platform is currently occupied restore current die to original location
            (3) Prober checks its configuration whether its equipped for chip state (wafer or die)
            (4) Prober loads wafer or picks die either from bluetape or gel pack
            (5) If needed Prober places die on probing station
            (6) Prober returns 'ready' or 'error'
        '''

        return 'ready'

    def store_chip(self,pack_id = None):
        '''
            Prober stores active chip in pack.
            * If no pack_id defined:
            (1) Return chip to previous location
            (2) Prober returns error/ready message.

            * If pack_id defined:
            (1) Prober checks location and fill-stage of pack_id
            (2) Prober stores chip in pack if possible
            (3) Prober updates database with location of chip about pack_id and location in pack
            (4) Prober returns error/ready message.

        '''

    def load_bluetape(self,bluetape_id):
        '''
            Prober loads bluetape to die ejector position. Sets state so that following coupling commands are executed for single die coupling.

            (1) Prober checks configuration
            (2) Prober checks whether ejector is free. If not stores loaded bluetape in casssette
            (3) Prober reads location of bluetape_id from database
            (4) Prober loads bluetape to die ejector
            (5) Prober returns error/success message

        '''

    def store_bluetape(self):
        '''
            Prober stores currently loaded bluetape in cassette.
            (2) Prober returns error/success message
        '''

    def load_wafer(self,wafer_id):
        '''
            Prober loads bluetape to die ejector position. Sets state so that following coupling commands are executed for wafer scale coupling.

            (1) Prober checks configuration
            (2) Prober checks whether wafer chuck is free. If not stores loaded wafer in casssette
            (3) Prober reads location of wafer_id from database
            (4) Prober loads wafer to wafer chuck
            (5) Prober returns error/success message

        '''

    def store_wafer(self):
        '''
            Prober stores currently loaded wafer in cassette.
            (2) Prober returns error/success message
        '''

    def get_structure_needs(self, structure):
        '''
            Prober gives information on the fibers that need to be connected with PowerMeter and/or MultiMeter
            attached to the Prober

            (1) Return (power_fiber_id, multi_fiber_id) -- can be None too
        '''

    def connect_structure(self,chip_id,structure_id,active_align=False):
        '''
            Prober connects probes and performs active alignment of optical probes.

            (1) Prober reads coordinates of structure IO from internal database - coordinates include type of IO and feedback signal source for active alignment
            (2) Prober checks whether it is configured to couple the structure
            (3) Prober couples structure and performs active alignment
            (4) Prober returns 'error'/'ready' message
        '''

        return 'error'

    def calibrate(self):
        '''
            Calibrate machine for current configuration

            Should be blocking until machine is calibrated

            return ready or error
        '''

        return 'ready'


    def set_chuck_temp(self,temp,lock):
        '''
            Prober sets wafer chuck temperature in degree Celsius

            (2) If lock = True  - tool driver returns functions only when temp is reached.
            (3) If lock = False - tool driver only initiates heating process
        '''

    def get_chuck_temp(self):
        '''
            Prober return wafer chuck temperature in degree Celsius
        '''

    def set_chip_temp(self,temp):
        '''
            Prober sets reticle holder temperature in degree Celsius

            (2) If lock = True  - tool driver returns functions only when temp is reached.
            (3) If lock = False - tool driver only initiates heating process
        '''

    def get_chip_temp(self):
        '''
            Prober returns reticle holder temperature in degree Celsius
        '''

    def free_prober(self):
        '''
            Prober returns all loaded devices (wafer and/or chip) to original location

            returns 'ready' / 'error'
        '''
        return 'ready'
