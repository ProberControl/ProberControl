# import Polatis
import re

# DEBUG flag
debug = 0
def sdebug(msg):
    if debug > 0:
        print 'SwitchHandler:: {}'.format(msg)

def _debug_setup(filename):
    class flushFile(object):
        def __init__(self, fileL):
            if debug == 0:
                return
            self.fileL = open(fileL, 'w')
        def writef(self, msg):
            if debug == 0:
                return
            self.fileL.write(msg + '\n')
            self.fileL.flush()
    logfile = flushFile(filename)
    return logfile

class SwitchHandler(object):
    '''The intention of this class if to provide a general implementation for any kind of fiber switch.
    The key features of the class are get_switch_state(), and switch_book object.'''

    def __init__(self, configFile, stages, resource):

        if not resource:
            raise ValueError('SwitchHandler:: invalid raw_switches dict passed in costructor')
        self._p = resource
        self.active = False # only for compliance with ScriptController

        sdebug('reading config file to fill in switch book...')
        self.switch_book = self._readIn(configFile,stages)
        sdebug('switch book complete.')

        self.active_connetions = {}

    def get_switch_state(self):
        '''
        Queries all current connections.

        :returns: String of all connections between devices
        '''
        #NOTE needs update w/ multiple switches

        formatted_output = ""
        for k,v in self.active_connetions:
            k_name, k_switch = k
            v_name, v_switch = v
            formatted_output += "{:20} : {:20} {:5} {:20} {:20}\n".format(
            k_name,
            '{}[{}]'.format(*k_switch),
            "--->",
            v_name,
            '{}[{}]'.format(*v_switch),
            )
        if formatted_output:
            return formatted_output
        else:
            return "No Connnections Logged"

    def connect_devices(self, in_device, out_device):
        '''
        Connect two devices together:
            in_device::out ---> out_device::in
        '''

        (_, pair_in), (pair_out, _) = (self.switch_book[in_device], self.switch_book[out_device])
        if pair_in[0] != pair_out[0]:
            raise RuntimeError('SwitchHandler:: Asked to connect devices ({}, {}) attached to separate switches.'.format(in_device, out_device))

        ingress = pair_in[1]
        egress  = pair_out[1]

        sdebug('connecting {}[{} - {}]'.format(switch_in, gress, egress))

        self._p[pair_in[0]].quick_connect(ingress, egress)

        # log the connection
        self.active_connetions[(in_device, pair_in)] = (out_device, pair_out)

    def _readIn(self, configFile,stages):
        '''Reads in the configFile info'''
        switch_book_init = {}

        bug = _debug_setup('switch_handler_debug.txt')
        bug.writef('stages: {}'.format(stages))

        for entry in configFile:
            if entry['O'] != 'Polatis' and 'P' in entry.keys(): #skip the Polatis
                bug.writef('\nentry: ' + str(entry))
                # continue parsing
                ports = list(map(lambda x: x.strip(), entry['P'].split('>')))
                if len(ports) == 1 or len(entry['P'].strip()) == 1:
                    # User didn't specify '>' or just declared '>'
                    raise AttributeError('Invalid switch port decalration in Config File. Hint: {}'.format(entry))

                ingress = []
                egress = []
                if len(ports[0].strip()) == 0:
                    # we only have output ports
                    bug.writef('we only have output ports')
                    egress = list(map(lambda x: _parseSwitchPair(x), ports[1].split(',')))
                    ingress = [None] * len(egress)
                elif len(ports[1].strip()) == 0:
                    # we only have input ports
                    bug.writef('we only have input ports')
                    ingress = list(map(lambda x: _parseSwitchPair(x), ports[0].split(',')))
                    egress = [None] * len(ingress)
                else:
                    # both input and output ports have been specified
                    bug.writef('both input and output ports have been specified')
                    ingress = list(map(lambda x: self._parseSwitchPair(x), ports[0].split(',')))
                    egress = list(map(lambda x: self._parseSwitchPair(x), ports[1].split(',')))

                ports = list(zip(ingress, egress))
                bug.writef('ports: ' + str(ports))

                for actualObject in zip(stages.keys(), stages.values()):
                    if entry['OBJ'] == actualObject[1]:
                        stage_name = actualObject[0]

                        bug.writef('stage_type: ' + str(stage_name))

                        for pair in ports:
                            switch_book_init[stage_name]=pair
                            bug.writef('inserted: {} --> {}'.format(stage_name, str(pair)))

        return switch_book_init

    def _parseSwitchPair(self, formatted):
        # parse out the raw_switch_id and port from -> SwitchId[PortNumber]
        bracket_match = re.match(r'\s*(\w+)\s*\[\s*(\w+)\s*\]', formatted)
        if not bracket_match:
            raise ValueError('Incorrect port specification in {}. Expected SwitchId[PortNo]\nHint: {}'.format(entry['P'], entry))
        switch, port_s = bracket_match.groups()
        return switch, port_s


    ## NOTE Thinking about getting rid of this
    def _integrateStages(self, stages):
        '''Integrates the stages dictionary after boot'''
        for actualObject in zip(stages.keys(), stages.values()):
            for k,entry in self.switch_book.items():
                if entry['device'] == str(actualObject[1]):
                    entry['ref'] = actualObject[0]


    def whoAmI(self):
        return 'SwitchHandler'

    def __str__(self):
        return ''


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
