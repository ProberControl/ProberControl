import sys, os, csv
from tqdm import tqdm
from Global_MeasureHandler import Global_MeasureHandler
from .. import procedures
import maitre
import inspect
import tkMessageBox
from Queue import Queue

from DataIO import DataIO

class ScriptController(object):
    '''
    The purpose of this class is to read-in a measurement script, then
    execute the script when appropriate. It also handles sending
    information to the Global_MeasureHandler about which stages are locked
    for usage. It communicates with GMH directly and the GMH returns data from
    instruments.
    '''

    def __init__(self, maitre, stages, scriptName = '', path = '', queue = None):

        self.__configurePaths(scriptName)

        self.gh = Global_MeasureHandler() # Handles the stages; Do not change this!
        self.maitre = maitre # Handles the structures and procedures
        self.stages = stages
        self.outputMode = None
        self.defaultBinFunc = None
        self.binningMode = None
        self.upQueue = queue
        self.downQueue = Queue()

    def read_execute(self):
        self.script = self.read_script() # Read in the script to be executed
        self.scriptHash = id(self) # get the hash for the script
        self.execute_script()

    def __configurePaths(self, scriptName):
        # This will be different depending on how the program was launched
        pwd = os.path.abspath(path='.')

        self.pwd = os.path.abspath(path='.\\..\\')
        self.configPath = os.path.join(self.pwd, 'ProberControl\\config\\'+scriptName)
        self.coordinatePath = os.path.join(self.pwd, 'ProberControl\\config\\Coordinates.conf')
        self.resultsPath = os.path.join(self.pwd, 'ProberControl\\config\\')

    def _promptForErrorHandling(self,text):
          self.upQueue.put((tkMessageBox.askquestion,('Prober Error', 'Could the Error be manually resolved ? \n Details: \n'+text),{},self.downQueue))
          return 'yes' == self.downQueue.get()

    def execute_script(self, path = 'results.csv'):
        '''Opens the results file(s) and executes experiments according to the configuration files'''
        with self._OutputConfiguration(self._GroupingInfo.group_designators,self.resultsPath, 'ResultsForID.csv', self.outputMode) as out:

            # Save initial chip and wafer
            # Load first Chip
            if 'chip' in self.script[0].keys():
                # Before loading first chip check state of MProber if connected
                if not self._checkProberState():
                    return
                # Load chip
                if not self._loadChip(self.script[0]['chip']):
                    return

                old_chip = self.script[0]['chip']

            if 'wafer' in self.script[0].keys():
                old_wafer = self.script[0]['wafer']

            # tqdm for progress bar
            for entry in tqdm(self.script):

                # Check whether the binning mode is chip and if a new chip block has begun
                # If yes possibly start local or default binning function
                # Store Old Die
                # Load New Die
                if self.binningMode == 'chip' and 'chip' in entry.keys():
                    if old_chip != entry['chip']:
                        print "\n Finished Measurement Block of "+old_chip

                        args = [old_chip]+out.getRelatedFiles(self.script,self.binningMode,old_entry)
                        binningResult = self._callBinningFunction(old_entry,args)
                        self._storeBinningResult(old_chip, binningResult)

                        self._storeChip(old_chip,binningResult)
                        self._loadChip(entry['chip'])

                        old_chip = entry['chip']

                # Check whether the binning mode is 'wafer' and if a new wafer block has begun
                # If yes possible start local or default binning function
                if self.binningMode == 'wafer' and 'wafer' in entry.keys():
                    if old_wafer != entry['wafer']:
                        print "\n Finished Measurement Block of "+old_wafer

                        args = [old_wafer]+out.getRelatedFiles(self.script,self.binningMode,old_entry)
                        binningResult = self._callBinningFunction(old_entry,args)
                        self._storeBinningResult(old_wafer, binningResult)

                        old_wafer = entry['wafer']

                # If it is a procedure
                elif 'structure' in entry.keys() and 'procedure' in entry.keys():
                    if not self._structureProcedure(entry, out.getOutFile(entry)):
                        break

                # If it is a procedure that doesn't need a structure
                elif 'procedure' in entry.keys() and 'structure' not in entry.keys():
                    self._procedure(entry, out.getOutFile(entry))

                # Safe old entry if wafer/chip stage is happening in next entry
                old_entry = entry

                # release locked user instruments
                self.gh.release_current_user_instruments()

        # check whether last wafer/chip needs to be binned and stored
        if self.binningMode == 'wafer' and old_wafer:
            print "Finished Measurement Block of "+old_wafer
            args = [old_wafer]+out.getRelatedFiles(self.script,self.binningMode,old_entry)
            binningResult = self._callBinningFunction(old_entry,args)
            self._storeBinningResult(old_wafer, binningResult)

            self._freeProber()
        elif self.binningMode == 'chip' and old_chip:
            print "Finished Measurement Block of "+old_chip
            args = [old_chip]+out.getRelatedFiles(self.script,self.binningMode,old_entry)
            binningResult = self._callBinningFunction(old_entry,args)
            self._storeBinningResult(old_chip,binningResult)

            self._storeDie(old_chip,binningResult)


    def _loadChip(self,chipId):
        '''
        Function sends the command to load chip with certain id on measurement platform.

        If Prober is present and provides load_chip() function
        '''
        if 'MProber' in self.stages.keys():
            if 'load_chip' in dir(self.stages['MProber']):
                if self.stages['MProber'].load_chip(chipId) == 'ready':
                    return True
                else:
                    return self._promptForErrorHandling('Prober signals error when loading chip')
            return True
        return True


    def _checkProberState(self):
        '''
        Function checks the states of the Prober if:
            - a Prober is in the stages lists
            - the driver provides a get_state() function

        Expected returns are:
            - ready : the function returns true and the script proceeds
            - uncalibrated: the function calls the driver to calibrate or prompts an error for manual handling
            - error: the function prompts for an error
        '''
        if 'MProber' in self.stages.keys():
            if 'get_state' in dir(self.stages['MProber']):
                state = self.stages['MProber'].get_state()

                if state == 'ready':
                    return True
                elif state == 'uncalibrated':
                    if 'calibrate' in dir(self.stages['MProber']):
                        if 'ready' == self.stages['MProber'].calibrate():
                            return True
                        else:
                            return self._promptForErrorHandling('Please Manually Calibrate the Machine')
                    else:
                        return self._promptForErrorHandling('Please Manually Calibrate the Machine')
                elif state == 'error':
                    return self._promptForErrorHandling('Prober responded with an error to get_state()')
            else:
                return True
        else:
            return True

    def _freeProber(self):
        if 'MProber' in self.stages.keys():
            if 'free_prober' in dir(self.stages['MProber']):
                if 'ready' == self.stages['MProber'].free_prober():
                    return True
                else:
                    return self._promptForErrorHandling('Prober responded with an error when freeing all loading platforms')
            else:
                return True
        else:
            return True

    def _storeDie(self, itemID, binningResult=None):
        '''
        Function sends the command to store the die. If Prober is presented and provides store_chip()

        If a binningResults is provided _getContainer is called to link bin to containerID
        Afterwards the prober is called to the store chip. If no ContainerID is provided the chip should be stored to original position
        '''
        if 'MProber' in self.stages.keys():
            if 'store_chip' in dir(self.stages['MProber']):
                container = None
                if binningResult:
                    container = _getContainer(itemID, binningResult)
                if container:
                    if 'ready' == self.stages['MProber'].store_chip(container):
                        return True
                    else:
                        return self._promptForErrorHandling('Prober responded with an error when storing chip')
                else:
                    if 'ready' == self.stages['MProber'].store_chip():
                        return True
                    else:
                        return self._promptForErrorHandling('Prober responded with an error when storing chip')
            else:
                return True
        else:
            return True

    def _getContainer(self, itemID, binningResult):
        '''
            Fetch from Database where to put the item depending on binningResult
        '''
        return None

    def _storeBinningResult(self, itemID, binningResult):
        pass

    def _callBinningFunction(self,entry,args):
        # Call Group Specific Binning Function if it exists
        if 'bin' in entry.keys():
            return self.maitre.execute_func_name(entry['bin'].split(':')[0],entry['bin'].strip().split(':')[1],args)
        # Call General Binning Function if it exists
        elif self.defaultBinFunc != None:
            return self.maitre.execute_func_name(self.defaultBinFunc.split(':')[0],self.defaultBinFunc.strip().split(':')[1],args)

    def _structureProcedure(self, entry, file):
        '''Executes experiments at the structural level using Procedures:
            The function is split into two cases:
            1) MProber is present
            2) ProberControl controls stages itself
            '''

        if 'MProber' in self.stages.keys():
            # Case when 'MProber' is present

            powerMeter = self.stages.get('MProberPower')
            multiMeter = self.stages.get('MProberMulti')
            power_out, multi_out = self.stages['MProber'].get_structure_needs(entry['structure'])
            # connect the according fibers to power/multi-meter
            if powerMeter is not None and power_out is not None:
                power_fiber = self.gh.choose_fiber_out(power_out)
                self.gh.connect_instruments(power_fiber, powerMeter)
            if multiMeter is not None and multi_out is not None:
                multi_fiber = self.gh.choose_fiber_out(multi_out)
                self.gh.connect_instruments(multi_fiber, multiMeter)

            if powerMeter is None and multiMeter is None:
                raise Exception()

            if 'ready' != self.stages['MProber'].connect_structure(entry['chip'],entry['structure']):
                if not self._promptForErrorHandling('Prober responded with error when coupling structure'):
                    if self._promptForErrorHandling('Do you want to proceed to next structure ?'):
                        # Write the error to the results but keep going
                        DataIO.writeData(file, "Error Connecting {}.".format(entry['structure']))
                        return True
                    else:
                        return False

            args = self._prepArguments(entry)

            data = None
            try:
                # Execute the function using maitre
                data = self.maitre.execute_func_name(entry['procedure'],entry['function'],args)
            except Exception as e:
                data = str(e)
            finally:
                # Write the results of the experiment to file
                DataIO.writeData(file, data, entry['measurement'])
            return True



        else:
            # Case when ProberControl controls connected stages
            if not connecting.connect_structure(
                self.stages,
                self.maitre,
                self.coordinatePath,
                entry['structure'] ):
                # Write the error to the results but keep going
                DataIO.writeData(file, "Error Connecting {}.".format(entry['structure']))
                return True
            else:
                args = self._prepArguments(entry)

                data = None
                try:
                    # Execute the function using maitre
                    data = self.maitre.execute_func_name(entry['procedure'],entry['function'],args)
                except Exception as e:
                    data = str(e)
                finally:
                    # Write the results of the experiment to file
                    DataIO.writeData(file, data, entry['measurement'])
                return True

    def _procedure(self, entry, file):
        '''executes experiments that use multiple tools or generalized algorythms'''
        args = self._prepArguments(entry)

        data = None
        try:
            # Execute the function using maitre
            data = self.maitre.execute_func_name(entry['procedure'],entry['function'],args)
        except Exception as e:
            data = str(e)
        finally:
            # Write the results of the experiment to file
            DataIO.writeData(file, data, entry['measurement'])

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
            elif 'tages' in elem:
                elem = self.Stages
            elif 'aitre' in elem:
                elem = self.Maitre
            elif str(elem).isdigit():
                elem=float(elem)
            if elem != '':
                ArgList.append(elem)

        return ArgList

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
                    # Look for default binning function
                    if self._checkBinningFunc(line, line_no):
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
            else:
                self._setBinningMode(measurement_collection)

            print "Detected Binning Group / Mode: " + str(self.binningMode)
            print "Detected Default Binning Function: " + str(self.defaultBinFunc)

            return measurement_collection
        except IOError as e:
            raise IOError("Error reading in configuration file:\n{}".format(e))

    def _setBinningMode(self,script):
        ''' Finds the grouping wise hierarchically highest entry in the script  (wafer,chip,etc..) and sets it as the binningMode'''

        for elem in script:
            groups = list( set(elem.keys()) & set(self._GroupingInfo.group_designators))
            counter = 999
            for group in groups:
                counter = self._GroupingInfo.group_designators.index(group) if self._GroupingInfo.group_designators.index(group) < counter else counter

            if counter != 999:
                self.binningMode = self._GroupingInfo.group_designators[counter]


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
        possibleKey = line[1:].strip().lower()
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

                # Finding Boundaries of Binning Group if Costume Binning was activated
                if groupInfo.binningGroup == groupKey and groupInfo.costumeBinning:
                    # Deactivate CostumeBinning
                    groupInfo.clearBinningGroup()
                    if 'bin' in measurement.keys():
                    # Delete Binning Entry
                        measurement['bin'] = None
                # Saving last binning GroupDesignator in case  costumeBinning gets activated
                if not groupInfo.costumeBinning and groupKey != 'bin':
                    groupInfo.setBinningGroup(groupKey)
                # A '> bin' will active costume binning
                if groupKey == 'bin':
                    groupInfo.setCostumeBinning()
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

    def _checkBinningFunc(self, line, line_no):
        BinningKeyWord = 'bin-by:'
        if line.startswith(BinningKeyWord):
            if self.defaultBinFunc is None:
                self.defaultBinFunc = line[len(BinningKeyWord):].strip()
            else:
                raise KeyError('.meas > cannot set default binning mode twice (line:{})'.format(line_no))
            return True
        else:
            return False

    def _checkOutputMode(self, line, line_no):
        outputModeKeyWord = 'group-by:'
        if line.startswith(outputModeKeyWord):
            if self.outputMode is None:
                self.outputMode = line[len(outputModeKeyWord):].strip().lower()
            else:
                raise KeyError('.meas > cannot set output mode twice (line:{})'.format(line_no))
            return True
        else:
            return False

    class _GroupingInfo(object):
        '''Class to keep grouping info organized'''
        group_designators = ['wafer', 'chip', 'group','bin']

        def __init__(self):
            self.keyId = None
            self.keyValue = None
            self.gettingKeyId = False
            self.previous = {}
            self.binningGroup = None
            self.costumeBinning = False
            for key in self.group_designators:
                self.previous[key] = None

        def setBinningGroup(self,key):
            self.binningGroup = key

        def setCostumeBinning(self):
            self.costumeBinning = True

        def clearBinningGroup(self):
            self.binningGroup = None
            self.costumeBinning = False

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

        def __init__(self,group_designators,resultsPath='', name_convention='.csv', outputMode=None):
            self.group_designators = group_designators
            self.FileMap = {}
            self.outputMode = outputMode
            self.name_convention = name_convention
            self.resultsPath = resultsPath

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
            return self.name_convention[0:dot] + '-' + identifier + self.name_convention[dot:]

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

        def getRelatedFiles(self,script,key,entry):
            # if binning key equals outputmode or in a lower hierarchy level than the outputMode (bin chips but output wafers) return current file path in a list
            if self.group_designators.index(key) >= self.group_designators.index(self.outputMode):
                return [os.path.join(self.resultsPath, self._generateFileName(entry))]
            else:
                # generate list of entries in which the current binning entity exists
                sub_entries = []
                for elem in script:
                    if elem[key] == entry[key]:
                        sub_entries.append(elem)
                # generate list with all related file names
                paths = []
                for elem in sub_entries:
                    paths.append(os.path.join(self.resultsPath, self._generateFileName(elem)))
                # clean paths of dubble sub_entries and return
                return list(set(paths))


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
