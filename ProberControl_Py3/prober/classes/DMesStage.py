#    Distance measurement Stage class
#    groups together:
#        - dist. sensor
#        - large newport controller
#        - lin. transl. stage to move the sensor

import threading

class DMesStage(object):

    def __init__(self, mtr_list):
        '''
        :param mtr_list: a list containing the following objects
            [
            distance_sensor,
            step_motor<X>,
            stepper<Y>,
            vetrical_stage
            ]
        '''

        self.caliAngleX = 0.4713
        self.caliAngleY = -0.175

        # def s_init():
        #     self.sensor = DSensor(ser_list[0])
        # def stp_x_init():
        #     self.stepper_x = StepMotor_KST_ZST(ser_list[1])
        # def stp_y_init():
        #     self.stepper_y = StepMotor_KST_ZST(ser_list[2])
        # def np_init():
        #     self.vertical = NewportPM500(ser_list[3])
        #
        # t_s = threading.Thread(target=s_init)
        # t_stp_x = threading.Thread(target=stp_x_init)
        # t_stp_y = threading.Thread(target=stp_y_init)
        # t_np = threading.Thread(target=np_init)
        #
        # t_s.start(), t_stp_x.start(),t_stp_y.start(), t_np.start()
        # t_s.join(), t_stp_x.join(),t_stp_y.join(), t_np.join()
        self.sensor, self.stepper_x, self.stepper_y, self.vertical = mtr_list

    def whoAmI(self):
        ''':returns: type of instrument'''
        return 'Distance'


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
