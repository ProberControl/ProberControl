Locking Scheme for Scripting
============================

Overview
--------
When the user implements the ``lock`` feature, described `here </source/howto/measurementScript.html>`_, there is a subroutine that disabled access to those instruments and 'locks' the specified instruments for the duration of the script. When the script is finished running, the instruments will appear in the drop down menu again. 


Usage
-----
The workflow for locking an instrument occurs as follows:

1. Instrument is marked as locked in the script configuration.

2. The object is added to the ``__locked`` collection, were the key is the ``ID( )`` of the ``ScriptController`` object that was initialized when the script was ran.

3. The graphical user interface is updated, removing the locked instruments from the ``Stages to Execute`` option menu.

4. When an instrument request is made, the ``Global_MeasureHandler`` traverses the stack of the request, looking for the ``ID( )`` of the object that made this call.
    - When the ``ID`` is determined, the ``Global_MeasureHandler`` then checks if that instrument is available in the ``__locked`` collection for that specific ``ID( )``.
    - The ``Global_MeasureHandler`` will always return an instrument from the ``__locked`` collection if one is available for that specific ``ID( )``.
    - When the ``Global_MeasureHandler`` traverses the stack, it is looking for the ``ID`` of the instance of ``ScriptHandler``. It is not necessarily looking for a specific ``ID``, but looking for the ``ID`` of the object that has invoked this exact instance of the ``get_instrument`` call. Due to the design of the locking scheme, the only functions that could have invoked ``get_instrument`` are stored in the list ``functions``. If the ``ID`` of the local namespace for ``self``, i.e. the object that invoked this function, appears in out ``__locked`` dictionary's keys, then it is in fact the ``ID`` of an instance of a ``ScriptController`` that locked the instrument during the initial setup.

.. code-block:: python

    functions = ['_structureProcedure','__executeCommand','_procedure']

    for entry in inspect.stack(context=0):
        if entry[3] in functions:
            id_ = id(entry[0].f_locals['self'])

        if (id_ in self.__locked.keys()):


5. When the script is done running, the ``Global_MeasureHandler`` will release all of the locked instruments associated with that ``ID( )``

.. code-block:: python

    def clear_locked(self, id_=''):
    '''
    clears the locked instruments, if id_ is passed as a parameter,
    this function clears all instruments associated with that script id
    '''
    if id_:
        self.__locked.pop(id_)
        print self.__locked
    else:
        self.__locked = {}

Snapshot
--------

Code that executes the locking scheme from the ``Global_MeasureHandler``:

.. code-block:: python

    def get_instrument(self, specifiedDevice):
        '''Finds and returns an unactive instrument corresponding to the one specified'''
        device = self.clean(specifiedDevice)

        # Try the locked instruments first
        instrumentActual = self.__checkLocked(device)
        if not instrumentActual: # if nothing was found in __checkLocked()

        # Then take a look for available instruments, if not in locked
            for instrument in self.Stages.keys():
                strippedInstrument = ''.join([self.clean(i) for i in instrument if not i.isdigit()])

                # If we find a device that fits and it isn't active right now
                if device in strippedInstrument and not self.Stages[instrument].active:
                    return self.Stages[instrument]

        #If you make it here, no available instrument
        return instrumentActual

    def __checkLocked(self, instrument):
        '''
        Function that traces the stack back to ScriptController, then uses
        the id() of that particular object to confirm who is calling on that
        particular instrument
        '''

        # As of August 6, 2017
        # The only functions that would be calling for objects/functions
        functions = ['_structureProcedure','__executeCommand','_procedure']
        id_ = ''

        # Iterate over the stack, finding the ID of the unique ScriptController object
        for entry in inspect.stack(context=0):
            if entry[3] in functions:
                id_ = id(entry[0].f_locals['self'])

            # If the ID of the caller is in the locked objects
            if (id_ in self.__locked.keys()):
                locked_objects = self.__locked[id_]

                # check instruments locked with that particular script
                for object_ in locked_objects:
                    cleanInstrument = ''.join([self.clean(i) for i in str(object_) if not i.isdigit()])
                    if instrument == cleanInstrument:
                        return object_

        # If nothing was found, return false
        return False 

Diagram of the workflow
-----------------------
.. image:: ..\..\_static\locking_scheme.PNG
    :width: 701px
    :align: center
    :height: 572px