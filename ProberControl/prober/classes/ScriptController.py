import sys, os, csv
from tqdm import tqdm
from Global_MeasureHandler import Global_MeasureHandler
import procedures
import maitre
import inspect

class ScriptController(object):
    '''
    The purpose of this class is to read-in a measurement script, then
    execute the script when appropriate. It also handles  sending
    information to the Global_MeasureHandler about which stages are locked
    for usage. It communicates with GMH directly and the GMH returns data from
    instruments.
    '''

    def __init__(self, maitre, stages, scriptName = '', path = ''):

        self.__configurePaths(scriptName)
    
        self.gh = Global_MeasureHandler(stages) # Handles the stages
        self.maitre = maitre # Handles the structures and procedures

    def read_execute(self):
        self.script = self.read_script() # Read in the script to be executed
        self.scriptHash = id(self) # get the hash for the script
        self.__reportLocked()
        self.execute_script()

    def __reportLocked(self):
        for entry in self.script:
            if 'lock' in entry.keys():
                self.gh.add_locked_instrument(self.scriptHash, entry['stage'])

    def __configurePaths(self, scriptName):
        # This will be different depending on how the program was launched
        pwd = os.path.abspath(path='.')
        if (pwd.split('\\')[-1:][0]=='server'): # Launched via ethernet
            self.pwd = pwd
            self.configPath = os.path.join(self.pwd, scriptName)
            self.coordinatePath = os.path.join(self.pwd, 'Coordinates.conf')
            self.resultsPath = self.pwd
        else: # conventional launch
            self.pwd = os.path.abspath(path='.\\..\\')
            self.configPath = os.path.join(self.pwd, 'config\\'+scriptName)
            self.coordinatePath = os.path.join(self.pwd, 'config\\Coordinates.conf')
            self.resultsPath = os.path.join(self.pwd, 'config\\')

    def execute_script(self, path = 'results.csv'):
        '''Opens the results file and executes experiments according to the configuration files'''
        path = os.path.join(self.resultsPath, path)
        with open(path, 'w') as file:

            # tqdm for progress bar
            for entry in tqdm(self.script):

                # If it is a function of a particular stage
                if 'stage' in entry.keys():
                    self._stageFunction(entry, file)

                # If it is a procedure
                elif 'structure' in entry.keys() and 'procedure' in entry.keys():
                    self._structureProcedure(entry, file)

                # If it is a procedure that doesn't need a structure
                elif 'procedure' in entry.keys() and 'structure' not in entry.keys():
                    self._procedure(entry, file)

                # If executing a function or procdure on a particular chip
                elif 'chip' in entry.keys():
                    self._chipFunction(entry, file)

        # Release all instruments that were associated with this script
        self.gh.clear_locked(self.scriptHash)

    def _stageFunction(self, entry, file):
        '''Executes experiment for at the stage level'''
        t = tuple([entry['stage'],entry['function'],entry['arguments']])
        data = "{}\t{}\t{}\n".format(t[0],t[1],t[2])
        try:
            # Execute the function
            data += self.__executeCommand(t[0],t[1],t[2])
            data += '\n'

        except KeyError as e:
            data = "\
            Experiment not executed on {}\
            \nError with configuration file:\n{}".format(t[0], e)

        # Write the results of experiment to file
        self._writeData(file, str(data), False)

    def _structureProcedure(self, entry, file):
        '''Executes experiments at the structural level using Procedures''' 
        if not connecting.connect_structure(
            self.stages,
            self.maitre,
            self.coordinatePath,
            entry['structure'] ):
            # Write the error to the results but keep going
            self._writeData(file, "Error Connecting {}.".format(entry['structure']), True)
        else:
            args = [self.stages, self.maitre]
            for elem in entry['arguments']:
                args.append(elem)

            # Execute the function using maitre
            data = maitre.execute_func_name(entry['procedure'],entry['function'],args)

            # Write the results of the experiment to file
            self._writeData(file, str(data), True, entry)

    def _procedure(self, entry, file):
        '''executes experiments that use heuristic Procedures'''
        args = [self.stages, self.maitre]
        for elem in entry['arguments']:
            args.append(elem)

        # Execute the function using maitre
        data = maitre.execute_func_name(entry['procedure'],entry['function'],args)

        # Write the results of the experiment to file
        self._writeData(file, str(data), procedure=True, entry=entry)

    def _chipFunction(self, entry, file):
        '''Handles experiments at the chip level'''
        pass

    def _writeData(self, openFile, data, procedure, entry = {}):
        '''Takes data and experiment names, if applicable and writes it to a results file'''

        if procedure:
            openFile.write("{}:\n".format(entry['measurement']))
            for pair in data:
                openFile.write("{}\t{}".format(pair[0],pair[1]))
        else:
            for element in data.split(' '):
                openFile.write('{}\t'.format(str(element)))
        
        # Seperate the experiments by two new lines
        openFile.write('\n\n')

    def __executeCommand(self, instrument, function, arguments):
        '''internal method for executing a particular directly with stage.function'''
        try:

            # retrieve the instrument from global_measure_handler object
            instrumentActual = self.gh.get_instrument(instrument)
            if instrumentActual:
                functionActual = getattr(instrumentActual,function)
                return str(functionActual(arguments))
            else:
                return Exception("Instrument {} not available.".format(instrument))
        except AttributeError as e:
            return "Attribute Error Executing: {}\t{}".format(function,e)
        except Exception as e:
            return "Error at __executeCommand(): {}".format(e)

    def read_script(self):
        return self.__readScript()

    def __readScript(self):

        measurement = {}
        measurement_collection = []
        key = ''
        designators = [
            'stage',
            'measurement',
            'structure',
            'function',
            'arguments',
            'procedure',
            'lock',
            'chipID'
        ]

        try:
            with open(self.configPath, 'r') as measurementFile:
                for line in measurementFile:
                    # If there isn't a key yet, assign one
                    if not key:
                        for item in designators: # Possible keys 
                            if self._isDesignator(line, item):
                                key = item; break
                    else:
                        line = line.strip()
                        if key is 'arguments': # preprocess arguments into a list 
                            measurement[key]=[str(i) for i in line.split(' ')]
                        else: # Case for all others just takes data
                            measurement[key]=line
                        key = ''
                        
                    if line == '\n': # When the measurement block is over; seperated by one line
                        measurement_collection.append(measurement)
                        measurement = {}

                # If the measurement config file ended without a new line character,
                # add the last block to the collection
                if measurement:
                    measurement_collection.append(measurement)
                        
            if len(measurement_collection) == 0:
                print("Something might be wrong with your Measurement.conf, read-in is empty.")

            return measurement_collection
        except IOError as e:
            raise IOError("Error reading in configuration file:\n{}".format(e))

    def _isDesignator(self, line, designation):
        '''Helper function for designators'''
        if line[0] == '#' and designation in line.lower():
            return True
        else:
            return False


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
