.. _DataIO:
DataIO
==============

The ``DataIO`` is a utility that provides functionality to control writing measurement results (in csv format) other output to files and reading data back from such output files. It handles the formatting of that output by parsing several data types.

**Interface:**
    The DataIO functionality is cleanly exposed by static methods contained in a single class called DataIO. Those functions are:

     - ``writeData(openFile, data, Data_Name=''):``
        This single function, given an open file object, can write data in that file (in csv) from diffrent data types: It can support single values, suck as *strings* or *numbers* as well as multi-dimensional lists consisted of those types. The function will flatten those lists to correctly output the measurement data in csv format.

     - ``get_test_names(path):``
        This function, given a path to an measuremnt results' file will parse it and retrieve the test names of the measurements included.

     - ``get_test_data(path, test_name):``
        This function will parse an retrieve the data of a specified test given the path to thhe file that it is output on.

Below we see an exmaple of DataIO functions used:

.. code-block:: python

    def _procedure(self, entry, file):
          '''executes experiments that use multiple tools or generalized algorythms'''
          args = self._prepArguments(entry)

          # Execute the function using maitre
          data = self.maitre.execute_func_name(entry['procedure'],entry['function'],args)

          # Write the results of the experiment to file
          DataIO.writeData(file, data, Data_Name=entry['measurement'])

As we see, the I/O code can become as small as a one-liner, making the code more readable, as the user does not need to take care of formatting or other pains of I/O.
