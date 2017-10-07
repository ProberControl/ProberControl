.. _interfaceMultiChannel:
Interface with a Multi-Channel Device
=====================================

Interfacing with a multi-channel device is relatively straight forward as long as the instrument class is appropraitely structured. See `this page <addNewInstrument.html>`_ for examples of an instrument class. For multi channel devices the constructor needs to be initialized like :  __init__(self,res_manager,address='169.254.115.242',channel=1). The channel parameter will parsed as string following 'Channel.Port'. Port will be only present if denoted in the config file.

In your configuration file, be sure to fill in the appropriate section ``#Numbering of channels`` which is discussed `here <writeConfigFile.html>`_.

When you launch ``ProberControl`` you'll see that 2 devices are listed in the ``Stage Function to Exec``. You can treat both devices as two different instruments, if that helps you conceptualize the channels-- as that's how ProberControl sees them.

.. image:: .\..\..\_static\MultiChannelUsageExample.png
    :width: 350px
    :align: center
    :height: 500px
