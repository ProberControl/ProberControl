# Step Motor Class
#    - wraps around Motor

from Motor import Motor, hexString, int2hexStr
import serial
import logging
import time
from struct import unpack

STEPS_PER_MM = 2184533.33    # 136533.33
LIMIT_SWITCH = 13 
BACKLASH_STEPS = 43691

# DEBUG
Constructor_Counter = 0
Home_Counter = 0

class StepMotor(Motor):
    
    def __init__(self, ser):
        '''
         Constructor
         
         ser (Serial): the Serial object that corresponds to the port
         the motor is connected to
        '''
        ###
        global Constructor_Counter
        Constructor_Counter += 1
        ###
        self.ser = ser
        self.moving = False
        Motor.__init__(self, ser)
        self.ext['ClassName'] = 'StepMotor'
        self.home()                # home motor
        self._set_backlash(0)    # set 0 backlash correction
        self.mm_pos = 0            # position of motor, in millimieters
        self.mm_zeros = 0        # the origin, in millimeters
        
    def home(self):
        '''
         Puts the motor to backward limit position, so that the
         position markers make sense
        '''
        ###
        global Home_Counter
        Home_Counter += 1
        ###
        self.moving = True
        self.logger.debug('Homing...', extra=self.ext)
        
        # save that change with < MGMSG_MOT_SET_EEPROMPARAMS >
        self.ser.write(hexString('B9 04 04 00 D0 01'))
        self.ser.write(hexString('01 00'))    # chanel id
        self.ser.write(hexString('FE 04'))    # the specific message we want to save
        
        # call < MGMSG_MOT_SET_TSTACTUATORTYPE > first 
        # to specify that we are using the ZFS 13mm actuator => 0x41
        # FE, 04, 41, 00, 50, 01
        self.ser.write(hexString('FE 04 41 00 50 01'))
        
        # home motor on the correct limit switch
        # < MGMSG_MOT_REQ_HOMEPARAMS >
        self.ser.write(hexString('41 04 01 00 50 01'))
        home_response = self.ser.read(20)
        if home_response[0:2] != hexString('42 04'):
            self.logger.error('problem reading data from controller while homing', extra=self.ext)
            exit()
        # < MGMSG_MOT_SET_HOMEPARAMS >
        self.ser.write(hexString('40 04 0E 00 D0 01'))    # header
        self.ser.write(hexString('01 00'))                # chan-ident
        self.ser.write(int2hexStr(1, 2))                # Home Dir
        self.ser.write(int2hexStr(1, 2))                # Limit Switch
        self.ser.write(home_response[12:16])            # Home Velocity
        self.ser.write(home_response[16:20])            # Offset Distance
        
        # MGMSG_MOT_MOVE_HOME
        self.ser.write(hexString('43 04 01 00 50 01'))
        self.ser.reset_input_buffer()
        response = self.ser.read(6)
        if response != hexString('44 04 01 00 01 50'):    # MGMSG_MOT_MOVE_HOMED
            self.logger.error('problem homing', extra=self.ext)
            exit()
        
        self.logger.info('homed successfully.', extra=self.ext)
        self.moving = False
        
    def get_info(self):
        '''
         Get information back form the controller
         Used for debugging purposes
        '''
        
        # MGMSG_HW_REQ_INFO
        self.ser.write(hexString('05 00 00 00 50 01'))
        response = self.ser.read(90)
        print response
        
    def _set_backlash(self, backlash_distance):
        '''
         Set the backlash correction distance for backwards motor 
         movement
         
         backlash_distance (int): in encoder steps
        '''
        
        # change backlash value
        self.ser.write(hexString('3A 04 06 00 D0 01'))        # header
        self.ser.write(hexString('01 00'))                    # chanel id
        self.ser.write(int2hexStr(backlash_distance, 4))    # backlash dist

        # request backlash data
        self.ser.write(hexString('3B 04 01 00 50 01'))
        # confirm backlash distance value
        res = self.ser.read(12)
        back_dist_r = unpack('<l', res[8:12])[0]
        if back_dist_r != backlash_distance:
            self.logger.error('Problem setting backlash distance [{}]'.format(backlash_distance), extra=self.ext)
        
    def delta_transl(self, dist):    #, m_callback = None, params = ()):
        '''
         Relative translation on the motor
         
         dist (float): the millimeters of translation (negative -> backwards)
         m_callback (function): (Optional) a function that will run while the motor
                                will be in motion. (e.g. show camera)
                                This callback's last parameter must be a callback itself,
                                named 'callback'
         params (tuple): the callback's parameters
        '''
        
        self.moving = True
        # check weather we are within limits
        if self.mm_pos + dist > LIMIT_SWITCH or self.mm_pos + dist < 0:
            self.logger.error('Out of bounds error (dist:{}, pos:{})'.format(dist, self.mm_pos), extra=self.ext)
            self.moving = False
            return False
        self.mm_pos += dist
        # convert millimeters to steps
        steps = int(round(dist * STEPS_PER_MM))
        
        if steps < 0:
            Motor.delta_move(self, -(steps - BACKLASH_STEPS))
            # manual backlash correction
            Motor.delta_move(self, -BACKLASH_STEPS)
        else:
            Motor.delta_move(self, -steps)
        
        self.moving = False
        return True

    def check_abs_transl(self,dist):
        '''
        Check wether a move to position 'dist' is in range 
        
        '''
        if dist > LIMIT_SWITCH or dist < 0:
            return False
        else:
            return True

    def abs_transl(self, dist):
        '''
         Absolute translation on the motor
         
         dist (float): the millmeters of rotation (negative -> backwards)
        '''
        self.moving = True
        # check weather we are within limits
        if dist > LIMIT_SWITCH or dist < 0:
            self.logger.error('Out of bounds error (abs_pos:{})'.format(dist), extra=self.ext)
            self.moving = False
            return
        # convert degrees to steps
        steps = int(round(dist * STEPS_PER_MM))
        
        # manual backlash correction
        if dist - self.mm_pos < 0:
            Motor.abs_move(self, -(steps - BACKLASH_STEPS))
            Motor.delta_move(self, -BACKLASH_STEPS)
        else:
            Motor.abs_move(self, -steps)
        self.mm_pos = dist
        self.moving = False
        
    def get_mm_pos(self):
        '''
         return the motors current position, in millimeters
        '''
        
        return self.mm_pos
        
    def set_as_zero(self, zer_mm):
        '''
         change the origin (zero)
        '''
        
        n_zero = int(round(zer_mm / STEPS_PER_MM))
        Motor.set_as_zero(self, n_zero)
        
        self.mm_zeros = zer_mm
        self.mm_pos -= zer_mm
        
    def __str__(self):
        '''
         <For Debugging Purposes>
         gives information relevant to the motor state
        '''
        
        return 'StepMotor({})\n'.format(self.ser.port) + '  position(millimeters): ' + str(self.mm_pos) + '\n  zeros-position(millimeters): ' + str(self.mm_zeros)


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
