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
        c.    #X / #Y / #Z – address of x,y,z axis controller for xyz stages
        d.    #A – angle deviations from perfect 90 setup
        e.    #R / #W /#E address of Chip Rotation Stage, East Gonio and West Gonio Controlers
        f.  #N - Number of channels for a particular laser e.g. ``1,2,3,4`` for a channel occupying channels 1-4
        g.    #P Ports corresponding to a switch, if a switch is present.
            a. A switch entry has the following sytax: ``1,2,3::17,18,19`` where `(1,17)`, `(2,18)`, and `(3,19)` are port-to-port connections in the switch.
            b. All input/ingress ports must be between 1-16 inclusive, then output ports 17-32 inclusive.

Examples
--------

`ProberConfig.py`::

    ## Object Type
    M
    #O Model
    AnritsuMS2667C
    #A Address
    GPIB0::23::INSTR
    #Number of Channels
    5,6,7,8
    ##

    ## Object Type
    M
    #O Model
    Wiltron68145B
    #A Address
    GPIB0::7::INSTR
    #P Ports for switch
    5,6,7::21,22,23
    ##

    ## Stage Identifier (E(lec) / O(ptic) / C(chip) / P(roximity) )
    E
    #O Orientation Identifier (N / E / S / W)
    S
    #X X-Axis interface
    COM8
    #Y Y-Axis interface
    COM5
    #Z Z-Axis interface
    COM6
    #Angle Offset to ideal axis
    0.122
    ##

    ## Tunable Laser
    C
    #O
    S
    #R
    COM3
    #W
    EMPTY
    #E
    EMPTY
    ##