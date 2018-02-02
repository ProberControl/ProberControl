Installation on Windows
============

1. Install Python 2.7.11
    * `Python Download Link <https://www.python.org/ftp/python/2.7.11/python-2.7.11.msi>`_ to Python 2.7.11 for Windows machines
    * When installing Python, be sure to choose to ``Add Python to path`` option.

.. image:: pythonPath.jpg
    :width: 400px
    :align: center
    :height: 250px

2. Install National Instruments driver, so you can interface with ``PyVisa``
    * `Driver Download Link <http://ftp.ni.com/support/softlib/gpib/Windows/3.1.2/ni488_312.exe>`_

3. If you don't have Visual C++ from Microsoft, you'll need to download that as well.
    * `Link <https://www.microsoft.com/en-us/download/confirmation.aspx?id=44266>`_

4. You'll likely have to restart your machine at this point.

5. Run ``install.bat``
    * Located in ``/ProberControl/setup``

6. Congratulations! You should be able to move over to ``/ProberControl/`` and run ``ProberControl.py`` which will launch the GUI for **ProberControl**


Installation MacOS
=========

1. Install X-Code
  * X-Code can be either installed from the App Store or from `here <https://itunes.apple.com/us/app/xcode/id497799835>`_

2. Install MacPorts
  * Follow installation instructions `here <https://guide.macports.org/#installing.macports>`_

3. Install native Python using MacPorts
  * open terminal
  * enter ``sudo port install python27``
  * set native python to standard python in path variable
  * enter ``sudo port select --set python python27``

4. Install native Pip using MacPorts
  * open terminal
  * enter ``sudo port install py27-pip``
  * set native pip to standard pip in path variable
  * enter ``sudo port select --set pip pip27``

5. Install complex python packages
  * open terminal
  * enter ``sudo port install py27-tkinter py27-numpy py27-matplotlib``

6. Install OpenCV
  * open terminal
  * enter ``sudo port install opencv +python27``

7. Install Xorg
  * open terminal
  * enter ``sudo port install xorg``
  * restart

8. Install standard python packages
  * open terminal
  * enter ``sudo pip install pyvisa pyserial tqdm``

9. Install USB to GPIB bridge if needed
  * for NI install `Module Driver <http://www.ni.com/download/ni-488.2-14.1/5090/en/>`_ and `Suite <http://www.ni.com/download/ni-488.2-15.5/5859/en/>`_
