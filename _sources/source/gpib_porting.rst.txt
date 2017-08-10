Serial and GPIB Port Handling
=============================

Serial Ports are currently assigned in the ``ProberControl.py`` using: ``from ProbeLib.Classes.apt_util import c2r``. The c2r(COM_Port) function returns a handler of a serial object from the pyserial package. The serial object opens the communication with the specified COM_Port using the configuration: Baud Rate = 115200, timeout=none, parity = PARITY_NONE. The serial objects are then linked to the objects representing stages or measurement tools by handing the serial object over to the stage object as a constructor parameter.

GPIB is a bus system so only one master is controlled by the pc. When in ``ProberControl.py`` the line from ProbeLib.InstrumentControlClasses import rm is executed a gpib resource manager (rm) is generated (see file ``ProbeLib\InstrumentControlClasses\__init__.py``). The rm is made available to all instrument control drivers by adding the rm as a constructor parameter.