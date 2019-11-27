# Step Motor Class
#    - wraps around Motor


from .Motor_MST_DRV import Motor_MST_DRV as Motor, hexString, int2hexStr, send_short_dst_src, send_long_dst_src,send_chan_ident,prep_short_src_dst,prep_long_src_dst

#import serial
import logging
import time
from struct import unpack
import threading

STEPS_PER_MM = 51200    # 136533.33
LIMIT_SWITCH = 13
BACKLASH_STEPS = 2560

# STEPS_PER_MM = 2184533.33    # 136533.33
# LIMIT_SWITCH = 13
# BACKLASH_STEPS = 43691

# DEBUG
Constructor_Counter = 0
Home_Counter = 0

class StepMotor_MST_DRV(Motor):

    def __init__(self, ser, bay=0,chan=1):
        '''
         Constructor

         :param ser: (Serial) the Serial object that corresponds to the port
         the motor is connected to. If the serial was successfully locked ser.write() can be called.
		 If the object waits for an answer from the serial object ser.in_buffer(pattern,trail_bytes) should be used.
		 :type ser: multi_serial Object

		 :param bay: the bay of the motor controller in main frame. For stand alone system bay should be 0.
		 :type ser: integer

		 :param chan: channel of motor controller in corresponding bay
		 :type chan: integer

		 :param lock: if the step motor shares a serial connection with other motors (by being a part of a mainframe)
		 the lock needs to be a threading.Lock() object shared with all objects making
		 calls to the shared serial interface. Before each serial call lock.acquire() and after each call lock.realease() needs to be called
		 :type lock: threading.Lock() object
        '''
        ###
        global Constructor_Counter
        Constructor_Counter += 1
        ###

        self.ser = ser
        self.ser.timeout = 0.1

        self.moving = False

        self.bay = int(bay)
        self.chan = int(chan)


        Motor.__init__(self, ser,bay,chan)
        self.ext['ClassName'] = 'StepMotor'
        self.home()                # home motor

        #self._set_backlash(0)     # set 0 backlash correction
        self.mm_pos = 0            # position of motor, in millimieters
        self.mm_zeros = 0          # the origin, in millimeters


    def home(self):
        '''
         Initializes all paremeters specific to the step motor and homes the motor.
		 The homing and backlash position need to be set up in a way that homing the system
		 brings the system into a safe position. The backlash correction needs to be performed
		 in such away that the correction is performed in the direction away from the chip
		 and the other probes.
        '''
        ###
        global Home_Counter
        Home_Counter += 1
        ###
        self.moving = True
        self.logger.debug('Homing...', extra=self.ext)


		#Acquire Lock over Serial
        if self.ser.lock:
			self.ser.lock.acquire()

		#### SETTING UP MOTOR PARAMETERS ####

        #MGMSG_MOT_SET_LIMSWITCHPARAMS
        self.ser.write(hexString('23 04 10 00'))    	 # header
        send_long_dst_src(self.ser,self.bay)
        send_chan_ident(self.ser, self.chan)
        self.ser.write(hexString('03 00'))                # CW Hard Limit
        self.ser.write(hexString('01 00'))                # CCW Hard Limit
        self.ser.write(hexString('00 84 03 00'))          # CW SoftLimit
        self.ser.write(hexString('00 64 00 00'))          # CCW SoftLimit
        self.ser.write(hexString('01 00'))          	  # SoftLimit Mode

		# CHECKING FOR ERROR MESSAGES
        #response = self.ser.read(1)
        #print map(hex,unpack('B'*len(response),response))
        #while map(hex,unpack('B'*len(response),response)) != []:
        #        response = self.ser.read(1)
        #    	 print map(hex,unpack('B'*len(response),response))


        # Check whether Parameters were written
        # < MGMSG_MOT_REQ_LIMSWITCHPARAMS >
        #self.ser.write(hexString('24 04 01 00 21 01'))
        #self.ser.reset_input_buffer()
        #switch_response = self.ser.read(22)
        #print map(hex,unpack('B'*len(switch_response),switch_response))

        #MGMSG_MOT_SET_VELPARAMS
        self.ser.write(hexString('13 04 0E 00'))    # header
        send_long_dst_src(self.ser,self.bay)
        send_chan_ident(self.ser, self.chan)
        self.ser.write(hexString('00 00 00 00'))          # Min Vel
        self.ser.write(hexString('00 32 00 00'))          # Acceleration
        self.ser.write(hexString('00 64 00 00'))          # Max Velocity

        # Check whether Parameters were written
        # < MGMSG_MOT_REQ_VELPARAMS >
        #self.ser.write(hexString('14 04 01 00 21 01'))
        #self.ser.reset_input_buffer()
        #switch_response = self.ser.read(22)
        #print map(hex,unpack('B'*len(switch_response),switch_response))

        #MGMSG_MOT_SET_JOGPARAMS
        self.ser.write(hexString('16 04 16 00'))    # header
        send_long_dst_src(self.ser,self.bay)
        send_chan_ident(self.ser, self.chan)
        self.ser.write(hexString('02 00'))                # Jog Mode
        self.ser.write(hexString('00 05 00 00'))          # Jog Step Size
        self.ser.write(hexString('00 00 00 00'))          # Jog Min Vel
        self.ser.write(hexString('00 C8 00 00'))          # Jog Acceleration
        self.ser.write(hexString('00 64 00 00'))          # Max Velocity
        self.ser.write(hexString('02 00'))          	  # Stop Mode

        # Check whether Parameters were written
        # < MGMSG_MOT_REQ_JOGPARAMS >
        #self.ser.write(hexString('17 04 01 00 21 01'))
        #self.ser.reset_input_buffer()
        #switch_response = self.ser.read(28)
        #print map(hex,unpack('B'*len(switch_response),switch_response))

        #MGMSG_MOT_SET_POWERPARAMS
        self.ser.write(hexString('26 04 06 00'))    # header
        send_long_dst_src(self.ser,self.bay)
        send_chan_ident(self.ser, self.chan)
        self.ser.write(hexString('14 00'))                # Rest Factor
        self.ser.write(hexString('64 00'))          	  # Move Factor

        # Check whether Parameters were written
        # < MGMSG_MOT_REQ_POWERPARAMS >
        #self.ser.write(hexString('27 04 01 00 21 01'))
        #self.ser.reset_input_buffer()
        #switch_response = self.ser.read(12)
        #print map(hex,unpack('B'*len(switch_response),switch_response))

        #MGMSG_MOT_SET_GENMOVEPARAMS
        self.ser.write(hexString('3A 04 06 00'))    # header
        send_long_dst_src(self.ser,self.bay)
        send_chan_ident(self.ser, self.chan)
        self.ser.write(hexString('00 0A 00 00'))          # Backlash Distance

        # Check whether Parameters were written
        # < MGMSG_MOT_REQ_GENMOVEPARAMS >
        #self.ser.write(hexString('3B 04 01 00 21 01'))
        #self.ser.reset_input_buffer()
        #switch_response = self.ser.read(12)
        #print map(hex,unpack('B'*len(switch_response),switch_response))

        #MGMSG_MOT_SET_MOVERELPARAMS
        self.ser.write(hexString('45 04 06 00'))    # header
        send_long_dst_src(self.ser,self.bay)
        send_chan_ident(self.ser, self.chan)
        self.ser.write(hexString('00 0A 00 00'))          # Relative Distance Distance

        # Check whether Parameters were written
        # < MGMSG_MOT_REQ_MOVERELPARAMS >
        #self.ser.write(hexString('46 04 01 00 21 01'))
        #self.ser.reset_input_buffer()
        #switch_response = self.ser.read(12)
        #print map(hex,unpack('B'*len(switch_response),switch_response))

        #MGMSG_MOT_SET_MOVEABSPARAMS
        self.ser.write(hexString('50 04 06 00'))    # header
        send_long_dst_src(self.ser,self.bay)
        send_chan_ident(self.ser, self.chan)
        self.ser.write(hexString('00 00 00 00'))          # Relative Distance Distance

        # Check whether Parameters were written
        # < MGMSG_MOT_REQ_MOVEABSPARAMS >
        #self.ser.write(hexString('51 04 01 00 21 01'))
        #self.ser.reset_input_buffer()
        #switch_response = self.ser.read(12)
        #print map(hex,unpack('B'*len(switch_response),switch_response))


        # < MGMSG_MOT_SET_HOMEPARAMS >
        #self.ser.write(hexString('40 04 0E 00'))    # header
        #send_long_dst_src(self.ser,self.bay)
        #send_chan_ident(self.ser, self.chan)
        #self.ser.write(hexString('02 00'))                # Home Dir
        #self.ser.write(hexString('01 00'))                # Limit Switch
        #self.ser.write('00 64 00 00')		               # Home Velocity
        #self.ser.write('00 32 00 00')                     # Offset Distance

        # Check whether Parameters were written
        # < MGMSG_MOT_REQ_HOMEPARAMS >
        #self.ser.write(hexString('41 04 01 00 21 01'))
        #self.ser.reset_input_buffer()
        #home_response = self.ser.read(20)
        #print map(hex,unpack('B'*len(home_response),home_response))

		# ACTUALLY STARTING THE HOMING

        # MGMSG_MOT_MOVE_HOME
        self.ser.write(hexString('43 04 {:02d} 00'.format(self.chan)))
        send_short_dst_src(self.ser,self.bay)

		# Relase Serial
        if self.ser.lock:
			self.ser.lock.release()

		# Wait for Homing Completion
        counter = 0
        found = False
        while counter < 60 and found == False: # MGMSG_MOT_MOVE_HOMED
            time.sleep(1)
            if self.ser.lock:
			    self.ser.lock.acquire()
            # self.ser.print_buffer()
            found = self.ser.in_buffer(hexString('44 04 {:02d} 00 '.format(self.chan)+prep_short_src_dst(self.bay)))
            if self.ser.lock:
                self.ser.lock.release()
            counter = counter + 1

        if counter >= 60:
            self.logger.error('problem homing', extra=self.ext)
            exit()

        self.logger.info('homed successfully.', extra=self.ext)
        self.moving = False

    def get_info(self):
        '''
         Get information back form the controller
         Used for debugging purposes
        '''
		#Acquire Lock over Serial
        if self.ser.lock:
			self.ser.lock.acquire()

        # MGMSG_HW_REQ_INFO
        self.ser.write(hexString('05 00 00 00'))
        send_short_dst_src(self.ser,self.bay)
        response = self.ser.read(90)
        self.ser.release()

		# Relase Serial
        if self.ser.lock:
			self.ser.lock.release()

        print(response)

    def _set_backlash(self, backlash_distance):
        '''
         Set the backlash correction distance for backwards motor
         movement

         backlash_distance (int): in encoder steps
        '''
		#Acquire Lock over Serial
        if self.ser.lock:
			self.ser.lock.acquire()

        # change backlash value
        self.ser.write(hexString('3A 04 06 00'))        # header
        send_long_dst_src(self.ser,self.bay)
        send_chan_ident(self.ser, self.chan)
        self.ser.write(int2hexStr(backlash_distance, 4))    # backlash dist
        self.ser.release()

        # request backlash data
        #self.ser.write(hexString('3B 04 01 00'))
        #send_short_dst_src(self.ser,self.bay)
		# confirm backlash distance value
        #res = self.ser.read(12)
        #back_dist_r = unpack('<l', res[8:12])[0]
        #if back_dist_r != backlash_distance:
        #    self.logger.error('Problem setting backlash distance [{}]'.format(backlash_distance), extra=self.ext)

		# Relase Serial
        if self.ser.lock:
			self.ser.lock.release()

    def delta_transl(self, dist):    #, m_callback = None, params = ()):
        '''
         Relative translation on the motor

         dist (float): the millimeters of translation (negative -> backwards)
         m_callback (function): (Optional) a function that will run while the motor
                                will be in motion. (e.g. show camera)
                                This callback's last parameter must be a callback itself,
                                named 'callback'
         params (tuple): the callback's parameters
        '''

        self.moving = True
        # check weather we are within limits
        if self.mm_pos + dist > LIMIT_SWITCH or self.mm_pos + dist < 0:
            self.logger.error('Out of bounds error (dist:{}, pos:{})'.format(dist, self.mm_pos), extra=self.ext)
            self.moving = False
            return False
        self.mm_pos += dist
        # convert millimeters to steps
        steps = int(round(dist * STEPS_PER_MM))

        if steps < 0:
            Motor.delta_move(self, (steps - BACKLASH_STEPS))
            # manual backlash correction
            Motor.delta_move(self, BACKLASH_STEPS)
        else:
            Motor.delta_move(self, steps)

        self.moving = False
        return True

    def check_abs_transl(self,dist):
        '''
        Check wether a move to position 'dist' is in range

        '''
        if dist > LIMIT_SWITCH or dist < 0:
            return False
        else:
            return True

    def abs_transl(self, dist):
        '''
         Absolute translation on the motor

         dist (float): the millmeters of rotation (negative -> backwards)
        '''
        self.moving = True
        # check whether we are within limits
        if dist > LIMIT_SWITCH or dist < 0:
            self.logger.error('Out of bounds error (abs_pos:{})'.format(dist), extra=self.ext)
            self.moving = False
            return
        # convert degrees to steps
        steps = int(round(dist * STEPS_PER_MM))

        # manual backlash correction
        if dist - self.mm_pos < 0:
            Motor.abs_move(self, (steps - BACKLASH_STEPS))
            Motor.delta_move(self, BACKLASH_STEPS)
        else:
            Motor.abs_move(self, steps)
        self.mm_pos = dist
        self.moving = False

    def get_mm_pos(self):
        '''
         return the motors current position, in millimeters
        '''

        return self.mm_pos

    def set_as_zero(self, zer_mm):
        '''
         change the origin (zero)
        '''

        n_zero = int(round(zer_mm / STEPS_PER_MM))
        Motor.set_as_zero(self, n_zero)

        self.mm_zeros = zer_mm
        self.mm_pos -= zer_mm

    def __str__(self):
        '''
         <For Debugging Purposes>
         gives information relevant to the motor state
        '''

        return 'StepMotor({})\n'.format(self.ser.port) + '  position(millimeters): ' + str(self.mm_pos) + '\n  zeros-position(millimeters): ' + str(self.mm_zeros)


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
