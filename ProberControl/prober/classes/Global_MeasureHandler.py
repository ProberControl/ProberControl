import inspect
import threading
import object_chain
from functools import cmp_to_key

debug = 0
def sdebug(msg):
    if debug > 0:
        print 'G_Mh:: {}'.format(msg)

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

def _look_for_obj(obj_list, comparator):
    '''
    comparator func(obj) -> bool : functions that returns if condition is
        met for obj
    '''
    for obj in obj_list:
        sdebug('comp: {}'.format(obj))
        if comparator(obj):
            return obj
    return None


@Singleton
class Global_MeasureHandler(object):

    def __init__(self):
        self.TriggerInfo = {}
        self.Stages = {}
        self.__locked = {}
        self.__chainSets = {}
        self.__access_lock = threading.Lock()
        self.switchHandler = None

    def update_stages(self, stages):
        self.Stages = stages
        if 'SwitchHandler' in self.Stages.keys():
            self.switchHandler = self.Stages['SwitchHandler']

    def get_locked(self):
        with self.__access_lock:
            return self._get_locked()

    def _get_locked(self):
        '''returns a list of the locked instruments pair(name, object)'''
        locked_objects = [instr for locked_per_user in self.__locked.values() for instr in locked_per_user]
        names = [self._get_name_from_instrument(instr) for instr in locked_objects]
        return zip(names, locked_objects)

    def is_locked(self, instrument):
        '''
        intended for external entities, e.g. GUI
        NOT for instrument users (i.e. Measure functions)
        Note: It is not completely safe to use object if !is_locked(),
              you would actually have to lock it (!!)
        '''
        with self.__access_lock:
            return instrument in [i[1] for i in self._get_locked()]



    def checkout_instrument(self, instrument):     #
        '''
        Marks an instrument as active until either checkin_instrument() or
        instrument.change_state() is called
        '''
        device = self.get_instrument(instrument)
        device.active = True

    def checkin_instrument(self, instrument):      #
        '''
        Marks an instrument as inactive until either checkout_instrument() or
        instrument.change_state() is called
        '''
        device = self.get_instrument(instrument)
        device.active = False

    def _get_owner(self):
        # REMEBER to update this if the way the get_instruments calls occur
        # through additional code paths
        functions = ['_structureProcedure','__executeCommand','_procedure', 'execute_script']
        for entry in inspect.stack(context=0):
            if entry[3] in functions:
                return id(entry[0].f_locals['self'])
        raise LookupError('Global_MeasureHandler not called within {}. The stack tracing was inconclusive on the instrument owner.'.format(functions))

    def _lock_instrument(self, instr, owner_id):
        # Requires the lock __access_lock to be acqured first
        owned = self.__locked.get(owner_id)
        if owned is None:
            self.__locked[owner_id] = [instr]
        else:
            owned.append(instr)

    def _connect_fiber(self, instrument, owner_id, fiber_id, isFiberIn):
        chainSet = self.__chainSets.get(owner_id)
        if chainSet is None:
            chainSet = {}
            self.__chainSets[owner_id] = chainSet
        chain = chainSet.get(fiber_id)
        if chain is None:
            chain = object_chain.ChainList(isFiberIn)
            chainSet[fiber_id] = chain

        prev_inst, next_inst = chain.insert(insert)
        if prev_inst != None or next_inst != None:
            raise RuntimeError('tried to choose fiber {} after acquiring instruemnts'.format(fiber_id))

    def _connect_to_chain(self, instrument, owner_id, fiber_id):
        if self.switchHandler is None:
            # maybe a warning here??
            return
        chainSet = self.__chainSets.get(owner_id)
        if chainSet is None:
            raise RuntimeError('tried to get instrument {} before geting a fiber'.format(self._get_name_from_instrument(instrument)))
        chain = chainSet.get(fiber_id)
        if chain is None:
            raise RuntimeError('tried to get instrument {} before geting a fiber'.format(self._get_name_from_instrument(instrument)))

        prev_inst, next_inst = chain.insert(insert)
        # make the actual connections on the switch
        inst_name = self._get_name_from_instrument(instrument)
        if prev_inst is not None:
            prev_inst_name = self._get_name_from_instrument(prev_inst)
            self.switchHandler.connect_devices(prev_inst_name, inst_name)
        if next_inst is not None:
            next_inst_name = self._get_name_from_instrument(next_inst)
            self.switchHandler.connect_devices(next_inst_name, inst_name)

    def _get_name_from_instrument(self, instrument):
        return self.Stages.keys()[self.Stages.values().index(instrument)]

    def _get_name_from_instrument(self, instrument):
        name = self._get_name_from_instrument(instrument)
        num_s = ''
        for c in name[::-1]:
            if not c.isdigit():
                break
            num_s += c
        if len(num_s) == 0:
            return -1, name
        return int(num_s[::-1]), name[:-len(num_s)]

    def _instrument_compare(self, left, right):
        lnum, lname = self._find_trail_number(left)
        rnum, rname = self._find_trail_number(right)
        if lname != rname:
            return -1 if lname < rname else 1
        return lnum < rnum

    def _order_instr(self, inst_list):
        return sorted(inst_list, key=cmp_to_key(self._instrument_compare))

    def _choose_fiber(self, fiber_id, isFiberIn):
        '''
        lets the user choose the fiber needed
        Returns an id for the fiber to be passed to the get_instrument family of
        functions
        '''
        inst_type = 'Fiber'
        with self.__access_lock:
            used = [inst for sub_l in self.__locked.values() for inst in sub_l]
            def isUnused(instrument):
                return instrument not in used and instrument.whoAmI() == inst_type and instrument.fiber_id == fiber_id

            found = _look_for_obj(self._order_instr(self.Stages.values()), isUnused)
            if found != None:
                self._lock_instrument(found, owner_id)
                # self._connect_fiber(found, owner_id, fiber_id, isFiberIn)
            return found

    def choose_fiber_in(self, fiber_id):
        self._choose_fiber(fiber_id, True)

    def choose_fiber_out(self, fiber_id):
        self._choose_fiber(fiber_id, False)

    def get_instrument(self, specifiedDevice, additional=False):
        '''
        Finds and returns an unactive instrument corresponding to the one specified
        Returns None if such instrument wasn't found/available.
        NOTE: used to have fiber_id param after specifiedDevice!
        '''

        owner_id = self._get_owner()
        sdebug('\nget_instrument > looking for: {}'.format(specifiedDevice))

        # serialize access to global ownership dictionary
        with self.__access_lock:

            if not additional:
                # Try the owned instruments first
                owned_list = self.__locked.get(owner_id)
                sdebug('OwnedList<{}>: {}'.format(owner_id, owned_list))
                if owned_list != None:
                    found = _look_for_obj(self._order_instr(owned_list), lambda x: x.whoAmI() == specifiedDevice)
                    if found != None:
                        return found

            # Then take a look for available instruments
            used = [inst for sub_l in self.__locked.values() for inst in sub_l]
            sdebug('used instruments: {}'.format(used))
            def isUnused(instrument):
                sdebug('{} | {} - {}'.format('used' if instrument in used else 'not used', instrument.whoAmI(), specifiedDevice))
                return instrument not in used and instrument.whoAmI() == specifiedDevice

            found = _look_for_obj(self._order_instr(self.Stages.values()), isUnused)
            if found != None:
                self._lock_instrument(found, owner_id)
                # self._connect_to_chain(found, owner_id, fiber_id)
            return found

    def _get_instrument_triggerX(self, triggerObject, specifiedDevice, returnTriggerable, fiber_id, additional=False):
        owner_id = self._get_owner()

        # doing reverse lookup on the Stages dict here; no that good, but correct!
        triggerObjectName = self.Stages.keys()[self.Stages.values().index(triggerObject)]
        triggers = self.TriggerInfo.get(triggerObjectName)
        if triggers == None:
            _print_mh('no trigger info associated with {}'.format(triggerObjectName))
            return None
        TrigNet = triggers[1] if returnTriggerable else triggers[0]
        if TrigNet == None:
            _print_mh('entry {} does not have {} defined'.format('TriggerOut' if returnTriggerable else 'TriggerIn'))
            return None

        # serialize access to global ownership dictionary
        with self.__access_lock:

            if not additional:
                # Try the owned instruments first
                owned_list = self.__locked.get(owner_id)
                if owned_list != None:
                    def findOwnedTriggerMatch(instrument):
                        instrument_name = self.Stages.keys()[self.Stages.values().index(instrument)]
                        triggerInfo = self.TriggerInfo.get(instrument_name)
                        if triggerInfo is None:
                            return False
                        canDoWantedTriggerAction = triggerInfo[0 if returnTriggerable else 1] == TrigNet
                        return instrument.whoAmI() == specifiedDevice and canDoWantedTriggerAction

                    found = _look_for_obj(self._order_instr(owned_list), findOwnedTriggerMatch)
                    if found != None:
                        return found

            # Then take a look for available instruments
            used = [inst for sub_l in self.__locked.values() for inst in sub_l]
            def findOtherTriggerMatch(instrument):
                instrument_name = self.Stages.keys()[self.Stages.values().index(instrument)]
                triggerInfo = self.TriggerInfo.get(instrument_name)
                if triggerInfo is None:
                    return False
                canDoWantedTriggerAction = triggerInfo[0 if returnTriggerable else 1] == TrigNet
                return instrument not in used and instrument.whoAmI() == specifiedDevice and canDoWantedTriggerAction

            found = _look_for_obj(self._order_instr(self.Stages.values()), findOtherTriggerMatch)
            if found != None:
                self._lock_instrument(found, owner_id)
                # self._connect_to_chain(found, owner_id, fiber_id)
            return found

    def get_instrument_triggered_by(self, triggerSource, specifiedDevice, additional=False):
        '''
        Finds and returns an unactive instrument, corresponding to the one
        specified, that can be triggered by trigger_source
        NOTE: used to have fiber_id param after specifiedDevice!
        '''
        return self._get_instrument_triggerX(triggerSource, specifiedDevice, True, -1, additional)

    def get_instrument_triggering(self, triggerTarget, specifiedDevice, additional=False):
        '''
        Finds and returns an unactive instrument, corresponding to the one
        specified, that can trigger by trigger_target
        NOTE: used to have fiber_id param after specifiedDevice!
        '''
        return self._get_instrument_triggerX(triggerTarget, specifiedDevice, False, -1, additional)

    def get_instrument_by_name(self, instrumentName):
        '''
        Finds and returns the instrument with the specified name
        Returns None if such instrument wasn't found/available.
        NOTE: used to have fiber_id param after specifiedDevice!
        '''

        owner_id = self._get_owner()
        sdebug('\nget_instrument_by_name > looking for: {}'.format(specifiedDevice))

        # serialize access to global ownership dictionary
        with self.__access_lock:

            # Try the owned instruments first
            owned_list = self.__locked.get(owner_id)
            sdebug('OwnedList<{}>: {}'.format(owner_id, owned_list))
            if owned_list != None:
                found = _look_for_obj(self._order_instr(owned_list), lambda x: instrumentName == self._get_name_from_instrument(x))
                if found != None:
                    return found

            # Then take a look for available instruments
            used = [inst for sub_l in self.__locked.values() for inst in sub_l]
            sdebug('used instruments: {}'.format(used))

            found = _look_for_obj(self._order_instr(self.Stages.values()), lambda x: x not in used and instrumentName == self._get_name_from_instrument(x))
            if found != None:
                self._lock_instrument(found, owner_id)
                # self._connect_to_chain(found, owner_id, fiber_id)
            return found

    def _check_owned(self, owner_id, instrument):
        owned_list = self.__locked.get(owner_id)
        return instrument in owned_list

    def connect_instruments(self, transmitting_instrument, receiving_instrument):
        owner_id = self._get_owner()

        # serialize access to global ownership dictionary
        with self.__access_lock:
            if self.switchHandler is None:
                # maybe WARNING
                sdebug('cannot connect > switchHandler is None | self: {}'.format(self))
                return
            if not self._check_owned(owner_id, transmitting_instrument):
                raise RuntimeError('tried to connect un-owned instrument {}'.format(self._get_name_from_instrument(transmitting_instrument)))
            if not self._check_owned(owner_id, receiving_instrument):
                raise RuntimeError('tried to connect un-owned instrument {}'.format(self._get_name_from_instrument(receiving_instrument)))
            tran_inst_name = self._get_name_from_instrument(transmitting_instrument)
            recv_inst_name = self._get_name_from_instrument(receiving_instrument)
            sdebug('connecting {} with {}'.format(tran_inst_name, recv_inst_name))
            self.switchHandler.connect_devices(tran_inst_name, recv_inst_name)

    def release_current_user_instruments(self):
        '''
        Releases all current user instruments
        Should be called at the end of a test entity and NOT normally
        inside Measure functions
        '''
        owner_id = self._get_owner()

        with self.__access_lock:
            owned = self.__locked.get(owner_id)
            chain = self.__chainSets.get(owner_id)
            if owned is not None:
                self.__locked[owner_id] = []
            if chain is not None:
                self.__chainSets[owner_id] = ChainList()

    def release_instrument(self, instrumentToRelease):
        '''
        Release a specified instrument if owned by current user
        Can be used inside Measure functions for a sparse and heavily used
        resource - might cause problems with CONNECTION CHAIN !
        (To Fix: If a single object is released then the surronding elements in
        the chain have to connect together.)
        '''
        owner_id = self._get_owner()

        with self.__access_lock:
            owned = self.__locked.get(owner_id)
            if owned is not None:
                if instrumentToRelease in owned:
                    # remove instrument from owned list
                    owned.pop(owned.index(instrumentToRelease))
                    return
            raise KeyError('{} not owned by current user. Should not hold ref to that instance!'.format(instrumentToRelease))

    def insert_instr(self, stage_name, triggers = None):
        '''
            Add an instrument to the handler
            << Carried from older Global_MeasureHandler version, now used
            only to define trigger network >>
        '''
        self.TriggerInfo[stage_name] = triggers


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
