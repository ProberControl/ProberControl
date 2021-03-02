# -*- coding: utf-8 -*-
import socket
import sys
import time

class TL2500(object):
    '''
    This class handles the communication with the fiContec TL2500 system.
    .. note::
    '''

    def __init__(self, res_manager, address='127.0.0.1:8888'):
        '''
            Add all code needed to start the communication with the TL2500.
            The interface-handler (interface) object is provided by the framework and will depend whether the system is controlled via gpib,ethernet or serial. All communication can be performed using interface.write() .read() .query().
            Non public functions are defined by leading _ in the function name e.g. _sum()
            The self.active is needed by the framework and should be toggled by the functions whenever they start to perform non atomic code and toggled back to false afterwads
        '''
        self.active = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.ip_address = address.split(":")[0]
        self.port       = int(address.split(":")[1])

        try:
            self.sock.connect((ip_address, port))


        except Exception:
            print("Error in Connection")


        self.active = False

    def whoAmI(self):
        ''':returns: instrument attributes'''
        return 'Prober'

    def __changeState(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def _communicate(self, message, option=2):
        ## 1 Base Cummincation - Just Send "message"
        if option == 0:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                sock.connect((self.ip_address, self.port))
                sock.sendall(message + '\n')
                sock.close()

            except Exception:
                print("Error in Connection")

        ## 2 Base Cummincation -  Send "message" and print answer
        if option == 2:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                sock.connect((self.ip_address, self.port))
                sock.sendall(message + '\n')
                print sock.recv(1024)
                sock.close()

            except Exception:
                print("Error in Connection")

################## TOOL COMMANDS ###############################

    def get_state(self):
        '''
            Returns the state of the prober. Minimal set of returns: error, uncalibrated, ready
        '''
        message = "STATUS"

        self._communicate(message)

    def load_chip(self,chip_id):
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
        message = "LDCHP " + chip_id

        self._communicate(message)

    def get_chipID(self):
        '''
            Tool reads ID from loaded chip
            Tool returns ID from loaded chip, alphanumeric format, or “False” if chip does not exist
        '''

        message = "CHPID"

        self._communicate(message)

    def store_die(self,pack_id = None):
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

        message = "STRDIE " + pack_id

        self._communicate(message)

    def load_bluetape(self,bluetape_id):
        '''
            Prober loads bluetape to die ejector position. Sets state so that following coupling commands are executed for single die coupling.

            (1) Prober checks configuration
            (2) Prober checks whether ejector is free. If not stores loaded bluetape in casssette
            (3) Prober reads location of bluetape_id from database
            (4) Prober loads bluetape to die ejector
            (5) Prober returns error/success message

        '''

        message = "LDBLTP " + bluetape_id

        self._communicate(message)

    def get_bluetape(self):
        '''
            Tool reads ID from loaded blue tape
            Tool returns ID from loaded blue tape, alphanumeric format, or “False” if blue tape does not exist
        '''

        message = "BLTPID"

        self._communicate(message)

    def store_bluetape(self, bluetape_id, slot=None):
        '''
            Prober stores currently loaded bluetape in cassette.
            (2) Prober returns error/success message
        '''

        if slot:
            message = "STRBLTP " + bluetape_id + " " +slot

            self._communicate(message)
        else:
            message = "STRBLTP " + bluetape_id

            self._communicate(message)

    def load_wafer(self,wafer_id):
        '''
            Prober loads bluetape to die ejector position. Sets state so that following coupling commands are executed for wafer scale coupling.

            (1) Prober checks configuration
            (2) Prober checks whether wafer chuck is free. If not stores loaded wafer in casssette
            (3) Prober reads location of wafer_id from database
            (4) Prober loads wafer to wafer chuck
            (5) Prober returns error/success message

        '''

        message = "LDWFR " + wafer_id

        self._communicate(message)

    def get_waferID(self):
        '''
            Tool reads ID from loaded wafer
            Tool returns ID from loaded wafer, alphanumeric format, or “False” if wafer does not exist
        '''

        message = "WFRID"

        self._communicate(message)

    def store_wafer(self, wafer_id, slot=None):
        '''
            Prober stores currently loaded wafer in cassette.
            (2) Prober returns error/success message
        '''
        if slot:
            message = "STRWFR " + wafer_id + " " + slot
        else:
            message = "STRWFR " + wafer_id

        self._communicate(message)

    def get_structure_needs(self, structure):
        '''
            Prober gives information on the fibers that need to be connected with PowerMeter and/or MultiMeter
            attached to the Prober

            (1) Return (power_fiber_id, multi_fiber_id) -- can be None too
        '''

        #TODO

    def connect_structure(self,chip_id,structure_id,active_align=False):
        '''
            Prober connects probes and performs active alignment of optical probes.

            (1) Prober reads coordinates of structure IO from internal database - coordinates include type of IO and feedback signal source for active alignment
            (2) Prober checks whether it is configured to couple the structure
            (3) Prober couples structure and performs active alignment
            (4) Prober returns 'error'/'ready' message
        '''
        if active_align:
            align = "C"
        else:
            align = "S"
        message = "CNCT " + chip_id + " " + structure_id + " " + align

        self._communicate(message)

    def calibrate(self):
        '''
            Calibrate machine for current configuration
            Should be blocking until machine is calibrated
            Return ready or error
        '''

        message = "CLBRT"

        self._communicate(message)

    def set_chuck_temp(self,temp,lock):
        '''
            Prober sets wafer chuck temperature in degree Celsius

            (2) If lock = True  - tool driver returns functions only when temp is reached.
            (3) If lock = False - tool driver only initiates heating process
        '''

        message = "STCHKTMP " + repr(temp) + " " + lock + " "

        self._communicate(message)

    def get_chuck_temp(self):
        '''
            Prober return wafer chuck temperature in degree Celsius
        '''

        message = "CHKTMP"

        self._communicate(message)

    def set_die_temp(self,temp, lock):
        '''
            Prober sets reticle holder temperature in degree Celsius
            (2) If lock = True  - tool driver returns functions only when temp is reached.
            (3) If lock = False - tool driver only initiates heating process
        '''

        message = "STDIETMP " + repr(temp) + " " + lock

        self._communicate(message)

    def get_die_temp(self):
        '''
            Prober returns reticle holder temperature in degree Celsius
        '''

        message = "DIETMP"

        self._communicate(message)

    def free_prober(self):
        '''
            Prober returns all loaded devices (wafer and/or chip) to original location
            returns 'ready' / 'error'
        '''

        message = "FREE"

        self._communicate(message)

    def set_mode(self,mode):
        '''
            Tool can be placed into wafer/bluetape/die mode
            Tool compares current configuration with model
            returns 'ready' if fine, returns 'error' if not compatible
        '''

        message = "STMODE " + mode

        self._communicate(message)

    def get_mode(self):
        '''
            Tool returns the state of the prober.
            returns 'wafer mode'/'bluetape mode'/'die mode'
        '''

        message = "MODE"

        self._communicate(message)

    def close(self):
        self.sock.close()

    def test_connection(self):
        self.sock.sendall('ANSWER ME FROM WITHIN THE CLASS\n')
        print self.sock.recv(1024)


if __name__ == "__main__":



    ip_address = "128.59.65.143"
    port = 12345
    option = 1

    print("Ethernet Connection Test Executable\nSends a message to a specified IP address, and waits for a reply\nMessage sent in the format \"message\\n\"\n")

    ip_address = raw_input("Enter the IP address of TL2500: ")
    port = int(raw_input("Enter the port of TL2500: "))

    message = raw_input("Enter message to send: ")

    ## 1 Base Commincation - Just Send "message"
    if option > 0:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((ip_address, port))
            sock.sendall(message + '\n')
            sock.close()

        except Exception:
            print("Error in Connection")

    ## 2 Base Cummincation -  Send "message" and print answer
    if option > 1:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((ip_address, port))
            sock.sendall(message + '\n')
            print sock.recv(1024)
            sock.close()

        except Exception:
            print("Error in Connection")

    ## 3 Same functionality as in #2 but using the Prober Class
    if option > 2:
        prober = TL2500(None, ip_address+":"+str(port))

        prober.test_connection()
        prober.close()

    ## 4 Full Chip Loading Example
    if option > 3:
        # DUMMY FUNCTION FOR prepare_for_coupling
        def prepare_for_coupling(needs):
            print "ProberControl Ready for Coupling "

        # Initiate communication channel with TL2500
        prober = TL2500(None, ip_address+":"+str(port))

        # Check for the state of the prober
        prober.get_state()

        # Load Chip
        prober.load_chip('Chip54')

        # What is needed to couple the structure
        needs = prober.get_structure_needs('BSplit3')

        # ProberControl switches-on lasers , sets switches etc
        prepare_for_coupling(needs)   #JUST FOR FLOW_IDEA

        # Couple the structure
        prober.connect_structure('BSplit3',False)

        # Stop communication
        prober.close()

    raw_input("\nPress any key to exit")
