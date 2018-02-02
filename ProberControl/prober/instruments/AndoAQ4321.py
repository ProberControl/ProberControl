import time
#import visa

class AndoAQ4321(object):
    '''
    This class models the AndoAQ4321 laser.

    .. note:: When using any laser command, remember to send shut-off-laser command at the end of each sweep command set.
        For Trigger Sweep, send shut-off-laser command after sweep ends (sweep end condition noted in TriggerSweepSetup function)
    '''

    def __init__(self, res_manager, address='GPIB0::24::INSTR'):
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

        self.gpib = res_manager.open_resource(address)
        self.gpib.write('PASSWORD4321')

        self.gpib.write('INIT')
        self.gpib.write ('IDN?')
        info = self.gpib.read()
        print ('Connection Successful: %s' % info)

        self.gpib.write ('LOCK?')
        info = self.gpib.read()
        print('Locked: %s' %info)

        #Ensure Output is OFF
        self.gpib.write ('L0')

        #Check Output Status
        time.sleep(0.55)
        self.gpib.write ('L?')
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

        if wavelength < 1520 or wavelength > 1620:
            print ('Specified Wavelength Out of Range')
        else :
        # Execute setting of wavelength
            self.gpib.write('TWL ' + str(wavelength))
            time.sleep(0.55)
            self.gpib.write('TWL?')
            info = self.gpib.read()
            print ('Wavelength Sent: %s' % info)

            self.gpib.write('L1')

            #High for test period
            while self.checkStatusSingle() == False:
                time.sleep(0.1)
                # Print if successful
            print('Single Wavelength Complete')

    def sweepWavelengthsStep (self, start, end, step):
        '''
        Executes a sweep with respect to a specified step

        :param start: Specified wavelength between 1520-1580
        :type start: Integer
        :param end: Specified wavelength between 1520-1580
        :type end: Integer
        :param step: Specified step must be greater or equal to than 0.001
        :type step: Float
        '''
        self.outputOFF()

        if (
            float(start) < 1520 or
            float(start) > 1580 or
            float(end) < 1520 or
            float(end) > 1580 or
            float(step) < 0.001
        ):
            print ('Start '+str(float(start))+' End '+str(float(end)))
            print ('Specified Wavelengths Out of Range, or Step Too Low')

        else:
            self.gpib.write('TSWM 0');
            self.gpib.write('TSTAWL ' + str(start))
            self.gpib.write('TSTPWL ' + str(end))
            self.gpib.write('TSTEWL ' + str(step))
            self.gpib.write('TSTET 0.2')    #Time between each step
            self.gpib.write ('L1')
            self.gpib.write('TSGL') #Step Sweep

            #Wait for reception
            while self.checkStatus() == False:
                pass

            # Print when successful
            print ('Sweep Wavelength Step Complete')

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

        self.outputOFF()

        if start < 1520 or start > 1580 or end < 1520 or end > 1580:
            print ('Specified Wavelengths Out of Range')

        else:
            self.gpib.write('TSWM 1')
            self.gpib.write('TSTAWL ' + str(start))
            self.gpib.write('TSTPWL ' + str(end))
            self.gpib.write('TSWET ' + str(time))
            self.gpib.write ('L1')
            self.gpib.write('TSGL') #Single Sweep

            while self.checkStatus() == False:
                pass
            print ('Sweep Wavelength Continuous Complete')

    def sweepWavelengthsTriggerSetup (self, start, end, step):
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
            float(start) < 1520 or
            float(start) > 1580 or
            float(end) < 1520 or
            float(end) > 1580 or
            float(step) < 0.001
        ):
            print ('Specified Wavelengths Out of Range, or Step Too Low')

        else:
            self.gpib.write('TSWM 2')
            self.gpib.write('TSTAWL ' + str(start))
            self.gpib.write('TSTPWL ' + str(end))
            self.gpib.write('TSTEWL ' + str(step))
            self.gpib.write('L1')
            self.gpib.write('TSGL') #Single Sweep
            time.sleep(4)
            print ('Trigger Setup Complete')

    def trigger(self):
        '''Triggers laser'''

        time.sleep(0.4)
        self.gpib.write('TRIG')
        time.sleep(0.05)

    def checkStatus(self):
        '''
        Checks the status of the laser. Handles timeout exception

        :returns: Boolean
        '''

        try:
            self.gpib.write('SRQ3?')
            status = int (self.gpib.read())
            print('Status: %d' %status)
            if status > 0:
                return True
            else:
                return False
        except Exception:
            time.sleep(0.2)
            return self.checkStatus()


    def checkStatusSingle(self):
        '''
        Checks the status of the laser. Handles timeout exception

        :returns: Boolean
        '''

        try:
            self.gpib.write('SRQ0?')
            status = int(self.gpib.read())
            if status > 0:
                return True
            else:
                return False
        except Exception:
            time.sleep(0.2)
            return self.checkStatus()

    def manualStep(self, step):
        '''
        Use if want to manually step by a particular size, in conjuction with Send Single Wavelength

        :param step: specified step increment, but be greater than or equal to 0.001
        :type step: Float
        '''

        if step < 0.001:
                print('Step size cannot be lower than 0.001')
        else:
            self.gpib.write('TSTEWL ' + str(step))
            self.gpib.write('TWLUP')

    def stopSweep(self):
        '''Stop sweep'''
        self.gpib.write('TSTP')

    def pauseSweep(self):
        '''Suspend sweep'''
        self.gpib.write('TPAS')

    def resumeSweep(self):
        '''
        Use after pause to resume, still have to call trigger() for next data point if using with trigger sweep
        '''
        self.gpib.write('TCONT')

    def outputOFF(self):
        '''
        Turns output of laser source OFF

        .. note:: Output occasionally doesn't turn off unless turned ON beforehand
        '''
        self.gpib.write('L0')

    def getwavelength(self):
        '''
        Queries wavelength of the laser

        :returns: Float
        '''
        self.gpib.write('TWL?')
        return float(self.gpib.read())

    def setpower(self,power = 0 ):
        '''
        Sets power in dbm

        :param power: Specified power to set the laser to in dbm
        :type power: Integer
        '''
        self.gpib.write('TPDB ' + str(power))

    def getpower(self):
        '''
        Gets output power in dbm

        :returns: Float
        '''
        self.gpib.write('TPDB?')
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
