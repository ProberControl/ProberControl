#from Classes.xyzstage import XYZ_Stage
from . import raster
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy
#to measure procedure run-time
import time
from ..classes.Global_MeasureHandler import Global_MeasureHandler as gh

def getCouplingData(stages, chip):
    '''
        Function to run test on step noise associated with ELL8 Thorlabs
        Rotator stage.
    '''
    #Initialize Variables
    deg_offset = 1
    stepsize = 0.0014
    numOfSteps = int((deg_offset*2)/stepsize)
    pos = -1*deg_offset

    #Open File and write first line
    f = open('data.txt', 'w')
    stages[chip].rot.delta_angle(pos)

    for i in range(numOfSteps):
        power = _get_signal(stages)
        f.write(str(pos) + ' ' + str(power) + '\n')
        stages[chip].rot.delta_angle(stepsize)
        pos += stepsize

    f.close()

def getCouplingData2(stages, chip, target):
    '''
        Function to run test on step noise associated with ELL8 Thorlabs
        Rotator stage.
    '''
    #Initialize Variables
    deg_offset = 0.4
    stepsize = 0.0014
    numOfSteps = int((deg_offset)/stepsize)
    pos = 0
    start_pos = list(stages[target].get_coor_2d())

    #Open File and write first line
    f = open('data.txt', 'w')

    for i in range(numOfSteps):
        smooth_cross(stages, target)
        power = _get_signal(stages)
        f.write(str(pos) + ' ' + str(power) + '\n')
        stages[chip].rot.delta_angle(stepsize)
        pos += stepsize

    stages[target].set_coor_2d(start_pos)
    stages[chip].rot.delta_angle(-pos-stepsize)
    pos = -stepsize

    for i in range(numOfSteps-1):
        smooth_cross(stages, target)
        power = _get_signal(stages)
        f.write(str(pos) + ' ' + str(power) + '\n')
        stages[chip].rot.delta_angle(stepsize)
        pos -= stepsize

    f.close()

def getLaserData(stages, target):
    t = 0
    f = open('data.txt', 'w')
    for i in range(60):
        power = _get_signal(stages)
        f.write(str(t) + ' ' + str(power) + '\n')
        time.sleep(30)
        if i == 0:
            print('Success!')
        t += 30
    f.close()

def getSearchNoise(stages, target):
    f = open('data.txt', 'w')
    for i in range(200):
        smooth_cross(stages, target)
        power = _get_signal(stages)
        f.write(str(i+1) + ' ' + str(power) + '\n')
    f.close()

def alignGrating(stages, target):
	optimalAngle = -2
	offset = getAngleOffset()
	delta = optimalAngle - offset
	stages[target].gon_T.delta_rot(delta)
