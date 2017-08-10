# This is the distance(proximity) sensor Class that wraps around 
# Micro Epsilon's Data Aquisition Library API (MeDaqLib) for accessing digital
# sensors
# MEDAQLib.dll is needed for this class to operate
# The implementation is targeted for ILD1420-10, but can be easily changed or 
# extended

from ctypes import *
import logging

#**********************  SENSOR IDs  **********************
NO_SENSOR=            0  # Dummy, only for internal use
SENSOR_ILR110x_115x= 19  # optoNCDT ILR
SENSOR_ILR118x=      20  # optoNCDT ILR
SENSOR_ILR1191=      21  # optoNCDT ILR
SENSOR_ILD1302=      24  # optoNCDT
SENSOR_ILD1320=      41  # optoNCDT
SENSOR_ILD1401=       1  # optoNCDT
SENSOR_ILD1402=      23  # optoNCDT
SENSOR_ILD1420=      42  # optoNCDT
SENSOR_ILD1700=       2  # optoNCDT
SENSOR_ILD2200=       5  # optoNCDT
SENSOR_ILD2300=      29  # optoNCDT
SENSOR_IFD2401=      12  # confocalDT
SENSOR_IFD2431=      13  # confocalDT
SENSOR_IFD2445=      39  # confocalDT
SENSOR_IFD2451=      30  # confocalDT
SENSOR_IFD2461=      44  # confocalDT
SENSOR_IFD2471=      26  # confocalDT
SENSOR_ODC1202=      25  # optoCONTROL
SENSOR_ODC2500=       8  # optoCONTROL
SENSOR_ODC2520=      37  # optoCONTROL
SENSOR_ODC2600=       9  # optoCONTROL
SENSOR_LLT27xx=      31  # scanCONTROL+gapCONTROL, only for SensorFinder functionality, OpenSensor will fail
SENSOR_DT3100=       28  # eddyNCDT
SENSOR_DT6100=       16  # capaNCDT
SENSOR_DT6120=       40  # capaNCDT
CONTROLLER_DT6200=   33  # capaNCDT
CONTROLLER_KSS6380=  18  # capaNCDT
CONTROLLER_DT6500=   15  # capaNCDT
#**********************************************************

#*********************  ERROR VALUES  *********************
ERR_NOERROR= 0
ERR_FUNCTION_NOT_SUPPORTED= -1
ERR_CANNOT_OPEN= -2
ERR_NOT_OPEN= -3
ERR_APPLYING_PARAMS= -4
ERR_SEND_CMD_TO_SENSOR= -5
ERR_CLEARUNG_BUFFER= -6
ERR_HW_COMMUNICATION= -7
ERR_TIMEOUT_READING_FROM_SENSOR= -8
ERR_READING_SENSOR_DATA= -9
ERR_INTERFACE_NOT_SUPPORTED= -10
ERR_ALREADY_OPEN= -11
ERR_CANNOT_CREATE_INTERFACE= -12
ERR_NO_SENSORDATA_AVAILABLE= -13
ERR_UNKNOWN_SENSOR_COMMAND= -14
ERR_UNKNOWN_SENSOR_ANSWER= -15
ERR_SENSOR_ANSWER_ERROR= -16
ERR_SENSOR_ANSWER_TOO_SHORT= -17
ERR_WRONG_PARAMETER= -18
ERR_NOMEMORY= -19
ERR_NO_ANSWER_RECEIVED= -20
ERR_SENSOR_ANSWER_DOES_NOT_MATCH_COMMAND= -21
ERR_BAUDRATE_TOO_LOW= -22
ERR_OVERFLOW= -23
ERR_INSTANCE_NOT_EXIST= -24
ERR_NOT_FOUND= -25
ERR_WARNING= -26
ERR_SENSOR_ANSWER_WARNING= -27
#**********************************************************

def Error(err, sensor):
    ''' Read errors from sensor '''
    buf = create_string_buffer(1024);
    mqlib.GetError(c_ulong(sensor), buf, len(buf))
    out = "Error in {}\n{}".format(err, buf.value)
    logging.error(out)
    return -1

class DSensor (object):

    def __init__(self, COM_Port, sensor_model = SENSOR_ILD1420):
        '''
        Constructor
        
        sensor_model (int)
        COM_Port (string)
        '''
        
        # load the dll
        windll.LoadLibrary('../MeDaqLib/MEDAQLib.dll')
        self.mqlib = windll.MEDAQLib
        if self.mqlib is None:
            logging.error('Problem opening MEDAQLib.dll!')
            exit()
            
        self.sensor = self.mqlib.CreateSensorInstance(sensor_model)
        if self.sensor == 0:
            logging.error('Cannot create driver instance!')
            exit()
            
        self.COM_Port = c_char_p(COM_Port)
        
        # open sensor
        if self.open() < 0:
            self.close()
            exit()
            
        # make sure output mode is RS422
        if self.InterfaceRS422() < 0:
            self.close()
            exit()
        
        
    def Error(self, err):
        ''' Read errors from sensor '''
        
        buf = create_string_buffer(1024);
        self.mqlib.GetError(c_ulong(self.sensor), buf, len(buf))
        out = 'Error in {}\n{}'.format(err, buf.value)
        logging.error(out)
        return -1
    
    def open(self):
        errCode = self.mqlib.OpenSensorRS232(c_ulong(self.sensor), self.COM_Port)
        if errCode != ERR_NOERROR:
            return self.Error('OpenSensor <{}>'.format(errCode))
        return ERR_NOERROR
        
    def poll(self, n = 1):
        ''' Retrieves last n values from sensor '''
        
        data = c_double()
        
        errCode = self.mqlib.Poll(c_ulong(self.sensor), None, byref(data), c_int(n))
        if errCode != ERR_NOERROR:
            self.Error('Poll <{}>'.format(errCode))
            self.close()
            exit()
        return data.value
        
    def InterfaceRS422(self):
        sensorCommand = c_char_p('Set_DataOutInterface')
        paramName = c_char_p('SP_DataOutInterface')
        paramValue = c_int(1)    # 1 = RS422
        errCode = self.mqlib.SetIntExecSCmd(c_ulong(self.sensor), sensorCommand, paramName, paramValue)
        if errCode != ERR_NOERROR:
            return self.Error('SetIntExecSCmd <{}>'.format(errCode))
        return ERR_NOERROR
        
    def close(self):
        if self.sensor != 0:
            if self.mqlib.CloseSensor(c_ulong(self.sensor)) != ERR_NOERROR:
                logging.error('Cannot close sensor!')
            if self.mqlib.ReleaseSensorInstance(c_ulong(self.sensor)) != ERR_NOERROR:
                logging.error('Cannot release driver instance!')