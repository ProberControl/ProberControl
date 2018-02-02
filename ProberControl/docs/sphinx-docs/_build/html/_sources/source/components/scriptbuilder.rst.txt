.. _scriptbuilder-label:

ScriptBuilder GUI
============

.. image:: ../../_static/ScripBuilderGUI.PNG
    :height: 610px
    :width: 788px
    :align: center


---------------

The ScriptBuilder GUI helps constructing measurement scripts in accordance with the ProberControl syntax. The GUI is split into four fields and the menu:
   0. Menu: The menu features two cascades:

      0.1 The ``File`` cascade contains the load and save function for scripts.

      0.2 The ``Edit`` cascade contains the search and replace functionality for the loaded script.

   1.	Add Measurements: This field allows to add measurements with a specified names and the structures at which this measurement should be taken. The function that should be calles can be specified with two drop down menus that use the data found by the ``Maitre``. The arguments of this function are displayed in the next display field that can be defined in the lower entry field. Finally hitting the AddMeasurements Button writes the corresponding code into the editor at the current place of the ``Cursor``. This allows to inject measurements at any points in the script or without changing the cursor position to keep adding new measurements.


    2.	The ‘Add Block’ field allows the creation of measurement blocks as mentioned in the scripting description. To do that the block type needs to be specified (wafer, chip, group) and the name of the block (i.e. identifier of this wafer / chip if applicable). If desired a local binning function can be defined for this block making again use of the drop down menus filled with the entries from the ``Maitre``
    If the option ``Copy Measurements from previous Block`` is selected and the ``AddBlock`` Button is used, the ScriptBuilder will copy all measurements from the previous block into this block while changing all occurrences of the previous block name to the current block name. This is helpful when the same set of tests should be applied to different wafers or chips. Again the ``AddBlock`` Button will insert the new code at the position of the cursor.

   3.	The block ‘Global Settings’ allows to set global binning functions used for all blocks. It also lets the user specify at which group level (wafer, chip, group) files should be written using the ``Group By`` drop down menu. Hitting the Update Button will always only change the header of the script.

   4.	The script is being constructed in the right half of the GUI. The script can be manually adapted directly in the GUI.
