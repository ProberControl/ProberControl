# APT controllers generic helper functions
try:
    from . import multi_serial
    import serial
except:
    pass

def c2r(COM_port, rate=115200):
    '''returns a serial object for the spec. port with the APT configuration'''
    try:
        temp = multi_serial.MultiSerial(COM_port, rate, timeout=None, parity=serial.PARITY_NONE)
        return temp
    except Exception as e:
        print(e)

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
