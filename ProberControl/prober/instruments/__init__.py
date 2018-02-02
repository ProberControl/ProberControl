try:
    import visa
    rm = visa.ResourceManager()
except:
    pass



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
    'AndoAQ6317',
	'AragonBOSA400',
    'DSensor_ILD1420',
    'ELL8',
    'GonStage_KST_Z812B',
    'Rotator_CR1_Z7',
    'Rotator_ELL8',
    'Keithley2280S',
    'NewportPM500',
    'Agilent34401A',
    'AEDFA_IL_23_B_FA',
    'Motor_KST_ZST',
    'Motor_MST_DRV',
    'StepMotor_KST_ZST',
    'StepMotor_MST_DRV',
    'TL2500',
    'AgilentE3643A'
]

pipe_instrument_groups = {
    'Laser': [
        'Laser'
    ],
    'BoostAmp': [],
    'Modulator': [],
    'Polarization': [],
    'DUT': [
        'Fiber'
    ],
    'PreAmp': [],
    'SignalSink': []
}

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
