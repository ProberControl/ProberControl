'''
Newport Controler Class
    implementation for vertical stage
'''

import visa
import time
import sys

class NewportPM500(object):

    def __init__(self, gpib_addr):
        '''
         Constructor
         
         gpib_addr (string): the GPIB adress of the controller (e.g. 'GPIB0::22::INSTR')
        '''
        
        if sys.platform.startswith('win'):
            self.rm = visa.ResourceManager()
            self.dev = self.rm.open_resource(gpib_addr)
            self.velocity = 0
            print 'PM500 Controler started on adress: {}'.format(gpib_addr)
            
    def set_velocity(self, vel):
        '''
         Set the velocity for the motor movement
         
         vel (integer): velocity in um/sec
        '''
        
        self.velocity = vel
        
    def move_up(self):
        '''
         Moves the stage to positive limit switch
        '''
        
        if self.velocity == 0:
            print 'PM500: invalid move, have to set velocity first.'
            return

        if self.dev.write('YS {}'.format(self.velocity))[1] != 0:
            print 'PM500: problem occured while sending command'
            return
            
        while self.dev.query('YSTAT') != 'YL':
            time.sleep(0.01)
            
        print 'PM500: move complete -> UP'
        
    def move_down(self):
        '''
         Moves the stage to negative limit switch
        '''
        
        if self.velocity == 0:
            print 'PM500: invalid move, have to set velocity first.'
            return

        if self.dev.write('YS -{}'.format(self.velocity))[1] != 0:
            print 'PM500: problem occured while sending command'
            return
            
        while self.dev.query('YSTAT') != 'YL':
            time.sleep(0.01)
            
        print 'PM500: move complete -> DOWN'
        
    def close(self):
        ''' release resources '''

        if sys.platform.startswith('win'):
            self.dev.close()

