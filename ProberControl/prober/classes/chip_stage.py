#    Chip Stage class
#
# Be aware positive rotation of gon_r move chip right edge downwards
# Be aware positive rotation of gon_l move chip top edge downwards


import threading
#from rotator import Rotator
from rotator_ELL8 import Rotator
from gonio_stage import GonStage
import numpy as np

# helper functions to add/subtract tuples
def t_add(tuple1, tuple2):
    return tuple(np.add(tuple1, tuple2))
    
def t_sub(tuple1, tuple2):
    return tuple(np.subtract(tuple1, tuple2))
##

class ChipStage(object):
    
    def __init__(self, ser_list):
            self.name = ''

            self.stepsize = 1
            
            # To bring the dist_measurement to valid start point
            # can be left at zero with wide enough chip holders
            self.width_off = 0 #3.5    # 2.5
            self.length_off = 4 #1.0    # 1.5
            
            #Calibration for Chip Leveling for X-Axis
            self.x_coordX = 0
            self.y_coordX = 3.5

            #Calibration for Chip Leveling for Y-Axis
            self.x_coordY = 8.5
            self.y_coordY = 1
            
            self.r, self.t, self.b = (0, 0, 0)
            self.zeros = (0, 0, 0)
            
            def r_init():
                self.rot = Rotator(ser_list[0])
            def gT_init():
                self.gon_T = GonStage(ser_list[1], 'GNL10')
            def gB_init():
                self.gon_B = GonStage(ser_list[2], 'GNL18')

            t_r = threading.Thread(target=r_init)
            t_gT = threading.Thread(target=gT_init)
            t_gB = threading.Thread(target=gB_init)

            t_r.start(), t_gB.start(), t_gT.start()
            t_r.join(), t_gB.join(), t_gT.join()

    def set_stepsize(self,stepsize):
        '''
        Updates the degree stepsize used in step() function
        '''
        self.stepsize = stepsize
    
    def home(self):
        ''' Sets all chip stage motors to home'''
        
        r = threading.Thread(self.rot.home())
        gT = threading.Thread(self.gon_T.home())
        gB = threading.Thread(self.gon_B.home())
        
        # Starts x-direction, then y-direction and z-direction
        r.start(); gT.start(), gB.start()
    
        # Reset isntance variables
        self.r, self.t, self.b = (0, 0, 0)
        self.zeros = (0, 0, 0)
        self.stepsize = 1
    
    def check_coordinates(self, target_pos):
        act_r, act_t, act_b = t_add(target_pos, self.zeros)
        if self.gon_T.check_abs_transl(act_t) and self.gon_T.check_abs_transl(act_b):
            return True
        else:
            return False
    
    def set_stepsize(self,stepsize):
        '''
        Updates the stepsize used in step() function
        '''
        self.stepsize = stepsiz

    def step(self, direction):
        '''
        - Move Stage in either direction by one step
        - Step Size defined in set_stepsize()
        - direction expected to be char: L(CW),R(CCW)
        '''
        if self.rot.moving == False:
            if direction == 'U':
                self.rot.delta_angle(self.stepsize)
                self.r += self.stepsize
            if direction == 'D':
                self.rot.delta_angle(-self.stepsize)
                self.r -= self.stepsize
        if self.gon_B.moving == False:
            if direction == 'L':
                self.gon_B.delta_rot(self.stepsize)
                self.b += self.stepsize
            if direction == 'R':
                self.gon_B.delta_rot(-self.stepsize)
                self.b -= self.stepsize
        if self.gon_T.moving == False:
            if direction == 'F':
                self.gon_T.delta_rot(self.stepsize)
                self.t += self.stepsize
            if direction == 'B':
                self.gon_T.delta_rot(-self.stepsize)
                self.t -= self.stepsize
                
    def get_coordinates(self):
        return (self.r, self.t, self.b)
    
    def get_rot(self):
        return self.rot.get_angle()
        
    def set_coordinates(self, target_pos):
        '''
         Move to a point in the plane
         
         target_pos (3-tuple): (rot,g_T ,g_B) coordinates of the final point
        '''
        # actual distances sent to motors
        act_r, act_t, act_b = t_add(target_pos, self.zeros)

        if not self.rot.moving and not self.gon_T.moving and not self.gon_B.moving and self.gon_T.check_abs_transl(act_t) and self.gon_B.check_abs_transl(act_b):
            self.r, self.t, self.b = target_pos
        
            # threading approach
            t_r = threading.Thread(target=Rotator.abs_angle, args=(self.rot, act_r))
            t_t = threading.Thread(target=GonStage.abs_rot, args=(self.gon_T, act_t))
            t_b = threading.Thread(target=GonStage.abs_rot, args=(self.gon_B, act_b))
            
            t_r.start(), t_t.start(), t_b.start()
            t_r.join(), t_t.join(), t_b.join()
        else:
            print 'chip_stage::error: Attempted move out of bounds (abs_pos:{},{},{})'.format(act_r, act_t, act_b)
    
    def set_rot(self, target_pos):
        '''
        Rotate the chip stage
        '''
        self.set_coordinates((target_pos, self.t, self.b))
    
    def close(self):
        '''
         Closes the underlying motors
        '''
        
        self.rot.close()
        self.gon_T.close()
        self.gon_B.close()
                
    def set_whoAmI(self, name):
        self.name = name

    def whoAmI(self):
        return self.name

    def whatCanI(self):
        return self.name



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
