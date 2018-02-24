ScriptController
==============

The **ScriptController** is a piece of the core of the ProberControl Software that is responsible for ``parsing``, ``scheduling`` and ``running`` the user-defined test recipies (.meas scripts)
The functionality of ScriptController can be summarized in the following points:

    1. Every time a new measuremnt script (or instance of a script) is ran from the GUI, a new instance of the ScriptController is instantiated. This design helps encapsulate the functionalty of the class in a way that allows for easy and straightforward parallelization of the test script execution.
    2. The process of a single ``ScriptController`` can be split into two parts:
      - The ``reading/parsing`` part ( read_script() ). Here the .meas script is read and the different measurements are parsed into structures that allow for the retrieval of the functions we need to execute to make a specific measurement, as well as the user specified parameters. This portion of code also sets label to the measurements, which will later be used to output the results in the correct file.
      - The ``execution`` part ( execute_script() ). as the name explains this is were the test recipies are actually run. The process will iterate through the test structures parsed in the reading section and for each one, the specified measure function will be executed. After each structures is done, the *ScriptController* will release the locks on the instruments used within the specified functions (acquired by the `Global_MeasureHandler <measure_handler.rst>`_) before executing the next one. The results of each measurement will also be output as each one finishes to avoid having to redo all the work if a failure occurs mid-test.
    3. The remaining functions in the ``ScriptController`` class are helpers for parsing and executing as well as an internal class used to define the structures for grouping the different measurements.

    The picture below shows the workflow followed by .meas script until its execution:

.. image:: ../../_static/proceduresWorkflow.png
    :height: 400px
    :width: 1600px
    :align: center

Data Output of ScriptController
-------------------------------
Results are saved in the ``config`` folder, as defined in the ``__configurePaths()`` function. Name and subfolders are currently hard coded in the ``execute_script()`` function by the line ``with self._OutputConfiguration(...) as out:``.

As described in :ref:`Measurement Script HowTo <measScriptLabel>` the output can be split into different files depending on the grouping in the measurement script. Files are either created on wafer, chip , or group level. File names are then appended by the wafer/chip/group label given in the script.

Decision on where data is saved is taken in the ``_OutputConfiguration`` class. If new features and options need to be implemented they should augment the function set of ``_OutputConfiguration``.


Wafer and Chip Prober Interaction Scheme of ScriptController
------------------------------------------------------------
All interactions between the ScriptController and a self contained prober are triggered  in the ``execute_script()`` function. They are on four levels:

  0. Checking Health of the Prober:
      Before loading the first Device under Test (DUT) the function ``_checkProberState()`` is called. The function relies on the prober driver to implement a ``get_state()`` function and handles according to its return values.

  1. DUT Loading:
      The ScriptController checks whether a new ``chip-block`` starts. If yes, the ScriptController calls the function ``_loadChip``, which relies again on the prober driver. The ScriptController only sense chip loading commands, even if the chip is still part of a wafer. The automated prober is assumed to handle loading of chips based on their ID. This means that a chipID is provided to the prober driver and it is assumed that the prober initiates everything necessary to load this device. This might include fetching the location of this device from an external or internal database , checking whether this chipID is in wafer shape or chip shape and reference all future commands to this chipID.
  2. Structure Connections:
      Every measurement block contains (if used in connection with a wafer or chip prober) a structureID. For every measurement the function ``_structureProcedure()`` is called that calls the driver's ``connect_structure()`` function. If a fiber switch is used to control light in and output, it is ensured that a the tools light source and sink is connected to the correct fiber.
  3. DUT Storing:
    a. binnning:
      If defined in the Measurement Script a binning function is called at the end of blocks of the hierarchically highest group. That means if waver groups are present then at the end of each wafer, if wafers are not present then at the end of each chip block. Binning functions are called in ``_callBinningFunction()`` using the Maitre and can be freely programmed in the procedures folder. Every binning function is supplied with:
        1. The last measurement-details, which include the waferID, chipID, groupID
        2. All file names in which measurement results were saved.
      The binning function should return a keyword (e.g. good / bad). The function ``_storeBinningResult()`` saves the result. Wafers are assumed to be placed back into the FOUP either when the next wafer is loaded or at the end of the script. If the DUT is in chip shape ``_storeDie()`` is called.
    b. _storeDie:
      ``_storeDie(itemID, binningResult)`` accepts the itemID and binningResult as parameters. The function calls ``_getContainer()`` to make a decision on where to store this die based on the binningResult. Afterwards it makes use of the Prober Driver's ``store_chip(container)`` to store the chip.
