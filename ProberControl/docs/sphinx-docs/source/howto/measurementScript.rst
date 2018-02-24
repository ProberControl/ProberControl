.. _measScriptLabel:
Write and Execute a Measurement Script
======================================

Measurement scripts are used to automate experiments that may take a long time. There are two ways to run measurement scripts. They can be run via the command line or they can be launched over the graphical user interface (GUI).

Running Scripts
---------------

Interfacing through the GUI allows you to locate the script to run via a navigation window. After choosing your script to be ran, use the ``Execute Script`` button to begin the script. You'll see a progress bar launched in the command-prompt window. The results will be written to a file ``results.csv`` in the ``config`` directory.

You can also run the script via the command line which is described in :ref:`launching-label`.

.. note::
    If you run a script, you can continue to interface with your ProberControl system. The instruments that are locked for the duration of the script will not be available to you until the script is finished, so you shouldn't worry about collisions between devices.

.. image:: ..\..\_static\scripting.PNG
    :width: 450px
    :align: center
    :height: 500px

Writing Scripts
---------------

Writing a measurement script is similar to writing a configuration file. We use the same notation, relying on the ``#`` symbol to designate certain features and a new line defining the beginning and end of an information block. For any experiment or execution of function, you'll need to write an information block.
.. note::
    Blocks of information are separated by a new line

Measurement Blocks
--------
* The ``Measurement Name`` field is whatever you would like to name it.
* The ``Structure`` field is defined in the coordinates file that you've written already.
* the ``procedure`` field refers to a ``.py`` file that you've written and placed in the procedures directory.
* The ``function`` field refers to the function in the procedures file that you've defined and wish to utilize
* The ``Arguments`` field refers to the arguments, if any, for the function you wish to utilize. If there are no arguments, write ``none`` before the arguments field.

.. parsed-literal::
        #Measurement Name
        Test_PhaseShifter_Spec
        #Structure
        phaseshift_cell_brian
        #procedure
        Measure
        #Function
        get_e_spectrum
        #Arguments
        10 300 10 0.1

        #Measurement Name
        Test_Ring_Bot_Res_Shift
        #Structure
        ring_bot
        #procedure
        Measure
        #Function
        dc_sweep_1d
        #Arguments
        none

Output Configuration
--------------------
By default all the measurements' results are output to one file, ``results.csv``. However, the tests specified in one .meas script can span multiple device groups, chips or wafers. The author of the measurement script can, therefore, classify the various information blocks into any of the following identifiers: ``wafer``, ``chip`` and ``group``, each one enclosing the next, from left to right.

The author need not specify all the identifiers for every block, but once one of those identifiers are used, every block should fall under a group denoted by this identifier. Here's is how we can use the grouping identifiers in the example provided above:

.. parsed-literal::
        group-by: group

        > chip
        OurOnlyChip

        > group
        PhaseShifters

        #Measurement Name
        Test_PhaseShifter_Spec
        #Structure
        phaseshift_cell_brian
        #procedure
        Measure
        #Function
        get_e_spectrum
        #Arguments
        10 300 10 0.1

        > group
        Rings

        #Measurement Name
        Test_Ring_Bot_Res_Shift
        #Structure
        ring_bot
        #procedure
        Measure
        #Function
        dc_sweep_1d
        #Arguments
        none

The scope of the identifiers lasts up until the next identifier of the same type is identified. That means that both measurements fall under ``chip`` OurOnlyChip, but each one in different groups, ``PhaseShifters`` and ``Rings`` respectively.
The purpose of grouping identifiers is to configure how the output will be distributed into files. The output ordering is determined by the optional first line in the measurement script:

.. parsed-literal::
        group-by: group

In this example, where we partition by ``group`` two files will be output with names ``results-PhaseShifters.csv`` and ``results-Rings.csv``, containing the respective measurement results.

Binning Configuration
----------------------
It is possible to pass all information gathered / measured to a binning function to evaluate the device or sort it into groups by any parameters. Binning functions need to be prepared in the procedures folder. Examples can be found in prober/procedures/Binning.py.

The binning function needs to accept exactly one argument that will be a list with the first argument being the device ID (defined under either ``> wafer`` or ``> chip``) followed by file paths for all files in which information about the device was written. The binning function should return a ``str`` object to classify the device.

The default binning function is defined at the head of the measurement file:
.. parsed-literal::
        bin-by: Binning:FuncA

where ``Binning`` refers to the Binning.py file in the procedures folder (any other file in the procedure folder can be specified and used) and ``FuncA`` refers to one function inside the file.

Block wide binning function can be defined with
.. parsed-literal::
        > bin
        Binning:FuncB

A block ends with the call of the binning function, which is executed when the wafer or chip parameter changes, see Output Configuration. Note that if a wafer group is declared only wafer parameter changes trigger binning functions. If no wafer parameter is present the changes of the chip parameters trigger the call of the binning function. If neither is present, the binning function won't be triggered.

Trigger function are only called if either a default or local binning function was declared.

Chip Storing
----------------------
If a binning function was called on a chip parameter change and a MProber is present in the stages dictionary, the result of the binning function is used to determine the storing container for the device.

This is done by querying a database or file in which binning groups are related to IDs of containers. The device ID and the container ID are then send to the MProber to store the device.

Graphically Aided Script Compiling
----------------------
In the ``Scripts`` menu the :ref:`scriptbuilder-label` can be opened. The GUI based editor helps with the creation of measurement scripts.
