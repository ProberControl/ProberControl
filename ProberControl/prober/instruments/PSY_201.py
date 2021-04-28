""" Driver for NI PIXe-4322 6 channel SMU

    Allows for user interfacing directly, as well as ProberControl API

    see https://probercontrol.github.io/ProberControl/source/howto/addNewInstrument.html for
    more info
"""
import sys
import visa
import argparse

import nidcpower

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
    a = parser.add_argument_group("driver actions")
    a.add_argument("function", metavar="function_name",
                   type=str,
                   help="The driver function to be run")
    a.add_argument("--value", metavar="function value",
                   type=str,
                   help="The value to be set for the function")

    return parser.parse_args(args)

class PSY_201(object):
    def __init__(self, res_manager, address='PXI1Slot2', **kwargs):
        self.address = address
        self.gpib = res_manager.open_resource(address)
        self.gpib.clear()
        self.gpib.write(':CONT:DIS')
        self.track = False

    def set_SOP(self,s1,s2,s3):
        self.track = False
        self.gpib.write(':CONT:SOP'+','.join([str(s1),str(s2),str(s3)]))

    def set_SOP_type(self,type):
        self.track = False
        self.gpib.write(':CONT:TSC:TYPE'+str(int(type)))

    def measure_polarization(self):
        try:
            return self.gpib.query(':MEAS:SOP?')
        except:
            return self.gpib.read()

    def toggle_track_polarization(self):
        if self.track:
            self.gpib.write(':CONT:DIS')
        else:
            self.gpib.write(':CONT:ENAB')
        self.track = not self.track

    def measure_power(self):
        try:
            return self.gpib.query(':MEAS:POW?')
        except:
            return self.gpib.read()        

    def whoAmI(self):
        return 'PolSynthesizer'

def main(options, stdout):
    #import visa
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
