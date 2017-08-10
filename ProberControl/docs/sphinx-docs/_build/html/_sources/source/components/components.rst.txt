Classes vs. Procedures vs. Instruments
======================================

The Software is split into 3 main folders or parts: Classes, Procedures and Instrument Control Classes. These 3 folders can be found in the ProbeLib Folder that must reside in the root folder.

* Classes: The Classes folders contains all files that deliver core functionality to the software. All core functions are handled as objects, e.g. the GUI, the DataViewer, the plotter, the maître or the motor class.

* Instruments: All measurement tools connected to the prober controller need to have a ‘python’ driver. The folder contains another folder for each supported device, usually named like ``[Brand][ExactModel]``. Inside the model folder needs to be the python file containing the class for this model. Depending on the tools class (e.g. Laser, see classes above) the class needs to contain a subset of functions, e.g. for the Laser setwavelength, setpower, etc. Those can be checked in the UML file in the Documentation folder. Those standardization of function names allows any higher hierarchical function to act independent of the exactly connected device. For example, any lasers wavelength can be changed by: ``Stages[‘MLaser’].setwavelength([NEW_WAVELENGTH])``

* Procedures: The procedure folder contains all files relating to higher hierarchical tasks like performing measurements, coordinating the movements of the stage, calibrating stages and chips. The functions are usually grouped in files by tasks, most important files are: Measure.py , Connecting.py. Most functionality extensions should be done in this folder by adding new files.