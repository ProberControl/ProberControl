Plotter
=======

The plotter allows to print measurement results using ``matplotlib.pyplot``. It provides the class NBPlot that is decorated as a singleton, which means that it will be only initialized once and new initializations will refer to already existing object. NBPlot has two functions:
* ``plot(data,title,xaxis-title,yaxis-title)``: It allows plotting the measured data
* ``set_clear(clear)``: if set clear receives a ‘1’ every new data received will clean the chart before plotting the data, if set clear receives a ‘0’ data is added to the already existing charts.

Matplotlib is not thread save in order to allow a function to plot data while running multiprocessing is used. Splitting a program under windows means to run the entire code again until the split. Therefore, the first command line in ``ProberControl.py`` is the first initialization of the ``NBPlot()`` that split the program and starts one instance of ``ProcessPlotter()`` as a daemon with a pipe in between those two objects. ``rocessPlotter()`` enters a ‘while 1’ loop in ``__call__`` constantly checking whether new data is ready in the pipe.