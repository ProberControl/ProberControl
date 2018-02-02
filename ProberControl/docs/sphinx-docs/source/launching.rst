.. _launching-label:

Launching ProberControl
=======================

Graphical User Interface
------------------------
In order to launch the graphical user interface (GUI), navigate to the ``prober`` directory, then run ``ProberControl.py``. The command-prompt will open and you will begin getting reports of instruments being connected. If any instrument fails to connect, you will be notified in the terminal and can use the ``refresh`` button in the GUI to reconnect any instrument that has previously failed to connect.


Scripting
---------

You can also choose to run a script that you've defined in the ``config`` directory. See `How to write a measurement script <howto/measurementScript.html>`_ for details on writing the script. In order to run the script, you can execute ``ProberControl.py`` with 2 command line arguments. The first is the option ``-s`` or ``--script`` which are the same, followed by the file name associated with your measurement script in the ``config`` directory. In sum, the 2 possible full commands to execute are:

.. code-block:: python

    python ProberControl.py --script measurementScript.conf

.. code-block:: python

    python ProberControl.py -s measurementScript.conf
