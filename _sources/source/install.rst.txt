Installation
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

3. Install PyGTK
    * `PyGTK Download Link <http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/pygtk-all-in-one-2.24.0.win32-py2.7.msi>`_

4. If you don't have Visual C++ from Microsoft, you'll need to download that as well. 
    * `Link <https://www.microsoft.com/en-us/download/confirmation.aspx?id=44266>`_

5. You'll likely have to restart your machine at this point.

6. Run ``install.bat``
    * Located in ``/ProberControl/setup``

7. Congratulations! You should be able to move over to ``/ProberControl/prober/`` and run ``ProberControl.py`` which will launch the GUI for **ProberControl**