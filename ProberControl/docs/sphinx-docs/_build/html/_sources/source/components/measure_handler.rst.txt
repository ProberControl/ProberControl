MeasureHandler
==============

The measure handler is the entity that will control and distribute access of the measurement instruments, such as dc multi-meters or optical power-meters, to the procedures or objects that require them. The handler takes away from the specific functions the responsibility to know exactly what instruments they are dealing with. The functions will only need to provide the type of instrument they need and the measure handler will perform all the necessary work to find such an instrument.

**Interface:**
    The measure handler functionality is cleanly exposed by a single class called Global_MeasureHandler. The class utilizes a Singleton scheme so the same object will be accessed from anywhere in the code. The constructor only needs a reference to the Stages dictionary:

.. code-block:: python

    @Singleton        # apply the Singleton decorator
    class Global_MeasureHandler(object):
        def __init__(self, Stages):
            self.Instruments = {}
            self.Stages = Stages

Internally the class should utilize a two level table[1]_ to classify the different instruments. It should look like this:

.. image:: ../../_static/diagram.png
    :height: 300px
    :width: 600px
    :align: center

The core of the measure handler’s functionality lies on the nature of the attribute type in the main dictionary. In the current implementation this attribute is the measurement type the instrument performs (ex. DC, RF, optical). The attribute type could as well be the kind of function that the specific interface of the instrument exposes (ex. Does it implement get_current() ?). The final entries are triplets (function, threshold, user). What the user of the Global_MeasureHandler is interested in is the measurement function and any associated values that help in the tests (ex. the power threshold for optical coupling).

A description of the class’s methods is provided below:
    ``insert_instr(stage_name, triggerNetwork)``
        This is the function that adds an instrument to the measure_handler.
    ``get_instrument(specifiedDevice, additional=False)``
        Finds and returns an inactive instrument corresponding to the one specified. Returns None if such instrument was found/available.
    ``get_instrument_triggered_by(self, triggerSource, specifiedDevice, additional=False)``
        Finds and returns an unactive instrument, corresponding to the one specified, that can be triggered by trigger_source
    ``connect_instruments(self, transmitting_instrument, receiving_instrument)``
        Connects two instruments together through the SwitchHandler.
    PARALLELISM
        In the method descriptions above the notion of availability is extensively referenced. The general idea behind that is that we would like in the future for the testing procedure to become pipelined so that different tests can be performed at the same time. In that case strict mechanism has to be defined to distribute the instrument resources. The Global_MeasureHandler is also responsible for that. This is what the user field in the table entries are for. Also if tests are to be performed in parallel, the measure_handler should be completely thread safe, securing the data structure with locks where necessary.
        SIDE EFFECTS
    CONFIGURATION FILE
        Because of the way we want the measure handler to work, we need to get instrument classification information from somewhere (that would go into the insert_instr call). Thus, the ProberConfig.conf file and its parsing mechanism within ProberControl.py should expand to accommodate the insertion of descriptions at least for the instrument entries that are used for measurements (whose names begin with ‘M’).
    SWITCHING
        The development of Global_MeasureHandler should also allow for an efficient way of interacting with the module that will control the large switch which will connect the different components. Some example code could look like:

.. code-block:: python

    def some_test_function(blah, blah):
        g_mh = Global_MeasureHandler()
        # more stuff...

    fun, thresh = g_mh.get_instr('DC', True)
    switch.connect(switch_id_of(fun), this_fiber)
    #continue with test...

The GUI is based on Tkinter. The constructor has the following dynamic parts:
1.    It generates the line with Item 6,7,8 dynamically depending whether a stage or measurement tool is connected
2.    Line A is equipped with buttons representing the stages keys in the stages Dictionary.
