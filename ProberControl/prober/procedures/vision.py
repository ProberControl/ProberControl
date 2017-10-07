import cv2
import numpy as np
import threading
import time

def _convertTheta(theta):
    '''
        Changes reference of the cv2.HoughLines line theta
    '''
    return theta*(180/np.pi) - 90
            
def setChipAngle(stages, video, chip, desired_angle, res=0.1):
    '''
        Set angle of chip edge as seen by video feed using chip stage
    '''
    stages[video]._beginScript()
    stages[video]._showLines()
    stages[video]._setRes(float(res))
    max_moves = 10
    while(stages[video].script_running):
        if np.any(stages[video].lines):
            actual_angle = _convertTheta(stages[video].lines[0][1])
            mismatch = float(desired_angle) - actual_angle
            if abs(mismatch) <= 2*res:
                stages[video]._endScript()
                break
            success = stages[chip].gon_T.delta_rot(mismatch)
            if success == False:
                stages[video]._endScript()
                print 'Procedure cannot be performed: Movement out of bounds'
                break

def setFiberChipOffset(stages, video, chip_stage, desired_offset, res=0.1):
    
    stages[video]._reset()
    stages[video]._setRegion()
    
    stages[video]._beginScript()
    stages[video]._showRegionLines()
    
    while(stages[video].script_running):
        if np.any(stages[video].lines):
            t0 = time.time()
            assignment = False
            chip_angle = None
            fiber_angle = None
            
            while(True):
                try:
                    chip_angle = _convertTheta(stages[video].lines['chip'][1])
                    fiber_angle = _convertTheta(stages[video].lines['fiber'][1]) #maybe replace the try with a if Boolean statement
                except:
                    pass
                if chip_angle == None or fiber_angle == None:
                    t1 = time.time()
                    if t1-t0 > 5:
                        print "Could not find both angles | Chip: {}, Fiber: {}".format(chip_angle,fiber_angle)
                        stages[video]._endScript()
                        break
                else:
                    assignment = True
                    break
                     
            if assignment == False:
                break
                
            actual_offset = chip_angle - fiber_angle
            mismatch = float(desired_offset) - actual_offset
            
            if abs(mismatch) <= 2*res:
                stages[video]._endScript()
                break
            
            success = stages[chip_stage].gon_T.delta_rot(mismatch)
            
            if success == False:
                stages[video]._endScript()
                print 'Procedure cannot be performed: Movement out of bounds'
                break
    
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