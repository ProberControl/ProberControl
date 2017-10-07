import matplotlib
from imp import find_module
matplotlib.use('gtkagg')

def _check_cv2():
    try:
        find_module('cv2')
        return True
    except ImportError:
        return False

installed = _check_cv2()

if not installed:
    __all__ = [
        'connecting',
        'fine_allign',
        'Measure',
        'raster',
    ]
else:
    __all__ = [
        'connecting',
        'fine_allign',
        'Measure',
        'raster',
		'vision'
    ]
'''
Copyright (C) 2017  Robert Polster
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
