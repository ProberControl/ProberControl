Adding a New Procedure
=======================

Overview
--------
When adding new higher level functionality to the software a new function inside an existing or a new procedure file should be written. 

Functions inside the procedure files should be written in an abstracted way so that they can be run independent of the exact models connected.

Requirements
------------
The finished procedure needs to be placed into the **prober/procedures** folder. Furthermore, the **__init__.py** file contains the list of all files inside the folder, which must be updated with the new driver.

Interaction with other objects 
------------------------------
All functions inside the procedures folder are made available to the GUI and the script controller using the Maitre. 

Procedure are pure functions. No classes are supported inside the procedure structure. Functions that are not supposed to be executed by the GUI or the scriptcontroller can be hidden with a leading underscore in their name e.g. def _helper()

The procedure functions can be recompiled during run time using the menu point **Refresh-> Refresh Procedures**

If procedure functions add stages and maitre to their input paramters ProberController passes automatically the stages Dictionary and the Maitre.

Functions can have direct access stages and equipment using the stages Dictionary. However, to make functions thread save the global measurement handler should be used.

To call procedures functions outside the current file the maitre should be used.
