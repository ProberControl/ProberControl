Adding a New Instrument
=======================

Overview
--------
There may be a point where you'll want to add a new instrument to the ProberControl's library. This can be implemented easily by using one of the templates and following the requirements for an instrument class.

Templates
---------
In the folder marked ``ProberControl/docs/templates`` you'll find several templates, one for each type of instrument that the ProberControl implements. As of version July 2017 there are templates for:
    * DC Sources
    * RF Sources
    * Multimeters
    * Lasers

Requirements
------------
There are 2 levels of requirements: requirements of **all** instrument classes and requirements for **specific** instrument classes. The requirements for **all** instrument classes are having a ``whoAmI()`` method, ``whatCanI()`` method, a boolean ``self.active`` parameter, a ``change_state()`` method that toggles the active parameter , and the ``__str__()`` methods.

The finished driver needs to be placed into the **prober/instruments** folder. Furthermore, the **__init__.py** file contains the list of all files inside the folder, which must be updated with the new driver.


Important Links to other parts of the Software
----------------------------------------------
The return  value of ``whoAmI()`` defines as what type of tool the device will show up in the stages dictionary and therefore in the GUI.

The ``self.active`` parameter is accessed by the Script Controller and Global Measurement Handler to check whether a tool is busy. When non atomic functions are performed by the driver (e.g. all communication with the tool) the driver function should set the device as busy while performing the function.

The constructor needs to accept the following arguments: ``__init__(self,res_manager, address='YourAddressHere')`` even if the res_manager is not needed (e.g. for ethernet communication - see the Keithley2280S driver for an ethernet exaple). For multi channel devices a channel parameter must be added.

Example:

.. code-block:: python

    class ClassNameHere(object):
    '''Purpose of this class here'''
        def __init__(self,res_manager, address='YourAddressHere'):
            '''
            Constructor method

            :param res_manager: PyVisa resource manager
            :type res_manager: PyVisa resourceManager object
            :param address: SCPI address of instrument
            :type address: String
            '''

            self.gpib = res_manager.open_resource(address)
            self.active = False

        def whoAmI(self):
            ''':returns: reference to device'''
            return 'RFSource'

        def change_state(self):
            ''' Toggles the self.active parameter'''
            if self.active == True:
                self.active = False
            else:
                self.active = True
