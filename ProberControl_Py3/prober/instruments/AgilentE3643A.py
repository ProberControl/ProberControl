# Class for Agilent E3643A DC Power Supply

import serial
import time

class AgilentE3643A(object):
    '''
    This class models the Agilent DC power supply.
    '''
    def __init__(self, res_manager, address='YourAddressHere'):
        '''
        Constructor method.

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False
        self.ser = serial.Serial(
            port=None,
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        self.ser.port = address

    def whoAmI(self):
        ''':returns: reference to device'''
        return 'DCSource'

    def change_state(self):
        ''' Toggles the self.active parameter'''
        if self.active == True:
            self.active = False
        else:
            self.active = True

    def get_voltage(self):
        '''Gets the voltage.
        :return: the measured DC voltage
        :raises: Exception when serial communication port is not open
        '''
        if self.ser.isOpen():
            self.ser.write(b'MEAS:VOLT:DC?\n')
            voltage = self.ser.readline().strip('\n')
            return float(voltage)
        else:
            raise Exception('Serial communication port is not open.')

    def get_current(self):
        '''Gets the current.
        :return: the measured DC current
        :raises: Exception when serial communication port is not open
        '''
        if self.ser.isOpen():
            self.ser.write(b'MEAS:CURR:DC?\n')
            current = self.ser.readline().strip('\n')
            return float(current)
        else:
            raise Exception('Serial communication port is not open.')

    def open(self):
        '''Opens serial connection.
        :raises: Exception when serial communication port is not open
        '''
        if not self.ser.isOpen():
            self.ser.open()
        else:
            raise Exception("Serial port is already open.")

    def close(self):
        '''Release resources, closes serial port.
        :raises: Exception when serial communication port is not open
        '''
        if self.ser.isOpen():
            self.ser.close()
        else:
            raise Exception("Serial port is not currently open, cannot be closed.")

    def setVoltage(self, value=0):
        '''
        Sets the voltage.

        :param value: Specified voltage value, defaults to 0
        :type value: float
        :raises: Exception when serial communication port is not open
        '''
        if self.ser.isOpen():
            self.ser.write(b'VOLT {}\n'.format(str(value)))
            self.ser.readline()
        else:
            raise Exception('Serial communication port is not open.')


    def setCurrent(self, value=0):
        '''
        Sets the current.

        :param value: Specified current value, defaults to 0
        :type value: float
        :raises: Exception when serial communication port is not open
        '''
        if self.ser.isOpen():
            self.ser.write(b'CURR {}\n'.format(str(value)))
            self.ser.readline()
        else:
            raise Exception('Serial communication port is not open.')


    def setovervoltage(self, value=0):
        '''
        Sets the over voltage.

        :param value: Specified voltage value, defaults to 0
        :type value: float
        :raises: Exception when serial communication port is not open
        '''
        if self.ser.isOpen():
            self.ser.write(b'VOLT:PROT {}\n'.format(str(value)))
            self.ser.readline()
        else:
            raise Exception('Serial communication port is not open.')


    def setOutputSwitch(self, value=0):
        '''
        Set the output switch to 1 -> ON or 0 -> OFF

        :param value: Specified state, defaults to 0 for OFF, 1 for ON
        :type value: Integer
        :raises: Exception when serial communication port is not open or value is not 0 or 1
        '''
        if self.ser.isOpen():
            if value == 0 or value == 1:
                if value == 1:
                    self.ser.write(b'OUTPUT ON\n')
                else:
                    self.ser.write(b'OUTPUT OFF\n')
                self.ser.readline()
            else:
                raise Exception('Input value is incorrect, must be 1 for ON or 0 for OFF')
        else:
            raise Exception('Serial communication port is not open.')


    def save_state(self,mem=1):
        '''
        Stores state within non-volatile memory

        :param mem: Specified space to write to
        :type mem: Integer
        '''
        if mem > 5 or mem < 1:
            raise Exception('Invalid memory space: ' + str(mem) + ', valid states are {1,2,3,4,5}')
        if self.ser.isOpen():
            self.ser.write(b'*SAV {}\n'.format(mem))
            self.ser.readline()
        else:
            raise Exception('Serial communication port is not open.')

    def recall_state(self,mem=1):
        '''
        Loads stored state from specified memory location

        :param mem: Specified space to query
        :type mem: Integer
        '''
        if mem > 5 or mem < 1:
            raise Exception('Invalid memory space: ' + str(mem) + ', valid states are {1,2,3,4,5}')
        if self.ser.isOpen():
            self.ser.write(b'*RCL {}\n'.format(mem))
            self.ser.readline()
        else:
            raise Exception('Serial communication port is not open.')
