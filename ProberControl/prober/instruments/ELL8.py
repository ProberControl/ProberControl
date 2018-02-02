# the motor class for ELL8/M Rotation Stage

#import serial
import threading
from struct import unpack
import logging
import binascii


def int2hexStr(integer, nb):
	'''
	 Convert an integer to its corresponding bytearray

	 integer (int): the number we want to convert
	 nb (int): the number of bytes
	'''

	bytes = []
	for i in range(nb):
		bytes.append(integer & 0x0FF)
		integer = integer >> 8
	bytes.reverse()
	s = str(binascii.hexlify(bytearray(bytes)))
	return s.upper()

def hexString(data):
	'''
	 Creates a string that is a byte sequense of the hex values
	 input
	 e.g. data = '0A 23 34 56'
	'''

	h_str = ''
	data = data.split(' ')
	for byte in data :
		h_str += r'\x' + byte

	return h_str.decode('string_escape')

# setup the Logger
# -> should be done once
# initialize the logger
logger = logging.getLogger(__name__)
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

class ELL8(object):

	def __init__(self, ser):
		'''
		    Constructor
		'''
		self.ser = ser
		self.ser.baudrate = 9600
		self.position = 0
		self.zeros_position = 0
		self.count = -1


		# request some info from controller to trigger the reading process
		self.ser.flushInput()
		self.ser.flushOutput()

		# get the logger we loaded once in the begining
		self.logger = logger

		# extra class info - for logger
		self.ext = {'com_port': self.ser.port, 'ClassName': 'Rot_Motor'}

                self.home()

	def delta_move(self, steps):
		'''
		    rotate the stage by specified # of steps
		'''
		self.position += steps

		#_HOSTREQ_MOVERELATIVE
		self.ser.write('0mr')
		self.ser.write(int2hexStr(steps,4))

		#wait for ell8 position message
		self.move_complete()

	def abs_move(self, steps):
		'''
		    rotate the stage by specified # of steps
		'''

		#_HOSTREQ_MOVERELATIVE
		self.ser.write('0mr')
		self.ser.write(int2hexStr(steps-self.position,4))

		self.position = steps

		#wait for ell8 position message
		self.move_complete()

	def home(self):
		'''
		    homes the stage
		'''
		#
		self.ser.write('0ho0')
		self.move_complete()

	def get_position(self):
		'''
		 return the motors current position
		'''
		#_HOSTREQ_HOME
		return self.position

	def set_as_zero(self, zer_deg):
		'''
		 change the origin (zero)
		'''

		self.zeros_position = new_zero
		self.position -= new_zero

	def set_vel_params(self, vel):
		'''
		 Set the velocity parameters for the motor in terms of percentage of max
		'''

		# _HOSTSET_VELOCITY
		self.ser.write('0sv')           # head
		self.ser.write(int2hexStr(vel))

	def __str__(self):
		'''
		 <For Debugging Purposes>
		 gives information relevant to the motor state
		'''

		return 'position: ' + str(self.position) + '\nzeros-position: ' + str(self.zeros_position)

	def close(self):
		'''
		    releases motor control
		'''
		self.ser.close()

	def move_complete(self):
		rx = ''
		while rx[:3] != '0PO':
			if self.ser.in_waiting > 0:
				rx = str(self.ser.read(13))

	def _get_count(self):
		return self._count






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
