import serial
import visa
import time
import sys, os
from instruments import *
from procedures import *
from classes import *

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Initializer(object):
    __metaclass__ = Singleton
    '''
    The purpose of this class is to assist in the setup for the program.
    The only usage of this class is during initial start-up.
    .. Note:: This code should not be modified.
    '''

    def __init__(self):
        self.rm = visa.ResourceManager()
        self.brokenInstruments = [] # collection for instruments not able to be instantiated
        self.stageCollection = {} # collection for instantiated stages
        self.configCollection = [] # collection for all configurations from config file

    def read_config(self):
        '''
        Method for reading in the configuration file. The config_collection object is a list of dictionaries. Each dictionary has information about a particular instrument.

        :raises: Exception
        '''
        paraIndex = ''
        stage_config = {}
        config_collection = []

        # This will be different depending on how the program was launched
        pwd = os.path.abspath(path='.')
        if (pwd.split('\\')[-1:][0]=='server'): # Launched via ethernet
            path = './../../config/ProberConfig.conf'
        else: # conventional launch
            path = './../config/ProberConfig.conf'


        try:
            with open(path, 'r') as config_inFile:

                for line in config_inFile:
                    # if it is a config block and non-empty
                    # add the dictionary to our collection
                    if self._isInstrumentBlock(line) and len(stage_config) > 1:
                        # If it is a multi-channel device, configure for every channel
                        if self._isMultichannel(stage_config):
                            stage_config = self._makeMoreChannels(stage_config)
                            
                        config_collection.append(stage_config)
                        stage_config = {}

                    # Set the key for the dictionary
                    if self._isInstrumentBlock(line):
                        paraIndex = 'Stage'

                    if self._isDeviceDesignator(line):
                        paraIndex = line[1]

                    # Set the value for the dictionary
                    if self._isInformation(line):
                        stage_config[paraIndex]=line[0:-1] # add to collection

        except Exception as e:
            print 'Problem with config file:\n' + str(e)

        # flatten the list, multi-dimensional because of multi-channel devices
        # Also check if the configuration file was updated
        self._checkNewInformation(self._flatten(config_collection))

    def _checkNewInformation(self, config_collection):

        for entry in config_collection:
            if entry not in self.configCollection:
                self.configCollection.append(entry)

        temp = []
        for entry in self.configCollection:
            if entry in config_collection:
                temp.append(entry)
        
        self.configCollection = temp

    def _isInformation(self, line):
        '''Determines if a line is device information'''
        if line[0] != '#' and line:
            return True
        else:
            return False

    def _isDeviceDesignator(self, line):
        '''Determines if line is device designator'''
        if line[0] == '#' and line[1] != '#':
            return True
        else:
            return False

    def _isInstrumentBlock(self, line):
        '''Determines if the line in the config file is beginning or ending a instrument block'''
        if line[0:2] == '##':
            return True
        else:
            return False

    def _isMultichannel(self, stage_config):
        '''Determines if an entry is a multi-channel device'''
        for entry in stage_config:
            if 'N' in entry:
                return True
            
    def _makeMoreChannels(self, stage_config):
        '''Produces more entries of lasers for every channel designated by the config file'''
        n = stage_config['N']
        begin, end = self._format(n)
        toReturn = []
        for i in range(begin, end+1):
            new_entry = stage_config.copy()
            new_entry['N'] = str(i)
            toReturn.append(new_entry)
        return toReturn    
        
    def _format(self, n):
        '''Helper function for _makeMoreChannels()'''
        n = [int(i) for i in n.split(',')]
        n.sort()
        return n[0], n[-1]

    def _flatten(self, config_collection):
        '''Flattens the list to return, not possible in list comp because of different data types'''
        toReturn = []
        for i in config_collection:
            if type(i) == list:
                for item in i:
                    toReturn.append(item)
            else:
                toReturn.append(i)
                
        return toReturn

    def generate_stages(self):
        '''Creates actual objects'''

        # Clear the brokenInstruments collection
        self.brokenInstruments = []
        instruments_instantiated = [str(i) for i in self.stageCollection.values()]    
        
        gm_handler = Global_MeasureHandler.Global_MeasureHandler(self.stageCollection)

        constructor_methods = {
            'O': self._genOptElecStage, #Optical stage
            'E': self._genOptElecStage, #Electrical stage
            'C': self._genChipStage, #Chip stage
            'M': self._genMeasureStage, #Measurement stage
        }

        for stage_config in self.configCollection:

            # Avoid initializing objects that already exist
            if stage_config['O'] not in instruments_instantiated:
                stage_type = stage_config['Stage']

                try:
                    # construct the instance of the class
                    newStage = constructor_methods[stage_type](stage_config,gm_handler)

                    # construct the key for GlobalMeasurement_Handler and stages dictionary
                    key = stage_type+newStage.whoAmI()

                    # add the instance of the class to the stages dictionary
                    self.stageCollection[key] = newStage

                    # add the new instance to the GlobalMeasurement_Handler
                    gm_handler.update_stages(self.stageCollection)
                    gm_handler.insert_instr(key, newStage.whatCanI())

                except Exception as e:
                    print '\nError Instantiating: ' + stage_config['O']
                    print 'Exception Raised: ' + str(e) + '\n'
                    self.brokenInstruments.append(stage_config)

        self.stageCollection = self._genHandlers(self.configCollection, self.stageCollection)

        self._checkInstruments()

        # Return the stages to the GUI
        return self.stageCollection

    def __generateStages(self, configuration):
        '''Internal generation of stages for refresh() method'''

        # reset broken devices collection
        self.brokenInstruments = []
        
        gm_handler = Global_MeasureHandler.Global_MeasureHandler(self.stageCollection)

        constructor_methods = {
            'O': self._genOptElecStage, #Optical stage
            'E': self._genOptElecStage, #Electrical stage
            'C': self._genChipStage, #Chip stage
            'M': self._genMeasureStage, #Measurement stage
        }

        for stage_config in configuration:
            stage_type = stage_config['Stage']

            try:
                # construct the instance of the class
                newStage = constructor_methods[stage_type](stage_config,gm_handler)

                # construct the key for GlobalMeasurement_Handler and stages dictionary
                key = stage_type+newStage.whoAmI()

                # add the instance of the class to the stages dictionary
                self.stageCollection[key] = newStage

                # add the new instance to the GlobalMeasurement_Handler
                gm_handler.update_stages(self.stageCollection)
                gm_handler.insert_instr(key, newStage.whatCanI())

            except Exception as e:
                print '\nError Instantiating: ' + stage_config['O']
                print 'Exception Raised: ' + str(e) + '\n'
                self.brokenInstruments.append(stage_config)

        self.stageCollection = self._genHandlers(self.configCollection, self.stageCollection)

        self._checkInstruments()

        return self.stageCollection

    def _genOptElecStage(self, stage_config, gm_handler):
        '''
        Reads information for optical or electrical stage

        :param stage_config: Configuration entry read from ProberConfig.conf
        :type stage_config: Dictionary
        '''
        ser_list = []
        space = None
        off_angle = None
        ser_list.append(apt_util.c2r(stage_config['X']))
        ser_list.append(apt_util.c2r(stage_config['Y']))
        ser_list.append(apt_util.c2r(stage_config['Z']))

        if 'S' in stage_config:
            space =  map(float,stage_config['S'].split(' '))

        if 'A' in stage_config:
            off_angle = float(stage_config['A'])

        if stage_config['Stage'] == 'O':
            temp = OptStage.OptStage(ser_list, space, off_angle)
            temp.set_whoAmI(stage_config['O'])
            return temp

        elif stage_config['Stage'] == 'E':
            temp = E_Stage.E_Stage(ser_list, space, off_angle)
            temp.set_whoAmI(stage_config['O'])
            return temp

    def _genChipStage(self, stage_config, gm_handler):
        '''Generates ChipStage object from stage_configuation dictionary'''
        ser_list = []
        ser_list.append(apt_util.c2r(stage_config['R']))
        return chip_stage.ChipStage(ser_list)

    def _genMeasureStage(self, stage_config, gm_handler):
        '''Generates the measurement stages'''
        address = stage_config['A']
        instrumentName = stage_config['O']

        # Special case for Amonics EDFA
        if instrumentName == 'AEDFA_IL_23_B_FA': 
            instrumentPort = __import__(instrumentName)
            instrumentActual = getattr(instrumentPort, instrumentName)(apt_util.c2r(address))

        # Special case for distance measurement setup
        elif instrumentName == 'Distance': 
            instrumentActual = self._distanceSetup(stage_config)
        
        # Importing a multi-channel device
        elif 'N' in stage_config: 
            instrumentPort = __import__(instrumentName)
            instrumentActual = getattr(instrumentPort, instrumentName)(self.rm, address, stage_config['N'])

        #Normal case
        else: 
            instrumentPort = __import__(instrumentName)
            instrumentActual = getattr(instrumentPort, instrumentName)(self.rm, address)

        return instrumentActual

    def _distanceSetup(self, stage_config):
        '''Internal helper function'''
        ser_list = []
        ser_list.append(stage_config['D']) #DSensor
        ser_list.append(apt_util.c2r(stage_config['X'])) #Stepper
        ser_list.append(apt_util.c2r(stage_config['Y'])) #Stepper
        ser_list.append(stage_config['A']) #Newport Controller
        return DMesStage(ser_list)

    def _genHandlers(self, stage_config, stages):
        '''
        Generates Handlers for Stages
        :note: Currently only generates switch handler
        '''
        handlerActual = ''
        
        for item in stages:
            if 'switch' in item.lower():
                handlerPort = __import__('SwitchHandler')
                handlerActual = getattr(handlerPort, 'SwitchHandler')(stage_config,stages,stages[item])
        
        if handlerActual:
            stages['SwitchHandler'] = handlerActual

        return stages

    def _checkInstruments(self):
        '''reports broken instruments to the user'''
        if (self.brokenInstruments):
            print 'The following instruments were not initialized:'
            for entry in self.brokenInstruments:
                print '{}'.format(entry['O'])

        else:
            print 'All instruments listed in the configuration file are initialized.'

    def refresh(self):

        self.read_config()
        self.generate_stages()

        #Return the collection to the GUI
        return self.stageCollection

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
