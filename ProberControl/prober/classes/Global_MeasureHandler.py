import inspect

# instrument_info indexes
FUNCTION = 0
THRESH = 1
USER = 2

class Singleton(object):
    ''' Singleton paradigm implementation '''
    def __init__(self, u_class):
        self.u_class = u_class
        self.instance = None
    def __call__(self, *args, **kwargs):
        if self.instance == None:
            self.instance = self.u_class(*args, **kwargs)
        return self.instance
        
def _print_mh(msg):
    print 'Global_MeasureHandler:: {}'.format(msg)

@Singleton        
class Global_MeasureHandler(object):

    def __init__(self, Stages):
        '''
            Stages (dict): Stages handle
        '''
        # Instruments will hold the different intruments types
        # eg. DC, OPT, etc. as a key to a dict where the val is
        # another dict with:  (Stage_name) -> []
        self.Instruments = {}
        self.Stages = Stages
        self.__locked = {}

    def update_stages(self, stages):
        self.Stages = stages

    def add_locked_instrument(self, scriptHash, instrument):
        '''Marks an instrument has locked for a particular script'''
        if scriptHash not in self.__locked.keys():
            self.__locked[scriptHash] = [self.get_instrument(instrument)]

        else:
            instrumentActual = self.get_instrument(instrument)

            if instrumentActual in self.__locked[scriptHash]:
                # Get another instrument
                # This is the case of the duplicates
                # Need to handle
                pass
            else:
                self.__locked[scriptHash].append(instrumentActual)

    def clear_locked(self, id_=''):
        '''
        clears the locked instruments, if id_ is passed as a parameter,
        this function clears all instruments associated with that script id
        '''
        if id_:
            self.__locked.pop(id_)
            print self.__locked
        else:
            self.__locked = {}

    def get_locked(self):
        '''returns a list of the locked instruments'''
        pairs = zip(self.__locked.keys(),self.__locked.values())
        return pairs
    
    def checkout_instrument(self, instrument):
        '''
        Marks an instrument as active until either checkin_instrument() or 
        instrument.change_state() is called
        '''
        device = self.get_instrument(instrument)
        device.active = True
        
    def checkin_instrument(self, instrument):
        '''
        Marks an instrument as inactive until either checkout_instrument() or 
        instrument.change_state() is called
        '''
        device = self.get_instrument(instrument)
        device.active = False

    def get_instrument(self, specifiedDevice):
        '''Finds and returns an unactive instrument corresponding to the one specified'''
        device = self.clean(specifiedDevice)

        # Try the locked instruments first
        instrumentActual = self.__checkLocked(device)
        if not instrumentActual: # if nothing was found in __checkLocked()
        # Then take a look for available instruments, if not in locked
        
            for instrument in self.Stages.keys():
                strippedInstrument = ''.join([self.clean(i) for i in instrument if not i.isdigit()])

                # If we find a device that fits and it isn't active right now
                if device in strippedInstrument and not self.Stages[instrument].active:
                    return self.Stages[instrument]

        #If you make it here, no available instrument
        return instrumentActual

    def clean(self, word):
        return word.lower()

    def __checkLocked(self, instrument):
        '''
        Function that traces the stack back to ScriptController, then uses
        the id() of that particular object to confirm who is calling on that
        particular instrument
        '''

        # As of August 6, 2017
        # The only functions that would be calling for objects/functions
        functions = ['_structureProcedure','__executeCommand','_procedure']
        id_ = ''

        # Iterate over the stack, finding the ID of the unique ScriptController object
        for entry in inspect.stack(context=0):
            if entry[3] in functions:
                id_ = id(entry[0].f_locals['self'])

            # If the ID of the caller is in the locked objects
            if (id_ in self.__locked.keys()):
                locked_objects = self.__locked[id_]

                # check instruments locked with that particular script
                for object_ in locked_objects:
                    cleanInstrument = ''.join([self.clean(i) for i in str(object_) if not i.isdigit()])
                    if instrument == cleanInstrument:
                        return object_

        # If nothing was found, return false
        return False 
                
    def call_function(self, instrument, function, arguments = ''):
        '''
        A method used to call functions from a specifc instrument via the GMH

        :returns: An instance of a function call that has been executed
        '''

        # Will only return objects that are not busy
        instrumentActual = self.get_instrument(instrument)

        if instrumentActual:
            functionActual = getattr(instrumentActual,function)
            if len(arguments) == 1:
                return functionActual(arguments)
            elif len(arguments) > 1:
                return functionActual(*arguments)
            else:
                return functionActual()
        else:
            return None # returns nothing becuase the instrument wasn't available

    def insert_instr(self, stage_name, instr_attr):
        '''
            Add an instrument to the handler
        '''
        if instr_attr not in self.Instruments.keys():
            self.Instruments[instr_attr] = {}

        try:
            self.Instruments[instr_attr][stage_name] = list(self._choose_fun(stage_name, instr_attr)) + [None]
        except KeyError:
            _print_mh('problem inserting {} in the instrument records.'.format(stage_name))
            raise
            
    def get_instr(self, instr_attr, pair=False):
        '''
            returns measure function (and associated threshold)
        '''
        if instr_attr in  self.Instruments:
            relevant_instruments = self.Instruments[instr_attr]
        else:
            return False
        for k, v in relevant_instruments.items():
            if v[USER] is None:
                if pair:
                    return v[FUNCTION], v[THRESH]
                return v[FUNCTION]
            else:
                return False
                
    def get_instr_by_name(self, instr_name, pair=False):
        for categ, sub_dict in self.Instruments.items():
            for name, v in sub_dict.items():
                if instr_name == name:
                    if v[USER] is None:
                        if pair:
                            return v[FUNCTION], v[THRESH]
                        else:
                            return v[FUNCTION]
                    else:
                        # return self.get_instr(categ, pair) -> return next available one
                        return False

    def _choose_fun(self, stage_name, instr_attr):
        '''
            Helper function. Will not be used in the future
        '''

        try:
            if instr_attr == 'OPT':
                return self.Stages[stage_name].get_power, -60
            elif instr_attr == 'DC':
                return self.Stages[stage_name].get_current, None
        except KeyError:
            pass
        finally:
            return self.Stages[stage_name].whatCanI(), None

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
