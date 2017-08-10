Auto-Prober

### WINDOWS ###

Install Software before use

FTDI Driver
ffmpeg
python 2.7
    numpy
    opencv 3.1
    matplotlib
    pyserial
WDK 10 > devcon.exe    -    included in path system environment variable

Install:
pygtk-all-in-one-2.24.2.win32-py2.7.msi
from:
http://ftp.gnome.org/pub/GNOME/binaries/win32/pygtk/2.24/

### LINUX ###

For Phyton:
- install tkinter using sudo apt-get install python-tk
- Tkinter online reference: http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html

For  Virtual Com Port (VCP) Driver working:
- add your  usesr to dialout group - see /etc/groups
- the devices are /dev/ttyUSB*
- the device rights need to be changes : sudo chmod a+rw /dev/ttyUSB0

For Point Grey Camera:
- follow https://www.ptgrey.com/tan/10685


