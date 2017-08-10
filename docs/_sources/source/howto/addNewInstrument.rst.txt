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
There are 2 levels of requirements: requirements of **all** instrument classes and requirements for **specific** instrument classes. The requirements for **all** instrument classes are having a ``whoAmI()``, ``whatCanI()``, and ``__str__()`` methods.

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

        def whoAmI(self):
            ''':returns: reference to device'''
            return 'RFSource'

        def whatCanI(self):
            ''':returns: instrument attributes'''
            return ''

        def __str__(self):
            '''Adds built in functionality for printing and casting'''
            return 'ClassNameHere'