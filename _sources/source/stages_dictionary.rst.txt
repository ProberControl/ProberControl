Stages Dictionary
=================

The Stages Dictionary is the central object in the Prober Control Software. It acts as handler for all attached hardware. It is initialized in the main file: ``ProberControler.py``

The Stages Dictionary is build up based on the ``ProberConfig.conf`` file that needs to be present in the base directory. Please see :ref:`How to Write a Config File <writeConfigFile>` for usages and examples.

The main call of the program first calls ``read_config()`` to interpret the information in ``ProberConfig.conf`` and then passes a list of dictionaries to ``Generate_Stages(StageConfigList)`` to call the constructor of each connected device and the device to Stages Dictionary.

Tool Keys in the Stages Dictionary
==================================

All Keys belonging to connected stages are defined by two letters:

    1. Tool base type
    2. Orientation of the stage

For example, ‘EN’ for an electrical stage at the north edge of the chip stage. The chip stage is considered to have a south orientation and its key is ‘CS’.

Keys for measurement tools are handled differently. The first letter of each measurement tool is ‘M’. Its followed by a keyword defining the class of the tool. Current Tool classes are:
 
    1.    Laser
    2.    PowerMeter
    3.    OptAmp (Optical Amplifier)
    4.    DCSource
    5.    DCMeter
    6.    RFSource
    7.    RFMeter
 
This standardization into tool types allows higher functions to control tools independently of their exact model and driver specifications. 

The Stages Dictionary will be handed over to the GUI constructor and will be passed from the GUI to all functions needing the Stages Dictionary.
