from xyzstage import XYZ_Stage

class OptStage(XYZ_Stage):
    '''
    This class models an optical probe stage.
    '''
    def __init__(self, ser_list,space=None,off_angle=None):
        self.name = ''
        
        if space == None:
            self.space = (0.127,0.127)
        else:
            self.space = space

        if off_angle == None:
            self.off_angle = 0
        else:
            self.off_angle = off_angle

        XYZ_Stage.__init__(self,ser_list,self.off_angle)

    def set_whoAmI(self, name):
        self.name = name

    def whoAmI(self):
        return self.name

    def whatCanI(self):
        return self.name

    def __str__(self):
        return self.name