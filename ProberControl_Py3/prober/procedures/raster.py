#from Classes.xyzstage import XYZ_Stage
#import Classes.multimeter
import numpy as np

import sys
if sys.platform.startswith('win'):    # because of problems with OpenCV on linux
    import cv2

# default unset
__selected_function = None
STD_TOOL = "MPowerMeter"

def _report(msg):
    prt_msg = 'raster: ' + msg
    print(prt_msg)

def _set_meas_fun(fn):
    global __selected_function
    __selected_function = fn

def set_signal_source(stages, source_string=''):

    if source_string in list(stages.keys()):
        feedbackfunc = getattr(stages[source_string], "get_feedback", None)
        if callable(feedbackfunc):
            _set_meas_fun(stages[source_string].get_feedback)
            return 1
        else:
            _report(str(source_string)+" does not supply get_feedback function")
            return -1;

    else:
        _report(str(source_string)+" is not a member of the Stages Dictionary")
        return -1;


def _get_signal(stages):
    global __selected_function

    if __selected_function == None:
        if not(set_signal_source(stages, source_string=STD_TOOL) or set_signal_source(stages, source_string=STD_TOOL+"1")):
            return "Error"

    return __selected_function()

def _generate_map(xyz, size, step):
    '''
     generates a map 3d map representing how much light is coupled
     over a specified region (size x step)

     xyz (XYZ_Stage)
     size (2-tuple): the dimension of the region scanned
     step (int): the step size

     returns a 2 dimensional list following the convention:
        returned_map[3][10] = the "power"(actually voltage for now) at point (3,10)
    '''

    map = [None] * size[0]
    # place the current point at the center
    cur_pos = xyz.get_coordinates()
    initial_pos = xyz.get_coordinates()
    print(size)
    new_pos = (cur_pos[0] - size[0]/70.0*50.0*step, cur_pos[1] - float(size[1])/2.0*step, cur_pos[2])
    xyz.set_coordinates(new_pos)
    # start scaning...
    for i in range(size[0]):    # width / x-axis
        line = []
        for j in range(size[1]):     # length / y-axis
            # get the voltage reading
            line.append(float(_get_signal(stages)))
            # move to the next place
            cur_pos = xyz.get_coordinates()
            new_pos = (cur_pos[0], cur_pos[1] + step, cur_pos[2])
            xyz.set_coordinates(new_pos)

        map[i] = line

        cur_pos = xyz.get_coordinates()
        new_pos = (cur_pos[0] + step, cur_pos[1] - size[1]*step, cur_pos[2])
        xyz.set_coordinates(new_pos)

    # return to initial scanning point
    xyz.set_coordinates(initial_pos)

    return map

def generate_map_d(stages, target, size, step):
    return _generate_map(stages[target], size, step)

def map_image(c_map, im_size, full_path=None, show=False):
    '''
     Takes a map returned from genearte_map() and visualizes it
     c_map (2d-list): map from generate_map()
     im_size(2-tuple): the dimensions of the produced image
    '''

    # calculations - normalization
    c_map = np.array(c_map, np.float32)
    maxi, mini = c_map.max(), c_map.min()
    c_map -= mini
    c_map /= maxi - mini
    fx_c = im_size[0]/c_map.shape[0]
    fy_c = im_size[1]/c_map.shape[1]

    print('Max. Voltage: {} | Min. Voltage: {}'.format(maxi, mini))

    # non-blurry scaling
    c_map = cv2.resize(c_map, None, fx=fx_c, fy=fy_c, interpolation=cv2.INTER_NEAREST)
    bgr_grey_map = cv2.cvtColor(c_map, cv2.COLOR_GRAY2BGR)
    # float32 -> unit8 image (np.array())
    grey_map_u8 = cv2.convertScaleAbs(bgr_grey_map, alpha=255.0)
    # jet-coloring
    col_map_u8 = cv2.applyColorMap(grey_map_u8, cv2.COLORMAP_JET)

    if full_path is not None:
        cv2.imwrite(full_path, col_map_u8)

    if show:
        cv2.imshow('map', col_map_u8)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

def make_map(stages, fiber, size_x, size_y, step, filename):
    map = _generate_map(stages[fiber], (int(size_x), int(size_y)), float(step))
    file = open(filename + '_data.txt', 'w')
    for line in map :
        file.write('{}\n'.format(line))
        file.flush()
    file.close()
    map_image(map, (300, 300), filename)
    print('make_map done.')

def optimal_point(c_map):
    '''
     find the point of highest voltage in map scanned by genearte_map()

     c_map (2d-list): map from generate_map()

     returns list containing:
        2-tuple (x,y) containing the coordinates of the optimal point
        the voltage on the optimal point
    '''

    c_map = np.array(c_map, np.float32)
    return [np.unravel_index(c_map.argmax(), c_map.shape), c_map.max()]

def _cross_scan(xyz, size, step):
    '''
     Performs a separate scan on each axis of length size*step.
     Should be used after the fiber has been somewhat alligned

     xyz (XYZ_Stage)
     size (int): the number of data point to take
     step (int): the step size

     retruns [y_axis_data, x_axis_data]
    '''

    # Y-Axis
    y_axis = []
    # go to far end to begin scanning
    cur_pos = xyz.get_coordinates()
    new_pos = (cur_pos[0], cur_pos[1] + size*step, cur_pos[2])
    xyz.set_coordinates(new_pos)
    # start scanning
    for i in range(size):
        y_axis.append(float(_get_signal(stages)))
        xyz.step('R')
    # go back to initial pos
    cur_pos = xyz.get_coordinates()
    new_pos = (cur_pos[0], cur_pos[1] + size*step, cur_pos[2])
    xyz.set_coordinates(new_pos)

    # X-Axis
    x_axis = []
    # go to far end to begin scanning
    cur_pos = xyz.get_coordinates()
    new_pos = (cur_pos[0] + size*step, cur_pos[1], cur_pos[2])
    xyz.set_coordinates(new_pos)
    # start scanning
    for i in range(size):
        y_axis.append(float(_get_signal(stages)))
        xyz.step('B')
    # go back to initial pos
    cur_pos = xyz.get_coordinates()
    new_pos = (cur_pos[0] + size*step, cur_pos[1], cur_pos[2])
    xyz.set_coordinates(new_pos)

    return [y_axis, x_axis]

def cross_scan_d(stages, target, size, step):
    return _cross_scan(stages[target], size, step)




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
