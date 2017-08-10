import visa

rm = visa.ResourceManager()

__name__ = "instruments"

__all__ = [
    'Polatis',
    'WT68145B',
    'Santec_TSL_210H',
    'RSY01',
    'Keithley2400',
    'HP8163A',
    'HP6624A',
    'AnritsuMS2667C',
    'AndoAQ4321',
    'Agilent34401A',
    'AEDFA_IL_23_B_FA',
    'Motor'
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
