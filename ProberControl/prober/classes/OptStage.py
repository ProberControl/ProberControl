from xyzstage import XYZ_Stage

class OptStage(XYZ_Stage):
    '''
    This class models an optical probe stage.
    '''
    def __init__(self, mtr_list,space=None,off_angle=None):
        self.name = ''

        if space == None:
            self.space = (0.127,0.127)
        else:
            self.space = space

        if off_angle == None:
            self.off_angle = 0
        else:
            self.off_angle = off_angle

        XYZ_Stage.__init__(self,mtr_list,self.off_angle)

    def set_whoAmI(self, name):
        self.name = name

    def whoAmI(self):
        return self.name

    def __str__(self):
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
