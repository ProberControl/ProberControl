# import visa
import datetime
from time import sleep

# DEBUG flag
debug = 0
def sdebug(msg):
    if debug > 0:
        print 'Polatis:: {}'.format(msg)

class Polatis(object):
    '''
    This class models the Polatis 16x16 optical switch. Dependencies: PyVisa, datetime, time.

    .. note:: there are a handful of sleep() calls throughout the class that slow down the performance of the switch. This is beacuase the firmware on the switch is not stable enough to support commands executed at high-speeds.
    '''

    def __init__(self, rm, address):
        self.active = False
        self._switch = self.__getResource(rm, address)

    def __getResource(self, rm, address):
        '''Handles errors for constructor method'''

        try:
            switch = rm.open_resource(address) # instantiate our resource object
            print('Resource Initialized: %s' % str(switch.query('*IDN?')))
            return switch
        except Exception as e:
            raise Exception(e)

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'switch'

    def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

    def get_all_connections(self):
        '''
        Query the existing complete switch state in the form of port pair lists

        :returns: String
        '''
        try:
            connections = str(self._switch.query(':oxc:swit:conn:stat?'))
        except Exception as e:
            print('Error:' + e)
            print('Querying again.')
            connections = str(self._switch.query(':oxc:swit:conn:stat?'))
        return connections[:-2]

    def get_port_state(self, portNumber):
        '''
        Query the port connected to the specified port <NR1>

        :param portNumber: integer of desired port to query
        :type portNumber: integer
        :returns:  String
        '''
        sleep(.1)
        to_return = str(self._switch.query(':oxc:swit:conn:port? %d' % portNumber))
        return to_return[:-2]

    def reset(self):
        '''Resets the instrument and disconnects all connections'''

        sleep(.1)
        self._switch.write('*RST;')

    def close(self):
        '''instrument cleanup'''
        self.reset()

    def quick_connect(self, ingress=0, egress=0):
        '''

        Allows the user to quickly make a connection between 2 ports

        :param ingress: input port
        :type ingress: integer
        :param egress: output port
        :type egress: integer
        '''

        ingress = int(ingress)
        egress = int(egress)
        
        if ingress > egress:
        	buff = egress
        	egress = ingress
        	ingress = buff

        ingress = self.__formatConventional(str(ingress))
        egress = self.__formatConventional(str(egress))

        ports = ingress+','+egress

        sleep(.1)
        sdebug('sending command to switch >> {}'.format(':oxc:swit:conn:add'+' '+ports+';'))
        self._switch.write(':oxc:swit:conn:add'+' '+ports+';')

    def make_connections(self, ingress, egress, explicit='only'):
        '''

        Makes connections between ports. The ingress range is 1 to 16 and egress range is 16-32. This means that at most 16 connections can be made at one time.

        :param ingress: a collection of input ports
        :type ingress: list of integers
        :param egress: a collection of output ports
        :type egress: list of integers
        :param explicit: The explicit parameter can either be: add, only, sub. Defaults to only, see pg.22 of tech manual for details of each.
        '''

        ports = self.__formatConnections(ingress, egress)

        sleep(.1)
        self._switch.write(':oxc:swit:conn:'+explicit+' '+ports+';')

    def __make_connections(self, ports):
        '''For internal use by the reader function'''

        sleep(.1)
        self._switch.write(':oxc:swit:conn:only'+' '+ports+';')

    def __formatConnections(self, ingress, egress):
        '''
        Formats <ingress> <egress> for querying the device. Indices determine the relationship between the two ports.

        :param ingress: a collection of input ports
        :type ingress: list of integers
        :param egress: a collection of output ports
        :type egress: list of integers
        :returns: String formatted for SCPI
        '''

        ingress = ''.join([str(i)+',' for i in ingress])
        egress = ''.join([str(i)+',' for i in egress])

        ingress = self.__formatConventional(ingress)
        egress = self.__formatConventional(egress)

        return ingress+','+egress

    def __formatConventional(self, toBeFormatted):
        '''
        Format String for query to device

        :param toBeFormatted: String of inputs to be formatted
        :type toBeFormatted: String
        :returns: String
        '''

        if (toBeFormatted[-1:] == ','):
            toBeFormatted = toBeFormatted[:-1] #remove last comma

        toBeFormatted = toBeFormatted[::-1]+'@(' #add conventional format
        toBeFormatted = toBeFormatted[::-1]+')' #closing bracket

        return toBeFormatted

    def get_boot_mode(self):
        '''
        Get the current boot mode, either: DARK, REST, AUT. More detailed documentation at pg.31 PROD-B-100-03-0

        :returns:  String
        '''

        return str(self._switch.query(':oxc:boot:mode?'))

    def set_boot_mode(self, mode='aut'):
        '''
        Allows the user set the boot mode

        :param mode: Possible modes are DARK, RESTore, AUTosave. See pg.31 for details
        :type mode: String
        '''

        self._switch.write(':oxc:boot:mode '+mode+';')

    def cmd_line(self, commands):
        '''
        Allows the user to pass raw commands to the device, the commands are passed in SCPI. See pg.5 PROD-B-100-03-0 for further documentation.

        :param commands: SCPI commands for the instrument
        :type commands: Sting
        :returns: varied
        '''

        commands = [i+';' for i in commands.split(';')]
        replies = [] # Storage for query replies

        for item in commands:
            if item[-1:] == '?': # indication of a query
                replies.append(self.__cmd_handler(item, True))
            else:
                self.__cmd_handler(item)

        return replies

    def __cmd_handler(self, command, query=False):
        '''
        Handles exceptions for raw_function()

        :param command: takes a single command as String
        :type command: String
        :param query: if command is a query, then True. Defaults to False.
        :type query: Boolean
        :returns: a reply if query as String
        :raises: Exception, VisaTimeoutError
        '''

        if query: # expects a reply
            try:
                return self._switch.query(item)
            except Exception as e:
                return e
        else: # expects no reply
            try:
                self._switch.write(command)
            except Exception as e:
                return e

    def write_pattern(self, name='newPattern.txt'):
        '''
        Stores the current pattern associated with the self._switch, writes the to a txt file.

        :param name: desired filename, defaults to newPattern.txt
        :type name: String
        '''

        with open(name, 'w') as f:
            f.write(name+' '+str(datetime.datetime.now())+'\n')
            sleep(.1)
            f.write(self.get_all_connections())

    def read_pattern(self, name='', boot=True):
        '''
        Reads in a pattern that is in store_pattern format.

        :param name: filename for desired pattern to be read, defaults to an empty String.
        :type name: String
        :param boot: Boot == true if you want to load this pattern into the instrument, defaults to True.
        :type boot: Boolean
        :returns: String
        :raises: Exception
        '''

        try:
            with open(name, 'r') as f:
                f.readline()
                pattern = f.readline()
                if boot:
                    self.__bootRead(pattern)
                else:
                    return pattern
        except Exception as e:
            print('Error: ', e)

    def __bootRead(self, pattern):
        '''
        Loads the pattern read from the pattern text file

        :param pattern: pattern read by the file
        :pattern type: String
        '''

        self.reset()

        #call the internal connect0 function
        self.__make_connections(ports=pattern)

    def get_zip_connections(self):
        '''Data Model for to string functionality'''
        connections = self.get_all_connections().split("),(")
        connections[0] = connections[0][2:].split(',')
        connections[1] = connections[1][1:-1].split(',')

        row1 = []
        for elem in connections[0]:
			print elem
			row1.append(int(elem))

        row2 = []
        for elem in connections[1]:
			print elem
			row2.append(int(elem))

        return zip(row1, row2)


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
