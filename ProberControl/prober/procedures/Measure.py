import numpy as np
import math
import time
import connecting

# Getting an instance of the Global_MeasureHandler singleton object
from Global_MeasureHandler import Global_MeasureHandler as g
if g.instance != None:
    gh = g.instance

def set_clear_plot(clear):
    pl = plotter.NBPlot()
    pl.set_clear(clear)

def get_o_power(stages,maitre,wavelength=1550,sweeping=False,result_path=0):
    if 'MLaser' in stages and sweeping == False:
        wavelength = gh.call_function('laser','getwavelength')
        #wavelength = stages['MLaser'].getwavelength() direct access alternative

    data = float(gh.call_function('PowerMeter'), 'get_power', float(wavelength))
    # data = float(stages['MPowerMeter'].get_power(float(wavelength), channel)) direct access alternative
    
    
    if result_path != 0:
        _write_data(data,result_path)

    return data

def get_current(stages, maitre):
    return gh.call_function('DCMeter', 'get_current')
    # return stages['MDCMeter'].get_current()

def get_o_spectrum(stages, maitre,start,stop,step,result_path=0):

    init_wavelength = float(gh.call_function('laser','getwavelength'))
    # init_wavelength=float(stages['MLaser'].getwavelength()) direct access alternative 

    gh.call_function('laser','sweepWavelengthsTriggerSetup', [float(start),float(stop),float(step)])
    # stages['MLaser'].sweepWavelengthsTriggerSetup(float(start),float(stop),float(step)) direct access alternative
    
    DataList = []

    for x in np.arange(float(start),float(stop)+float(step),float(step)):
        gh.call_function('laser','trigger')
        # stages['MLaser'].trigger() direct access alternative
        DataList.append([x,get_o_power(stages,maitre,x,True)])        

    gh.call_function('laser','setwavelength',init_wavelength)
    gh.call_function('power','get_power',init_wavelength)

    #stages['MLaser'].setwavelength(init_wavelength) direct access alternative
    #stages['MPowerMeter'].get_power(init_wavelength,channel) direct access alternative; channel deprecated
                
    pl = plotter.NBPlot()
    pl.plot(
        DataList,
        'Optical Spectrum',
        'Wavelengt [nm]',
        'Measured Power [dB]'
        )
    
    if result_path != 0:
        _write_data(DataList,result_path)

    return DataList

def _thresh_wavelength(stages, maitre,start,stop,step,thresh=-60,result_path=0):

    gh.call_function('laser','sweepWavelengthsTriggerSetup', [float(start),float(stop),float(step)])
    # stages['MLaser'].sweepWavelengthsTriggerSetup(float(start),float(stop),float(step))
    
    DataList = []

    for x in np.arange(float(start),float(stop)+float(step),float(step)):
        gh.call_function('laser','trigger')
        # stages['MLaser'].trigger() direct access alternative
        power = get_o_power(stages,maitre,x,True)
        DataList.append([x,get_o_power(stages,maitre,x,True)])       
        if power > thresh:
            return DataList
    
    return DataList

def get_e_spectrum(stages,maitre,start=1,stop=1000,step=10,power=0.1,result_path=0):
    
    gh.call_function('RFSource','set_power',[float(power)])
    gh.call_function('RFSource','sweepTriggerSetup',[float(start),float(stop),float(step)])
    gh.call_function('RFSource','out_on')

    # stages['MRFSource'].set_power(float(power)) direct access alternative
    # stages['MRFSource'].sweepTriggerSetup(float(start),float(stop),float(step)) direct access alternative
    # stages['MRFSource'].out_on() direct access alternative

    DataList = []

    for x in np.arange(float(start),float(stop)+float(step),float(step)):
        rfval = gh.call_function('RFMeter','getPeak',[x,5])[1]
        # rfval  = stages['MRFMeter'].getPeak(x,5)[1] direct access alternative
        optval = get_o_power(stages,maitre)
        print(x,rfval,optval)
        DataList.append([x,rfval-optval])
        gh.call_function('RFSource','trigger')
        # stages['MRFSource'].trigger() direct access alternative
    
    rfval = gh.call_function('RFMeter','getPeak',[x,5])[1]
    # rfval  = stages['MRFMeter'].getPeak(x,5)[1] direct access alternative
    optval = get_o_power(stages,maitre)
    
    print(x,rfval,optval)
    
    DataList.append([x,rfval-optval])
    
    gh.call_function('RFSource','out_off')
    # stages['MRFSource'].out_off()
    
    pl = plotter.NBPlot()
    pl.plot(
        DataList,
        'Electrical Spectrum',
        'Frequency Input Signal [MHz]',
        'Measured Power [??]'
        )

    data = DataList

    
    if result_path != 0:
        _write_data(data,result_path)

    return data

def get_VI_curve(stages,maitre,channel=1,start = 0, stop = 1, step = 0.1,result_path=0):
    dc_sweep_1d(stages, maitre,channel,start,stop,step,'get_current','',result_path)
    
def dc_power_sweep(stages, maitre,start=0,stop=1,step=0.1,result_path=0):
        
    DataList = []
    
    gh.call_function('DCSource','save_state')
    # stages['MDCSource'].save_state() direct access alternative

    gh.call_function('DCSource','setvoltage',float(start))
    # stages['MDCSource'].setvoltage(float(start)) direct access alternative 

    gh.call_function('DCSource','setOutputSwitch',1)
    #stages['MDCSource'].setOutputSwitch(1)


    for x in np.arange(float(start),float(stop)+float(step),float(step)):
        gh.call_function('DCSource','setvoltage',x)
        # stages['MDCSource'].setvoltage(x)
        time.sleep(0.1)
        DataList.append([x,get_o_power(stages,maitre)])

    gh.call_function('DCSource','recall_state')
    # stages['MDCSource'].recall_state() direct access alternative

    pl = plotter.NBPlot()
    pl.plot(
        DataList,
        'Optical Power dep on Bias',
        'Bias Voltage [V]',
        'Measured Power [dBm]'
    )

    
    if result_path != 0:
        _write_data(DataList,result_path)

    return data
    
def dc_sweep_1d(stages, maitre,start=0,stop=1,step=0.1,func=False,args=False,result_path=0):
        
    DataList = []
    
    gh.call_function('DCSource','save_state')
    # stages['MDCSource'].save_state() direct access alternative

    gh.call_function('DCSource','setvoltage',float(start))
    gh.call_function('DCSource','setOutputSwitch',1)
    # stages['MDCSource'].setvoltage(float(start)) direct access alternative
    # stages['MDCSource'].setOutputSwitch(1) direct access alternative


    for x in np.arange(float(start),float(stop)+float(step),float(step)):

        gh.call_function('DCSource','setvoltage',x)
        # stages['MDCSource'].setvoltage(x)  direct access alternative
        time.sleep(0.1)
        arglist = [stages,maitre]
        for elem in args:
            arglist.append(elem)
        data = maitre.execute_func_name('Measure',func,arglist)

        DataList.append([x,data])
    
    if isinstance(DataList[0][1], int) or isinstance(DataList[0][1], float):
        pl = plotter.NBPlot()
        pl.plot(
            DataList,
            'DC Voltage Sweep',
            'Bias Voltage [V]',
            func
        )
        
    stages['MDCSource'].recall_state()

    if result_path != 0:
        _write_data(DataList,result_path)

    return data

def find_depl_MZI_bias(stages, maitre,channel=0,max_volt=5):
    
     dc_data=dc_power_sweep(stages,maitre,channel,0,max_volt,50)

     # Add plotting of data

     trans=zip(*dc_data)

     max_o = max(trans[1])
     min_o = min(trans[1])

     max_ind = trans[1].index(max_o)
     min_ind = trans[1].index(min_o)

     max_dc = dc_data[max_ind][0]
     min_dc = dc_data[min_ind][0]

     opt_volt = (max_dc-min_dc)/2 + min_dc
     max_swing = max_dc-min_dc
     ext_ratio = max_o/min_o
     max_o_power = max_o

     return ('Biasing V',opt_volt,'Max Vsignalpp',max_swing,'Extinction Ratio',ext_ratio,'Max Opt Output',max_o_power)

def carac_MZI(stages, maitre, dc_sig1_chan,max_volt=5,result_path=0):
    # Set optimal bias
    # Get Vpi
    # Get Extinction Ratio
    # Get Loss

    dc_data = find_depl_MZI_bias(stages, maitre,dc_sig1_chan,max_volt)

    # Get e bandwidth
    gh.call_function('DCSource','setvoltage',[dc_data[0],dc_sig1_chan])
    gh.call_function('DCSource','setOutputSwitch',[1,dc_sig1_chan])
    # stages['MDCSource'].setvoltage(dc_data[0],dc_sig1_chan) direct access alternative
    # stages['MDCSource'].setOutputSwitch(1,dc_sig1_chan) direct access alternative

    best_power = 10 * math.log10((0.354*dc_data[1])**2/50/0.001)

    rf_data = get_e_bandwidth(stages, maitre,0.5,20,100,best_power)

    dc_data.append(['RF_Spectrum',rf_data])

    data = dc_data


    if result_path != 0:
        _write_data(data,result_path)

    return data


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
