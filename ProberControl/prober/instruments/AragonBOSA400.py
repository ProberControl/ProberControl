#import visa

import time
import socket
import logging
import csv
import numpy

OK = True
OK_MSG = 'OK'
ERROR_BGN = 'Command'

class AragonBOSA400(object):
    '''
    This class models the AndoAQ4321 laser.

    .. note:: When using any laser command, remember to send shut-off-laser command at the end of each sweep command set.
        For Trigger Sweep, send shut-off-laser command after sweep ends (sweep end condition noted in TriggerSweepSetup function)
    '''

    def __init__(self, res_manager, address='128.59.65.231'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: string
        '''

        self.active = False

        self.max_wavelength = 1579.9
        self.min_wavelength = 1520

        self.osa = BOSA("LAN", address)


    def whoAmI(self):
        ''':returns: reference to device'''
        return 'OSA'


    def change_state(self):
        self.active = not self.active

############## LASER FUNCTION CALLS

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

    def setwavelength(self, wavelength):
        '''
        Loads a single wavelength (in nanometers) and sets output high

        :param waveLength: Specified wavelength
        :type waveLength: Integer
        '''
        command = 'sens:wav:stat {} nm'.format(wavelength)
        response = self.osa.ask(command)
        check_response(command, response, OK)

    def setpower(self, wavelength):
        '''
            BOSA cannot adjust output power - raise exception
        '''
        raise BOSAException('Cannot adjust output power.')

    def sweepWavelengthsTriggerSetup (self, start, end, step):
        '''
        Have to keep track of Triggers in main command, use Stop Sweep Command to end sweep.
        Extra triggers do not make the laser sweep outside of specified end wavelength.
        Remeber to shut off laser after sweep ends

        :param start: Specified wavelength between 1520-1580
        :type start: Integer
        :param end: Specified wavelength between 1520-1580
        :type end: Integer
        :param step: Specified step in nm
        :type step: Float
        '''
        if start < self.get_min_wavelength() or start > self.get_max_wavelength():
            raise BOSAException('start wavelength Out of Bounds.')
        if end < self.get_min_wavelength() or end > self.get_max_wavelength():
            raise BOSAException('end wavelength Out of Bounds.')
        if start > end:
            raise BOSAException('start wavelength must be smaller than end.')

        # set single sweep
        command = 'sens:wav:single on'
        response = self.osa.ask(command)
        check_response(command, response, OK)
        # set start waveLength
        command = 'sens:wav:star {} nm'.format(start)
        response = self.osa.ask(command)
        check_response(command, response, OK)
        # set end wavelength
        command = 'sens:wav:stop {} nm'.format(end)
        response = self.osa.ask(command)
        check_response(command, response, OK)
        # set sweep speed
        command = 'sens:wav:speed {} nm'.format(step)
        response = self.osa.ask(command)
        check_response(command, response, OK)

    def trigger(self):
        '''Triggers laser - Now this just starts the sweep'''
        command = 'sens:sweep on'
        response = self.osa.ask(command)
        check_response(command, response, OK)

    def stopSweep(self):
        '''Stop sweep'''
        command = 'sens:sweep off'
        response = self.osa.ask(command)
        check_response(command, response, OK)

    def outputOFF(self):
        '''
        Turns output of laser source OFF
        '''
        command = 'sens:switch off'
        response = self.osa.ask(command)
        check_response(command, response, OK)

    def outputON(self):
        '''
        Turns output of laser source OFF
        '''
        command = 'sens:switch on'
        response = self.osa.ask(command)
        check_response(command, response, OK)

        # wait until the laser is on
        while True:
            command = 'sens:switch?'
            response = self.osa.ask(command)
            check_response(command, response)
            if response.lower().startswith('on'):
                break

    def getwavelength(self):
        '''
        Queries wavelength of the laser

        :returns: Float
        '''
        command = 'sens:wav:stat?'
        response = self.osa.ask(command)
        check_response(command, response)
        print(response)  # TODO finalize how to parse and return a nmber

    def getpower(self):
        '''
        Gets output power in dbm

        :returns: Float
        '''
        pass

    def get_feedback(self):
        return self.getpower()

    def getAuxInputPower(self):
        pass

    def sweepWavelengthsContinuous (self, start, end, time):
        '''
        Executes a sweep with respect to a specified time

        :param start: Specified wavelength between 1520-1580
        :type start: Integer
        :param end: Specified wavelength between 1520-1580
        :type end: Integer
        :param time: Specified time
        :type time: Float
        '''
        pass

###### Function Calls Component Analyzer
    def getIL(self, start, end , step, polarization):
        '''
        Executes a sweep with respect to a specified time and collect injection loss information

        :param start: Specified wavelength between 1520-1580
        :type start: Integer
        :param end: Specified wavelength between 1520-1580
        :type end: Integer
        :param step: Specified step
        :type step: Float
        :param step: polarization mode
        :type step: String
        '''

    def getRL(self, start, end , step, polarization):
        '''
        Executes a sweep with respect to a specified time and collect reflection loss information

        :param start: Specified wavelength between 1520-1580
        :type start: Integer
        :param end: Specified wavelength between 1520-1580
        :type end: Integer
        :param step: Specified step
        :type step: Float
        :param step: polarization mode
        :type step: String
        '''


##### Function Calls OSA
    def getSpectrum(self, start, end , step, polarization):
        '''
        Executes a sweep with respect to a specified time and collect reflection loss information

        :param start: Specified wavelength between 1520-1580
        :type start: Integer
        :param end: Specified wavelength between 1520-1580
        :type end: Integer
        :param step: Specified step
        :type step: Float
        :param step: polarization mode
        :type step: String

        NOTE: polarization arg doesn't do anything yet!
        '''
        if start < self.get_min_wavelength() or start > self.get_max_wavelength():
            raise BOSAException('start wavelength Out of Bounds.')
        if end < self.get_min_wavelength() or end > self.get_max_wavelength():
            raise BOSAException('end wavelength Out of Bounds.')
        if start > end:
            raise BOSAException('start wavelength must be smaller than end.')

        resolution = nm_to_ghz(step)

        # set start
        command = 'sens:wav:star {} nm'.format(start)
        response = self.osa.ask(command)
        check_response(command, response, OK)
        # set stop
        command = 'sens:wav:stop {} nm'.format(end)
        response = self.osa.ask(command)
        check_response(command, response, OK)
        # set resolution
        command = 'sens:wav:res {} ghz'.format(resolution)
        response = self.osa.ask(command)
        check_response(command, response, OK)

        # command = 'trace:data:count?'
        # response = self.osa.ask(command)
        # check_response(command, response)
        # print response

        # get the trace
        command = 'trace:data?'
        response = self.osa.ask(command)
        check_response(command, response)

        # parse csv string
        trace_data = response.split(',')
        n_trace_data = numpy.array(trace_data)
        n_trace_data = numpy.reshape(n_trace_data, (len(trace_data) / 2, 2))

        # take only enough points accoridng to step
        # NOTE: BOSA does't change its sampling rate; it only changes it on the display
        original_size = numpy.size(n_trace_data, 0)
        print(('orig: ', original_size))
        target_size = int((end - start + 1) / float(step) + 1)
        print(('targ: ', target_size))
        skip_step = original_size / target_size
        print(('skip: ', skip_step))
        return_data = n_trace_data[::skip_step]

        return return_data.astype(float).tolist()

def check_response(command, response, OK=False):
    if response.startswith(ERROR_BGN) or (OK and not response.startswith(OK_MSG)):
        raise BOSAException('cmd:< {} > repsonded with: {}'.format(command, response))

def nm_to_ghz(nm):
    return nm * 125

class BOSAException(Exception):
    pass

# create logger
log = logging.getLogger(__name__)
if(len(log.handlers) == 0): # check if the logger already exists
    # create logger
    log.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    log.addHandler(ch)

class BOSA:
    """ class BOSA: driver used to communicate with BOSA equipment"""
    def __init__(self, interfaceType, location, portNo = 10000, IDN=True, Reset = False):
        """create the OSA object and tries to establish a connection with the equipment
            Parameters:
                interfaceType -> LAN, GPIB interface utilyzed in connection
                location      -> IP address or GPIB address of equipment.
                portN         -> no of the port where the interface is open (LAN)
        """
        self.interfaceType = interfaceType
        self.location = location
        self.portNo = portNo
        self.activeTrace = None

        if(interfaceType.lower() == "lan"):
            log.info("Connection to OSA using Lan interface on %r",location)
            try:
                self.connectLan()
            except Exception as e:
                log.exception("Could not connect to OSA device")
                print(e)
                raise e
                return
        elif(interfaceType.lower() == "gpib"):
            log.info("GPIB interface chosen to connect OSA on %r",location)
            try:
                self.interface = visa.GpibInstrument(location)
            except Exception as e:
                log.exception("couldn't connect to device")
                print(e)
                raise e
                return
            log.info("Connected to device.")
        else:
            log.error("Interface Type " + interfaceType + " not valid")
            raise Exception("interface type invalid")
            return

        if(IDN):
            try:
                log.debug("Sending IDN to device...")
                self.write("*IDN?")
            except Exception as e:
                log.exception("Could not send *IDN? device")
                print(e)
                raise e

            log.debug("IDN send, waiting response...")
            try:
                response = self.read()
            except Exception as e:
                log.exception("Could read response from device")
                print(e)
                raise e
            print(("IDN= " + response))

        if(Reset):
            try:
                log.info("resting device")
                self.write("*RST")
            except Exception as e:
                log.exception("Could not reset device")
                print(e)
                raise e

    def __del__(self):
        try:
            if(self.interfaceType == "LAN"):
                self.interface.close()
            elif(self.interfaceType == "GPIB"):
                self.interface.close()
        except Exception as e:
            log.warning("could not close interface correctly: exception %r", e.message)


    def connectLan(self):
        """ connect the instrument to a LAN """
        log.debug("creating socket")
        self.interface = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.interface.settimeout(30)

        try:
            log.debug("Connecting to remote socket...")
            self.interface.connect((self.location, self.portNo))
        except Exception as e:
            log.exception("Could not connection to remote socket")
            print(e)
            raise e

        log.debug("Connected to remote socket")
        log.info("OSA ready!")


    def write(self, command):
        """ write to equiment: independent of the interface
            Parameters:
                command -> data to send to device + \r\n
        """
        if(self.interfaceType.lower() == "lan"):
            log.debug("Sending command '" + command + "' using LAN interface...")
            try:
                self.interface.sendall( (command + "\r\n").encode())
            except Exception as e:
                log.exception("Could not send data, command %r",command)
                print(e)
                raise e
        elif(self.interfaceType.lower() == "gpib"):
            log.debug("Sending command '" + command + "' using GPIB interface...")
            try:
                self.interface.write(command + "\r\n")
            except Exception as e:
                log.exception("Could not send data, command %r",command)
                print(e)
                raise e


    def read(self):
        """ read something from device"""
        message = ""
        if(self.interfaceType.lower() == "lan"):
            log.debug("Reading data using LAN interface...")
            while(1):
                try:
                    data = self.interface.recv(19200)
                    message += data.decode()
                except Exception as e:
                    log.exception("Could not read data")
                    print(e)
                    raise e
                if("\n" in message):
                    break
            log.debug("All data readed!")
        elif(self.interfaceType.lower() == "gpib"):
            log.debug("Reading data using GPIB interface...")
            while(1):
                try:
                    message = self.interface.read()
                except Exception as e:
                    log.exception("Could not read data")
                    print(e)
                    raise e
                if("\n" in message):
                    break
            log.debug("All data readed!")

        log.debug("Data received: " + message)
        return message


    def ask(self, command):
        """ writes and reads data"""
        data = ""
        self.write(command)
        data = self.read()
        return data

if __name__ == '__main__':
    import visa
    from time import sleep
    import matplotlib.pyplot as plt

    bosa = AragonBOSA400(visa.ResourceManager(), '128.59.87.222')

    spec = bosa.getSpectrum(1540.5, 1560, 0.01, 0)
    print((len(spec)))

    plt.scatter(*list(zip(*spec)))
    plt.show()

    print('done.')


'''
Copyright (C) 2017  Robert Polster
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
