import time
#import visa

class AnritsuMS2667C(object):
    '''
    This class models a Spectrum Analyzer
    '''

    def __init__(self, res_manager, address='GPIB0::23::INSTR'):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: String
        '''

        self.active = False

        self.gpib = res_manager.open_resource(address)
        self.gpib.write('INI')
        time.sleep(0.55)
        self.gpib.write ('*IDN?')
        info = self.gpib.read()
        info = info.strip()
        print ('Connections Successful: %s' %info)

        self.gpib.write('RL 30DBM') #reference level is 30 dBm, corresponds to 10Vpp

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'RFMeter'

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def waveformReadCentral(self, central, span, resolutionStep = 1):
        '''
        Queries the wave form

        :param central: Specified central
        :type central: Float
        :param span: Specified span
        :type span: Float
        :param resolutionStep: Defaults to 1; specified step size
        :type resolutionStep: Integer
        :returns: List of readings
        '''

        self.gpib.write('CF %dMHZ' % central) # all in MHz
        self.gpib.write('SP %dMHZ' % span)
        self.gpib.write('TS') #take sweep

        self.gpib.write('BIN 0')

        eSpecValues = []
        counter = 0

        while (counter <= 500):

            self.gpib.write('XMA? %d, %d' % (counter, resolutionStep))
            eSpecValues.append(float(self.gpib.read()))
            counter = counter + resolutionStep

        return eSpecValues

    def waveformReadRange(self, start, end, resolutionStep = 1):
        '''
        Queries the wave form

        :param start: Specified start
        :type start: Float
        :param end: Specified end
        :type end: Float
        :param resolutionStep: Defaults to 1; specified step size
        :type resolutionStep: Integer
        :returns: List of readings
        '''

        self.gpib.write('FA %dMHZ' % start) # all in MHz
        self.gpib.write('FB %dMHZ' % end)
        self.gpib.write('TS') #take sweep

        self.gpib.write('BIN 0')

        eSpecValues = []
        counter = 0

        while (counter <= 500):

            self.gpib.write('XMA? %d, %d' % (counter, resolutionStep))
            eSpecValues.append(float(self.gpib.read()))
            counter = counter + resolutionStep

        return eSpecValues

    def getPeak(self, central, span):
        '''
        Queries the peak for a specified central and span.

        :param central: Specified central
        :type central: Float
        :param span: Specified span
        :type span: Float
        :returns: Tuple of readings
        '''

        self.gpib.write('CF %dMHZ' % central) # all in MHz
        self.gpib.write('SP %dMHZ' % span)
        self.gpib.write('TS') #take sweep


        self.gpib.write('MKR 0') # all in MHz
        self.gpib.write('MKPK')
        self.gpib.write('MKF?')
        peakfreq = float(self.gpib.read())

        self.gpib.write('MKL?')
        level = float(self.gpib.read())

        return (peakfreq, level)


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
