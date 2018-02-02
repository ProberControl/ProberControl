Serial, GPIB and Ethernet Connection Handling in Instrument Classes
=============================

**Serial Ports** are currently assigned in the ``ProberControl.py`` using: ``from ProbeLib.Classes.apt_util import c2r``. The c2r(COM_Port) function returns a handler of a serial object from the pyserial package. The serial object opens the communication with the specified COM_Port using the configuration: Baud Rate = 115200, timeout=none, parity = PARITY_NONE. The serial objects are then linked to the objects representing stages or measurement tools by handing the serial object over to the stage object as a constructor parameter.
If the serial settings/parameters described above are not the optimal ones for a specific instrument, the user can change them at any point (usually in the constructor ``__init__``) just like any serial object as described in the pyserial documentation found `here <http://pythonhosted.org/pyserial/>`_. Below we see an exmaple:

.. code-block:: python

    def __init__(self, ser, bay=0,chan=1):
          '''
           Constructor

           :param ser: (Serial) the Serial object that corresponds to the port
           the motor is connected to. If the serial was successfully locked ser.write() can be called.
           [...]

          '''
          ###
          global Constructor_Counter
          Constructor_Counter += 1
          ###

          self.ser = ser
          self.ser.timeout = 0.1

          self.moving = False
          # ...

**GPIB** is a bus system so only one master is controlled by the pc. When in ``ProberControl.py`` the line from ProbeLib.InstrumentControlClasses import rm is executed a gpib resource manager (rm) is generated (see file ``ProbeLib\InstrumentControlClasses\__init__.py``). The rm is made available to all instrument control drivers by adding the rm as a constructor parameter. Here's an example of how ``rm`` is used inside an instrument class:

.. code-block:: python

    def __init__(self, res_manager, address='GPIB0::24::INSTR'):
          '''
          Constructor method

          :param res_manager: PyVisa resource manager
          :type res_manager: PyVisa resourceManager object
          :param address: SCPI address of instrument
          :type address: string
          '''

          self.active = False

          self.max_wavelength = 1579.9
          self.min_wavelength = 1520

          self.gpib = res_manager.open_resource(address)
          self.gpib.write('PASSWORD4321')

          self.gpib.write('INIT')
          self.gpib.write ('IDN?')
          info = self.gpib.read()
          print ('Connection Successful: %s' % info)
          # ...

To use and program an **Ethernet** connected instrument all we need from the core software is the ip address of the instrument, which is given as the second argument of the constructor (and is parsed from the .config file). The user can choose to use any networking python module that they are comfortable with. We normally just use the standard socket module for portability reasons. Here's an example where the instrument class connects to the instrument as a TCP/IP client:

.. code-block:: python

    def __init__(self,res_manager,address='169.254.115.242',channel=1):

          self.active = False
          self.__channel = channel

          self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

          try:

              self.sock.connect((address, 5025))
              self.sock.sendall('*IDN?\n')
              print self.sock.recv(1024)
              self.sock.sendall(':DATA:CLE:AUTO 1\n')
              self.sock.sendall(':TRAC:FEED:CONT ALW\n')
              self.sock.sendall(':TRAC:POIN 2\n')
              # ...

We see that for the sake of uniformity we always include the two arguments ``res_manager`` and ``address`` in the constructor even if, for example, we do not use res_manager for an Ethernet connected instrument.
