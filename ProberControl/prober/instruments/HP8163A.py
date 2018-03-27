#import visa
#import time
#import sys
import struct

class HP8163A(object):
    '''
    This class models a Powermeter Agilent 8163A/B Lightwave Multimeter.
    '''
    CURRENT_CHANNEL = 1

    def __init__(self,res_manager,address='GPIB0::14::INSTR', channel=1):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False
        self.gpib = res_manager.open_resource(address)
        if '.' in str(channel):
			self.__channel = int(channel.split('.')[0])
			self.__port = int(channel.split('.')[1])
        else:
			self.__channel = channel
			self.__port = 1

        # Set Power Unit to dbm
        self.gpib.write('sens1:pow:unit 0')
        self.gpib.write('sens2:pow:unit 0')

    def _checkChannel(self):

        if CURRENT_CHANNEL != self.__channel:
            _setChannel(self.__channel)

    def _setChannel(self, newChannel):
        '''
        The purpose of this method is to change channels
        The syntax of usage will depend on the particular device.
        '''
        pass

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'PowerMeter'

    def get_power(self,wavelength=1550):
        ''' return power meter reading after setting correct wavelength'''
        self.gpib.write('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':pow:wav '+str(wavelength)+'nm')
        return float(self.gpib.query('read'+str(int(self.__channel))+':chan'+str(int(self.__port))+':pow?'))

    def get_feedback(self):
        return self.get_power()


    def close(self):
        '''
        Release resources
        '''
        self.gpib.close()

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def config_meter(self, range):
        if self.__port != 2:
			range = int(range)

			self.gpib.write('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':pow:unit 0')
			#print self.gpib.query('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':pow:unit?')
			self.gpib.write('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':pow:range:auto 0')
			self.gpib.write('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':pow:rang '+str(range)+'DBM')

    def prep_measure_on_trigger(self, samples = 64):
		if self.__port != 2:
			self.gpib.write('*CLS')
			samples = int(samples)

			# self.gpib.write('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':func:stat stab,stop') #switch stab with logg depending
			self.gpib.write('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':func:stat logg,stop') #switch stab with logg depending
			self.gpib.write('trig'+str(int(self.__channel))+':chan'+str(int(self.__port))+':inp sme') #Set up trigger
			print self.gpib.query('trig'+str(int(self.__channel))+':inp?')
			self.gpib.write('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':func:par:logg '+str(samples)+',100us')
			print self.gpib.query('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':func:par:logg?')
			self.gpib.write('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':func:stat logg,start')

			print self.gpib.query('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':func:stat?')
			print self.gpib.query('syst:err?')


    def get_result_from_log(self,samples=64):

        if self.__port != 2:
			print self.gpib.query('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':func:stat?')

        self.gpib.write('sens'+str(int(self.__channel))+':chan'+str(int(self.__port))+':func:res?')
        data = self.gpib.read_raw()
        print self.gpib.query('syst:err?')


        samples = int(samples)

        #print data

        NofDigits = int(data[1])

        HexData = data[2+NofDigits:2+NofDigits+samples*4]

        FloData = []

        for x in range(0, samples*4-1,4):
            dat = HexData[x:x+4]
            val = struct.unpack('<f', struct.pack('4c', *dat))[0]
            FloData.append(val)

        #self.gpib.write('trig'+str(int(self.__channel))+':inp:rearm on')
        return FloData[1:]


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
