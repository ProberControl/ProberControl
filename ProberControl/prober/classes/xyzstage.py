# XYZ-Stage Class

from stp_mtr import StepMotor
import threading
import numpy as np
import logging
import math

# helper functions to add/subtract tuples
def t_add(tuple1, tuple2):
    return tuple(np.add(tuple1, tuple2))
    
def t_sub(tuple1, tuple2):
    return tuple(np.subtract(tuple1, tuple2))
##


class XYZ_Stage(object):

    def __init__(self, ser_list,off_angle=0):
        '''
         Constructor
         
         ser_list (list): a list with serial objects corresponding to 
                          the x, y and z motors respectively
        '''
        
        # self.x_axis = StepMotor.__new__(StepMotor)    # StepMotor(ser_list[0])
        # self.y_axis = StepMotor.__new__(StepMotor)    # StepMotor(ser_list[1])
        # self.z_axis = StepMotor.__new__(StepMotor)    # StepMotor(ser_list[2])
        
        ## threading approach
        # t_x = threading.Thread(target=StepMotor.__init__, args=(self.x_axis, ser_list[0]))
        # t_y = threading.Thread(target=StepMotor.__init__, args=(self.y_axis, ser_list[1]))
        # t_z = threading.Thread(target=StepMotor.__init__, args=(self.z_axis, ser_list[2]))
        
        # new threading approach
        def init_x_axis():
            self.x_axis = StepMotor(ser_list[0])
        def init_y_axis():
            self.y_axis = StepMotor(ser_list[1])
        def init_z_axis():
            self.z_axis = StepMotor(ser_list[2])
            
        t_x = threading.Thread(target=init_x_axis)
        t_y = threading.Thread(target=init_y_axis)
        t_z = threading.Thread(target=init_z_axis)
        
        t_x.start(), t_y.start(), t_z.start()
        # t_x.join(), t_y.join(), t_z.join()
    
        self.x, self.y, self.z = (0, 0, 0)
        self.zeros = (0, 0, 0)
        self.stepsize = 0.001
        
                # virtual leveling helpers
        self.ang_x = None
        self.ang_y = None

        # offset angle of x and y stages from optimal axis
        self.off_angle = float(off_angle)
        

        def set_off_angle(self,off_angle):
            self.off_angle = float(off_angle)

        def get_off_angle(self):
            return self.off_angle
        
        def get_calibrated(self):
            '''
                Check whether the stage was calibrated to chip by checking whether zeros are unequal 0
            '''
            if self.zeros == (0,0,0):
                return False
            else:
                return True

    def home(self):
        '''Sets all of step-motors to home position'''
        
        # Create threads for homing
        x = threading.Thread(self.x_axis.home())
        y = threading.Thread(self.y_axis.home())
        z = threading.Thread(self.z_axis.home())
        
        # Starts x-direction, then y-direction and z-direction
        x.start(); y.start(), z.start()
    
        # Reset isntance variables
        self.x, self.y, self.z = (0, 0, 0)
        self.zeros = (0, 0, 0)
        self.stepsize = 0.001
    
    def check_coordinates_2d(self, target_pos):
        '''
         Check whather move to a point in space is possible within actuator range
         
         target_pos (2-tuple): (x,y) coordinates of the final point
        '''            
        return self.check_coordinates((target_pos[0], target_pos[1], self.z))


    def check_coordinates(self, target_pos):
        '''
         Check whather move to a point in space is possible within actuator range
         
         target_pos (3-tuple): (x,y,z) coordinates of the final point
        '''
        act_x, act_y, act_z = t_add(target_pos, self.zeros)
        if self.x_axis.check_abs_transl(act_x) and self.y_axis.check_abs_transl(act_y) and self.z_axis.check_abs_transl(act_z):
            return True
        else:
            return False

    def set_coordinates(self, target_pos, long=False):
        '''
         Move to a point in the plane
         
         target_pos (3-tuple): (x,y,z) coordinates of the final point
        '''
        # actual distances sent to StepMotor
        act_x, act_y, act_z = t_add(target_pos, self.zeros)

        if not self.x_axis.moving and not self.y_axis.moving and not self.z_axis.moving and self.x_axis.check_abs_transl(act_x) and self.y_axis.check_abs_transl(act_y) and self.z_axis.check_abs_transl(act_z):
            x_d = target_pos[0] - self.x
            y_d = target_pos[1] - self.y
            
            self.x, self.y, self.z = target_pos
            
            z_extra = 0
            if long :
                if self.leveled():
                    z_extra += x_d * math.tan(math.radians(self.ang_x)) + y_d * math.tan(math.radians(self.ang_y))
                self.z += z_extra
                act_z += z_extra
        
            # threading approach
            t_x = threading.Thread(target=StepMotor.abs_transl, args=(self.x_axis, act_x))
            t_y = threading.Thread(target=StepMotor.abs_transl, args=(self.y_axis, act_y))
            t_z = threading.Thread(target=StepMotor.abs_transl, args=(self.z_axis, act_z))
            
            if z_extra > 0:
                t_x.start(), t_y.start()
                t_x.join(), t_y.join()
                t_z.start()
                t_z.join()
            elif z_extra < 0:
                t_z.start()
                t_z.join()
                t_x.start(), t_y.start()
                t_x.join(), t_y.join()
            else:
                t_x.start(), t_y.start(), t_z.start()
                t_x.join(), t_y.join(), t_z.join()
        else:
            print 'XYZ_stage::error: Attempted move out of bounds (abs_pos:{},{},{})'.format(act_x, act_y, act_z)
            
    def set_coor_2d(self, target_pos, long=False):
        '''
         Move to a point in the plane
         
         target_pos (2-tuple): (x,y) coordinates of the final point
        '''
        
        self.set_coordinates((target_pos[0], target_pos[1], self.z), long)

    def set_stepsize(self,stepsize):
        '''
        Updates the stepsize used in step() function
        '''
        self.stepsize = stepsize
        
    def step(self, direction):
        '''
        - Move Stage in either direction by one step
        - Step Size defined in set_stepsize()
        - direction expected to be char: U(p),D(own) L(eft),R(ight) F(orward),B(ackward)
        '''
        if self.x_axis.moving == False:
            if direction == 'F':
                if self.x_axis.delta_transl(self.stepsize):
                    self.x += self.stepsize
            if direction == 'B':
                if self.x_axis.delta_transl(-self.stepsize):
                    self.x -= self.stepsize
        if self.y_axis.moving == False:
            if direction == 'L':
                if self.y_axis.delta_transl(self.stepsize):
                    self.y += self.stepsize        
            if direction == 'R':
                if self.y_axis.delta_transl(-self.stepsize):
                    self.y -= self.stepsize
        if self.z_axis.moving == False:
            if direction == 'U':
                if self.z_axis.delta_transl(-self.stepsize):
                    self.z -= self.stepsize    
            if direction == 'D':
                if self.z_axis.delta_transl(self.stepsize):
                    self.z += self.stepsize            

                                                
    def get_coordinates(self):
        '''
         Returns the current position of the XYZ-Stage relative to the set origin
        '''
        return (self.x, self.y, self.z)
        
    def get_coor_2d(self):
        '''
         Returns the current position of the XYZ-Stage relative to the set origin
        '''
        return (self.x, self.y)
        
    def get_real_coordinates(self):
        '''
         Returns the actual position of the XYZ-Stage (relative to homing)
        '''
        return t_add((self.x, self.y, self.z), self.zeros)
        
    def set_as_zero(self, new_zero):
        '''
         Change the origin
         
         new_zero (3-tuple): (x,y,z) coordinates of the new origin
        '''
        
        actual = t_add((self.x, self.y, self.z), self.zeros)
        self.x, self.y, self.z = t_sub(actual, new_zero)
        self.zeros = new_zero
        
    def set_cur_as(self, correct_pos):
        '''
         Changes the coordinates of the current position, esentially
         computing the new origin. Does NOT involve any motor movement
         
         correct_pos (3-tuple): (x,y,z) coordinates of the "corect" position
        '''
        
        zero_trans = t_sub((self.x, self.y, self.z), correct_pos)
        self.set_as_zero(t_add(self.zeros, zero_trans))
        
    def set_cur_as_2d(self, correct_pos):
        '''
         Changes the coordinates of the current position, esentially
         computing the new origin. Does NOT involve any motor movement
         
         correct_pos (2-tuple): (x,y) coordinates of the "corect" position
        '''
        
        correct_pos_3 = (correct_pos[0], correct_pos[1], self.z)
        self.set_cur_as(correct_pos_3)
        
    def set_level(self, ang_x, ang_y):
        '''
         set variables for virtual leveling
         Note: the axes are relative to the stage
         
         ang_x (float): angle in x-axis
         ang_y (float): anfle in y-axis
        '''
        
        self.ang_x = ang_x
        self.ang_y = ang_y
        
    def leveled(self):
        '''
         Check if virtual leveling parameters have been set
        '''
        x = self.ang_x == None
        y = self.ang_y == None
        if not x :
            if y:
                raise AssertionError('Incorrect virtual level initialization')
            else:
                return True
        else:
            return False
        
    def close(self):
        '''
         Closes the underlying motors
        '''
        
        self.x_axis.close()
        self.y_axis.close()
        self.z_axis.close()
    


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
