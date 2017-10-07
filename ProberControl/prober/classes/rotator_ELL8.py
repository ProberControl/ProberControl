# the rotating stage class for the ELL8/M motor
# 	- wraps around Rot_Motor

from ..instruments.ELL8 import ELL8

DEG_PER_CNT = 0.00137329

class Rotator(ELL8):

	def __init__(self, ser):
		'''
		 Constructor

		 ser (Serial): the Serial object that corresponds to the port
		 the motor is connected to
		'''

		ELL8.__init__(self, ser)
		self.moving = False     #set to false
		self.deg_pos = 0	# position of motor, in degrees
		self.deg_zeros = 0	# the origin, in degrees

	def delta_angle(self, deg):	#, m_callback = None, params = ()):
		'''
		 Relative rotation on the motor

		 deg (float): the degrees of rotation (negative -> counter-clockwise)
		'''
		self.moving = True
		self.deg_pos += deg
		# convert degrees to steps
		steps = int(round(deg / DEG_PER_CNT))

		ELL8.delta_move(self, steps)
		while self.deg_pos >= 360:
			self.deg_pos -= 360
		self.moving = False

	def abs_angle(self, deg):
		'''
		 Relative rotation on the motor

		 deg (float): the degrees of rotation (negative -> counter-clockwise)
		'''
		d = deg
		while d >= 360:
			d -= 360

		self.moving = True
		# convert degrees to steps
		steps = int(round(d / DEG_PER_CNT))

		ELL8.abs_move(self, steps)
		self.deg_pos = d
		self.moving = False

	def get_angle(self):
		'''
		 return the motors current position, in degrees
		'''

		return self.deg_pos

	def set_as_zero(self, zer_deg):
		'''
		 change the origin (zero)
		'''

		n_zero = int(round(zer_deg / DEG_PER_CNT))
		ELL8.set_as_zero(self, n_zero)

		self.deg_zeros = zer_deg
		self.deg_pos -= zer_deg

	def __str__(self):
		'''
		 <For Debugging Purposes>
		 gives information relevant to the motor state
		'''

		return 'position(degrees): ' + str(self.deg_pos) + '\nzeros-position(degrees): ' + str(self.deg_zeros)


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
