# APT controllers generic helper functions
import serial

def c2r(COM_port):
    '''returns a serial object for the spec. port with the APT configuration'''

    try:
        temp = serial.Serial(COM_port, 115200, timeout=None, parity=serial.PARITY_NONE)
        return temp
    except Exception as e:
        print e