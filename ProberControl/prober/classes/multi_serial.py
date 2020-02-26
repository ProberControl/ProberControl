from serial import Serial

from struct import unpack
import time
import threading

class MultiSerial(Serial):
    '''This class should be used for all serial connections. It inherits the pyserial class and
    adds the in_buffer(), print_buffer() and clear_buffer() functions. For easy thread save
    communication with the serially connected devices'''
    buffer  = ''

    def __init__(self, *args, **kwrags):
        # call default (base) constructor
        Serial.__init__(self, *args, **kwrags)
        self.lock = None
        self.lock_given = False

    def in_buffer(self, answer,tail_bytes=0):
        '''
        This function updates the serial buffer and searches for patterns(answer) inside the buffer.
        If found the answer and the following tail_bytes are deleted from the buffer. The function
        should be used to check whether the slave reported a certain answer.

        :param answer: the pattern to search for in the buffer
        :type answer: string

        :param tail_bytes: number of bytes following the pattern to be deleted if pattern was found
        :type tail_bytes: integer
        '''
        response = Serial.read(self, 1)
        while list(map(hex,unpack('B'*len(response),response))) != []:
            self.buffer = self.buffer + response
            response = Serial.read(self,1)

        if answer in self.buffer:
            if tail_bytes != 0:
                Serial.read(self,tail_bytes)

                index = self.buffer.find(answer)
                self.buffer = self.buffer[:index]+self.buffer[index+len(answer)+tail_bytes:]

            else:
                self.buffer = self.buffer.replace(answer,'')

            return True
        else:
            return False

    def print_buffer(self):
        '''
        Prints the current buffer. The buffer is printed is interpreted as hex numbers and send to print
        '''

        print('Ascii-fied Hex Representation of Buffer:')
        print((list(map(hex,unpack('B'*len(self.buffer),self.buffer)))))

    def clear_buffer(self):
        '''
        Empties the current buffer and calls Serial.flushInput() Serial.flushOutput().
        '''
        self.buffer = ''
        Serial.flushInput()
        Serial.flushOutput()


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
