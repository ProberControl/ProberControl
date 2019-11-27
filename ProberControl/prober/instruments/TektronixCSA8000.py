################################################################################
###### This is a template for a multimeter class. The Methods in this class ####
###### are mandatory, as other methods are expecting them. #####################
################################################################################

# Note: it is a good practice to indicate what packages the instrument utilizes
#        even if the package is passed as a parameter. In that case, you can just
#        leave it commented out.
#
#import visa
#import time
#import sys

class TektronixCSA8000(object):
    '''
    This class models a sampling oscilloscope...
    '''

    def __init__(self,res_manager,address='GPIB0::16::INSTR', channel=1):
        '''
        Constructor method

        :param res_manager: PyVisa resource manager
        :type res_manager: PyVisa resourceManager object
        :param address: SCPI address of instrument
        :type address: String
        '''
        self.active = False
        self.gpib = res_manager.open_resource(address) #call vis
        self.channel = channel
        self.sampleRate = []


    def whoAmI(self):
        ''':returns: reference to device'''
        return 'SamplingOscilloscope'

    def change_state(self):
        ''' Toggles the self.active parameter'''
        if self.active == True:
            self.active = False
        else:
            self.active = True

    # def get_voltage(self):
        # '''
        # Query the powermeter reading after setting correct wavelength

        # :returns: Float
        # '''

##### Basic Acquisition

    def getAcquisitionParam(self):
        return self.gpib.query('ACQuire?')

    def setAcquisitionMode(self,sample=True,average=False,envelope=False):
        sample = bool(sample)
        average = bool(sample)
        envelope = bool(envelope)

        if(int(sample)+int(average)+int(envelope)!=1):
            print("Exactly one paramter needs to be set to True")
            return

        if sample:
            self.gpib.write('ACQuire:MODe SAMple')
            return

        if average:
            self.gpib.write('ACQuire:MODe AVERage')
            return

        if envelope:
            self.gpib.write('ACQuire:MODe ENVElope')
            return

    def setAveragingNum(self,num=16):
        self.gpib.write('ACQuire:NUMAVg '+int(num))
        return

    def startAcquisition(self):
        self.gpib.write('ACQuire:STATE ON')
        self.gpib.write('ACQuire:STATE RUN')
        return

    def stopAcquisition(self):
        self.gpib.write('ACQuire:STATE STOP')
        self.gpib.write('ACQuire:STATE OFF')
        return

##### Horizontal paramter
    def getSampleRate(self,scale):
        '''
        Notes:
        '''
        return self.gpib.query('HORizontal:MAIn:SCAle?')

    def setSampleRate(self,scale):
        '''
        Notes:
        '''
        #self.gpib.write('HORizontal:DISPlayscale:SEConds PERScreen; HORizontal:UNIts S; HORizontal:MAIn:SCAle {:.10E}'.format(scale))
        scale = float(scale)
        self.gpib.write('HORizontal:MAIn:SCAle {:.10E}'.format(scale))
        return

##### Trigger paramter

#TOOODDOOOOOO

##### Mask paramter
    def getMaskParamter(self):
        return self.gpib.query('MASK?')

    def runMaskAutoFit(self):
        self.gpib.write('MASK:AUTOFit EXECute')
        return

    def runMaskAutoSize(self):
        self.gpib.write('MASK:AUTOSEEk EXECute')
        return

    def setMaskHitRatioTarget(self, ratio):

        if not(1e-8 < float(ratio) < 0.1):
            print("Ratio must be within 1E-8 and 0.1")
            return

        self.gpib.write('MASK:AUTOSEEk:HITRatio '+str(float(ratio)))
        return

    def setMaskHitCountTarget(self, count):
        self.gpib.write('MASK:AUTOSEEk:MASKCount '+str(int(count)))
        return

    def getMaskHitRatio(self):
        return self.gpib.query('MASK:AUTOSEEk:MEASHitratio?')

    def resetMask(self):
        self.gpib.write('MASK:COUNt')
        return

    def getMaskHitCount(self):
        return self.gpib.query('MASK:COUNt:TOTal?')

    def setMaskSource(self, source='CH1'):
        '''
            source options are:
                CH1 - CH8
                MATH1 - MATH8
                REF1 - REF8
        '''

        self.gpib.write('MASK:SOUrce '+source)
        return

    def setMaskStandard(self, standard="NONe"):
        '''
            Supported Standards are:
            NONe | CUSTom | ATARXG1 | ATARXG2 | ATARXG3
            | ATATXG1 | ATATXG2 | ATATXG3 | ENET40GB_LR4 | ENET40GB_SR4
            | ENET1250 | ENET2500 | ENET3125 | ENET9953 | ENET10313|
            ENET10GB_LRM | ENET100B_BX10 | ENET100GB_ER4 | ENET100GB_LR4
            | ENET100GB_SR4 | ENET100GB_SR10 | ENET100B_LX10 |
            ENET1000B_KX | ENET10313 | ENET11096 | ENET41250 | FC133
            | FC133E | FC266 | FC266E | FC531 | FC531E | FC1063 |
            FC1063E | FC2125 | FC2125E_ABR | FC2125E_ABT | FC2125E_AGR
            | FC2125E_AGT | FC4250E_ABR | FC4250E_ABT | FC4250E_AGR
            | FC4250E_AGT | FC8500E_ABR | FC8500E_ABT | FC8500E_AGR|
            FC8500E_AGT | FC8500D | FC8500FINAL | FC4250 | FC10519
            | FC11317 | FC14025_MMR6_1 | FC14025_SMR6_1 | FEC2666 |
            FEC10664 | FEC10709 | FEC42657 | FEC43018 | INF2500 |
            INFIE25 | INFIniband | OC1 | OC3 | OC9| OC12 | OC18 | OC24
            | OC36 | OC48 | OC192 | OC768 | OTU27952 |PCIEXPRESS_Rcv
            | PCIEXPRESS50_Rcv | PSM4_100G_TX | RIO_SERIAL1G |
            RIO_SERIAL2G | RIO_SERIAL3G | SAS3_0_XR | SAS3_0_XR_AASJ
            | SAS3_0_SATA | USERMask | XFI9950_TAA | XFI9950_RAD |
            XFI9950_THB | XFI9950_RHC | XFI9950_TMBP | XFI9950_RMCP
            |XAUIFar | XAUIRFar | XAUINear | XAUIRNear
        '''
        self.gpib.write('MASK:STANDARD '+standard)
        return


##### Histogram options
    def resetHistogramCount(self):
        self.gpib.write('HIStogram:COUNt')
        return

    def setHistogramMode(self,HORizontal=True,VERtical=False):
        HORizontal = bool(HORizontal)
        VERtical   = bool(VERtical)

        if int(VERtical) + int(HORizontal) != 1:
            print("Exactly one paramter needs to be set to True")
            return

        if HORizontal:
            self.gpib.write('HIStogram:MODe HORizontal')
            return

        if VERtical:
            self.gpib.write('HIStogram:MODe VERtical')
            return

    def setHistogramSource(self, source = 'CH1'):
        '''
            source options are:
                CH1 - CH8
                MATH1 - MATH8
                REF1 - REF8
        '''

        self.gpib.write('HIStogram:SOUrce '+source)
        return

    def getHistogramStatistics(self):
        return self.gpib.query('HIStogram:STATistics?')

    def setHistogramAxis(self,linear = True, log = True):
        linear = bool(linear)
        log   = bool(log)

        if int(log) + int(linear) != 1:
            print("Exactly one paramter needs to be set to True")
            return

        if linear:
            self.gpib.write('HIStogram:TYPE LINEAr')
            return

        if log:
            self.gpib.write('HIStogram:TYPE LOG')
            return

##### MATH
    def selectMathSlot(self,num):
        '''
            num can be between 1 and 8
        '''

        if not(0 < int(num) < 9):
            print("num must be between 1 and 8")
            return

            self.gpib.write('SELect:MATH'+str(int(num))+' ON')
            return

    def setMathFunction(self,func_string = 'C1+C2'):
        '''
            Example for the func_string:
                C1+C2
                C2*R2
                Log(C1+C2)

            Cx representing the channel x
        '''

        self.gpib.write('MATH<x>:DEFine '+str(func_string))
        return


##### Measurements
    def getFrequency(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'FREQuency',measType,source='CH1',measSlot=1)

    def getPeriod(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'PERIod',measType,source='CH1',measSlot=1)

    def getFallTime(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'FALL',measType,source='CH1',measSlot=1)

    def getRiseTime(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'RISe',measType,source='CH1',measSlot=1)

    def getOMA(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'OMA',measType,source='CH1',measSlot=1)

    def getRmsNoise(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'RMSNoise',measType,source='CH1',measSlot=1)

    def getMean(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'MEAN',measType,source='CH1',measSlot=1)

    def getMinimum(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'MINImum',measType,source='CH1',measSlot=1)

    def getMaximum(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'MAXimum',measType,source='CH1',measSlot=1)

    def getAmplitude(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'AMPLitude',measType,source='CH1',measSlot=1)

    def getPk2Pk(self,source='CH1',measSlot=1):
        return getMeasurementVal(self,'PK2Pk',measType,source='CH1',measSlot=1)

    def getMeasurementVal(self,measType,source='CH1',measSlot=1):
            '''
            This function specifiecs a measurement channel to collect a specific type of data

            meaSlot is the measuement slot on the oscilloscope. Valid numbers and integers between 1-8
            source is the source channel for the measurement. Valid numbers are integers between 1-8

            Options for Measurements are:
            HIGH | LOW | AMPLitude | MEAN | MAXimum | MINImum | PK2Pk | MID | POVershoot |
            NOVershoot | RMSNoise | PKPKNoise | AOPTPWRDBM | RMS |
            ACRMs | CRMs | CMEan | SNRatio | AOPTPWR | GAIN | OMA |
            RISe | FALL | PERIod | FREQuency | PCROss | NCROss | PWIdth
            | NWIdth | PDUty | NDUty | BURst | RMSJitter | PKPKJitter
            | DELay | PHAse | AREa | CARea | EXTINCTDB | EXTINCTPCT |
            EXTINCTRATIO | EXTINCTCAL | EYEHeight | PCTCROss | LEVCROss
            | QFACtor | EYEWIdth | DISTDUty | BITTime | BITRate |
            TIMCROss | EYEOfactor | SUPRSDB | SUPRSPCT | SUPRSRATIO | PULSESym
            '''

            measSlot = int(measSlot)

            self.gpib.write('MEASUrement:STATIstics:ENABle ON')
            self.gpib.write('MEASUrement:MEAS{}:SOUrce1:WFM {}'.format(measSlot, source))
            self.gpib.write('MEASUrement:MEAS{}:TYPe {}'.format(measSlot, measType))
            return self.gpib.query('MEASUrement:MEAS{}:MEAN?'.format(measSlot))

##### Misc
    def unlockFront(self):
        self.gpib.write('MEASUrement:STATIstics:ENABle ON')
        return
