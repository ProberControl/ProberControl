import numpy as np
import math
import time
from . import connecting
from ..classes.plotter import NBPlot
from ..classes.DataIO import DataIO

# Getting an instance of the Global_MeasureHandler singleton object
from ..classes.Global_MeasureHandler import Global_MeasureHandler as g
# Getting Global_MeasureHandler (singleton)instance; Do not change this!
gh = g()

def test(maitre,data):
    pl = NBPlot()
    data = [data,data,data]
    DataList = [[[1,1,1],data,data],[[2,2,2],data,data],[[3,3,3],data,data],[[4,4,4],data,data]]
    pl.plot(DataList,'Optical Spectrum','Wavelength [nm]','Measured Power [dB]')


    DataIO.writeData('NextTest.txt', DataList, Data_Name='')
    return DataList


def get_o_power(maitre,wavelength=1550,sweeping=False,result_path=0):
    laser = gh.get_instrument('Laser', additional=False)
    print("laser "+str(laser))
    if laser is not None:
        wavelength = laser.getwavelength()

    pm = gh.get_instrument('PowerMeter')
    print("PM "+str(pm))
    gh.connect_instruments(laser, pm)
    data = pm.get_power(float(wavelength))
    print(data)

    if result_path != 0:
        DataIO.writeData(result_path,data,'get_o_power')

    return data

def get_o_spectrum_OSA(maitre,start, stop, step, result_path = 0):

    DataList = []
    osa = gh.get_instrument('OSA')
    DataList = osa.get_o_spectrum(start, stop, step, result_path)

    pl = NBPlot()
    pl.plot(DataList,'Optical Spectrum','Wavelength [nm]','Measured Power [dB]')

    return DataList

def get_o_spectrum_PowerMeter(maitre,start, stop, step, channels, result_path = 0):

    start = float(start)
    stop = float(stop)
    step = float(step)

    channels = int(channels)

    sweepWidth = stop-start
    sampleNumber = sweepWidth/(step) + 1

    pms = []
    for i in range(channels):
        pm = gh.get_instrument('PowerMeter', additional=True)
        pm.config_meter(-30)
        pm.prep_measure_on_trigger(sampleNumber)
        pms.append(pm)



    t0 = time.time()
    osa = gh.get_instrument('OSA')
    OSAData = osa.get_o_spectrum(start, stop, step)

    time.sleep(3)

    AllDataList = [OSAData]
    for i in range(channels):
    	PowerList = pms[i].get_result_from_log(sampleNumber)

    	DataList =[]

    	for j in range(len(PowerList)):
    		if (PowerList[j] < 100 and PowerList[j] > 0):
    			power  = 10*math.log10(PowerList[j]/0.001)
    			#if (power < -70):
    			#	DataList.append([start+j*step, -70])
    			#else:
    			DataList.append([start+j*step, power])
    		#DataList.append([start+j*step, PowerList[j]])
    	pl = NBPlot()
    	pl.plot(DataList,'Optical Spectrum for Channel ' + str(i),'Wavelength [nm]','Measured Power [dBm]')

    	AllDataList.append(DataList)

    #pl.plot(OSAData,'Optical Spectrum for OSA', 'Wavelength [nm]','Measured Power [dBm]')

    if result_path != 0:

    	_write_data(OSAData,str(result_path)+'_OSA.txt')
    	for i in range(len(AllDataList)):
    		_write_data(AllDataList[i],str(result_path)+'_PM'+str(i)+'.txt')


    return AllDataList

def get_current(maitre):
    dc = gh.get_instrument('DCSource')
    data = dc.get_current()
    return data

def get_o_spectrum(maitre,start,stop,step,result_path=0):

    laser = gh.get_instrument('Laser')
    pm = gh.get_instrument_triggered_by(laser, 'PowerMeter')

    init_wavelength = float(laser.getwavelength())

    laser.sweepWavelengthsTriggerSetup(float(start),float(stop),float(step))

    DataList = []

    for x in np.arange(float(start),float(stop)+float(step),float(step)):
        laser.trigger()
        DataList.append([x,pm.get_o_power(x,True)])


    laser.setwavelength(init_wavelength)
    pm.get_power(init_wavelength,channel)

    pl =  NBPlot()
    pl.plot(
        DataList,
        'Optical Spectrum',
        'Wavelengt [nm]',
        'Measured Power [dB]'
        )

    if result_path != 0:
        DataIO.writeData(result_path,DataList,'get_o_spectrum')

    return DataList

def _thresh_wavelength(maitre,start,stop,step,thresh=-60,result_path=0):

    laser = gh.get_instrument('Laser')
    laser.sweepWavelengthsTriggerSetup(float(start),float(stop),float(step))
    pm = gh.get_instrument_triggered_by(laser, 'PowerMeter', additional=False)

    DataList = []

    for x in np.arange(float(start),float(stop)+float(step),float(step)):
        stages['MLaser'].trigger()
        power = get_o_power(x,True)
        DataList.append([x,get_o_power(x,True)])
        if power > thresh:
            return DataList

    return DataList

def get_e_spectrum(maitre,start=1,stop=1000,step=10,power=0.1,result_path=0):
    rf = gh.get_instrument('RFSource')
    rf.set_power(float(power))
    rf.sweepTriggerSetup(float(start),float(stop),float(step))
    rf.out_on()

    rf_meter = gh.get_instrument('RFMeter')

    DataList = []

    for x in np.arange(float(start),float(stop)+float(step),float(step)):
        rfval  = rf_meter.getPeak(x,5)[1]
        optval = get_o_power()
        print((x,rfval,optval))
        DataList.append([x,rfval-optval])
        rf.trigger()

    rfval  = rf_meter.getPeak(x,5)[1]
    optval = get_o_power()

    print((x,rfval,optval))

    DataList.append([x,rfval-optval])

    rf.out_off()

    pl =  NBPlot()
    pl.plot(
        DataList,
        'Electrical Spectrum',
        'Frequency Input Signal [MHz]',
        'Measured Power [??]'
        )

    data = DataList


    if result_path != 0:
        DataIO.writeData(result_path,data,'get_e_spectrum')


    return data

def get_VI_curve(maitre,start = 0, stop = 1, step = 0.1,channel=1,result_path=0):
    return dc_sweep_1d(start,stop,step,'get_current',str(int(channel)),result_path,channel)

def dc_power_sweep(maitre,start=0,stop=1,step=0.1,result_path=0):

    DataList = []
    dc = gh.get_instrument('DCSource')

    dc.save_state()

    dc.setvoltage(float(start))

    dc.setOutputSwitch(1)

    for x in np.arange(float(start),float(stop)+float(step),float(step)):
        #gh.call_function('DCSource','setvoltage',x)
        dc.setvoltage(x)
        time.sleep(0.1)
        DataList.append([x,get_o_power()])

    #gh.call_function('DCSource','recall_state')
    dc.recall_state() #direct access alternative

    pl =  NBPlot()
    pl.plot(
        DataList,
        'Optical Power dep on Bias',
        'Bias Voltage [V]',
        'Measured Power [dBm]'
    )


    if result_path != 0:
        DataIO.writeData(result_path,DataList,'dc_power_sweep')

    return data


def dc_sweep_1d(maitre, start=0,stop=1,step=0.1,func=False,args=False,result_path=0):

    DataList = []

    dc = gh.get_instrument('DCSource')
    dc.save_state()

    dc.setvoltage(float(start))
    dc.setOutputSwitch(1)


    for x in np.arange(float(start),float(stop)+float(step),float(step)):

        dc.setvoltage(x)
        time.sleep(0.1)
        arglist = [stages,maitre]
        for elem in args:
            arglist.append(elem)
        data = maitre.execute_func_name('Measure',func,arglist)


        DataList.append([x,data])

    if isinstance(DataList[0][1], int) or isinstance(DataList[0][1], float):
        pl =  NBPlot()
        pl.plot(
            DataList,
            'DC Voltage Sweep',
            'Bias Voltage [V]',
            func
        )

    dc.recall_state()

    if result_path != 0:
        DataIO.writeData(result_path,DataList,'dc_sweep_1d')


    return DataList

def find_depl_MZI_bias(maitre,channel=0,max_volt=5):

     dc_data=dc_power_sweep(channel,0,max_volt,50)

     # Add plotting of data

     trans=list(zip(*dc_data))

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

def carac_MZI(maitre,dc_sig1_chan,max_volt=5,result_path=0):
    # Set optimal bias
    # Get Vpi
    # Get Extinction Ratio
    # Get Loss

    dc = gh.get_instrument('DSource')
    dc_data = find_depl_MZI_bias(stages, maitre,dc_sig1_chan,max_volt)

    # Get e bandwidth
    dc.setvoltage(dc_data[0],dc_sig1_chan)
    dc.setOutputSwitch(1,dc_sig1_chan)

    best_power = 10 * math.log10((0.354*dc_data[1])**2/50/0.001)

    rf_data = get_e_bandwidth(0.5,20,100,best_power)

    dc_data.append(['RF_Spectrum',rf_data])

    data = dc_data


    if result_path != 0:
        _write_data(data,result_path)

    return data

def simpleConnectFiberTest():
    gh = g()

    laser = gh.get_instrument('Laser')
    print('laser, ' + str(laser))
    fiber_in = gh.choose_fiber_in(1)
    print('fiber ' + str(fiber_in))
    gh.connect_instruments(laser, fiber_in)

    fiber_out = gh.choose_fiber_out(3)
    p_meter = gh.get_instrument('PowerMeter')
    gh.connect_instruments(fiber_out, p_meter)

    wavelength = 1550
    laser.setwavelength(wavelength)
    power = p_meter.get_power(wavelength)
    print(power)

    return power

def noFiberMeasureTest(maitre):
    # setup
    gh = g()
    laser = gh.get_instrument('Laser')
    osa = gh.get_instrument('OSA')
    gh.connect_instruments(laser, osa)
    # measure
    laser.setwavelength(1560)
    data = osa.getSpectrum(1530, 1570 , 0.1, 0)
    # output
    # print data
    return data

def noFiberTriggerTest(maitre):
    # setup
    gh = g()
    dc1 = gh.get_instrument('DCSource')
    dc2 = gh.get_instrument_triggered_by(dc1, 'DCSource')
    # measure
    dc1.setvoltage(1)
    dc2.setvoltage(2)
    # output
    return 'Test complete.'

def testConnectDebug():
    gh = g()
    las = gh.get_instrument('Laser')
    fib = gh.get_instrument('OSA')
    # fib = gh.choose_fiber_in(1)
    print('laser: {}\nfiber: {}\n'.format(las, fib))

    gh.connect_instruments(las, fib)
    return 23.0

def testBlockingCalls():
    print('entering blocking instance')
    gh = g()
    osa = gh.get_instrument_w('OSA', additional=True)
    osa.getSpectrum(1550, 1551, 0.1, 0)
    for i in range(10):
        print('sleeping ...{}'.format(i + 1))
        time.sleep(1)
    osa.getSpectrum(1552, 1553, 0.1, 0)
    print('blocking instance done.')

    return 'Test complete.'


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
