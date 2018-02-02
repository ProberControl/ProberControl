'''
Defines a thin struct to represent a "fiber array" object for the purpose of
providing a handle for the Measure functions
'''

class Fiber(object):
    def __init__(self, fiber_id):
        '''
        array_id (string): array specifier
        fiber_ids (list of string): list of owned fiber id's
        '''
        self.fiber_id = fiber_id

    def whoAmI(self):
        return 'Fiber'
