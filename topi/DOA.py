"""
FileName: DOA.py
##############################
created : Jan 17, 2021 

last edit : 
	date: Apr 1, 2021
	reason: added new method to format data from buffer
				
lasteditor:
	William Wagner
##############################	
File Description:
	direction of arrival Music Algorithm
Next Steps:
	-accepting csv files  
	-code testing and timing
	-optimization
	-retest and time
"""

import numpy as np
from numpy.lib import scimath as SM
from numpy import linalg as LA
import pandas as pd
#import readcsv
#import base

class DOA():
	#defaults number_e = 4, 
	#		number_s = 1024, 
	#		separation_d = 0.5, 
	#		noise_v = 0.4
	#		angle_stp = .1
	def __init__(self,number_e = 4, number_s = 1024, 
					separation_d = 0.5, noise_v = 0.4, angle_stp = .1):
		super().__init__()
		
		self.angle_step = angle_stp
		self.data_s = 0
		self.format_s = 0
		self.response = 0
		self.angles = (np.arange(-90,90,angle_stp))
		self.number_elements = number_e
		self.number_snapshots = number_s;
		self.separation_distance = separation_d;
		self.noise_variance = noise_v;
		self.complete_response = self.steering(self.angles);
		self.number_signals = len(self.angles)	
	
	#set_data(array data)
	#set the data_s to formatted data
	#formats data array from single n array to 4x(n/8)
	def set_data(self, data):

		for i in range(8192):
			if(data[i] == 0):
				print("Zero at {}".format(i))
		print("")

		
		# if ((len(data)%self.number_elements) != 0):
		# 	print ("not a good size must be divisable by number_elements")
		# else:
		chan_Buf_len = int(len(data)/self.number_elements)
		print("chan_Buf_len = {}".format(int(chan_Buf_len/2)))
		b_data = np.array([0,0,0,0])
		dataPort0 = np.zeros(int(chan_Buf_len/2), dtype=np.complex)
		dataPort1 = np.zeros(int(chan_Buf_len/2), dtype=np.complex)
		dataPort2 = np.zeros(int(chan_Buf_len/2), dtype=np.complex)
		dataPort3 = np.zeros(int(chan_Buf_len/2), dtype=np.complex)

		index = 0
		for i in range(0,chan_Buf_len-1,2):
			dataPort0[index] = data[ i ]+(( data[ i+1 ] ) * 1j)
			dataPort1[index] = data[ i + chan_Buf_len ] + ( ( data[ i + ( chan_Buf_len + 1 ) ] ) * 1j)
			dataPort2[index] = data[ i + ( chan_Buf_len * 2 ) ]+ (( data[ i + ( (chan_Buf_len * 2) + 1 ) ] ) * 1j)
			dataPort3[index] = data[ i + ( chan_Buf_len * 3 ) ]+ (( data[ i + ( (chan_Buf_len * 3) + 1 ) ] ) * 1j)

			# complex0 = (( data[ i+1 ] ))
			# complex1 = (( data[ i + ( chan_Buf_len + 1 ) ] ))
			# complex2 = (( data[ i + ( (chan_Buf_len * 2) + 1 ) ] ))
			# complex3 = (( data[ i + ( (chan_Buf_len * 3) + 1 ) ] ))


			# print("{} {} {} {}".format(complex0, complex1, complex2, complex3))
			
			index += 1

		# A = np.matrix(np.delete(b_data,0,0))

		A = np.array([dataPort0, dataPort1, dataPort2, dataPort3])
		# , dataPort2, dataPort3])
		
		self.data_s = A
		self.format_s = 2

		

		
	#data_set(int t)
#set which data set is going to be used
#pulls data from datas_s.py and b_data.py
# 1-1024	format 1
# 2-10		format 1 
# 3-4		format 1
# 4-512		format 2
# all else defaults to 1024	format 1
	def data_set(self, t = 5, filename1 = None, filename2 = None):
		
		if t == 1:
			self.data_s = datas_s.data_U #1024 snapshots
			self.format_s = 1
			

		elif t == 2:
			self.data_s = datas_s.data_T #10 snapshots
			self.format_s = 1
			

		elif t == 3:
			self.data_s = datas_s.data_s #4 snapshots
			self.format_s = 1

		elif t == -1:

			self.data_s = filename1
			self.format_s = 2
			
		
		elif t == 4:
			self.data_s = b_data.blade_data
			self.format_s = 2
			
			
		elif t == 5:
			# print("Filename = {}".format(filename))
			try:
				A = pd.read_csv(filename1,index_col=False,header=None,engine='c', delimiter=',')
			except:
				return 0

			try:
				B = pd.read_csv(filename2,index_col=False,header=None,engine='c', delimiter=',')
			except:
				return 0
			A = A.to_numpy()
			B = B.to_numpy()
			# print(len(A))
			#TODO FIX Breaking on not divisible by 4 data, probably NANS
			if (((len(A)%4) != 0) or ((len(B)%4) != 0)):
				return 0
				# print ("not a good size must be divisable by 4")
			else:
				A = np.reshape(A,(int((len(A))),4))
				b_data = np.array([[0,0,0,0]])
				for row in range(len(A)):
					temp1 = A[row][0]+(A[row][1])*1j
					temp2 = A[row][2]+(A[row][3])*1j
					temp3 = B[row][0]+(B[row][1])*1j
					temp4 = B[row][2]+(B[row][3])*1j
					temp_array = np.array([[temp1,temp2,temp3,temp4]])
					b_data = np.concatenate((b_data, temp_array))

				A = np.matrix(np.delete(b_data,0,0))
	
				self.data_s = A
				self.format_s = 2
				return 1
				
		else:
			self.data_s = datas_s.data_U #1024 snapshots
			self.format_s = 1
			
			
		
	#function Normalize_data(matrix data_s)
	#normalizes data for use in algorithm
	#return data matrix normalized
	def Normalize_data(self, data_s):
		
		# data_s = np.transpose(data_s)
		s_data = np.power(data_s,2)
		s_data = np.absolute(s_data)
		set_s = []
		for i in range(0, np.size(s_data[1,:])):
			set_s.append(np.nansum(s_data[:,i]))
 

		s_data = set_s
		s_data = np.divide(s_data, len(data_s[0]))
		s_data = np.sqrt(s_data)
		set_s = np.divide(data_s,s_data)
		return(set_s)
		# return(np.transpose(set_s))
	
		
	#function steering(array doa_signals)
	#creates steering vector
	#this function takes an array of angles  
	# returns vector steering_v	
	def steering(self, doa_signals):
			#mue of steering vector
		mue = (np.arange(self.number_elements).reshape((self.number_elements,1)))
		mue = -1j*2*np.pi*self.separation_distance*mue*np.sin((doa_signals)*np.pi/180)
		steering_v = np.matrix(np.exp(mue))
			#returning steering vector
		return steering_v
		
		
	#function find_eg_v(matrix data_s)
	#computes eigen analysis of data matrix
	#returns eigen vector of if smallest eigen value
	def find_eg_v(self, data):

		#create spacial covariance matrix
		if(self.format_s == 2):
			covariance_matrix = (data.getH()*data)/self.number_snapshots
		else:
			covariance_matrix = (data*data.getH())/self.number_snapshots

		#create Eigen-Decomposition of Covariance matrix
		try:
			eigen_val, eigen_vec = LA.eigh(covariance_matrix)
		except:
			return(None)

		#sort eigen_val and eigen_vec
		idx = eigen_val.argsort()[::-1]
		eigen_val = eigen_val[idx]
		eigen_vec = eigen_vec[:,idx]

		unc_noise_eigen_vec = eigen_vec[:,self.number_elements-1]
		return(unc_noise_eigen_vec)
		

	#function find_music_spectrum()
	#takes data in form of matrix
	#computes music DOA spectrum
	#returns array music_spectrum
	def find_music_spectrum(self):

		self.convergence = 0
		# print(np.shape(data_s))
		self.data_s = self.Normalize_data(self.data_s)
		
		unc_noise_eigen_vec = self.find_eg_v(self.data_s)
		if(unc_noise_eigen_vec[0] == None):
			self.convergence = 1
			return(None)
		# music algorithm

		#create music_spectrum array
		music_spectrum = []

		#fill music_spectrum array
		for i in range(0,len(self.angles)):

			# transposition = self.complete_response[:,i]
			# eigneGetH = unc_noise_eigen_vec.getH()
			# responseItem = self.complete_response[:,i].getH()

			# A = np.transpose(responseItem) * np.transpose(unc_noise_eigen_vec)
			# B = A * np.transpose(eigneGetH)
			# C = np.transpose(B) * transposition

			# item = (  (  (1)  /  C  ).item())

			# music_spectrum.append(item)

			music_spectrum.append((1)/
				(( self.complete_response[:,i].getH()*unc_noise_eigen_vec*
				unc_noise_eigen_vec.getH()* self.complete_response[:,i]).item()))
	
		music_spectrum = np.around(music_spectrum, 4) 
		music_spectrum = np.real(music_spectrum)		#returns only real part os spectrum
		music_spectrum = np.absolute(music_spectrum)
		self.response = music_spectrum
