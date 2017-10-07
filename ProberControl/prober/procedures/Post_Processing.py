import numpy as np
import math
import time
import sys
#from scipy import signal
#import connecting
#from ProbeLib.Classes.plotter import NBPlot


def main(argv):

	baseline =  _read_data('baseline.txt')
	data = [_read_data('test1_PM1.txt'), _read_data('test1_PM2.txt') ] # Data is list of all files. 

	#print data
	#norm_data = normalize(data, baseline)

	#filtered = IIR_filter(filtered, 500)

	#prelim_res_list, std_list, res_list = Find_Res(wavelength, power)

	ring_res, prelim_res_list = All_Ring_Res(data)

	#res_list, prelim_res_list = Find_Res(data[1])


	#data_prime = np.gradient(power).tolist()
 	
 	#combined = combine(wavelength, data_prime)

 	#print res_list
 	
 	for i in xrange(0, len(ring_res)):
 		_write_data(ring_res[i], 'ring_' + str(i) +'.txt')
	
	#_write_data(res_list, 'res.txt')
 	_write_data(prelim_res_list, 'prelim.txt')

def Find_Resonance(stages, maitre, file, low, high, step_size, baseline = '0'):
	
	if baseline != '0':
		baseline = _read_data('baseline.txt')

	low = float(low)
	high = float(high)
	step_size = float(step_size)

	data = _read_data(file)
	steps_per_nm = int(1/step_size)
	ring_res, prelim_res_list = All_Ring_Res(data)
	 #can only find res of single file, if called from Prober Controller. No way to split files at the moment

def	split(data):

	values = map(lambda x: data[x][1], xrange(0, len(data)))
	prefix = map(lambda x: data[x][0], xrange(0, len(data)))

	return prefix, values

def combine(prefix, values):

	combined = map(lambda x: [prefix[x], values[x]], xrange(0, len(values)))

	return combined

def normalize(data, baseline):

	norm_data = []
	baseline_tracker = 0

	for i in xrange(0, len(data)):
		while (baseline[baseline_tracker][0] < data[i][0]):
			baseline_tracker += 1
		if baseline_tracker < len(baseline) and data[i][0] == baseline[i][0]:
			norm_data.append([data[i][0], data[i][1] - baseline[i][1]])
			baseline_tracker += 1

	return norm_data

'''
def IIR_filter(data, n):

	b, a = signal.butter(3, 0.05)

	filtered = signal.filtfilt(b, a, data)

	return filtered
'''

def All_Ring_Res(data, dist_btwn_same_res = 0.75, steps_per_nm = 100):  #Takes a list of resonance data, splits it up for comparison

	new_ring, prelim_res_list = Find_Res(data[0])
	new_ring = Find_ER_and_FWHM(new_ring, data[0])

	ring_res = [new_ring]
	
	for i in xrange(1, len(data)):  #not efficient - Finds ER before comparing is not very good. Fix when have time
		reference = new_ring
		new_ring,_ = Find_Res(data[i])
		new_ring = Find_ER_and_FWHM(new_ring, data[i], steps_per_nm) #Doesn't work for Drop Data
		ring_res.append(Comp_Res(new_ring, reference, dist_btwn_same_res))
	
	return ring_res, prelim_res_list #Do something with this

def Find_ER_and_FWHM(filtered_res_list, file, steps_per_nm):

	wavelength, data = split(file)
	list_with_ER = []

	for i in xrange(0, len(filtered_res_list)):

		index = filtered_res_list[i][0]
		largest = data[index]
		index -= 1
		counter = 0

		while(counter < int(steps_per_nm/10) and index >=0):   #only goes to the left to find the largest (and average). maybe collaborate with the right?
			if (largest < data[index]):
				largest = data[index]
				counter = 0
			else:
				counter +=1
				index -=1

		#largest found, get average
		if (index-int(steps_per_nm/10) >= 0):
			average = np.average(data[index-int(steps_per_nm/10):index+1])
		else: 
			average = np.average(data[0:index+1])

		filtered_res_list[i].append(average - filtered_res_list[i][2])  #ER Added to List


		####Finding FWHM
		HM = average-3 #3dB difference

		index = filtered_res_list[i][0]
		while(data[index] < HM):
			index-=1
		left = wavelength[index]

		index = filtered_res_list[i][0]
		while(data[index] < HM):
			index+=1
		right = wavelength[index]

		filtered_res_list[i].append(right - left)

	return filtered_res_list



def Comp_Res(new_data, ref_data, dist_btwn_same_res): #Find new res that belongs to a certain ring

	j = 0
	new_res = []

	for i in xrange(0, len(new_data)):

		if (j == len(ref_data)):

			new_res.append(new_data[i:])
			break

		while (new_data[i][1] - ref_data[j][1] >= dist_btwn_same_res):
			j += 1 #ref res not existant in new data. Skip it.

		if (math.fabs(new_data[i][1] - ref_data[j][1]) < dist_btwn_same_res):
			j += 1 ##same res, moves on to next value

		elif(new_data[i][1] - ref_data[j][1] <= -1*dist_btwn_same_res):
			new_res.append(new_data[i]) #new res detected
 		else:
			print('Weird data. How is this even possible?')

	return new_res		

def Find_Res(file, transmission = True, n = 100, confidence = 5, confidence_high = 5.5, dist_btwn_res = 0.75):

	#file is file name
	#n is the number of points/2 used in rolling average
	#high confidence used only if one point in prelim list

	wavelength, data = split(file)

	data_prime = [math.fabs(elem) for elem in np.gradient(data).tolist()] #rectifies
	data_prime_unrect = np.gradient(data).tolist()

	_write_data(combine(wavelength, data_prime_unrect), 'gradient.txt')

	prelim_res_list = []
	avg_list = []

	#get rolling for a certain range, find point outside confidence level
	for i in xrange(0, len(data_prime)):
		if (i < n):
			data_avg = np.average(data_prime[:2*n])   #sample size: 2*n points
		elif (i >= len(data_prime)-(n+1)):
			data_avg = np.average(data_prime[-2*n:])
		else:
			data_avg = np.average(data_prime[i-n:i+n])

		avg_list.append([wavelength[i], data_avg]) 

		if (math.fabs(data_prime[i])/data_avg > confidence): 

			prelim_res_list.append([i, wavelength[i], data_prime_unrect[i]/data_avg])

	res_list = []

	single = True #removes single result
	for i in xrange(0, len(prelim_res_list)):

		if(i == len(prelim_res_list)-1):
			if (math.fabs(prelim_res_list[i][1] - prelim_res_list[i-1][1]) > dist_btwn_res and math.fabs(prelim_res_list[i][2]) < confidence_high):
				prelim_res_list.pop(i)
			else:
				break		
		elif(math.fabs(prelim_res_list[i][1] - prelim_res_list[i+1][1]) < dist_btwn_res):
			single = False
		elif(math.fabs(prelim_res_list[i][1] - prelim_res_list[i+1][1]) > dist_btwn_res and single == False):
			single = True
		elif(math.fabs(prelim_res_list[i][1] - prelim_res_list[i+1][1]) > dist_btwn_res and single == True and math.fabs(prelim_res_list[i][2]) < confidence_high):
			prelim_res_list.pop(i)

	largest_so_far = 0.0
	index_largest = 0
	
	#checks the prelimiary list of resonance, makes a rough guess about where each resonance lies 
	for i in xrange(1, len(prelim_res_list)):

		if (prelim_res_list[i][1] - prelim_res_list[i-1][1] < dist_btwn_res):

			if (prelim_res_list[i-1][2] < 0 and prelim_res_list[i][2] > 0):  #res occures between - and + slope
				res_list.append(prelim_res_list[i])
				largest_so_far = 0.0
				index_largest = 0

			elif (math.fabs(prelim_res_list[i-1][2]) > largest_so_far):
				largest_so_far = prelim_res_list[i][2]
				index_largest = i

		elif (res_list == [] or prelim_res_list[i-1][1] - res_list[-1][1] > dist_btwn_res):
			res_list.append(prelim_res_list[index_largest])
			largest_so_far = prelim_res_list[i][2]
			index_largest = i

		else:
			largest_so_far = prelim_res_list[i][2]
			index_largest = i

	#Finds each resonance for real, using the original data (not the gradient data) and the guessed resonance in previous step
	#works for both transmission style Lorentzians and Drop style Lorentians, based on whether Transsision is True or False
	filtered_res_list = []
	
	for i in xrange(0, len(res_list)):
		
		index = res_list[i][0]
			#go right
		if ((data[index-1] < data[index] and transmission == True) or (data[index-1] > data[index] and transmission == False)):
			while True:
				index = index-1
				if (index == 0 or (data[index] < data[index-1] and transmission == True) or (data[index] > data[index-1] and transmission == False)) :
					break;
				#go left
		elif (data[index+1] < data[index] and transmission == True) or (data[index+1] > data[index] and transmission == False):
			while True:
				index = index+1
				if (index == len(data)-1 or (transmission == True and data[index] < data[index+1]) or (transmission == False and data[index] > data[index+1])):
					break;
			
		filtered_res_list.append([index, wavelength[index], data[index]])

	return filtered_res_list, prelim_res_list

def set_clear_plot(clear):
    pl = NBPlot()
    pl.set_clear(clear)

def _read_data(path):
    
    MeasFile = open(path, 'r')

    if MeasFile is None:
    	print 'Problem reading measurement file.'
    	return 0
    
    MeasFile.close()
    
    with open(path) as f:
    	DataList = [list(map(float, (i.strip('\n'))[:-2].split('\t'))) for i in f]  #dirty string manipulation --> maybe maxsplit 2?
    	#currently just removes the last two blank letters from the each line ('\s')

    return DataList

def _write_csv(file,data):

	for elem in data:
		for item in elem:
			file.write(str(item))
			file.write('\t')
		file.write('\n')

def _write_data(data,path='results.meas'):
    result_file = open(path,"w")

    _write_csv(result_file,data)

if __name__ == "__main__":
	main(sys.argv)