import sys, os, csv
from tqdm import tqdm
from Global_MeasureHandler import Global_MeasureHandler
from .. import procedures
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

        self.gh = Global_MeasureHandler() # Handles the stages; Do not change this!
        self.maitre = maitre # Handles the structures and procedures
        self.stages = stages
        self.outputMode = None

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
        '''Opens the results file(s) and executes experiments according to the configuration files'''
        with self._OutputConfiguration() as out:

            # tqdm for progress bar
            for entry in tqdm(self.script):

                # If it is a function of a particular stage
                if 'stage' in entry.keys():
                    self._stageFunction(entry, out.getOutFile(entry))

                # If it is a procedure
                elif 'structure' in entry.keys() and 'procedure' in entry.keys():
                    self._structureProcedure(entry, out.getOutFile(entry))

                # If it is a procedure that doesn't need a structure
                elif 'procedure' in entry.keys() and 'structure' not in entry.keys():
                    self._procedure(entry, out.getOutFile(entry))

                # If executing a function or procdure on a particular chip
                elif 'chip' in entry.keys():
                    self._chipFunction(entry, out.getOutFile(entry))

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
            args = self._prepArguments(entry)

            # Execute the function using maitre
            data = maitre.execute_func_name(entry['procedure'],entry['function'],args)

            # Write the results of the experiment to file
            self._writeData(file, data, True, entry['measurement'])

    def _procedure(self, entry, file):
        '''executes experiments that use multiple tools or generalized algorythms'''
        args = self._prepArguments(entry)

        # Execute the function using maitre
        data = self.maitre.execute_func_name(entry['procedure'],entry['function'],args)

        # Write the results of the experiment to file
        self._writeData(file, data, procedure=True, Meas_Name=entry['measurement'])

    def _prepArguments(self, entry):
        '''
            Prepares the arguments for the function to be executed.
            1) Interpretes lists
            2) Swaps Maitre and Stages in if needed by function
        '''
        PreArgList = entry['arguments']
        ArgList=[]

        # String Interpretation
        for elem in PreArgList:
            if '[' in elem:
                SubList=elem.replace('[','').replace(']','').split(',')
                elem=map(float,SubList)
            if 'Stages' in elem:
                elem = self.Stages
            if 'Maitre' in elem:
                elem = self.Maitre
            if str(elem).isdigit():
                elem=float(elem)
            if elem != '':
                ArgList.append(elem)

                direct_list = inspect.getargspec(self.ActiveStageFuncList[self.ActiveStageFunc])[0]
                insert_list = []

                if "Stages" in direct_list:
                    insert_list.append([direct_list.index("Stages"),self.stages])

                if "stages" in direct_list:
                    insert_list.append([direct_list.index("stages"),self.stages])

                if "Maitre" in direct_list:
                    insert_list.append([direct_list.index("Maitre"),self.maitre])

                if "maitre" in direct_list:
                    insert_list.append([direct_list.index("maitre"),self.maitre])

                insert_list.sort(key=operator.itemgetter(0))

                if insert_list != []:
                    for x in insert_list:
                        ArgList.insert(x[0],x[1])
        return ArgList


    def _chipFunction(self, entry, file):
        '''Handles experiments at the chip level'''
        pass

    def _writeData(self, openFile, data, procedure, Meas_Name=''):
        '''Takes data in form of nested (x,y) lists and experiment names, if applicable and writes it to a results file'''

        if procedure:
            if self._test_dim(data) > 2:
        		for substruct in data:
        		    self._writeData(openFile, substruct, procedure, Meas_Name+'_'+str(data.index(substruct)))
            elif self._test_dim(data) ==2:
                self._write_csv(openFile, data ,Meas_Name)
            else:
        		print "Could not write data to file: Error in Data Format"
        else:
            for element in data.split(' '):
                openFile.write('{}\t'.format(str(element)))

        # Seperate the experiments by one extra new lines
        openFile.write('\n')

    def _write_csv(self, openFile, data ,name):
        ''' Writes Single dimensional lists to file'''

        openFile.write("##{}:\n".format(name))
        for pair in data:
            openFile.write("{}\t{} \n".format(pair[0],pair[1]))

    def _test_dim(self, testlist, dim=0):
       """tests if testlist is a list and how many dimensions it has
       returns -1 if it is no list at all, 0 if list is empty
       and otherwise the dimensions of it"""
       if isinstance(testlist, list):
          if testlist == []:
              return dim
          dim = dim + 1
          dim = self._test_dim(testlist[0], dim)
          return dim
       else:
          if dim == 0:
              return -1
          else:
              return dim

    def __executeCommand(self, instrument, function, arguments):
        '''internal method for executing a particular directly with stage.function'''
        try:

            # retrieve the instrument from global_measure_handler object
            instrumentActual = self.gh.get_instrument(instrument)
            if instrumentActual:
                functionActual = getattr(instrumentActual,function)
                print arguments
                print functionActual
                return str(functionActual(*arguments))
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
                groups = self._GroupingInfo()
                line_no = 0
                for line in measurementFile:
                    line_no += 1

                    # Look for output grouping mode
                    if self._checkOutputMode(line, line_no):
                        continue
                    # Look for group designators
                    if self._setGroupingMetadata(line, groups, measurement, line_no):
                        continue

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
                        if len(measurement) != 0:
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

    def _getGroupingDesignator(self, line):
        '''helper: check if line designates wafers chips and sub-groups and return grouping key'''
        if len(line) < 3:
            return None
        possibleKey = line[2:].rstrip().lower()
        if line[0] == '>' and possibleKey in self._GroupingInfo.group_designators:
            return possibleKey
        else:
            return None

    def _handleGroupingDesignators(self, line, groupInfo, measurement, line_no):
        '''
        helper: store intermdiate grouping values before inserting them in
        measurement dicts
        '''
        if not groupInfo.gettingKeyId:
            groupKey = self._getGroupingDesignator(line)
            if groupKey is not None:
                groupInfo.setId(groupKey)
                return True
            else:
                return False
        if line != '\n':
            if self._getGroupingDesignator(line) != None:
                raise KeyError('bad grouping designator (line: {}): did not specify name'.format(line_no - 1))
            groupInfo.keyValue = line.rstrip()
            return True
        if groupInfo.keyValue == None:
            raise KeyError('bad grouping designator (line: {}): did not specify name'.format(line_no - 1))
        else:
            measurement[groupInfo.keyId] = groupInfo.keyValue
            groupInfo.clear()
            return True

        return False

    def _setGroupingMetadata(self, line, groupInfo, measurement, line_no):
        '''
        assign extra grouping information in measurement dicts that help when
        exporting output in different files
        Returns True if it acted signaling the read function that it should not
        parse this line as it does regularly; False otherwise
        '''
        previous = groupInfo.previous
        changed = self._handleGroupingDesignators(line, groupInfo, groupInfo.previous, line_no)
        for key in groupInfo.previous:
            current_res = groupInfo.previous[key]
            if current_res is not None:
                measurement[key] = current_res
        if changed:
            return True
        else:
            return False

    def _checkOutputMode(self, line, line_no):
        outputModeKeyWord = 'group-by: '
        if line.startswith(outputModeKeyWord):
            if self.outputMode is None:
                self.outputMode = line[len(outputModeKeyWord):].rstrip().lower()
            else:
                raise KeyError('.meas > cannot set output mode twice (line:{})'.format(line_no))
            return True
        else:
            return False

    class _GroupingInfo(object):
        '''Class to keep grouping info organized'''
        group_designators = ['wafer', 'chip', 'group']

        def __init__(self):
            self.keyId = None
            self.keyValue = None
            self.gettingKeyId = False
            self.previous = {}
            for key in self.group_designators:
                self.previous[key] = None

        def setId(self, groupId):
            self.keyId = groupId
            self.gettingKeyId = True

        def clear(self):
            self.keyId = None
            self.keyValue = None
            self.gettingKeyId = False

    class _OutputConfiguration(object):
        '''
        This class stores the settings for the presentation of the output.
        e.g. splitting the measurement results to separate files according to
        chip, wafer, etc.
        '''

        def __init__(self, name_convention='.csv', outputMode=None):
            self.FileMap = {}
            self.outputMode = outputMode
            self.name_convention = name_convention

        def __enter__(self):
            '''implementing "with" semantics'''
            return self

        def _generateFileName(self, entry):
            '''
            helper function to generate the names of the output files from
            information
            '''
            dot = self.name_convention.rfind('.')
            default_outputMode = self.outputMode is None or self.outputMode == ''
            identifier = '' if default_outputMode else entry[self.outputMode]
            return self.name_convention[0:dot] + '-' + identifier + sel.name_convention[dot:]


        def getOutFile(self, entry):
            '''get an open file handle from measurement entry struct'''
            filename = self._generateFileName(entry)
            if filename in self.FileMap:
                return self.FileMap[filename]
            else:
                path = os.path.join(self.resultsPath, filename)
                file = open(path, 'w')
                self.FileMap[filename] = file
                return file

        def __exit__(self, type, value, traceback):
            '''implementing "with" semantics'''
            for file in self.FileMap.values():
                file.close()



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
