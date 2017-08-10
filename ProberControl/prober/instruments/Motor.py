# the Motor class

import serial
import threading
from struct import unpack
import logging

def int2hexStr(integer, numberOfBytes):
    '''
    Convert an integer to its corresponding bytearray

    :param integer: the number we want to convert 
    :type integer: Integer
    :param numberOfBytes: The number of bytes
    :type numberOfBytes: Integer
    :returns: Mutable sequence of integers of type bytearray
    '''
    
    bytes = []
    for i in range(numberOfBytes):
        bytes.append(integer & 0x0FF)
        integer = integer >> 8
        
    return bytearray(bytes)
    
    
def hexString(data):
    '''
    Creates a string that is a byte sequense of the hex values input
    :param data: Example is '0A 23 34 56'
    '''
    
    h_str = ''
    data = data.split(' ')
    for byte in data :
        h_str += r'\x' + byte
    
    return h_str.decode('string_escape')

# setup the Logger
# -> should be done once
# initialize the logger
logger = logging.getLogger('MotorLog')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('[%(asctime)-15s] %(ClassName)s<%(com_port)s>: %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
    

class Motor(object):
    '''This class models a motor for stages'''
    def __init__(self, serial):
        '''
        Constructor method

        :param serial: the serial object that that corresponds to the port the motor is conected
        :type serial: serial object
        '''

        self.serial = serial      # 
        self.position = 0    # the position of the motor in steps
        self.zeros_position = 0    # the zero position
        self._count = -1    # internal step count from controller
    
        # request some info from controller to trigger the reading process
        self.serial.flushInput()
        self.serial.flushOutput()
        
        # MGMSG_HW_REQ_INFO
        self.serial.write(hexString('05 00 00 00 50 01'))
        self.serial.read(90)    # just read the response
        
        # get the logger we loaded once in the begining
        self.logger = logger
        
        # extra class info - for logger
        self.ext = {'com_port': self.serial.port, 'ClassName': 'Motor'}

        
    def delta_move(self, steps):
        '''
        Relative rotation onpos the motor

        :param steps: the number of steps to move (negative -> backwards)
        :type steps: Integer
        '''
    
        self.position += steps
    
        # MGMSG_MOT_MOVE_RELATIVE extended
        self.serial.write(hexString('48 04 06 00 D0 01'))    # header
        self.serial.write(hexString('01 00'))                # chanel id
        self.serial.write(int2hexStr(steps, 4))            # relative distance
        
        self.move_complete()
        
    def abs_move(self, steps):
        '''
        Relative rotation on the motor

        :param steps: the endpoint of motion
        :type steps: Integer
        '''
    
        # MGMSG_MOT_MOVE_RELATIVE extended
        self.serial.write(hexString('48 04 06 00 D0 01'))            # header
        self.serial.write(hexString('01 00'))                        # chanel id
        self.serial.write(int2hexStr(steps - self.position, 4))    # absolute distance
        
        self.position = steps
        
        # wait until move is complete
        self.move_complete()
        
    def get_position(self):
        '''return the motors current position'''
        
        return self.position
        
    def set_as_zero(self, new_zero):
        '''change the origin (zero)'''
        
        self.zeros_position = new_zero
        self.position -= new_zero
        
    def set_vel_params(self, vel_init, accel, vel_fin):
        '''
        Set the velocity parameters for the motor

        :param vel_init: initial velocity (steps / sec)
        :type vel_init: Integer
        :param accel: acceleration (steps / sec^2)
        :type accel: Integer
        :param vel_fin: max(final) velocity (steps / sec)
        :type vel_fin: Integer
        '''
        
        # MGMSG_MOT_SET_VELPARAMS
        self.serial.write(hexString('13 04 0E 00 D0 01'))        # head
        self.serial.write(hexString('01 00'))                    # chanel id
        self.serial.write(int2hexStr(vel_init, 4))                # initial velocity
        self.serial.write(int2hexStr(accel, 4))                # acceleration
        self.serial.write(int2hexStr(vel_fin, 4))                # final velocity
        
    def close(self):
        '''releases motor resources'''
        
        self.serial.close()
        
    def __str__(self):
        '''
         <For Debugging Purposes>
         gives information relevant to the motor state
        '''
        return 'position: ' + str(self.position) + '\nzeros-position: ' + str(self.zeros_position)
        
    def move_complete(self):
        '''
        Waits until the MOVE_COMPLETE message is received by the controller.
        Helper-function for delta_move() and abs_move() functions.
        '''
        
        self.serial.reset_input_buffer()
        
        # read the beginning of the header
        response = self.serial.read(2)

        while response != hexString('64 04'):    # MGMSG_MOT_MOVE_COMPLETED
            response = self.serial.read(2)
        # read the rest of the structure (20 bytes total)
        response_rest = self.serial.read(18)
        self._count = unpack('<l', response_rest[6:10])[0]
        
        # DEBUG
        self.logger.debug('move complete {}'.format(self._count), extra=self.ext)
        self.isMoving = False
        
    def _get_count(self):
        ''':returns: the count'''
        return self._count
        
    def _go_to_abs(self, steps):
        # MGMSG_MOT_MOVE_RELATIVE extended
        self.serial.write(hexString('53 04 06 00 D0 01'))            # header
        self.serial.write(hexString('01 00'))                        # chanel id
        self.serial.write(int2hexStr(steps, 4))    # absolute distance
        
        self.position = steps
        self.move_complete()