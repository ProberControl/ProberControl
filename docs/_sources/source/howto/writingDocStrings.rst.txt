Write a Doc-String
==================

Overview
--------

A doc-string appears below every function header and indicates the following:
    1) What, how, and why the function does
    2) Parameters and their types
    3) Any Exceptions the function may raise
    4) The return type and expected value
    5) Usage Example

The doc-string is important for several reasons. It is not up to the reader of source code to figure out the logic, implementation, reasoning, and usage of any given function. The designer should provide insights into the function's attributes and usage by using a doc-string and appropriate comments.

There are a few of conventions any doc-string in ProberControl will follow:
    1) Use the syntax for the following:
        a. ``:param YourNameHere:`` Description of parameter
        b. ``:type YourNameHere:`` Data type of parameter
        c. ``:returns: ...`` The expected value and data type returned by a function
        d. ``:raises: ...`` Any exceptions this function may raise

Doc-strings are strictly indicated by the triple single quotes: ``'''Doc-String'''``

Examples
--------

.. code-block:: python

    def get_voltage(self,scaled=False,query_range=10,resolution=0.01):
        '''
        Queries the voltage of multimeter.
        
        :param scaled: Optional scaling
        :type scaled: Boolean
        :param query_range: range for query
        :type query_range: Integer
        :param resolution: resolution for query
        :type resolution: Float
        :returns: current voltage reading as float
        '''

        val = float(self.gpib.query('MEAS:VOLT:DC?)
        return val

.. code-block:: python

    def __cmd_handler(self, command, query=False):
        '''
        Handles exceptions for raw_function()

        :param command: takes a single command as String
        :type command: String
        :param query: if command is a query, then True. Defaults to False.
        :type query: Boolean
        :returns: a reply if query as String
        :raises: Exception, VisaTimeoutError
        '''
        
        if query: # expects a reply
            try:
                return self._switch.query(item)
            except Exception as e:
                return e
        else: # expects no reply
            try:
                self._switch.write(command)
            except Exception as e:
                return e
