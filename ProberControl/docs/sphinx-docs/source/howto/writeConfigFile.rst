.. _writeConfigFile:
Writing a Configuration File
============================

Overview
--------
The purpose of the configuration file is to provide the user a place to indicate all of the tools that will be implemented in ProberControl.

Usage
-----

The ``ProberConfig.conf`` file uses the following syntax, which is similar for all configuration files of the ProberControl Software:

    1) Lines starting with ## at start and end define one instrument block.
    2) The following line defines the tool base type:
        a.    O – optical Stage
        b.    E – electrical Stage
        c.    C – Chip Stage
        d.    M – Measurement Tool
    3) Lines starting with a single followed by one character e.g. #O define properties of that tool
        a.    #O – Orientation of Stages (E/S/N/W) or exact model for Measurement Tools
        b.    #A – address for tools e.g. COM4 or GPIB0::24::INSTR
        c.    #X / #Y / #Z – info for x,y,z axis stepper motors for xyz stages
            a. The info should look like : ``Instrument Class; Address [; additional int args (';' separated)]``
            b. The first two arguments, ``Instrument class`` and ``Address`` must be provided, optionally followed by any other (integer) arguments that the constructor for that instrument takes
        d.    #A – angle deviations from perfect 90 setup
        e.    #R / #W /#E info for Chip Rotation Stage, East Gonio and West Gonio Controlers
            a. The info should look like : ``Instrument Class; Address [; additional int args (';' separated)]``
            b. The first two arguments, ``Instrument class`` and ``Address`` must be provided, optionally followed by any other (integer) arguments that the constructor for that instrument takes
        f.    #N -
            a. If multiple times the same device is present the #N parameter controls the index of the device e.g. #N 3 for a laser creates the object **MLaser3** in the ``Stages Dictionary``.
            b. If one device has multiple channels e.g. for a laser: 1:3 maps channel 3 to the object MLaser1. If a device has more than one port per channel mapping follows: 1:4.2 - to link the object MLaser1 to channel 4 port 2. Also see :ref:`Interface with a Multi-Channel Devic <interfaceMultiChannel>`.
            c. Multiple entries need to be separated by ;
        g.    #P - Ports corresponding to a switch, if a switch is present.
            a. A switch entry has the following syntax: ``3:15,16>7,8.`` the `3:` represents the 3rd entity of the device e.g. MLaser3 if the there is only one laser present it can be neglected.
            b. `15,16` represent the tools input ports at the switch. `7,8` are the prelimary output ports at the switch.
            c. Multiple entries need to be separated by ;
Examples
--------

`ProberConfig.py`::

    ## Object Type
    M
    #O Model
    AnritsuMS2667C
    #A Address
    GPIB0::23::INSTR
    #Numbering of Channels
    5:1;6:2.1;7:2.2
    #P Ports for switch
    5:10>7;6:11>8;7:12>1
    ##

    ## Object Type
    M
    #O Model
    Wiltron68145B
    #A Address
    GPIB0::7::INSTR
    ##

    ## Stage Identifier (E(lec) / O(ptic) / C(chip) / P(roximity) )
    E
    #O Orientation Identifier (N / E / S / W)
    S
    #X X-Axis interface
    StepMotor_MST_DRV; COM8; 1; 1
    #Y Y-Axis interface
    StepMotor_MST_DRV; COM5; 1; 2
    #Z Z-Axis interface
    StepMotor_KST_ZST; COM6
    #Angle Offset to ideal axis
    0.122
    ##

    ## Chip Stage
    C
    #O
    S
    #R
    Rotator_ELL8; COM3
    #W
    GonStage_KST_Z812B; COM4; 10
    #E
    EMPTY
    ##
