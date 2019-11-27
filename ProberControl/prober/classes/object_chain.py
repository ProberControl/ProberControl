'''
Contains info and convenience functions to determine the order
of the connected chain of instruments needed for each test
'''
import sys
sys.path.insert(0, "C:\\Users\\asus\\Desktop\\Prober\\2to3\\python3Prober\\ProberControl\\prober")


from instruments import pipe_instrument_groups

order_in = ['Laser', 'BoostAmp', 'Modulator', 'Polarization', 'DUT']
order_out = ['DUT', 'PreAmp', 'SignalSink']

class ChainList(object):
    def __init__(self, isInputChain):
        self.chainList = []
        if isInputChain:
            self.order = order_in
        else:
            self.order = order_out

    def _getOrderNumber(self, instrument):
        found = None
        for chain_element, group in pipe_instrument_groups.items():
            if instrument.whoAmI() in group:
                found = chain_element
                break
        if found is None:
            raise KeyError('{} not inluded in \'pipe_instrument_groups\' dict of instruments\\__init__.py'.format(instrument.__class__))

        if found not in self.order:
            raise KeyError('key {} of \'pipe_instrument_groups\' dict of instruments\\__init__.py not in original order:\n{}'.format(found, self.order))

        return self.order.index(found)

    def insert(self, instrument):
        '''
        Adds instrument to chainList
        Returns instances of instruments that come before and after that instrument,
        or None for either one that doesn't exist
        '''
        elem = ChainElement(instrument, self._getOrderNumber(instrument))
        i = 0
        while i < len(self.chainList):
            next_elem = self.chainList[i]
            if next_elem.ordinal > elem.ordinal :
                next_inst = next_elem.instance
                self.chainList.insert(i, elem)
                if i == 0:
                    return None, next_inst
                prev_inst = self.chainList[i-1].instance
                return prev_inst, next_inst
        self.chainList.append(elem)
        if i == 0:
            return None, None
        prev_inst = self.chainList[i-2].instance
        return prev_inst, None

class ChainElement(object):
    def __init__(self, instance, ordinal):
        '''
        instance (instrument)   : an instrument object
        ordinal (int)           : the order in the connection chain
        '''
        self.ordinal = ordinal
        self.instance = instance
