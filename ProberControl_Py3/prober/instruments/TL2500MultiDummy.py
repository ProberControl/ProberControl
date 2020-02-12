'''
Dummy holder for the multimeter attached to the TL2500 prober system
'''

class TL2500MultiDummy(object):
    def __init__(self, res_manager, address='0.0.0.0'):
        pass

    def whoAmI():
        return 'ProberMulti'
