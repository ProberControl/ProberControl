'''
[DatabaseWriter]
This module handles output of test results to a remote database.
Implements the ProberControl's OutputStream implicit interface.
'''

import sqlalchemy

class DatabaseWriter(object):
    def __init__(self):
        pass

    def getOutTargets(self, entry):
        pass

    def __exit__(self, type, value, traceback):
        pass

    def write(openFile, data, Data_Name=''):
        pass
