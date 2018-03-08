'''
Dummy holder for the powermeter attached to the TL2500 prober system
'''

class TL2500PowerDummy(object):
    def __init__(self, res_manager, address='0.0.0.0'):
        pass

    def whoAmI():
        return 'ProberPower'
