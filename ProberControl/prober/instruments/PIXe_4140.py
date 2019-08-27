""" Driver for NI PIXe-4322 6 channel SMU

    Allows for user interfacing directly, as well as ProberControl API

    see https://probercontrol.github.io/ProberControl/source/howto/addNewInstrument.html for
    more info
"""
import sys
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

class PIXe_4140(object):
    def __init__(self, rm, address='PXI1Slot2', channel='ao0', **kwargs):
        self.address = address
        self.channel = channel
        self.last_set_voltage = 0
        self.last_set_current = 0
        with nidcpower.Session(resource_name=self.address, channels=self.channel) as session:
            session.output_enabled = False
            session.initiate()

    def setvoltage(self,value):
        with nidcpower.Session(resource_name=self.address, channels=self.channel) as session:
            session.output_function = nidcpower.OutputFunction.DC_VOLTAGE
            session.output_enabled = True
            session.voltage_level_autorange = True
            session.voltage_level = float(value)
            session.initiate()

    def setcurrent(self,value):
        with nidcpower.Session(resource_name=self.address, channels=self.channel) as session:
            session.output_function = nidcpower.OutputFunction.DC_CURRENT
            session.output_enabled = True
            session.current_level_autorange = True
            session.current_level = float(value)
            session.initiate()

    def set_voltage_get_voltage(self, value, query_range):
        query_range = int(query_range)
        with nidcpower.Session(resource_name=self.address, channels=self.channel) as session:
            session.output_function = nidcpower.OutputFunction.DC_VOLTAGE
            session.output_enabled = True
            session.voltage_level_autorange = True
            session.measure_record_length = query_range
            session.measure_record_length_is_finite = True
            session.measure_when = nidcpower.MeasureWhen.AUTOMATICALLY_AFTER_SOURCE_COMPLETE
            session.voltage_level = float(value)
            samples = []
            samples_acquired = 0
            with session.initiate():
                while samples_acquired < query_range:
                    measurements = session.fetch_multiple(count=session.fetch_backlog)
                    samples_acquired += len(measurements)
                    for i in range(len(measurements)):
                        samples.append(measurements[i].voltage)

        return samples


    def set_current_get_voltage(self, value, query_range):
        query_range = int(query_range)
        with nidcpower.Session(resource_name=self.address, channels=self.channel) as session:
            session.output_function = nidcpower.OutputFunction.DC_CURRENT
            session.output_enabled = True
            session.current_level_autorange = True
            session.measure_record_length = query_range
            session.measure_record_length_is_finite = True
            session.measure_when = nidcpower.MeasureWhen.AUTOMATICALLY_AFTER_SOURCE_COMPLETE
            session.current_level = float(value)
            samples = []
            samples_acquired = 0
            with session.initiate():
                while samples_acquired < query_range:
                    measurements = session.fetch_multiple(count=session.fetch_backlog)
                    samples_acquired += len(measurements)
                    for i in range(len(measurements)):
                        samples.append(measurements[i].voltage)

        return samples

    def set_voltage_get_current(self, value, query_range):
        query_range = int(query_range)
        with nidcpower.Session(resource_name=self.address, channels=self.channel) as session:
            session.output_function = nidcpower.OutputFunction.DC_VOLTAGE
            session.output_enabled = True
            session.voltage_level_autorange = True
            session.measure_record_length = query_range
            session.measure_record_length_is_finite = True
            session.measure_when = nidcpower.MeasureWhen.AUTOMATICALLY_AFTER_SOURCE_COMPLETE
            session.voltage_level = float(value)
            samples = []
            samples_acquired = 0
            with session.initiate():
                while samples_acquired < query_range:
                    measurements = session.fetch_multiple(count=session.fetch_backlog)
                    samples_acquired += len(measurements)
                    for i in range(len(measurements)):
                        samples.append(measurements[i].current)

        return samples


    def set_current_get_current(self, value, query_range):
        query_range = int(query_range)
        with nidcpower.Session(resource_name=self.address, channels=self.channel) as session:
            session.output_function = nidcpower.OutputFunction.DC_CURRENT
            session.output_enabled = True
            session.current_level_autorange = True
            session.measure_record_length = query_range
            session.measure_record_length_is_finite = True
            session.measure_when = nidcpower.MeasureWhen.AUTOMATICALLY_AFTER_SOURCE_COMPLETE
            session.current_level = float(value)
            samples = []
            samples_acquired = 0
            with session.initiate():
                while samples_acquired < query_range:
                    measurements = session.fetch_multiple(count=session.fetch_backlog)
                    samples_acquired += len(measurements)
                    for i in range(len(measurements)):
                        samples.append(measurements[i].current)

        return samples

    def retreive_voltage(self):
        return self.voltage

    def whoAmI(self):
        return 'DCSource'

    def source_off(self):
        '''Release resources'''
        with nidcpower.Session(resource_name=self.address, channels=self.channel) as session:
            session.output_enabled = False
            session.initiate()

def main(options, stdout):
    device = PIXe_4140(options.address,options.channel)
    if hasattr(PIXe_4140, options.function):
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
