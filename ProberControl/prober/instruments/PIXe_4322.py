""" Driver for NI PIXe_4322 8 channel Power Supply

    Allows for user interfacing directly, as well as ProberControl API

    see https://probercontrol.github.io/ProberControl/source/howto/addNewInstrument.html for
    more info
"""
import sys
import argparse

import nidaqmx

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_args(args=sys.argv[1:]):
    """Parse arguments."""
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)

    g = parser.add_argument_group("driver settings")
    g.add_argument("address", metavar="gpib_address",
                   type=str,
                   help="The address of the device to be controlled")
    g.add_argument("channel", metavar="device_channel",
                   type=str,
                   help="The channel to be controlled for the device")
    a = parser.add_argument_group("driver actions")
    a.add_argument("function", metavar="function_name",
                   type=str,
                   help="The driver function to be run")
    a.add_argument("--value", metavar="function value",
                   type=str,
                   help="The value to be set for the function")

    return parser.parse_args(args)

class PIXe_4322(object):
    def __init__(self, rm, address='PXI1Slot2', channel='ao0', **kwargs):
        self.address = address
        self.channel = channel
        self.set_voltage(0)
        self.voltage = 0
        return

    def set_voltage(self,value):
        with nidaqmx.Task() as task:
            print(self.address)
            task.ao_channels.add_ao_voltage_chan(self.address + '/' + self.channel)
            task.write(value)
            task.stop()

    def retreive_voltage(self):
        return self.voltage

    def whoAmI(self):
        return 'PowerSupply'

def main(options, stdout):
    device = PIXe_1084(options.address,options.channel)
    if hasattr(PIXe_1084, options.function):
        if isempty(options.value):
            value = getattr(device, options.function)
        else:
            value = getattr(device, options.function)(options.value)
        print('Function: %s' % options.function)
    else:
        print("Function does not exist.")

if __name__ == '__main__':
    def _script_io():
        from sys import argv, stdout
        options = parse_args()
        main(options, stdout)

    _script_io()
