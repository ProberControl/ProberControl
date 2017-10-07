# import Polatis

class SwitchHandler(object):
    '''The intention of this class if to provide a general implementation for any kind of fiber switch.
    The key features of the class are get_switch_state(), make_new_connection() and switch_book object.'''

    def __init__(self, configFile, stages, resource):

        self._p = resource
        self.active = False # only for compliance with ScriptController

        self.switch_book = self._readIn(configFile,stages)
        self._connect()

    def get_switch_state(self):
        '''
        Queries all current connections.

        :returns: String of all connections between devices
        '''
        
        formatted_output = ""
        for k,v in self.switch_book.items():
            formatted_output += "{:15} {:20}{:3} {:5} {:10}\n".format(
            'Device',k,v[0],"-->",v[1]
            )
        if formatted_output:
            return formatted_output
        else:
            return "No Connnections Logged"

    def make_new_connection(self, device, egress): 
        '''
        User specified connection between a device and an output port.

        :param devie: Specified device Key according to Stages Dict to be reconnected
        :type device: Str
        :param egress: Specified output port
        :type egress: Int
        '''
        
        ingress = self.switch_book[device][0]
		
        self._p.quick_connect(ingress, int(egress))
		
        self._updateSwitchBook()

    def _readIn(self, configFile,stages):
        '''Reads in the configFile info'''
        switch_book_init = {}
		
        for entry in configFile:
            if entry['O'] != 'Polatis' and 'P' in entry.keys(): #skip the Polatis
                ports = entry['P'].split('>')
                ingress = list(map(int,ports[0].split(',')))
                egress = list(map(int,ports[1].split(',')))
                ports = list(zip(ingress, egress))

                for actualObject in zip(stages.keys(), stages.values()):
                	if entry['O'] == str(actualObject[1]):
                		stage_type = actualObject[1].whoAmI()

				
                for pair in ports:
					if 'N' in entry.keys():
						switch_book_init[stage_type+str(entry['SysChan'])]=pair
					else:
						switch_book_init[stage_type]=pair
						
        return switch_book_init
            
    def _connect(self):
        '''makes connections between ports for SwitchIntegration.__init__()'''
        for k,entry in self.switch_book.items():	
            # Call function for making connections
            self._p.quick_connect(
                ingress=entry[0],
                egress=entry[1]
            )

    ## Thinking about getting rid of this
    ## Why is it here? What was the original intention?
    def _integrateStages(self, stages):  
        '''Integrates the stages dictionary after boot'''
        for actualObject in zip(stages.keys(), stages.values()):
            for k,entry in self.switch_book.items():
                if entry['device'] == str(actualObject[1]):
                    entry['ref'] = actualObject[0]

    def _updateSwitchBook(self):
        '''Updates the global switch_book following a new connection being made'''
        actual = self._p.get_zip_connections()

        for k,entry in self.switch_book.items():
		
            for pair in actual:
                if self._hasChangedOutput(entry, pair): # then this device changed output
                    if entry[0] == pair[0]:
                    	entry = [entry[0],pair[1]]
                    elif entry[0] == pair[1]:
                    	entry = [entry[0],pair[0]]
                    else:
                    	print 'Error encoding switch configuration'
                    self.switch_book[k]=entry
                elif self._hasLostOutput(entry, pair, actual): # then this device changed output
                    entry =[entry[0],'']
		
    def _hasChangedOutput(self, entry, pair):
        '''helper for _updateSwitchBook'''
        if entry[0] in pair:
        	if entry[1] == pair[0] or entry[1] == pair[1]:
        		return False
        	else:
        		return True
        return False

    def _hasLostOutput(self, entry, pair, actual):
        '''helper for _updateSwitchBook'''
        return entry[0] not in [i[0] for i in actual] and entry[0] not in [i[1] for i in actual]

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
