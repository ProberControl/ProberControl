import time
import visa

class Keysight8164B_Laser(object):
    '''
    This class models the AndoAQ4321 laser.

    .. note:: When using any laser command, remember to send shut-off-laser command at the end of each sweep command set.
        For Trigger Sweep, send shut-off-laser command after sweep ends (sweep end condition noted in TriggerSweepSetup function)
    '''

    def __init__(self, res_manager, address='GPIB0::1::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: string
        '''

        self.active = False

        self.max_wavelength = 1650
        self.min_wavelength = 1450

        self.gpib = res_manager.open_resource(address)
        self.gpib.write('LOCK 0, 1234')

        self.gpib.write ('*IDN?')
        info = self.gpib.read()
        print ('Connection Successful: %s' % info)

        self.gpib.write ('LOCK?')
        info = self.gpib.read()
        print('Locked: %s' %info)

        #Ensure Output is OFF
        self.gpib.write ('SOURCE0:CHAN1:POW:STATE 0')
		
		#Default Laser Power Unit to dBm
        self.gpib.write ('SOURCE0:CHAN1:POW:UNIT 0')
		
		#Enables Display
        self.gpib.write ('DISP:ENAB 1')

        #Check Output Status
        time.sleep(0.55)
        self.gpib.write ('SOURCE0:CHAN1:POW:STATE?')
        info = self.gpib.read()
        print('Output: %s' %info)

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
        Loads a single wavelength and sets output high

        :param waveLength: Specified wavelength
        :type waveLength: Integer
        '''
        self.outputOFF()

        if wavelength < 1450 or wavelength > 1650:
            print ('Specified Wavelength Out of Range')
        else :
        # Execute setting of wavelength
            self.gpib.write('SOURCE0:CHAN1:WAV ' + str(wavelength)+ "nm")
            print(str(wavelength))
            time.sleep(0.55)
            self.gpib.write('SOURCE0:CHAN1:WAV?')
            info = self.gpib.read()
            print ('Wavelength Sent: %s' % info)

            self.gpib.write('SOURCE0:CHAN1:POW:STATE 1')

            #High for test period
            while self.checkStatusSingle() == False:
                time.sleep(0.2)
                # Print if successful
            print('Single Wavelength Complete')


    def sweepWavelengthsContinuousTriggerOut (self, start, end, step, speed = 1):
        '''
        Executes a sweep, for use with triggered PowerMeters

        :param start: Specified wavelength between 1520-1580
        :type start: Integer
        :param end: Specified wavelength between 1520-1580
        :type end: Integer
        :param speed: Specified nm/s
        :type time: Float
        '''

        self.outputOFF()

        if start < 1450 or start > 1650 or end < 1450 or end > 1650:
            print ('Specified Wavelengths Out of Range')

        else:
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:MODE CONT')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STAR ' + str(start) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STOP ' + str(end) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STEP ' + str(step) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:SPE ' + str(speed) + 'NM/S')
            
			
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:LLOG 0') #Start Logging
            self.gpib.write('TRIG0:CHAN1:OUTP STF') #Trigger on
            self.gpib.write('SOURCE0:CHAN1:AM:STAT OFF') #Disabled Amplitude Modulation
			
            info = int(self.numberOfTriggers())
            print ('Number of Triggers %s' % info)
			
            self.outputON()

    def sweepWavelengthsContinuous (self, start, end, step, speed = 1):
        '''
        Executes a sweep with respect to a specified time

        :param start: Specified wavelength between 1520-1580
        :type start: Integer
        :param end: Specified wavelength between 1520-1580
        :type end: Integer
        :param speed: Specified nm/s
        :type time: Float
        '''

        self.outputOFF()
        self.stopSweep()

        if start < 1450 or start > 1650 or end < 1450 or end > 1650:
            print ('Specified Wavelengths Out of Range')

        else:
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:MODE CONT')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STAR ' + str(start) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STOP ' + str(end) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STEP ' + str(step) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:SPE ' + str(speed) + 'NM/S')
            self.outputON()
			
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STAR?')
            start_1 = self.gpib.read()
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STOP?')
            end_1 = self.gpib.read()
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:SPE?')
            spe_1 = self.gpib.read()
			
            print ('Sweep Parameters: %s %s %s' % (start_1, end_1, spe_1))

            self.startSweep() #Single Sweep

            while self.checkSweepStatus() == False:
				pass
            print ('Sweep Wavelength Continuous Complete')
            self.outputOFF()

    def sweepWavelengthsStep (self, start, end, step, dwell):
        '''
        Have to keep track of Triggers in main command, use Stop Sweep Command to end sweep.
        Extra triggers do not make the laser sweep outside of specified end wavelength.
        Remeber to shut off laser after sweep ends

        :param start: Specified wavelength between 1520-1580
        :type start: Integer
        :param end: Specified wavelength between 1520-1580
        :type end: Integer
        :param time: Specified time
        :type time: Float
        '''

        self.outputOFF()
        self.stopSweep()

        if (
            float(start) < 1450 or
            float(start) > 1650 or
            float(end) < 1450 or
            float(end) > 1650 or
            float(step) < 0.001
        ):
            print ('Specified Wavelengths Out of Range, or Step Too Low')

        else:
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:MODE:STEP')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STAR ' + str(start) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STOP ' + str(end) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STEP ' + str(step) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:DWEL ' + str(dwell) + 'MS')
            self.outputON();
            self.startSweep(); #Single Sweep
            print ('Stepped Sweep Started')
			
    def numberOfTriggers (self):
	'''Number of Triggers for Sweep'''
        self.gpib.write('SOURCE0:CHAN1:WAV:SWE:EXP?')
        info = self.gpib.read()
        print info
        return info

    def trigger(self):
        '''Software Triggers laser'''

        self.gpib.write('SOURCE0:CHAN1:WAV:SWE:SOFT')
		
    def step(self):
        '''Manual Step laser'''

        time.sleep(0.4)
        self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STEP:NEXT')
        time.sleep(0.05)

    def checkSweepStatus(self):
        '''
        Checks the status of the laser. Handles timeout exception

        :returns: Boolean
        '''

        try:
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE?')
            status = int (self.gpib.read())
            #self.gpib.write('SOURCE0:CHAN1:WAV:SWE:FLAG?')
            #print int(self.gpib.read())
            print('.'),
            if status == 0:
                return True
            else:
                return False
        except Exception:
            time.sleep(0.2)
            return self.checkSweepStatus()


    def checkStatusSingle(self):
        '''
        Checks the status of the laser, just once. Handles timeout exception

        :returns: Boolean
        '''

        self.gpib.write('*OPC?')
        status = int(self.gpib.read())
        if status > 0:
			return True
        else:
			return False

    def sweepWavelengthsManual(self, start, end, step):
        '''
        Use if want to manually step by a particular size, in conjuction with Send Single Wavelength

        :param step: specified step increment, but be greater than or equal to 0.001
        :type step: Float
        '''
        self.outputOFF()
        self.stopSweep()

        if (
            float(start) < 1450 or
            float(start) > 1650 or
            float(end) < 1450 or
            float(end) > 1650 or
            float(step) < 0.001
        ):
            print ('Specified Wavelengths Out of Range, or Step Too Low')

        else:
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:MODE:Manual')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STAR ' + str(start) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STOP ' + str(end) + 'NM')
            self.gpib.write('SOURCE0:CHAN1:WAV:SWE:STEP ' + str(step) + 'NM')
            self.outputON();
            self.startSweep(); #Single Sweep
            print ('Manual Setup Complete')
			
			
    def startSweep(self):
        '''Start sweep'''
        self.gpib.write('SOURCE0:CHAN1:WAV:SWE STAR')	

    def stopSweep(self):
        '''Stop sweep'''
        self.gpib.write('SOURCE0:CHAN1:WAV:SWE STOP')

    def pauseSweep(self):
        '''Suspend sweep'''
        self.gpib.write('SOURCE0:CHAN1:WAV:SWE PAUS')

    def resumeSweep(self):
        '''
        Use after pause to resume, still have to call trigger() for next data point if using with trigger sweep
        '''
        self.gpib.write('SOURCE0:CHAN1:WAV:SWE CONT')

    def outputON(self):
        '''
        Turns output of laser source ON
        '''
        self.gpib.write('SOURCE0:CHAN1:POW:STATE 1')
		
    def outputOFF(self):
        '''
        Turns output of laser source OFF

        .. note:: Output occasionally doesn't turn off unless turned ON beforehand
        '''
        self.gpib.write('SOURCE0:CHAN1:POW:STATE 0')

    def getwavelength(self):
        '''
        Queries wavelength of the laser

        :returns: Float
        '''
        self.gpib.write('SOURCE0:CHAN1:WAV?')
        return float(self.gpib.read())

    def setpower(self,power = 0 ):
        '''
        Sets power in dbm

        :param power: Specified power to set the laser to in dbm
        :type power: Integer
        '''
        self.gpib.write('SOURCE0:CHAN1:POW ' + str(power))

    def getpower(self):
        '''
        Gets output power in dbm

        :returns: Float
        '''
        self.gpib.write('SOURCE0:CHAN1:POW?')
        return float(self.gpib.read())

    def reset(self):
        '''
        Release resources
        '''
        self.gpib.write('SOURCE0:CHAN1:WAV:SWE:LLOG 0') #Start Logging
        self.gpib.write('TRIG0:CHAN1:OUTP DIS') #Trigger on
        self.gpib.write('SOURCE0:CHAN1:AM:STAT OFF') #Disabled Amplitude Modulation
		
        return 'Laser Reset'
		
    def close(self):
        '''
        Release resources
        '''
        self.outputOFF()
        self.gpib.close()
		
		
#if __name__ == "__main__":

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
