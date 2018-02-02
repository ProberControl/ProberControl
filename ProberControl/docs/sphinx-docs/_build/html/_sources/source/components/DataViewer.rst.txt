DataViewer
==============

The ``DataViewer`` is a component of the ProberControl GUI, which enables the user to visualize data from current or older measurements. A preview of the *DataViewer* window is shown below:

.. image:: ../../_static/DataViewer.png
    :height: 524px
    :width: 680px
    :align: center


The GUI is pretty straightforward to use:
    - We first browse the file containing the results we want to display and load it
    - Then we can choose which specific test to load from that file
    - Using the ``Back`` and ``Next`` buttons we can traverse through all the tests in the selected file.

The **DataViewer** uses :ref:`DataIO <DataIO>`  in the back-end. So it can handle test data in the form of multi dimensional lists. If the dimensions exceed 4, only the first 2 are used to plot x, y on the DataViewer.
