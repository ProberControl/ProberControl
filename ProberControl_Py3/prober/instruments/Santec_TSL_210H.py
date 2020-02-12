import time
import numpy

class Santec_TSL_210H(object):
    '''
    This class models the Santec_TSL_210H TUNABLE LD LIGHT SOURCE.

    .. note:: When using any laser command, remember to send shut-off-laser command at the end of each sweep command set.
    For Trigger Sweep, send shut-off-laser command after sweep ends (sweep end condition noted in TriggerSweepSetup function)
    '''

    def __init__(self, res_manager, address = 'GPIB0::3::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: String
        '''

        self.active = False

        self.max_wavelength = 1580
        self.min_wavelength = 1510

        # open resource
        self.gpib = res_manager.open_resource(address)

        #First need to turn the current of laser diode ON
        self.outputON()
        time.sleep(2)

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'Laser'

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def get_max_wavelength(self):
        '''
        Queries the maximum allowed wavelength.

        :returns: Float
        '''
        return self.max_wavelength

    def get_min_wavelength(self):
        '''
        Queries the minimum allowed wavelength.

        :returns: Float
        '''
        return self.min_wavelength

    def setwavelength(self, wavelength):
        '''
        Loads a single wavelength and sets output high.

        :param wavelength: Specified wavelength, must be greater than minimum and less than maximum wavelength
        :type wavelength: Float
        '''
        if (
            wavelength < self.min_wavelength or
            wavelength > self.max_wavelength
            ):
            print ('Specified Wavelength Out of Range')

        else :
            wavelength = float(str(numpy.round(wavelength, 3)))
            self.gpib.write('WA' + str(wavelength))
            time.sleep(0.5)
            self.gpib.write('WA')
            info = float(self.gpib.read())
            while(info != wavelength):
                time.sleep(0.1)
                info = float(self.gpib.read())
            print(('Wavelength Sent: %s' % self.gpib.read()))

    def sweepWavelengthsTriggerSetup (self, start, end, step):
        '''
        Execute a sweep of the wavelength trigger. Have to keep track of Triggers in main command.
        Use Stop Sweep Command to end sweep. Extra triggers do not make the laser sweep outside of specified end wavelength.
        Remeber to shut off laser after sweep ends.


        :param start: Starting point for sweep
        :type start: Float
        :param end: Ending point for sweep
        :type end: Float
        :param step: Size of increment
        :type step: Float
        '''


        if (
            start < self.min_wavelength or
            start > self.max_wavelength or
            end < self.min_wavelength or
            end > self.max_wavelength or
            step < 0.001
            ):
            print ('Specified Wavelengths Out of Range, or Step Too Low')

        else:
            self.sweepstart = float(start)
            self.sweepend = float(end)
            self.sweepstep = float(step)
            self.sweepcurrent = float(start)
            self.setwavelength(start)

    def trigger(self):
        '''
        Trigger the laser
        '''
        if(self.sweepcurrent <self.sweepend and self.sweepcurrent >=self.sweepstart):
            self.sweepcurrent = float(self.sweepcurrent) + float(self.sweepstep)
            self.setwavelength(self.sweepcurrent)

    def startSweep(self):
        '''
        Start sweep
        '''
        self.setwavelength(self.sweepstart)

    def pauseSweep(self):
        '''
        Pause sweep
        '''
        self.gpib.write('WA')

    def stopSweep(self):
        '''
        Stop the sweep
        '''
        self.outputOFF()

    def checkStatus(self):
        '''
        Check the status of the instrument

        :returns: Booleans
        '''
        try:
            self.gpib.write('SU')
            status = int (self.gpib.read())
            if status > 0:
                return True
            else:
                return False
        except Exception:
            time.sleep(0.2)
            return self.checkStatus()

    def outputON(self):
        '''
        Turns output of laser source ON.
        '''
        self.gpib.write('LO') # turn on diode

    def outputOFF(self):
        '''
        Turns output of laser source OFF. Output occasionally doesn't turn off unless turned ON beforehand
        '''
        self.gpib.write('LF') # turn off diode

    def getwavelength(self):
        '''
        Query the current wavelength

        :returns: Float
        '''
        self.gpib.write('WA')
        return float(self.gpib.read())

    def setpower(self, power):
        '''
        Set power in dbm

        :param power: power specified to set
        :type power: Float
        '''
        self.gpib.write('OP' + str(power))

    def getpower(self):
        '''
        Gets output power in dbm

        :returns: Float
        '''
        self.gpib.write('OP')
        return float(self.gpib.read())

    def setcurrent(self, current):
        '''
        Set the current. Note: current is mA

        :param current: specified current to set
        :type current: Integer
        '''
        self.gpib.write('CU' + str(current))

    def getcurrent(self):
        '''
        Queries the current, Note: current is mA

        :returns: Float
        '''
        self.gpib.write('CU')
        return float(self.gpib.read())

    def settemperature(self, temperature):
        '''
        Set the temperature. Note: temperature is C

        :param temperature: specified temperature to set
        :type temperature: Integer
        '''
        self.gpib.write('TL' + str(temperature))

    def gettemperature(self):
        '''
        Queries the temperature, Note: temperature is C

        :returns: Float
        '''
        self.gpib.write('TL')
        return float(self.gpib.read())

    def setACC(self):
        '''
        Sets the ACC
        '''
        self.gpib.write('AO')

    def setAPC(self):
        '''
        Sets the APC
        '''
        self.gpib.write('AF')

    def getstatus(self):
        '''
        Queries the status of the...

        :returns: String
        '''
        self.gpib.write('SU')
        return self.gpib.read()

    def setpowermw(self, powermw):
        '''
        Sets the powerMW

        :param powerMW: specified powerMW to set
        :type powerMW: Integer
        '''
        self.gpib.write('LP' + str(powermw))

    def getpowermw(self):
        '''
        Queries the status of the powerMW

        :returns: Float
        '''
        self.gpib.write('LP')
        return float(self.gpib.read())

    def coherenceON(self):
        '''
        Turns coherence ON
        '''
        self.gpib.write('CO')

    def coherenceOFF(self):
        '''
        Turns coherence OFF
        '''
        self.gpib.write('CF')

    def setcoherence(self, coherence):
        '''
        Sets the coherence

        :param coherence: Specified coherence
        :type coherence: Integer
        '''
        self.gpib.write('CV' + str(coherence))

    def getcoherence(self):
        '''
        Queries the coherence value

        :returns: Float
        '''
        self.gpib.write('CV')
        return float(self.gpib.read())


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
