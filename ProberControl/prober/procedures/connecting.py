#from Classes.xyzstage import XYZ_Stage
import fine_allign
import Measure
import numpy as np
import math
from ..classes.Global_MeasureHandler import Global_MeasureHandler

# to be used for vitual leveling purposes

__vl_point = []
__vl_flag_disable = False
__vl_id = None

# to be used for calib_chip_rot purposes

__ccr_point = []
__ccr_id = None


# ---------------------------------------

# helper functions to add/subtract tuples
def t_add(tuple1, tuple2):
    return tuple(np.add(tuple1, tuple2))

def reset_chip_rot():
    print __ccr_point
    del __ccr_point[:]
    __ccr_id = None

def calib_chip(Stages, id):
    global __vl_id
    global __vl_point
    global __vl_flag_disable
    #------------------------
    global __ccr_id
    global __ccr_point

    if __vl_id is not None and id != __vl_id:
        print 'Calibrate Chip: Changed Stage\n\texpected: {}\n\tgot: {}'.format(__vl_id, id)
        return
    elif __ccr_id is not None and id != __ccr_id:
        print 'Calibrate Chip: Changed Stage\n\texpected: {}\n\tgot: {}'.format(__vl_id, id)
        return
    else:
        __vl_id = id
        #------------
        __ccr_id = id

        if len(__vl_point) == 0:
            __vl_flag_disable = True
            print 'Calibrate Chip: getting base point. Arrow up/down next.'
            __vl_point.append(Stages[id].get_coordinates())
            #----------------------------------------------
            print 'Move along edge to next corner on chip. Move along x axis of stage correct using y axis.'
            __ccr_point.append(Stages[id].get_coordinates())
            Stages[id].set_coordinates([__ccr_point[0][0],__ccr_point[0][1],__ccr_point[0][2]-0.2])

        elif len(__vl_point) == 1:
            print 'virtual_level: getting UP point.'
            __vl_point.append(Stages[id].get_coordinates())
            #----------------------------------------------
            __ccr_point.append(Stages[id].get_coordinates())

            print 'Calibrate Chip Rotation: Computing rotation...'
            p0, p1 =  __ccr_point
            ang_x = math.degrees(math.atan( (p1[1]-p0[1])/(p1[0]-p0[0]) ))

            print 'Ang_x'+str(ang_x)

            if 'CS' in Stages:
                print 'Calibrate Chip Rotation: Performing rotation...'
                Stages['CS'].rot.delta_angle(ang_x)


            del __ccr_point[:]
            __ccr_id = None
            #---------------
            Stages[id].set_coordinates([__vl_point[1][0],__vl_point[1][1],__vl_point[1][2]-0.2])
            print 'virtual_level: Arrow right/left next.'

        elif len(__vl_point) == 2:
            print 'virtual_level: getting RIGHT point.'
            __vl_point.append(Stages[id].get_coordinates())

            print 'virtual_level: performing leveling...'
            p0, p1, p2 =  __vl_point
            ang_x = math.degrees(math.atan( (p1[2]-p0[2])/(p1[0]-p0[0]) ))
            ang_y = math.degrees(math.atan( (p2[2]-p1[2])/(p2[1]-p1[1]) ))

            print 'Ang_x'+str(ang_x)
            print 'Ang_y'+str(ang_y)


            # insert info to selcted stage
            Stages[id].set_level(ang_x, ang_y)
            # insert on the rest of the stages
            c_ang = coord_s2c(Stages,(ang_x, ang_y), id)
            for k,v in Stages.items():
                if k[0] in 'EO' and k != id :
                    Stages[k].set_level(*coord_c2s(Stages,c_ang, k))

            del __vl_point[:]
            __vl_id = None
            __vl_flag_disable = False

            print 'Calibrate Chip: Finished.'

def calib_chip_rot(Stages, id):
    global __ccr_id
    global __ccr_point

    if __ccr_id is not None and id != __ccr_id:
        print 'Calibrate Chip Rotation: Changed Stage\n\texpected: {}\n\tgot: {}'.format(__ccr_id, id)
        return
    else:
        __ccr_id = id
        if len(__ccr_point) == 0:
            print 'Calibrate Chip Rotation: Move along edge to next corner on chip. Move along x axis of stage correct using y axis.'
            __ccr_point.append(Stages[id].get_coordinates())
            Stages[id].set_coordinates([__ccr_point[0][0],__ccr_point[0][1],__ccr_point[0][2]-0.2])

        elif len(__ccr_point) == 1:
            __ccr_point.append(Stages[id].get_coordinates())

            print 'Calibrate Chip Rotation: Computing rotation...'
            p0, p1 =  __ccr_point
            ang_x = math.degrees(math.atan( (p1[1]-p0[1])/(p1[0]-p0[0]) ))

            print 'Ang_x'+str(ang_x)

            if 'CS' in Stages:
                print 'Calibrate Chip Rotation: Performing rotation...'
                Stages['CS'].rot.delta_angle(ang_x)


            del __ccr_point[:]
            __ccr_id = None


def virtual_level(Stages, id):
    global __vl_id
    global __vl_point
    global __vl_flag_disable
    if __vl_id is not None and id != __vl_id:
        print 'virtual level: Changed Stage\n\texpected: {}\n\tgot: {}'.format(__vl_id, id)
        return
    else:
        __vl_id = id
        if len(__vl_point) == 0:
            __vl_flag_disable = True
            print 'virtual_level: getting base point. Arrow up/down next.'
            __vl_point.append(Stages[id].get_coordinates())
        elif len(__vl_point) == 1:
            print 'virtual_level: getting UP point. Arrow right/left next.'
            __vl_point.append(Stages[id].get_coordinates())
        elif len(__vl_point) == 2:
            print 'virtual_level: getting RIGHT point.'
            __vl_point.append(Stages[id].get_coordinates())

            print 'virtual_level: performing leveling...'
            p0, p1, p2 =  __vl_point
            ang_x = math.degrees(math.atan( (p1[2]-p0[2])/(p1[0]-p0[0]) ))
            ang_y = math.degrees(math.atan( (p2[2]-p1[2])/(p2[1]-p1[1]) ))

            print 'Ang_x'+str(ang_x)
            print 'Ang_y'+str(ang_y)


            # insert info to selcted stage
            Stages[id].set_level(ang_x, ang_y)
            # insert on the rest of the stages
            c_ang = coord_s2c(Stages,(ang_x, ang_y), id)
            for k,v in Stages.items():
                if k[0] in 'EO' and k != id :
                    Stages[k].set_level(*coord_c2s(Stages,c_ang, k))

            del __vl_point[:]
            __vl_id = None
            __vl_flag_disable = False

            print 'virtual_level: Finished.'

def save_coarse_coordinates(Stages, path='PreAlign.conf'):
    global __vl_flag_disable
    print 'flag: ', __vl_flag_disable
    if __vl_flag_disable :
        print 'virtual_level:ERROR: cannot perform operation while leveling in progress.'
        return

    coarse_file = open(path,"w")

    for k,v in Stages.items():
        if k[0] == 'E' or k[0]== 'O':
            save_coords = t_add(Stages[k].get_real_coordinates(),[0,0,-0.5])
            coarse_file.write(k+' '+str(save_coords[0])+' '+str(save_coords[1])+' '+str(save_coords[2])+' '+str(Stages[k].ang_x)+' '+str(Stages[k].ang_y)+'\n')

    coarse_file.close()

def set_coarse_coordinates(Stages, path='PreAlign.conf'):
    global __vl_flag_disable
    if __vl_flag_disable :
        print 'virtual_level:ERROR: cannot perform operation while leveling in progress.'
        return

    #Check wheather stages are homed:
    homed = True
    for k,v in Stages.items():
        if k[0] == 'E' or k[0] == 'O':
            if Stages[k].zeros != (0,0,0) or  Stages[k].get_coordinates() != (0,0,0):
                print "Stages not homed or system already recalibatrate, cannot apply set_coarse_coordinates"
                return 0


    coordinates={}
    angles = {}

    CoordsFile =  open(path, 'r')
    for line in CoordsFile:
        k = line.split()[0]
        v = map(float,line.split()[1:6])
        coordinates[k]= v[0:3]
        angles[k]=v[3:5]
        print coordinates[k]
        print angles[k]


    outward_dim=0
    sideward_dim=1

    # Step 1: Go through coordinates and split sideward from inward moves
    # coordinates are already in stage coordinates
    inward_coordinates={}
    sideward_coordinates={}


    for k,v in coordinates.items():
        if k not in ['Structure','SignalSource']:
                side_coord = list(Stages[k].get_coordinates())
                side_coord[sideward_dim] = v[sideward_dim]
                sideward_coordinates[k] = side_coord

                inward_coordinates[k] = v

    print sideward_coordinates
    print inward_coordinates

    # Step 2: Apply sideward moves
    for k,v in sideward_coordinates.items():
        if k not in ['Structure','SignalSource']:
            Stages[k].set_coordinates(v)

    # Step 3: Apply inward moves
    for k,v in inward_coordinates.items():
        if k not in ['Structure','SignalSource']:
            Stages[k].set_coordinates(v)

    # Step 4: Apply virtual levelling angles
    for k,v in angles.items():
        Stages[k].ang_x = v[0]
        Stages[k].ang_y = v[1]

def connect_structure(Stages,Maitre, path='Coordinates.conf', struct_name='0'):
    global __vl_flag_disable
    if __vl_flag_disable :
        print 'virtual_level:ERROR: cannot perform operation while leveling in progress.'
        return

    coords = read_coords_file( path )[str(struct_name)]
    print coords

    gmh = Global_MeasureHandler()

    if 'SignalSource' in coords:
        # fine_allign.set_signal_source(coords['SignalSource'])
        measurement_instr = gmh.get_instrument_by_name(coords['SignalSource'])
        if measurement_instr is None:
            raise ValueError('connecting: Bad SignalSource specified for structure <{}>: {}'.format(struct_name, coords['SignalSource']))
        fine_allign.set_meas_fun(measurement_instr.get_power)
    else:
        # try to fing a PowerMeter
        measurement_instr = gmh.get_instrument('PowerMeter')
        if measurement_instr is None:
            raise ValueError('connecting: No compatible instrument to run fine-align')
        fine_allign.set_meas_fun(measurement_instr.get_power)

    if connect_coordinates( coords, Stages, Maitre):
        return True
    else:
        return False

def calibrate_on_structure(Stages, path='Coordinates.conf', struct_name='0'):
    global __vl_flag_disable
    if __vl_flag_disable :
        print 'virtual_level:ERROR: cannot perform operation while leveling in progress.'
        return

    coords = read_coords_file( path )[str(struct_name)]
    for k,v in coords.items():
        if k not in ['Structure','SignalSource']:
            Stages[k].set_cur_as_2d(coord_c2s(Stages,v,k))
            if k[0] == 'E':
                Stages[k].setLowZ()

def check_coordinate_set(Stages, coordinates):
        '''
        To prevent collision dont allow a coordinate more West than the W stage, more East than the E Stage etc also add stage
        depending buffer zones, the two dimensions of the buffer zones (dx,dy) are to be understood in the coordinate system
        of the stages
        '''
        limits={}
        for k,v in coordinates.items():
            print limits
            print k
            if k[1]=='E':
                limits[k[1]] = v[1]+Stages[k].space[0]/2
            if k[1]=='W':
                limits[k[1]] = v[1]-Stages[k].space[0]/2
            if k[1]=='S':
                limits[k[1]] = v[0]+Stages[k].space[0]/2
            if k[1]=='N':
                limits[k[1]] = v[0]-Stages[k].space[0]/2
        print limits
        for k,v in coordinates.items():
            if k[1]=='E':
                if 'N' in limits:
                  if v[0]+Stages[k].space[1]/2>limits['N']:
                    return False
                if 'S' in limits:
                  if v[0]-Stages[k].space[1]/2<limits['S']:
                    return False
                if 'W' in limits:
                  if v[1]+Stages[k].space[0]/2>limits['W']:
                    return False
            if k[1]=='W':
                if 'N' in limits:
                  if v[0]+Stages[k].space[1]/2>limits['N']:
                    return False
                if 'S' in limits:
                  if v[0]-Stages[k].space[1]/2<limits['S']:
                    return False
                if 'E' in limits:
                  if v[1]-Stages[k].space[0]/2<limits['E']:
                    return False
            if k[1]=='N':
                if 'S' in limits:
                  if v[0]-Stages[k].space[0]/2<limits['S']:
                    return False
                if 'W' in limits:
                  if v[1]+Stages[k].space[1]/2>limits['W']:
                    return False
                if 'E' in limits:
                  if v[1]-Stages[k].space[1]/2<limits['E']:
                    return False
            if k[1]=='S':
                if 'N' in limits:
                  if v[0]+Stages[k].space[0]/2>limits['N']:
                    return False
                if 'W' in limits:
                  if v[1]+Stages[k].space[1]/2>limits['W']:
                    return False
                if 'E' in limits:
                  if v[1]-Stages[k].space[1]/2<limits['E']:
                    return False

        return True

def connect_coordinates( coordinates, Stages, Maitre):
    '''
        Zero    Step: Check whether all connected probes are used / create safe positions of unsused stages
        0.25    Step: Check whether Coordinates are not leading to collisions
        0.5     Step: Go through coordinates and check wether positions can be reached by probes if not quite
    First   Step: Split outward sideward inward moves from each other to avoid collision of probes.
    Second  Step: Unconnect E-Probes
    Third   Step: Apply outward moves
    Fourth  Step: Apply side moves
        Fifth   Step: Apply inward moves
    Sixth   Step: Connect E-Proves
    Seventh Step: Get Spectrum and adjust laser to highest throughput for optimal coupling
    Eight   Step: Perform FineAllign on O-Stages
    Nineth  Step: Reset system coordinates to 'planned' coordinates as on the fly recalibration
    '''

    outward_dim=0
    sideward_dim=1

    used=[]
    unused=[]

    power_threshold = -60

    # Step 0: Check whether all connected probes are used
    for k,v in Stages.items():
        if k[0] == 'E' or k[0] == 'O':
            if k in coordinates:
                used.append(k)
            else:
                unused.append(k)

    # bring unsused stages to x-home positions if they were calibrated on chip before
    for k in unused:
        if Stages[k].get_calibrated():
            coordinates[k] = coord_s2c(Stages,(round(Stages[k].get_coor_2d()[0]-Stages[k].get_real_coordinates()[0] + 0.001, 3),Stages[k].get_coor_2d()[1]),k)

    # Step 0.25: Check whether coordinates are not leading to collisions
    #    if not check_coordinate_set(Stages, coordinates):
    #    print 'Coordinates might lead to collision'
    #        return False

    # Step 0.5: Go through coordinates and check wether positions can be reached by probes if not return False
    for k,v in coordinates.items():
        if k not in ['Structure','SignalSource']:
            if not Stages[k].check_coordinates_2d(coord_c2s(Stages,v,k)):
                print 'Coordinates out of range for Stage '+k
                return False


    # Step 1: Go through coordinates and split outward / sideward / inward moves
    # coordinates are already in stage coordinates
    outward_coordinates={}
    sideward_coordinates={}

    for k,v in coordinates.items():
        if k not in ['Structure','SignalSource']:
            if Stages[k].get_coor_2d()[outward_dim]-coord_c2s(Stages,v,k)[outward_dim] > 0:
                # print 'outward detected...'
                out_coord = list(Stages[k].get_coor_2d())
                out_coord[outward_dim] = coord_c2s(Stages,v,k)[outward_dim]
                outward_coordinates[k] = out_coord

                side_coord = out_coord[:]    # slice idx to copy list
                side_coord[sideward_dim] = coord_c2s(Stages,v,k)[sideward_dim]
                sideward_coordinates[k] = side_coord

            else:
                side_coord = list(Stages[k].get_coor_2d())
                side_coord[sideward_dim] = coord_c2s(Stages,v,k)[sideward_dim]
                sideward_coordinates[k] = side_coord


    # Step 2: Unconnect E-Probes
    for k,v in Stages.items():
        if k[0] == 'E':
            Stages[k].disconnect()

    # Step 3: Apply outward moves
    for k,v in outward_coordinates.items():
        if k not in ['Structure','SignalSource']:
            # print 'applying outward\n\t{}\n\t{}\n'.format(Stages[k].get_coordinates(), v)
            Stages[k].set_coor_2d(v, True)

    # Step 4: Apply sideward moves
    for k,v in sideward_coordinates.items():
        if k not in ['Structure','SignalSource']:
            Stages[k].set_coor_2d(v, True)

    # Step 5: Apply inward moves
    for k,v in coordinates.items():
        if k not in ['Structure','SignalSource']:
            print 'Attemp to move'+str(k)+'to:'
            print coord_c2s(Stages,v,k)
            Stages[k].set_coor_2d(coord_c2s(Stages,v,k), True)


    # Step 6: Connect E-Probes
    for k in used:
        if k[0] == 'E':
            Stages[k].connect()

    # Step 7: Find wavelength with high enough / highest throughput
    #if Stages['MPowerMeter'].get_power() < power_threshold:
    #    data = Measure._thresh_wavelength(Stages,Maitre,Stages['MLaser'].get_min_wavelength(),Stages['MLaser'].get_max_wavelength(),1)
    #    trans = zip(*data)

    #    max_ind = trans[1].index(max(trans[1]))
    #    max_wavelength = data[max_ind][0]

    #    print 'Found threshold power wavelength'
    #    print max_wavelength

    #    Stages['MLaser'].setwavelength(max_wavelength)

    # Step 8: FineAllign O-Probes
    # try to allign all
    failed = []
    retry = False
    for k,v in Stages.items():
        if 'O' in k:
            if fine_allign.fast_align(Stages,k,power_threshold) == False:
                failed.append(k)
            else:
                retry = True

    # one at least succeeded so re-allign the rest
    if retry:
        for k in failed:
            fine_allign.fast_align(Stages, k, power_threshold)
    else:
        print 'no structures could be connected - Aborting connect_structure...'
        return False

    # Step 9: Reset coordinates
    for k,v in Stages.items():
        if 'O' in k:
            Stages[k].set_cur_as_2d(coord_c2s(Stages,coordinates[k],k))

    return True

def read_coords_file( path ):
    global __vl_flag_disable
    if __vl_flag_disable :
            print 'virtual_level:ERROR: cannot perform operation while leveling in progress.'
            return

    CoordsFile = open(path, 'r')

    if CoordsFile is None:
        print 'Problem reading Coordinates file.'
        return 0

    Coords = {}
    CoordsList = []

    for line in CoordsFile:
        print line

        if line[0]=='#':
            ParaIndex = line[1:3]

        if line[0:3]=='#Si':
            ParaIndex = 'SignalSource'

        if line[0:2]=='##':
            ParaIndex = 'StructName'
            if Coords != {}:
                CoordsList.append(Coords)
                Coords = {}

        if line[0]!='#':
            if ParaIndex == 'StructName':
                Coords[ParaIndex]=line.split()[0]
            elif ParaIndex == 'SignalSource':
                Coords[ParaIndex]=line.split()[0]
            else:
                Coords[ParaIndex]=map(float,line.split())

    CoordsDict = {}
    for elem in CoordsList:
            name = str(elem['StructName'])
            del elem['StructName']
            CoordsDict[name]=elem

    return CoordsDict

def coord_c2s(Stages,coords,StageKey):

    print StageKey
    print coords

    if StageKey[1] == 'S':
        angle = math.radians(0   + float(Stages[StageKey].get_off_angle()))
    if StageKey[1] == 'E':
        angle = math.radians(90  + float(Stages[StageKey].get_off_angle()))
    if StageKey[1] == 'N':
        angle = math.radians(180 + float(Stages[StageKey].get_off_angle()))
    if StageKey[1] == 'W':
        angle = math.radians(270 + float(Stages[StageKey].get_off_angle()))

    print math.degrees(angle)
    print angle
    print [math.cos(angle)*coords[0]+math.sin(angle)*coords[1],math.sin(-angle)*coords[0]+math.cos(angle)*coords[1]]
    return [math.cos(angle)*coords[0]+math.sin(angle)*coords[1],math.sin(-angle)*coords[0]+math.cos(angle)*coords[1]]


def coord_s2c(Stages,coords,StageKey):
    if StageKey[1] == 'S':
        angle = math.radians(0   + float(Stages[StageKey].get_off_angle()))
    if StageKey[1] == 'E':
        angle = math.radians(90  + float(Stages[StageKey].get_off_angle()))
    if StageKey[1] == 'N':
        angle = math.radians(180 + float(Stages[StageKey].get_off_angle()))
    if StageKey[1] == 'W':
        angle = math.radians(270 + float(Stages[StageKey].get_off_angle()))


    return [math.cos(-angle)*coords[0]+math.sin(-angle)*coords[1],math.sin(angle)*coords[0]+math.cos(-angle)*coords[1]]

if __name__ == '__main__':
    coords = read_coords_file('Test-Coordinates.conf')
    print coords



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
