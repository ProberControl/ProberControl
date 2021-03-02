import time
import visa

class EXFOT100_Laser(object):
    '''
    This class models the EXFO T100S-HP laser. There is a
    1260-1360 nm and a 1500-1630 nm version.

    .. note:: When using any laser command, remember to send shut-off-laser command at the end of each sweep command set.
        For Trigger Sweep, send shut-off-laser command after sweep ends (sweep end condition noted in TriggerSweepSetup function)
        Note that these lasers do not have trigger inputs or outputs.
    '''

    def __init__(self, res_manager, address='GPIB0::3::INSTR'):
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
        
        #Default Spectral Unit Selection
        self.gpib.write('NM')
        
        #Get min and max wavelengths
        #self.get_min_wavelength()
        #self.get_max_wavelength()
        
    def whoAmI(self):
        ''':returns: reference to device'''
        return 'Laser'
    
    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True
        print 'state = ', self.active
        
    def chan_enable(self, channel):
        print 'Enable CH' + str(int(channel)) +':ENABLE'
        self.gpib.write('CH' + str(int(channel)) +':ENABLE')
        
    def chan_disable(self, channel):
        print 'Disable CH' + str(int(channel)) +':DISABLE'
        self.gpib.write('CH' + str(int(channel)) +':DISABLE')

    def All_chan_enable(self):
        #Disable the laser output on allinstalled OCICS modules
        self.gpib.write('ENABLE')

    def All_chan_disable(self):
        #Enable the laser output on allinstalled OCICS modules
        self.gpib.write('DISABLE')

        
    def get_type(self, channel): # Updated 11/5/2019 Jim Davis
        '''
        Queries the channel type

        :returns: String
        ''' 
        if (channel == 1) or (channel == 2):
            self.gpib.write ('CH' + str(int(channel)) +':TYPE?')
            self.type = str(self.gpib.read())
        else:
            print 'Channel not yet implemented in driver'
            self.type = ''
        
        return self.type

    def setwavelength(self, channel, wavelength):
        '''
        Loads a single wavelength and channel
        Sets output wavelength
        
        :param waveLength: Specified wavelength
        type channel: int
        :type waveLength: Float
        '''
        wavelength = float(wavelength)
        if channel == 1:
            if  (wavelength < 1260.0) or (wavelength > 1360.0):
               print 'Channel 1 Wavelength setting out of 1260.0 - 1360.0 nm range'
            else:
               self.chan_enable(channel)            # Errors if channel not enabled
               self.gpib.write('CH' + str(int(channel)) + ':L = ' + str(wavelength))
        elif channel == 2:
            if  (wavelength < 1520.0) or (wavelength > 1630.0):
               print 'Channel 2 Wavelength setting out of 1520.0 - 1630.0 range'
            else:
               self.chan_enable(channel)            # Errors if channel not enabled
               self.gpib.write('CH' + str(int(channel)) + ':L = ' + str(wavelength))
        else:
            print 'Channel not yet implemented in driver'    
    
    def checkOPC(self):
         # check OPC bit of STB status bit. Mask out other bits with &
         return (int(self.gpib.write ('*STB?')[0] & 1))

    def getwavelength(self, channel):
        '''
        Queries wavelength of the laser
        Checks wavelength by channel

        :returns: float
        '''
        if (channel == 1) or (channel == 2):
            self.gpib.write('CH' + str(int(channel)) + ':L?')
            return float(self.gpib.read()[6:])
        else:
            print 'Channel not yet implemented in driver'
            return ''            
       
    def setpower(self, channel, power = 0.0 ):
        '''
        Sets power in dbm for channels implement in driver
        Checks range for each laser

        :param power: Specified power to set the laser to in dbm
        :type power: Float
        '''
        power = float(power)      
        if channel == 1:
            if  (power < -6.9) or (power > 11.6):
               print 'Channel 1 Power setting out of -6.9 to +11.6 dBm range'
            else:
               self.gpib.write('CH' + str(int(channel)) +':ENABLE')        
               self.gpib.write('CH' + str(int(channel)) + ':P = ' + str(power))        
        elif channel == 2:
            if  (power < -6.9) or (power > 7.8):
               print 'Channel 2 Power setting out of -6.9 to +7.8 dBm range'
            else:
               self.gpib.write('CH' + str(int(channel)) +':ENABLE')        
               self.gpib.write('CH' + str(int(channel)) + ':P = ' + str(power))        
        else:
            print 'Channel not yet implemented in driver'



    def getpower(self, channel):
        '''
        Gets output power in dbm

        :returns: Float
        '''
        
        if (channel == 1) or (channel == 2):
            self.gpib.write('CH' + str(int(channel)) + ':P?')
            self.power = self.gpib.read()
            return self.power
        else:
            print 'Channel not yet implemented in driver'
            self.power = '' 
            return self.power            
        
    def Coherence_ctrl (self, channel, ctrl):
        '''
        Sets coherence control on for ctrl = 1, off for ctrl = 0
        Returns 0 for Coherence control OFF, 1 for Coherence control ON
        '''
        
        if (channel == 1) or (channel == 2):
            if (ctrl == 0):

                self.gpib.write('CH' + str(int(channel)) + ':CTRL OFF')
                self.gpib.write('CH' + str(int(channel)) + ':CTRL?')
                Coherence = self.gpib.read()
                print 'CH', str(int(channel)), ':CTRL OFF'
                return Coherence[4]
                #print self.gpib.read()[4]
            elif (ctrl == 1):
                self.gpib.write('CH' + str(int(channel)) + ':CTRL ON')
                self.gpib.write('CH' + str(int(channel)) + ':CTRL?')
                Coherence = self.gpib.read()
                print 'CH', str(int(channel)), ':CTRL ON'
                return Coherence[4]
            else:
                print 'Error in ctrl: ON: ctrl=1, OFF: ctrl=0'
                
        else:
            print 'Channel not yet implemented in driver'
            return ''
		
    def close(self):
        '''
        Release resources
        '''
        self.All_chan_disable()
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
