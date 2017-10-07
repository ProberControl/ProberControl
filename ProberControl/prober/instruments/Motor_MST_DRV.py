# the Motor class

import serial
import time
import threading
from struct import unpack
import logging

def send_short_dst_src(ser, bay=0):
	if bay == 0:
		ser.write(hexString('50 01'))

	else:
		ser.write(hexString('2{:1d} 01'.format(int(bay))))


def send_long_dst_src(ser, bay=0):
	if bay == 0:
		ser.write(hexString('D0 01'))

	else:
		ser.write(hexString('A{:1d} 01'.format(int(bay))))

def send_chan_ident(ser, chan=1):
	ser.write(hexString('{:02d} 00'.format(int(chan))))

def prep_short_src_dst(bay=0):
	if bay == 0:
		return '01 50'

	else:
		return '01 2'+str(int(bay))

def prep_long_src_dst(bay=0):
	if bay == 0:
		return '81 50'

	else:
		return '81 2'+str(int(bay))

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


class Motor_MST_DRV(object):
    '''This class models a motor for stages'''
    def __init__(self, serial,bay=0,chan=1):
        '''
        Constructor method

        :param serial: the serial object that that corresponds to the port the motor is conected
        :type serial: multi_serial object

		:param bay: the bay of the motor controller in main frame. For stand alone system bay should be 0.
		:type ser: integer

		:param chan: channel of motor controller in corresponding bay
		:type chan: integer

		:param lock: if the step motor shares a serial connection with other motors (by being a part of a mainframe)
		the lock needs to be a threading.Lock() object shared with all objects making
		calls to the shared serial interface. Before each serial call lock.acquire() and after each call lock.realease() needs to be called
		:type lock: threading.Lock() object
        '''

        self.serial = serial

        self.bay  = int(bay)
        self.chan = int(chan)

        self.position = 0          # the position of the motor in steps
        self.zeros_position = 0    # the zero position
        self._count = -1           # internal step count from controller

		#Acquire Lock over Serial
        if self.ser.lock:
            self.ser.lock.acquire()

        # request some info from controller to trigger the reading process
        self.serial.flushInput()
        self.serial.flushOutput()

		#MGMSG_HW_NO_FLASH_PROGRAMMING
        self.serial.write(hexString('18 00 00 00'))
        send_short_dst_src(self.ser,self.bay)

		#MGMSG_MOD_SET_CHANENABLESTATE
        self.serial.write(hexString('10 02 {:02d} 01'.format(int(self.chan))))
        send_short_dst_src(self.ser,self.bay)

		# Relase Serial
        if self.ser.lock:
			self.ser.lock.release()

        # get the logger we loaded once in the begining
        self.logger = logger

        # extra class info - for logger
        self.ext = {'com_port': self.serial.port+':'+str(self.bay)+':'+str(self.chan), 'ClassName': 'Motor'}


    def delta_move(self, steps):
        '''
        Relative rotation onpos the motor

        :param steps: the number of steps to move (negative -> backwards)
        :type steps: Integer
        '''

        self.position += steps

		#Acquire Lock over Serial
        if self.ser.lock:
			self.ser.lock.acquire()

        # MGMSG_MOT_MOVE_RELATIVE extended

        self.serial.write(hexString('48 04 06 00'))    # header
        send_long_dst_src(self.ser, self.bay)
        send_chan_ident(self.ser, self.chan)
        self.serial.write(int2hexStr(steps, 4))        # relative distance

		# Relase Serial
        if self.ser.lock:
			self.ser.lock.release()

        self.move_complete()

    def abs_move(self, steps):
        '''
        Relative rotation on the motor

        :param steps: the endpoint of motion
        :type steps: Integer
        '''

		#Acquire Lock over Serial
        if self.ser.lock:
			self.ser.lock.acquire()

        # MGMSG_MOT_MOVE_RELATIVE extended
        self.serial.write(hexString('48 04 06 00'))            # header
        send_long_dst_src(self.ser, self.bay)
        send_chan_ident(self.ser, self.chan)
        self.serial.write(int2hexStr(steps - self.position, 4))   # absolute distance

		# Relase Serial
        if self.ser.lock:
			self.ser.lock.release()

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

		#Acquire Lock over Serial
        if self.ser.lock:
			self.ser.lock.acquire()

        # MGMSG_MOT_SET_VELPARAMS

        self.serial.write(hexString('13 04 0E 00'))        # head
        send_long_dst_src(self.ser, self.bay)
        send_chan_ident(self.ser, self.chan)
        self.serial.write(int2hexStr(vel_init, 4))                # initial velocity
        self.serial.write(int2hexStr(accel, 4))                # acceleration
        self.serial.write(int2hexStr(vel_fin, 4))                # final velocity

		# Relase Serial
        if self.ser.lock:
			self.ser.lock.release()

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

        counter = 0
        found = False
        while counter < 60 and found == False: # MGMSG_MOT_MOVE_COMPLETED
            time.sleep(1)
            #self.ser.print_buffer()
            #Acquire Lock over Serial
            if self.ser.lock:
			    self.ser.lock.acquire()
            found = self.ser.in_buffer(hexString('64 04 0E 00 '+prep_long_src_dst(self.bay)+' {:02d} 00'.format(self.chan)),12)
            if self.ser.lock:
			    self.ser.lock.release()
            counter = counter + 1

        if counter >= 60:
            self.logger.error('problem with recent move', extra=self.ext)

        # DEBUG
        self.logger.debug('move complete {}'.format(self._count), extra=self.ext)
        self.isMoving = False

    def _get_count(self):
        ''':returns: the count'''
        return self._count

    def _go_to_abs(self, steps):

		#Acquire Lock over Serial
        if self.ser.lock:
			self.ser.lock.acquire()

        # MGMSG_MOT_MOVE_RELATIVE extended

        self.serial.write(hexString('53 04 06 00'))            # header
        send_long_dst_src(self.ser, self.bay)
        send_chan_ident(self.ser, self.chan)
        self.serial.write(int2hexStr(steps, 4))    # absolute distance

		# Relase Serial
        if self.ser.lock:
			self.ser.lock.release()

        self.position = steps
        self.move_complete()

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
