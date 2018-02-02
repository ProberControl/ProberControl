# Gonio-Stage class
# Inherits from Motor
# For motors/controllers attatched to the GNL10 or GNL18 gonio endpoint

# TODO: - find the specific step to degree coeff.
#        - design a precise mechanism to detect when the stage has reached a limit

from Motor_KST_ZST import Motor_KST_ZST as Motor, hexString
#import serial
import logging

GNL10 = 10
GNL18 = 18

STEPS_PER_MM = 34304

# GNL18 data
GNL18_ZERO_2_FIVE = 7    # in mm
GNL18_STEPS_PER_DEG = STEPS_PER_MM * GNL18_ZERO_2_FIVE / 5
GNL18_STOP_LIMIT = 5

# GNL10 data
GNL10_TEN_2_ZERO = 7.6    # in mm
GNL10_STEPS_PER_DEG = STEPS_PER_MM * GNL10_TEN_2_ZERO / 10
GNL10_STOP_LIMIT = 10

class GonStage_KST_Z812B(Motor):

    def __init__(self, ser, GNL_model):
        '''
         Constructor

         self (serial.Serial): the serial object bound to the device
         GNL_model (int): the goniometer stage model ( 10 for 'GNL10' or 18 for 'GNL18')
        '''

        self.ser = ser
        Motor.__init__(self, ser)
        self.ext['ClassName'] = 'GonStage'    # for logging
        self.home()
        # set internal constants based on model
        if model == GNL18:
            self.STEPS_PER_DEG = GNL18_STEPS_PER_DEG
            self.STOP_LIMIT = GNL18_STOP_LIMIT
        elif model == GNL10:
            self.STEPS_PER_DEG = GNL10_STEPS_PER_DEG
            self.STOP_LIMIT = GNL10_STOP_LIMIT
        else:
            self.logger.error('invalid model <{}>'.format(model), extra=self.ext)
            exit()
        # move to middle
        self.deg_pos = 0
        self.deg_zero = 0
        self.moving = False
        self.delta_rot(float(self.STOP_LIMIT))
        self.set_as_zero(float(self.STOP_LIMIT))
        if model == 'GNL10':
            self.STOP_LIMIT = GNL10_TEN_2_ZERO


    def home(self):
        '''
         Puts the motor to backward limit position, so that the
         position markers make sense
        '''

        # NOTE: Might need to call < MGMSG_MOT_SET_TSTACTUATORTYPE > first
        self.moving = True
        # MGMSG_MOT_MOVE_HOME
        self.ser.write(hexString('43 04 01 00 50 01'))
        self.ser.reset_input_buffer()
        response = self.ser.read(6)
        if response != hexString('44 04 01 00 01 50'):    # MGMSG_MOT_MOVE_HOMED
            self.logger.error('problem homing', extra=self.ext)
            exit()

        self.logger.info('homed successfully.', extra=self.ext)
        self.moving = False

    def delta_rot(self, degs):     #, m_callback = None, params = ()):
        '''
         Relative translation on the motor

         degs (float): the millimeters of rotation (negative -> backwards)
        '''

        self.moving = True
        # check that we will be within limits
        if abs(self.deg_pos + degs) > self.STOP_LIMIT or (self.deg_pos + degs) < -self.STOP_LIMIT:
            self.logger.warning('input would cause out of bounds error [{}]'.format(self.deg_pos + degs), extra=self.ext)
            self.moving = False
            return False

        self.deg_pos += degs
        # convert millimeters to steps
        steps = int(round(degs * self.STEPS_PER_DEG))

        Motor.delta_move(self, steps)
        self.moving = False
        return True

    def abs_rot(self, degs):
        '''
         Absolute translation on the motor

         degs (float): the millmeters of rotation (negative -> backwards)
        '''

        # check limits
        self.moving = True
        if abs(degs) > self.STOP_LIMIT:
            self.logger.warning('out of bounds error [{}]'.format(degs), extra=self.ext)
            self.moving = False
            return False

        # convert degrees to steps
        steps = int(round(degs * self.STEPS_PER_DEG))

        Motor.abs_move(self, steps)
        self.deg_pos = degs
        self.moving = False
        return True

    def get_deg_pos(self):
        '''
         return the motors current position, in millimeters
        '''

        return self.deg_pos

    def check_abs_transl(self,dist):
        '''
        Check wether a move to position 'dist' is in range

        '''
        if dist > self.STOP_LIMIT or dist < 0:
            return False
        else:
            return True

    def set_as_zero(self, zer_deg):
        '''
         change the origin (zero)
        '''

        n_zero = int(round(zer_deg * self.STEPS_PER_DEG))
        Motor.set_as_zero(self, n_zero)

        self.deg_zero = zer_deg
        self.deg_pos -= zer_deg



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
