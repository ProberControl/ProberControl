Write and Execute a Measurement Script
======================================

Measurement scripts are used to automate experiments that may take a long time. There are two ways to run measurement scripts. They can be run via the command line or they can be launched over the graphical user interface (GUI).

Running Scripts
---------------

Interfacing through the GUI allows you to locate the script to run via a navigation window. After choosing your script to be ran, use the ``Execute Script`` button to begin the script. You'll see a progress bar launched in the command-prompt window. The results will be written to a file ``results.csv`` in the ``config`` directory.

You can also run the script via the command line which is described `here </launching.html>`_.

.. note::
    If you run a script, you can continue to interface with your ProberControl system. The instruments that are locked for the duration of the script will not be available to you until the script is finished, so you shouldn't worry about collisions between devices.

.. image:: ..\..\_static\scripting.PNG
    :width: 450px
    :align: center
    :height: 500px

Writing Scripts
---------------

Writing a measuremeant script is similiar to writing a configuration file. We use the same notation, relying on the ``#`` symbol to designate certain features and a new line defining the beginning and end of an information block. For any experiment or execution of function, you'll need to write an information block. The ``direct`` and ``indirect`` information blocks are defined below. 

There are two kinds of interactions that you can have when scripting. You can either interface with an instrument directly, i.e. telling a laser to have a certain wavelength or you can interface with an entire structure that you've defined in a coordinates file. You can find an example of a each in the ``templates`` folder. You can also mix these two types of interactions into one script. The defining difference is that your structure scripting will utilize methods that you've defined and placed into the ``procedures`` folder, whereas the stages interface allows you to refer to an instrument directly. We'll refer to them as ``direct`` and ``indirect``.

.. note::
    Blocks of information are seperated by a new line

Direct
------
* The ``stage`` field refers to the instrument stage name, ie ``Laser`` or ``DCSource`` that you've defined in the instrument class under the function ``whoAmI()``.
* The ``function`` field refers to the function of the instrument you wish to utilize.
* The ``Arguments`` field refers to the arguments, if any, for the function you wish to utilize. If there are no arguments, write ``none`` before the arguments field.
* The ``lock`` field is optional and you can use it to lock an instrument for the time that the script it running. If you lock an instrument, it will not appear in the ``Stages to Execute`` option menu in the GUI. then when the script is finished, the previously locked instrument will reappear in stages menu again.

.. parsed-literal::
        #Stage
        MPowerMeter
        #function
        get_power
        #arguments
        none
        #lock
        true

Indirect
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
        