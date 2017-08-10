#    Distance measurement Stage class
#    groups together:
#        - dist. sensor
#        - large newport controller
#        - lin. transl. stage to move the sensor

import threading
from dist_sensor import DSensor
from stp_mtr import StepMotor
from newport_controller import NewportPM500

class DMesStage(object):
    
    def __init__(self, ser_list):
        
        self.caliAngleX = 0.4713
        self.caliAngleY = -0.175
        
        def s_init():
            self.sensor = DSensor(ser_list[0])
        def stp_x_init():
            self.stepper_x = StepMotor(ser_list[1])
        def stp_y_init():
            self.stepper_y = StepMotor(ser_list[2])
        def np_init():
            self.vertical = NewportPM500(ser_list[3])
            
        t_s = threading.Thread(target=s_init)
        t_stp_x = threading.Thread(target=stp_x_init)
        t_stp_y = threading.Thread(target=stp_y_init)
        t_np = threading.Thread(target=np_init)
        
        t_s.start(), t_stp_x.start(),t_stp_y.start(), t_np.start()
        t_s.join(), t_stp_x.join(),t_stp_y.join(), t_np.join()
    
    def whoAmI(self):
        ''':returns: type of instrument'''
        return 'Distance'

    def whatCanI(self):
        ''':returns: device attributes'''
        return ''