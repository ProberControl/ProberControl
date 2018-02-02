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
