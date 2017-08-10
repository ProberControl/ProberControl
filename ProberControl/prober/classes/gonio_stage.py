# Gonio-Stage class
# Inherits from Motor

# TODO: - find the specific step to degree coeff.
#        - design a precise mechanism to detect when the stage has reached a limit

from Motor import Motor
from Motor import hexString
import serial
import logging

STEPS_PER_MM = 34304

# GNL18 data
GNL18_ZERO_2_FIVE = 5.6    # in mm
GNL18_STEPS_PER_DEG = STEPS_PER_MM * GNL18_ZERO_2_FIVE / 5
GNL18_STOP_LIMIT = 5

# GNL10 data
GNL10_TEN_2_ZERO = 6.6999    # in mm
GNL10_STEPS_PER_DEG = STEPS_PER_MM * GNL10_TEN_2_ZERO / 10
GNL10_STOP_LIMIT = 10

class GonStage(Motor):
    
    def __init__(self, ser, model):
        '''
         Constructor
         
         self (serial.Serial): the serial object bound to the device
         model (string): the goniometer stage model ('GNL10' or 'GNL18')
        '''
    
        Motor.__init__(self, ser)
        self.ext['ClassName'] = 'GonStage'    # for logging
        self.home()
        # set internal constants based on model
        if model == 'GNL18':
            self.STEPS_PER_DEG = GNL18_STEPS_PER_DEG
            self.STOP_LIMIT = GNL18_STOP_LIMIT
        elif model == 'GNL10':
            self.STEPS_PER_DEG = GNL10_STEPS_PER_DEG
            self.STOP_LIMIT = GNL10_STOP_LIMIT
        else:
            self.logger.error('invalid model <{}>'.format(model), extra=self.ext)
            exit()
        # move to middle
        self.deg_pos = 0
        self.deg_zero = 0
        self.delta_rot(float(self.STOP_LIMIT))
        self.set_as_zero(float(self.STOP_LIMIT))
        
        
    def home(self):
        '''
         Puts the motor to backward limit position, so that the
         position markers make sense
        '''
        
        # NOTE: Might need to call < MGMSG_MOT_SET_TSTACTUATORTYPE > first
        
        # MGMSG_MOT_MOVE_HOME
        self.ser.write(hexString('43 04 01 00 50 01'))
        self.ser.reset_input_buffer()
        response = self.ser.read(6)
        if response != hexString('44 04 01 00 01 50'):    # MGMSG_MOT_MOVE_HOMED
            self.logger.error('problem homing', extra=self.ext)
            exit()
        
        self.logger.info('homed successfully.', extra=self.ext)
        
    def delta_rot(self, degs):     #, m_callback = None, params = ()):
        '''
         Relative translation on the motor
         
         degs (float): the millimeters of rotation (negative -> backwards)
        '''
        
        # check that we will be within limits
        if abs(self.deg_pos + degs) > self.STOP_LIMIT:
            self.logger.warning('input would cause out of bounds error [{}]'.format(self.deg_pos + degs), extra=self.ext)
            return
        
        self.deg_pos += degs
        # convert millimeters to steps
        steps = int(round(degs * self.STEPS_PER_DEG))
        
        Motor.delta_move(self, steps)
        
    def abs_rot(self, degs):
        '''
         Absolute translation on the motor
         
         degs (float): the millmeters of rotation (negative -> backwards)
        '''
        
        # check limits
        if abs(degs) > self.STOP_LIMIT:
            self.logger.warning('out of bounds error [{}]'.format(degs), extra=self.ext)
            return
        
        # convert degrees to steps
        steps = int(round(degs * self.STEPS_PER_DEG))
        
        Motor.abs_move(self, steps)
        self.deg_pos = degs
        
    def get_deg_pos(self):
        '''
         return the motors current position, in millimeters
        '''
        
        return self.deg_pos
        
    def set_as_zero(self, zer_deg):
        '''
         change the origin (zero)
        '''
        
        n_zero = int(round(zer_deg * self.STEPS_PER_DEG))
        Motor.set_as_zero(self, n_zero)
        
        self.deg_zero = zer_deg
        self.deg_pos -= zer_deg
        
