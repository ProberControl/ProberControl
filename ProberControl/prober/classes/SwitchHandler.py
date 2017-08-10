# import Polatis

class SwitchHandler(object):
    '''The intention of this class if to provide an implementation of the Polatis switch.
    The key features of the class are get_switch_state(), make_new_connection() and switch_book object.'''

    def __init__(self, configFile, stages, resource):

        self._p = resource

        self.switch_book = self._readIn(configFile)
        self._connect()

        # See note at the method definition
        # self._integrateStages(stages)

    def get_switch_state(self):
        '''
        Queries all current connections.

        :returns: String of all connections between devices
        '''
        
        formatted_output = ""
        for entry in self.switch_book:
            formatted_output += "{:15} {:20}{:3} {:5} {:10}\n".format(
            'Device',entry['device'],entry['ingress'],"-->",entry['egress']
            )
        if formatted_output:
            return formatted_output
        else:
            return "No Connnections Logged"

    def make_new_connection(self, ingress, egress): 
        '''
        User specified connection between device ingress port and output port.

        :param ingress: Specified input port
        :type ingress: Int
        :param egress: Specified output port
        :type egress: Int
        '''
        
        self._p.quick_connect(ingress, egress)
        self._updateSwitchBook()

    def _readIn(self, configFile):
        '''Reads in the configFile info'''
        switch_book_init = []
        for entry in configFile:
            if entry['O'] != 'Polatis' and 'P' in entry.keys(): #skip the Polatis
                ports = entry['P'].split('::')
                ingress = ports[0].split(',')
                egress = ports[1].split(',')
                ports = zip(ingress, egress)

                for pair in ports:
                    new_entry = {}
                    new_entry['ingress'] = pair[0]
                    new_entry['egress'] = pair[1]
                    new_entry['device'] = entry['O']
                    switch_book_init.append(new_entry)
                
        return switch_book_init
            
    def _connect(self):
        '''makes connections between ports for SwitchIntegration.__init__()'''
        for entry in self.switch_book:
            # Call function for making connections
            self._p.quick_connect(
                ingress=entry['ingress'],
                egress=entry['egress']
            )

    ## Thinking about getting rid of this
    ## Why is it here? What was the original intention?
    def _integrateStages(self, stages):  
        '''Integrates the stages dictionary after boot'''
        for actualObject in zip(stages.keys(), stages.values()):
            for entry in self.switch_book:
                if entry['device'] == str(actualObject[1]):
                    entry['ref'] = actualObject[0]

    def _updateSwitchBook(self):
        '''Updates the global switch_book following a new connection being made'''
        actual = self._p.get_zip_connections()
        for entry in self.switch_book:
            for pair in actual:
                if self._hasChangedOutput(entry, pair): # then this device changed output
                    entry['egress'] = pair[1]
                elif self._hasLostOutput(entry, pair, actual): # then this device changed output
                    entry['egress'] = ''
                    
    def _hasChangedOutput(self, entry, pair):
        '''helper for _updateSwitchBook'''
        return pair[0] == entry['ingress'] and pair[1] != entry['egress']

    def _hasLostOutput(self, entry, pair, actual):
        '''helper for _updateSwitchBook'''
        return entry['ingress'] not in [i[0] for i in actual]

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
