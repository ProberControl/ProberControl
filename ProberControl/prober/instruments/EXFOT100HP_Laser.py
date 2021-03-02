import time
import visa

class EXFOT100HP_Laser(object):
    '''
    This class models the EXFO T100S-HP laser. There is a
    1260-1360 nm and a 1500-1630 nm version.

    .. note:: When using any laser command, remember to send shut-off-laser command at the end of each sweep command set.
        For Trigger Sweep, send shut-off-laser command after sweep ends (sweep end condition noted in TriggerSweepSetup function)
        Note that these lasers do not have trigger inputs or outputs.
    '''

    def __init__(self, res_manager, address='GPIB0::2::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: string
        '''

        self.active = False

        self.gpib = res_manager.open_resource(address)
        
        self.gpib.write ('*IDN?')
        info = self.gpib.read()
        print ('Connection Successful: %s' % info)
        
        #Ensure Output is OFF
        self.gpib.write ('DISABLE')
		
		#Default Laser Power Unit to dBm       
        self.gpib.write ('DBM')
        
        #Set system operation to constant power models
        self.gpib.write ('APCON')
        
        #Get min and max wavelengths
        self.get_min_wavelength()
        self.get_max_wavelength()
        
    def whoAmI(self):
        ''':returns: reference to device'''
        return 'Laser'
    
    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True
        print 'state = ', self.active

    def get_max_wavelength(self): # Updated 9/20/2019 Jim Davis
        '''
        Queries the maximum allowed wavelength

        :returns: Float
        '''        
        self.gpib.write ('L? MAX')
        
        self.max_wavelength = float(self.gpib.read()[2:])
        print 'Wavelength Max: ',  self.max_wavelength, 'nm'
        return self.max_wavelength

    def get_min_wavelength(self): # Updated 9/20/2019 Jim Davis
        '''
        Queries the minimum allowed wavelength

        :returns: Float
        '''
        self.gpib.write ('L? MIN')
        self.min_wavelength = float(self.gpib.read()[2:])
        print 'Wavelength Min: ',  self.min_wavelength, 'nm'     
        return self.min_wavelength

    def setwavelength(self, wavelength):
        '''
        Loads a single wavelength and sets output on

        :param waveLength: Specified wavelength
        :type waveLength: Integer
        '''
        self.outputOFF()

        if wavelength < self.min_wavelength or wavelength > self.max_wavelength:
            print ('Specified Wavelength Out of Range: ' +str(wavelength))
        else :
        # Execute setting of wavelength
            self.gpib.write('L = ' + str(wavelength))
            print(str(wavelength))
            time.sleep(0.55)
            self.gpib.write('L?')
            info = self.gpib.read()
            print ('Wavelength Sent: %s' % info)

            #self.gpib.write('SOURCE0:CHAN1:POW:STATE 1')
            self.outputON()


    def sweepWavelengthsContinuous (self, start, end, power):
        '''
        Executes a continuous sweep, not for use with triggered PowerMeters

        :param start: Specified wavelength between 1260-1360 nm, or 1500-1630 nm
        :type start: Float
        :param end: Specified wavelength between 1260-1360 nm, or 1500-1630 nm
        :type end: Float
        :param power: Specified power for sweep
        :type power: Float
        :Note: motor_speed is calculated from end - start to be < 2 seconds
        :to avoid a timeout from PyVisa before laser scan completes
        '''

        self.outputOFF()
        
        # time to wait before checking OPC = operation complete bit
        sleepTime = 0.01
        
        # Calcualte motor speed to key scan time < 2 s
        wavelength_span = (end - start)
        max_scan_time = 2.0 #s
        #reverse ordered to make search easy
        motor_speed_list = [100,67,50,40,33,29,25,22,20,18,17,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1]
        for x in motor_speed_list:
           scan_time = wavelength_span /x 
           if scan_time < max_scan_time:
              new_scan_time = scan_time
              print ' new_scan_time',new_scan_time
              print 'speed = ', 
        motor_speed = wavelength_span / new_scan_time
        print 'scan motor_speed = ', motor_speed
        print 'scan_time = ', new_scan_time
        
        if (start < self.min_wavelength 
        or start > self.max_wavelength 
        or end < self.min_wavelength 
        or end > self.max_wavelength
        or end <= start):
            print ('Specified Wavelengths Out of Range')

        else:
             while not self.checkOPC():
                time.sleep(sleepTime) 
             else:
                self.setpower(power)

             while not self.checkOPC():
                time.sleep(sleepTime) 
             else:
                self.setwavelength(start)
             
             while not self.checkOPC():
                time.sleep(sleepTime) 
             else:                  
                self.gpib.write('MOTOR_SPEED ' +str(motor_speed))
             
             while not self.checkOPC():
                time.sleep(sleepTime) 
             else:                  
                self.gpib.write('ACTCTRLON')
                         
             while not self.checkOPC():
                time.sleep(sleepTime) 
             else:                  
                self.setwavelength(end)
                print 'setwavelength(end)'
             
             # maximum motor speed to return
             while not self.checkOPC():
                print 'INSIDE not self.checkOPC'
                time.sleep(sleepTime) 
             else:                  
                self.gpib.write('MOTOR_SPEED = ' + '100')
                self.gpib.write('MOTOR_SPEED?')                
                print 'MOTOR_SPEED = ', self.gpib.read()
             
             while not self.checkOPC():
                time.sleep(sleepTime) 
             else:                  
                self.gpib.write('ACTCTRLOFF')
                
    def checkOPC(self):
         # check OPC bit of STB status bit. Mask out other bits with &
         return (int(self.gpib.write ('*STB?')[0] & 1))

    def outputON(self):
        '''
        Turns output of laser source ON
        '''
        self.gpib.write('ENABLE')
		
    def outputOFF(self):
        '''
        Turns output of laser source OFF

        '''
        self.gpib.write('DISABLE')

    def getwavelength(self):
        '''
        Queries wavelength of the laser

        :returns: Float
        '''
        self.gpib.write('L?')
        return float(self.gpib.read()[2:])

    def setpower(self, power = 0.0 ):
        '''
        Sets power in dbm

        :param power: Specified power to set the laser to in dbm
        :type power: Float
        '''
        power = float(power)
        if  (power < -6.99) or (power > 13.4):
           print 'Power setting out of -6.99 to +13.4 dBm range'
        else:
           self.gpib.write('P = ' + str(power))

    def getpower(self):
        '''
        Gets output power in dbm

        :returns: Float
        '''
        self.gpib.write('P?')
        self.power = self.gpib.read()
        print 'power read as: ', type(self.power), self.power
        if self.power[0:2] == 'P=':
            print 'Laser ENABLED'
            self.power = float(self.power[2:])
        else:
            print 'Laser DISABLED'
            self.power = 'DISABLED'
           
        return self.power
		
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
