import time
import numpy
#import visa

class AndoAQ6317(object):
  '''
  This class models the AndoAQ4321 optical soectrum Analyzer.

  .. note:: Currently this class and therefore get_o_spectrum() is explicitly written to set up the connection and work only with the AQ4321 Laser.
  '''

  def __init__(self, res_manager, address = 'GPIB0::2::INSTR'):


    self.gpib = res_manager.open_resource(address)
    self.gpib.write('INIT')
    #time.sleep(0.55)
    self.gpib.write ('*IDN?')
    info = self.gpib.read()
    print ('OSA Connection Successful: %s' + info)

  def whoAmI(self):
        ''':returns: reference to device'''
        return 'OSA'

  def change_state(self):

        if self.active == True:
            self.active = False
        else:
            self.active = True

  def get_o_spectrum(self, start, stop, step, result_path = 0):

    self.gpib.write('SNHD') 					#Sets Sensitivity to Normal Range (HOLD)
    self.gpib.write('AVG1')						#Sets the number of averaging times for measurement to 1
    self.gpib.write('TLSADR24') 				#Sets the GPIB Address of Laser to 24
    self.gpib.write('TLSADR?') 					#Double checks that it is set
    info = self.gpib.read()
    print ('Laser Address Set At: ' +info)

    self.gpib.write('GP2ADR20') 				#Sets the GPIB of OSA to 20
    self.gpib.write('GP2ADR?') 					#Double checks
    info = self.gpib.read()
    print ('GP-IB2 Address of OSA set to: ' +info)

    self.gpib.write('TLSSYNC1') 				#Syncs Laser and OSA
    self.gpib.write('TLSSYNC?') 				#Double checks
    info = self.gpib.read()
    print ('Laser and OSA Link Status: ' +info)
    #1 on, 0 off

    start = float(start)
    stop = float(stop)
    step = float(step)
    self.gpib.write('RESLN2') 					#set to lowest resolution, step size now indicates resolution
    self.gpib.write('SRMSK254') 				#Sets mask to be 254, Masking for 'Sweep Complete' (Bit 0)
    self.gpib.write('SRQ1') 					#Status Bit on
    self.gpib.stb 								#Discard Initial status bit

    sweepWidth = stop-start
    sampleNumber = sweepWidth/(step) + 1

    self.gpib.write('SMPL' + str(sampleNumber)) #Resolution of sweep
    self.gpib.write('STAWL' + str(start)) 		#Beginning of sweep
    self.gpib.write('STPWL' + str(stop)) 		#End of sweep

    print('Scan Starts: ' + str(start) + ' to ' + str(stop) + ' at ' + str(step) + 'nm step')

    self.gpib.write('SGL') # Start Single Sweep

    self.checkStatus()  #Checks if sweep is complete

    print('[Sweep Done]')
    #time.sleep(60)

    self.gpib.write('SD1, LDATA') #Reads Data from Buffer
    self.gpib.read()
    DataList = []

    for x in numpy.arange(float(start), float(stop) + float(step), float(step)):
      reading = float(self.gpib.read().strip(' \t\r\n'))  #Strips all blank space characters. Readings in dBm
      if reading > -200 and reading < 100: #If readings within reasonable range, append
		DataList.append([x, reading])

    return DataList

  def checkStatus(self):
    status = int(self.gpib.stb)
    print('Status: %d' %status)
    print('Scanning.'),
    while status == 0:
	  time.sleep(0.5)
	  status = int(self.gpib.stb)
	  print('.'),
      #print('Status: %d' %status)
    return True
