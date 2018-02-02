Locking Scheme for Scripting
============================

Overview
--------
When the user acquires and uses instruments in ``procedures'`` functions that are called from a script, there is a subroutine that disabled access to those instruments and 'locks' the specified instruments for the duration of the script. When the script is finished running, the instruments will appear in the drop down menu again.


Usage
-----
The workflow for locking an instrument occurs as follows:

1. Every time the user runs a script a new instance of the ``ScriptController`` is instantiated to undertake the task. Each script contoller is associated with a unique ``ID``.

2. The Script controller will serially go through the entries of the measurement script, executing the specified ``procedure`` function.

3. The graphical user interface is updated, blocking the locked instruments from the ``Stages to Execute`` option menu.

4. When an instrument request is made within a ``procedure`` function through the ``Global_MeasureHandler``, the ``Global_MeasureHandler`` traverses the stack of the request, looking for the ``ID`` of the ScriptController that made this call.
    - When the ``ID`` is determined, the ``Global_MeasureHandler`` can check if that instrument is available in the ``__locked`` collection for that specific ``ID``.
    - When the ``Global_MeasureHandler`` traverses the stack, it is looking for the ``ID`` of the instance of ``ScriptHandler``. It is not necessarily looking for a specific ``ID``, but looking for the ``ID`` of the object that has invoked this exact instance of the ``get_instrument`` call. Due to the design of the locking scheme, the only functions that could have invoked ``get_instrument`` are stored in the list ``functions``. If the ``ID`` of the local namespace for ``self``, i.e. the object that invoked this function, appears in out ``__locked`` dictionary's keys, then it is in fact the ``ID`` of an instance of a ``ScriptController`` that locked the instrument during the initial setup.

.. code-block:: python

    functions = ['_structureProcedure','__executeCommand','_procedure']

    for entry in inspect.stack(context=0):
        if entry[3] in functions:
            id_ = id(entry[0].f_locals['self'])

        if (id_ in self.__locked.keys()):


5. When the ``procedure`` function is done running, the ``Global_MeasureHandler`` will release all of the locked instruments associated with that ``ID(``

.. code-block:: python

      def release_current_user_instruments(self):
      '''
      Releases all current user instruments
      Should be called at the end of a test entity and NOT normally
      inside Measure functions
      '''
      owner_id = self._get_owner()

      with self.__access_lock:
          owned = self.__locked.get(owner_id)
          chain = self.__chainSets.get(owner_id)
          if owned is not None:
              self.__locked[owner_id] = []
          if chain is not None:
              self.__chainSets[owner_id] = ChainList()

Snapshot
--------

Code that executes the locking scheme from the ``Global_MeasureHandler``:
    - Note: ``_look_for_obj`` is just a convenience function that will return the first occurence of an element in a list, for which a lambda function, provided as an argument, returns true.

.. code-block:: python

      def get_instrument(self, specifiedDevice, additional=False):
      '''
      Finds and returns an unactive instrument corresponding to the one specified
      Returns None if such instrument was found/available.
      '''

      owner_id = self._get_owner() # This is where we get the ID

      # serialize access to global ownership dictionary
      with self.__access_lock:

          if not additional:
              # Try the owned instruments first
              owned_list = self.__locked.get(owner_id)
              sdebug('OwnedList<{}>: {}'.format(owner_id, owned_list))
              if owned_list != None:
                  found = _look_for_obj(owned_list, lambda x: x.whoAmI() == specifiedDevice)
                  if found != None:
                      return found

          # Then take a look for available instruments
          used = [inst for sub_l in self.__locked.values() for inst in sub_l]
          sdebug('used instruments: {}'.format(used))
          def isUnused(instrument):
              return instrument not in used and instrument.whoAmI() == specifiedDevice

          found = _look_for_obj(self.Stages.values(), isUnused)
          if found != None:
              self._lock_instrument(found, owner_id)
              # self._connect_to_chain(found, owner_id, fiber_id)
          return found

Diagram of the workflow
-----------------------
.. image:: ..\..\_static\locking_scheme.PNG
    :width: 701px
    :align: center
    :height: 572px
