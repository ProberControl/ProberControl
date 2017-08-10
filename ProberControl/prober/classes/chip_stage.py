#    Chip Stage class
#
# Be aware positive rotation of gon_r move chip right edge downwards
# Be aware positive rotation of gon_l move chip top edge downwards


import threading
from rotator import Rotator
from gonio_stage import GonStage

class ChipStage(object):
    
    def __init__(self, ser_list):

            self.stepsize = 10
            
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
            
            def r_init():
                self.rot = Rotator(ser_list[0])
            def gl_init():
                self.gon_l = GonStage(ser_list[1], 'GNL10')
            def gr_init():
                self.gon_r = GonStage(ser_list[2], 'GNL18')

            t_r = threading.Thread(target=r_init)
            #t_gl = threading.Thread(target=gl_init)
            #t_gr = threading.Thread(target=gr_init)

            t_r.start()#, t_gl.start(), t_gr.start()
            t_r.join()#, t_gl.join(), t_gr.join()

    def set_stepsize(self,stepsize):
        '''
        Updates the degree stepsize used in step() function
        '''
        self.stepsize = stepsize

    def step(self, direction):
        '''
        - Move Stage in either direction by one step
        - Step Size defined in set_stepsize()
        - direction expected to be char: L(CW),R(CCW)
        '''
        if self.rot.moving == False:
            if direction == 'L':
                self.rot.delta_angle(self.stepsize)
                self.angle = self.rot.deg_pos
            if direction == 'R':
                self.rot.delta_angle(-self.stepsize)
                self.angle = self.rot.deg_pos
    


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
