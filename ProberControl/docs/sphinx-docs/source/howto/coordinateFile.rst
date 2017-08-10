Writing a Coordinate File
=========================

Structures on chip are defined by the 2 dimensional coordinates of the IO ports, no matter whether the ports are electrical or optical.

Each structure must be listed on the coordinates files a typical entry would be:

.. parsed-literal::
        ## Structure Name
        BSplit3
        #OW
        1.850477 1.513309
        #OE
        1.765477 1.19150
        ##

Each structure must be confined within a set of two ``##``. The Structure Name will be used to in ``ProberControl`` to refer to this structure. To define the stage for an optical stages oriented in the West a first line ``#OW`` is followed by the coordinates x and y. An electrical stage on the north would be defined as ``#EN``, etc. Although internally the ProberControl has dedicated coordinate systems for each stage (see figure) the coordinates file always refers to the chip coordinate system which is the same as a south oriented stage.

.. image:: ..\..\_static\coordinatePlanes.PNG
    :width: 450px
    :align: center
    :height: 500px

Note that the y axis is reversed compared to an intuitive coordinate system. When a structure is connected the software will try to fine align the optical probes. The default signal source is a connected powermeter. However, different sources can be defined using: 

.. parsed-literal::
        #SignalSource
        MDCSource

In this example a DC Source is used specifically its get_current() function, which is needed when a photodiode is coupled.
