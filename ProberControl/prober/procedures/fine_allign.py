''' Set of functions for fine-allignment of fibers over grating couplers. '''

#from Classes.xyzstage import XYZ_Stage
from . import raster
import matplotlib
import collections
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy
#to measure procedure run-time
import time
from ..classes.Global_MeasureHandler import Global_MeasureHandler as gh

# Getting Global_MeasureHandler (singleton)instance; Do not change this!
gh = gh()

# default unset
__selected_function = None
STD_TOOL = "MPowerMeter"

def _report(msg):
    prt_msg = 'fine-allign: ' + msg
    print(prt_msg)

def _set_meas_fun(fn):
    global __selected_function
    __selected_function = fn

def set_signal_source(stages, source_string=''):

    if source_string in list(stages.keys()):
        feedbackfunc = getattr(stages[source_string], "get_feedback", None)
        if isinstance(feedbackfunc, collections.Callable):
            _set_meas_fun(stages[source_string].get_feedback)
            return True
        else:
            _report(str(source_string)+" does not supply get_feedback function")
            return False;

    else:
        _report(str(source_string)+" is not a member of the Stages Dictionary")
        return False;


def _get_signal(stages):
    global __selected_function

    if __selected_function == None:
        if not(set_signal_source(stages, source_string=STD_TOOL) or set_signal_source(stages, source_string=STD_TOOL+"1")):
            return "Error"

    return __selected_function()


def fast_align(stages, target,thresh=-60):
    # If power reading is below threshold search by raster
    if _get_signal(stages) < thresh:
        if not _raster_thresh(stages, target,thresh):
            print('Cannot get first light - abort alignment')
            return False

    # Perform Gradient Ascent to move quickly to higher powers
    gradient_ascent(stages, target,False)

    # Perform cross peak search
    smooth_cross(stages,target)


def _raster_thresh(stages, target,thresh=-55, size=(15,15),step=0.001):
    # place the current point at the center
    cur_pos = stages[target].get_coordinates()
    print(size)
    new_pos = (cur_pos[0] - size[0]/2.0*step, cur_pos[1] - size[1]/2.0*step, cur_pos[2])
    stages[target].set_coordinates(new_pos)
    # keep track of the power for each point in case of failiure
    pow_tbl = []
    # start scaning...
    for i in range(size[0]):    # width / x-axis
            pow_ln = []
            for j in range(size[1]):     # length / y-axis
                # get the power reading and compare to threshold if larger than exit
                reading = float(_get_signal(stages))
                pow_ln.append(reading)
                if thresh < reading:
                    return True
                # move to the next place
                cur_pos = stages[target].get_coordinates()
                new_pos = (cur_pos[0], cur_pos[1] + step, cur_pos[2])
                stages[target].set_coordinates(new_pos)

            pow_tbl.append(pow_ln)
            cur_pos = stages[target].get_coordinates()
            new_pos = (cur_pos[0] + step, cur_pos[1] - size[1]*step, cur_pos[2])
            stages[target].set_coordinates(new_pos)

    # return to the best place scanned
    opt_point, _ = raster.optimal_point(pow_tbl)
    cur_pos = stages[target].get_coordinates()
    new_pos = (cur_pos[0] + (-size[0] + opt_point[0])*step,
               cur_pos[1] + (size[1] - opt_point[1])*step,
               cur_pos[2])
    stages[target].set_coordinates(new_pos)
    return False

def smooth_cross(stages,target):
    smooth_align(stages, target, 0)
    smooth_align(stages, target, 1)

def smooth_align(stages, target, dim=0):
    '''
        Searches and alligns on the maximum on an axis
    '''
    jump_back   = 0.010
    grad_thresh = 0.1/(0.0025)
    approaching = False
    max_cycle   = 50
    data_list   = []

    for i in range(max_cycle):
        data =  _get_meas(stages,target,int(dim))
        grad =  _comp_gradient(data)

        if grad > grad_thresh:
            # loop
            continue

        if grad > 0 and grad < grad_thresh:
            # append data
            data_list += data
            approaching = True
            continue

        if grad < 0 and approaching == True:
            # append data
            data_list += data
            break

        if grad < 0 and approaching == False:
            # Jump back
            coordinates = list(stages[target].get_coor_2d())
            coordinates[int(dim)] -= jump_back
            stages[target].set_coor_2d(coordinates)
            continue

    pos=[]
    max_val = -9999
    max_pos = -9999

    print(data_list)

    for point in data_list:
        if max_val < point[1]:
            max_val = point[1]
            max_pos = point[0]

    coordinates = list(stages[target].get_coor_2d())[:]
    coordinates[int(dim)] = max_pos
    print(coordinates)
    stages[target].set_coor_2d(coordinates)

def smooth_rot(stages, target):
    '''
        Searches and alligns on the maximum of rotation offset
    '''
    jump_back   = 0.0014*20
    grad_thresh = 0.1/(0.0025)
    approaching = False
    max_cycle   = 50
    data_list   = []

    for i in range(max_cycle):
        data =  _get_meas_r(stages,target)
        grad =  _comp_gradient(data)

        if grad > grad_thresh:
            # loop
            continue

        if grad > 0 and grad < grad_thresh:
            # append data
            data_list += data
            approaching = True
            continue

        if grad < 0 and approaching == True:
            # append data
            data_list += data
            break

        if grad < 0 and approaching == False:
            # Jump back
            coordinates = stages[target].get_rot()
            coordinates -= jump_back
            stages[target].set_rot(coordinates)
            continue

    max_val = -9999
    max_pos = -9999

    print(data_list)

    for point in data_list:
        if max_val < point[1]:
            max_val = point[1]
            max_pos = point[0]

    coordinates = max_pos
    print(coordinates)
    stages[target].set_rot(coordinates)

def _get_meas(stages,target,dim):
    stepsize = 0.0014
    data = []
    nr_samples = 5

    dim = int(dim)

    for i in range(nr_samples):
        coordinates = list(stages[target].get_coor_2d())
        data.append([coordinates[dim],_get_signal(stages)])
        coordinates[dim] += stepsize
        stages[target].set_coor_2d(coordinates)

    # smooth data
    smooth_data =[]
    for i in range(nr_samples):
        if i == 0:
            smooth_data.append([data[i][0],(2*data[i][1]+data[i+1][1])/3])
        elif i== nr_samples -1:
            smooth_data.append([data[i][0],(2*data[i][1]+data[i-1][1])/3])
        else:
            smooth_data.append([data[i][0],(data[i][1]+data[i-1][1]+data[i+1][1])/3])

    return smooth_data

def _get_meas_r(stages, target):
    stepsize = 0.0005
    data = []
    nr_samples = 5

    for i in range(nr_samples):
        coordinates = stages[target].get_rot()
        data.append([coordinates,_get_signal(stages)])
        coordinates += stepsize
        stages[target].set_rot(coordinates)

    # smooth data
    smooth_data =[]
    for i in range(nr_samples):
        if i == 0:
            smooth_data.append([data[i][0],(2*data[i][1]+data[i+1][1])/3])
        elif i== nr_samples -1:
            smooth_data.append([data[i][0],(2*data[i][1]+data[i-1][1])/3])
        else:
            smooth_data.append([data[i][0],(data[i][1]+data[i-1][1]+data[i+1][1])/3])

    return smooth_data

def _comp_gradient(data):
    x=[]
    y=[]

    for point in data[1:-1]:
        x.append(point[0])
        y.append(point[1])

    a,b=numpy.polyfit(x,y,1)


    return _sign(a)

def _sign(number):
    if number >= 0:
        return 1
    else:
        return -1

def gradient_ascent(stages, target, plot=False, stepsize=0.001,beta_p=0.001,max_steps=100,min_d=1):
    '''
        Two Dimensional Gradient Ascent Algorythm to position fiber.
        Gradient computed by power measurements at position a,b,c.
        The gradient then defines the stepsize to the next position a'
        The fiber is considered coupled if:
            a) If the gradient is below a threshold 3 times in a row
    '''

    start_time = time.clock()
    # Define Constants
    beta = beta_p * stepsize
    # Initialize counters, references etc
    d0 = 1
    d1 = 1
    ref_d0 = 1
    ref_d1 = 1
    d_counter = 0
    coord_list=[]
    power_list=[]

    for ii in range(max_steps):
        # Get intial power
        coordinates_a = list(stages[target].get_coor_2d())
        coord_list.append(coordinates_a)
        power_a = _get_signal(stages)
        power_list.append(power_a)

        # Get 'side' powers
        # point b
        coordinates_b = coordinates_a[:]
        coordinates_b[0] = coordinates_a[0]+stepsize
        stages[target].set_coor_2d(coordinates_b)
        power_b = _get_signal(stages)

        #point c
        coordinates_c = coordinates_b[:]
        coordinates_c[1] = coordinates_b[1]+stepsize
        stages[target].set_coor_2d(coordinates_c)
        power_c = _get_signal(stages)

        # compute gradients
        ref_d0 = d0
        ref_d1 = d1
        d0 = -(power_a - power_b)/stepsize
        d1 =  (power_c - power_b)/stepsize

        # check break condition
        if d0 < min_d and d1 < min_d:
            d_counter += 1
        else:
            d_counter  = 0

        if d_counter > 1:
            _report('Optical Stage '+target+' aligned')
            stages[target].set_coor_2d(coordinates_a)
            if plot:
                _print_path(coord_list,power_list)
            print(time.clock() - start_time, "seconds")
            return

        # compute and set new coordinates
        coordinates_aa = coordinates_b
        coordinates_aa[0] += beta*d0
        coordinates_aa[1] += beta*d1

        stages[target].set_coor_2d(coordinates_aa)

    if plot:
        _print_path(coord_list,power_list)
    _report('Stopped without hitting the break condition')
    print(time.clock() - start_time, "seconds")

def gradient_ascent_m(stages, target, plot=False, stepsize=0.001,beta_p=0.001,p_p = 0.001, max_steps=100,min_d=1):
    '''
        Two Dimensional Gradient Ascent Algorythm to position fiber.
        Gradient computed by power measurements at position a,b,c.
        The gradient then defines the stepsize to the next position a'
        The fiber is considered coupled if:
            a) If the gradient is below a threshold 3 times in a row
    '''
    start_time = time.clock()
    # Define Constants
    beta = beta_p*stepsize
    p = p_p*stepsize

    # Initialize counters, references etc
    d0 = 1
    d1 = 1
    ref_d0 = 1
    ref_d1 = 1
    d_counter = 0
    coord_list=[]
    power_list=[]

    for ii in range(max_steps):
        # Get intial power
        coordinates_a = list(stages[target].get_coor_2d())
        coord_list.append(coordinates_a)
        power_a = _get_signal(stages)
        power_list.append(power_a)

        # Get 'side' powers
        # point b
        coordinates_b = coordinates_a[:]
        coordinates_b[0] = coordinates_a[0]+stepsize
        stages[target].set_coor_2d(coordinates_b)
        power_b = _get_signal(stages)

        #point c
        coordinates_c = coordinates_b[:]
        coordinates_c[1] = coordinates_b[1]+stepsize
        stages[target].set_coor_2d(coordinates_c)
        power_c = _get_signal(stages)

        # compute gradients
        ref_d0 = d0
        ref_d1 = d1
        d0 = -(power_a - power_b)/stepsize
        d1 =  (power_c - power_b)/stepsize

        # check break condition
        if d0 < min_d and d1 < min_d:
            d_counter += 1
        else:
            d_counter  = 0

        if d_counter > 1:
            _report('Optical Stage '+target+' aligned')
            stages[target].set_coor_2d(coordinates_a)
            if plot:
                _print_path(coord_list,power_list)
            print(time.clock() - start_time, "seconds")
            return

        # compute and set new coordinates
        coordinates_aa = coordinates_b
        coordinates_aa[0] += (beta*d0 + ref_d0*p)
        coordinates_aa[1] += (beta*d1 + ref_d1*p)

        stages[target].set_coor_2d(coordinates_aa)

    if plot:
        _print_path(coord_list,power_list)
    _report('Stopped without hitting the break condition')
    print(time.clock() - start_time, "seconds")

def gradient_ascent_miniBatch(stages, target, plot=False):
    '''
        Two Dimensional Gradient Ascent Algorythm to position fiber.
        Gradient computed by power measurements at position a,b,c.
        The gradient then defines the stepsize to the next position a'
        The fiber is considered coupled if:
            a) If the gradient is below a threshold 3 times in a row
    '''
    start_time = time.clock()
    # Define Constants
    stepsize  = 0.001
    beta      = 0.001*stepsize
    max_steps = 100
    min_d     = 1

    # Initialize counters, references etc
    d_xy = [1,1,1,1,1,1,1,1]
    d = d_xy[:]
    d_counter = 0
    coord_list=[]
    power_list=[]

    for ii in range(max_steps):
        # Get intial power
        coordinates_a = list(stages[target].get_coor_2d())
        coord_list.append(coordinates_a)
        power_a = _get_signal(stages)
        power_list.append(power_a)

        # Get 'side' powers
        # point b
        coordinates_b = coordinates_a[:]
        coordinates_b[0] = coordinates_a[0]-stepsize
        stages[target].set_coor_2d(coordinates_b)
        power_b = _get_signal(stages)

        #point c
        coordinates_c = coordinates_b[:]
        coordinates_c[1] = coordinates_b[1]-stepsize
        stages[target].set_coor_2d(coordinates_c)
        power_c = _get_signal(stages)

        # point d
        coordinates_d = coordinates_c[:]
        coordinates_d[0] = coordinates_c[0]+stepsize
        stages[target].set_coor_2d(coordinates_d)
        power_d = _get_signal(stages)

        #point e
        coordinates_e = coordinates_d[:]
        coordinates_e[0] = coordinates_d[0]+stepsize
        stages[target].set_coor_2d(coordinates_e)
        power_e = _get_signal(stages)

        # point f
        coordinates_f = coordinates_e[:]
        coordinates_f[1] = coordinates_e[1]+stepsize
        stages[target].set_coor_2d(coordinates_f)
        power_f = _get_signal(stages)

        #point g
        coordinates_g = coordinates_f[:]
        coordinates_g[1] = coordinates_f[1]+stepsize
        stages[target].set_coor_2d(coordinates_g)
        power_g = _get_signal(stages)

        # point h
        coordinates_h = coordinates_g[:]
        coordinates_h[0] = coordinates_g[0]-2*stepsize
        stages[target].set_coor_2d(coordinates_h)
        power_h = _get_signal(stages)

        #point i
        coordinates_i = coordinates_h[:]
        coordinates_i[0] = coordinates_h[0]+stepsize
        stages[target].set_coor_2d(coordinates_i)
        power_i = _get_signal(stages)


        # compute gradients
        f
        d0 = -(power_a - power_b)/stepsize
        d1 =  (power_c - power_b)/stepsize

        # check break condition
        if d0 < min_d and d1 < min_d:
            d_counter += 1
        else:
            d_counter  = 0

        if d_counter > 1:
            _report('Optical Stage '+target+' aligned')
            stages[target].set_coor_2d(coordinates_a)
            if plot:
                _print_path(coord_list,power_list)
            print(time.clock() - start_time, "seconds")
            return

        # compute and set new coordinates
        coordinates_aa = coordinates_b
        coordinates_aa[0] += beta*d0
        coordinates_aa[1] += beta*d1

        stages[target].set_coor_2d(coordinates_aa)

    if plot:
        _print_path(coord_list,power_list)
    _report('Stopped without hitting the break condition')
    print(time.clock() - start_time, "seconds")


def _print_path(coord_list, powers):

    fig = plt.figure()
    ax = Axes3D(fig)

    x = zip(*coord_list)[0]
    y = zip(*coord_list)[1]
    z = powers

    ax.plot(xs=x, ys=y, zs=z )

    plt.show(block=False)


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
