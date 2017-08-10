class TL2500(object):
    '''
    This class handles the communication with the fiContec TL2500 system. 
    
    .. note:: 
    '''

    def __init__(self, interface, address):
        '''
            Add all code needed to start the communication with the TL2500. 

            The interface-handler (interface) object is provided by the framework and will depend whether the system is controlled via gpib,ethernet or serial. All communication can be performed using interface.write() .read() .query().

            Non public functions are defined by leading _ in the function name e.g. _sum()

            The self.active is needed by the framework.
        '''
        self.active = False


    def whoAmI(self):
        ''':returns: instrument attributes'''
        return 'prober'

    def whatCanI(self):
        ''':returns: instrument attributes'''
        return 'prober'

    def __changeState(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def __str__(self):
        '''Adds built in functionality for printing and casting'''
        return 'TL2500'


################## TOOL COMMANDS ###############################

    def get_state(self):
        '''
            Returns the state of the prober. Minimal set of returns: Error, Uncalibrated, Ready
        '''

    def load_reticle(self,reticle_id):
        '''
            Prober loads reticle onto single die probing station. Sets state so that following coupling commands are executed for single die coupling.

            (1) Prober checks its configuration whether its equipped for single die tests
            (2) Prober checks location of die in database
            (3) Prober picks die either from bluetape or gel pack
            (4) Prober places die on probing station
            (5) Prober returns error/success message 
        '''

    def store_reticle(self,pack_id):
        '''
            Prober stores active reticle in pack.

            (1) Prober checks location and fill-stage of pack_id
            (2) Prober stores reticle in pack if possible
            (3) Prober updates database with location of reticle about pack_id and location in pack
            (4) Prober returns error/success message.

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

    def connect_structure(self,reticle_id,structure_id,active_align):
        '''
            Prober connects probes and performs active alignment of optical probes.

            (1) Prober reads coordinates of structure IO from internal database - coordinates include type of IO and feedback signal source for active alignment
            (2) Prober checks whether it is configured to couple the structure
            (3) Prober couples structure and performs active alignment
            (4) Prober returns error/success message
        '''

    def calibrate(self):
        '''
            Calibrate machine for current configuration
        '''


    def set_chuck_temp(self,temp):
        '''
            Prober sets wafer chuck temperature in degree Celsius
        '''

    def get_chuck_temp(self):
        '''
            Prober return wafer chuck temperature in degree Celsius
        '''

    def set_reticle_temp(self,temp):
        '''
            Prober sets reticle holder temperature in degree Celsius
        '''

    def get_reticle_temp(self):
        '''
            Prober returns reticle holder temperature in degree Celsius
        '''
