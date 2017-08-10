# Electronic Probe Stage Class
# The E Stage is just a wrapper of the XYZ Stage for uniformity with the fibre stages

from xyzstage import XYZ_Stage
import math

class E_Stage(XYZ_Stage):

    def __init__(self, ser_list,space=None,off_angle=None):
        '''
        Constructor

        ser_list (list): a list with serial objects corresponding to
        the x, y and z motors respectively
        '''        
        self.name = ''
        if space == None:
            self.space = (0.060,0.300)
        else:
            self.space = space

        if off_angle == None:
            self.off_angle = 0
        else:
            self.off_angle = off_angle

        XYZ_Stage.__init__(self,ser_list,self.off_angle)

        self.contactDist = self.z
        self.highZ = (self.x,self.y,self.z)
        self.lowZ = (self.x,self.y,self.z)

    def set_whoAmI(self, name):
        self.name = name

    def whoAmI(self):
        return self.name

    def whatCanI(self):
        return self.name
        
    def setHighZ(self):
        '''
        Set the height at which the probe will be from the chip while disconnected
        '''
        self.highZ = [self.x,self.y,self.z]

    def setLowZ(self, dis_height=0.1):
        '''
        Set the height at which the probe is touching the chip
        '''
        self.lowZ =  [self.x,self.y,self.z]
        self.highZ = [self.x,self.y,self.z - dis_height]

    def connect(self):
        '''
        Moves z position of probe to the Low Z value
        '''
        z_extra = 0
        if self.leveled():
            x_d = (self.x-self.lowZ[0])
            y_d = (self.y-self.lowZ[1])
        z_extra += x_d * math.tan(math.radians(self.ang_x)) + y_d * math.tan(math.radians(self.ang_y))


        if self.z is not self.highZ:
            self.set_coordinates([self.x,self.y,self.highZ[2]+z_extra])
        self.set_coordinates([self.x,self.y,self.lowZ[2]+z_extra])

    def disconnect(self):
        '''
        Moves z position of probe to the High Z value.
        '''
        z_extra = 0
        if self.leveled():
            x_d = (self.x-self.highZ[0])
            y_d = (self.y-self.highZ[1])
        z_extra += x_d * math.tan(math.radians(self.ang_x)) + y_d * math.tan(math.radians(self.ang_y))

        self.set_coordinates([self.x,self.y,self.highZ[2]+z_extra])

    def jumpDownToNext(self,pitch):
        '''
        Experimental
        pitch: spacing of pads in mm
        '''
        self.disconnect()
        self.set_coor_2d([self.x,self.y-pitch])
        self.connect()
 
    def __str__(self):
        return self.name