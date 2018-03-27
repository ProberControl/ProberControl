Global Measure Handler
==============

The measure handler is the entity that controls and distributes access of the measurement instruments, such as dc multi-meters or optical power-meters, to the procedures or objects that require them. The handler takes away from the specific functions the responsibility to know exactly what instruments(models) they are dealing with. The functions will only need to provide the type of instrument they need and the measure handler will perform all the necessary work to find such an instrument.

**Description**
    The measure handler functionality is cleanly exposed by a single class called Global_MeasureHandler. The class utilizes a Singleton scheme so the same object will be accessed from anywhere in the code. The constructor only needs a reference to the Stages dictionary:

.. code-block:: python

    @Singleton        # apply the Singleton decorator
    class Global_MeasureHandler(object):
        def __init__(self, Stages):
            self.Instruments = {}
            self.Stages = Stages

.
    Internally the class keeps information about:
        - All the instruments (and fibers) that were registered in the main configuration file
        - Which instruments are at any time owned by a user (eg. instance of ScriptController, GUI)
        - The triggering networks, meaning which instrument can trigger which other instrument, as defined in the configuration file

    ... and provides functionality to control:
        - The provision of instruments according to type
        - The serialization to instrument ownership
        - The interconnection of "owned" instruments through the ``SwitchHandler``

    The Global_MeasureHandler is a necessary and fundamental entity of the ProberControl framework and serves to optimally utilize the available instruments of a setup. It enables the correct parallelization of test recipe execution, keeping tally of available and used instruments and implementing a sophisticated internal locking scheme, which is necessary for thread safety.

    The class was originally to be used explicitly in the custom measurement functions defined by the test engineer, but is now also used internally in the software, for organization purposes.

**Interface**
    The Global_MeasureHandler exposes a simplistic API that is intuitive and easy to use, while providing a full range of options for the test engineer writing the measurement functions. Below are the most important/useful methods:

``get_instrument(specifiedDevice, additional=False)``
        Finds and returns an inactive instrument corresponding to the one specified. Returns None if such instrument was found/available.
``get_instrument_triggered_by(triggerSource, specifiedDevice, additional=False)``
        Finds and returns an inactive instrument, corresponding to the one specified, that can be triggered by trigger_source instrument
``get_instrument_triggering(triggerTarget, specifiedDevice, additional=False)``
        Finds and returns an inactive instrument, corresponding to the one specified, that can trigger trigger_source instrument
``get_instrument_by_name(instrumentName)``
        Finds and returns the instrument with the specified name, used in the cases where a specific model in necessary
``choose_fiber_in(self, fiber_id)``
        Returns a holder to the input fiber with id fiber_id (as specified in the configuration file)
``choose_fiber_out(self, fiber_id)``
        Returns a holder to the output fiber with id fiber_id (as specified in the configuration file)
``connect_instruments(self, transmitting_instrument, receiving_instrument)``
        Connects two instruments together (through the SwitchHandler)


    The functions of the family get_instrument... listed above all return **None** if the instrument is not found or is already in use by a different user. In a multi-threaded environment, however, it makes sense for to wait for the instrument to become available before returning to the user. As such, the following blocking alternatives exist (denoted by the **_w** for "wait"):

``get_instrument_w(specifiedDevice, additional=False, timeout=0.0)``
``get_instrument_triggered_by_w(triggerSource, specifiedDevice, additional=False, timeout=0.0)``
``get_instrument_triggering_w(triggerTarget, specifiedDevice, additional=False, timeout=0.0)``
``get_instrument_by_name_w(instrumentName)``

    The functions above take the exact arguments as the respective non-blocking ones, plus an optional parameter ``timeout`` which determines how long to wait if the instrument is not available. A timeout of 0 means wait until it becomes available.

**Example**
    Here is an examples which demonstrate the ease of use of the Global_MeasureHandler API for measurement functions:

.. code-block:: python

    def simpleConnectFiberTest():
        gh = Global_MeasureHandler()

        # wait for laser
        laser = gh.get_instrument_w('Laser')
        # choose input fiber
        fiber_in = gh.choose_fiber_in(1)
        # connect laser to fiber
        gh.connect_instruments(laser, fiber_in)

        # choose output fiber
        fiber_out = gh.choose_fiber_out(3)
        # wait for a powermeter
        p_meter = gh.get_instrument_triggered_by_w(laser, 'PowerMeter')
        # connect fiber to powermeter
        gh.connect_instruments(fiber_out, p_meter)

        # make measurement
        wavelength = 1550
        laser.setwavelength(wavelength)
        power = p_meter.get_power(wavelength)
        print power

.
    Here we use the blocking version of get_instrument which means that if all lasers and all power-meters are in use, we will wait until some are available. We also demonstrate the use of the trigger-conscious functions. The powermeter selected will by triggerable by the laser.

    We can see how in 6 lines of code with Global_MeasureHandler we have acquired and connected together all the instruments we need to make an optical power measurement!
