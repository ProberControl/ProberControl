Maitre
======

The Maitre is an object that is initialized in the GUI constructor. It acts as handler for all functions inside the Procedure folder. At initialization the Maitre reads the ``__init__.py`` file in which all files, from here on called modules, need to be listed that are supposed to be available using the GUI. Afterwards the maitre imports all these modules and prepares:
    a) the ``mod_list`` containing all modules
    b) the 2 dimensional func_list containing all functions

The Maitre ignores all functions that start with a ‘_’ to enable the developer to write sub routines not available in the GUI. The Maitre has the following functions:

* ``get_all_modules``: Returns a list of all module names
* ``get_func_names(Mod_Index)``: Returns the names of all functions in the module defined by the mod_index. The index is defined by the position in the mod_list
* ``get_func_params(Mod_Index,Func_Index)``: Returns the function parameters of a function.
* ``execute_func(Mod_Index,Func_Index, Func_Params)``: executes a function based on indices
* ``execute_func_name(Mod_Name, Func_Name, Func_Params)``: executes a function based on names
* ``refresh()``: Recompiles and Reimports the entire Procedures folder. This functionality is very helpful for debugging the a new function.