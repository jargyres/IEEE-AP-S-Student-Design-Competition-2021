"""
FileName: DOA.py
##############################
created : Jan 17, 2021 

last edit : 
	date: Jan 17, 2021
	reason: creation
				
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
	def __init__(self,number_e = 2, number_s = 1024, 
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
	
		
	#data_set(int t)
#set which data set is going to be used
#pulls data from datas_s.py and b_data.py
# 1-1024	format 1
# 2-10		format 1 
# 3-4		format 1
# 4-512		format 2
# all else defaults to 1024	format 1
	def data_set(self, t = 5, filename = None):
		
		if t == 1:
			self.data_s = datas_s.data_U #1024 snapshots
			self.format_s = 1
			

		elif t == 2:
			self.data_s = datas_s.data_T #10 snapshots
			self.format_s = 1
			

		elif t == 3:
			self.data_s = datas_s.data_s #4 snapshots
			self.format_s = 1
			
		
		elif t == 4:
			self.data_s = b_data.blade_data
			self.format_s = 2
			
			
		elif t == 5:
			A = pd.read_csv(filename,index_col=False,header=None,engine='c')
			A = A.to_numpy()
			A = np.reshape(A,(512,4))
			b_data = np.array([[0,0]])
			for row in A:
				temp1 = row[0]+(row[1])*1j
				temp2 = row[2]+(row[3])*1j
				temp_array = np.array([[temp1,temp2]])
				b_data = np.concatenate((b_data, temp_array))

			A = np.matrix(np.delete(b_data,0,0))
	
			self.data_s = A
			self.format_s = 2
				
		else:
			self.data_s = datas_s.data_U #1024 snapshots
			self.format_s = 1
			
		
	#function Normalize_data(matrix data_s)
	#normalizes data for use in algorithm
	#return data matrix normalized
	def Normalize_data(self, data_s):
		
		s_data = np.power(data_s,2);
		s_data = np.absolute(s_data);
		set_s = [];
		for i in range(0, np.size(s_data[1,:])):
			set_s.append(np.nansum(s_data[:,i]));
 

		s_data = set_s;
		s_data = np.divide(s_data, len(data_s[0]));
		s_data = np.sqrt(s_data);
		set_s = np.divide(data_s,s_data);
		return(set_s);
	
		
	#function steering(array doa_signals)
	#creates steering vector
	#this function takes an array of angles  
	# returns vector steering_v	
	def steering(self, doa_signals):
			#mue of steering vector
		mue = (np.arange(self.number_elements).reshape((self.number_elements,1)));
		mue = -1j*2*np.pi*self.separation_distance*mue*np.sin((doa_signals)*np.pi/180);
		steering_v = np.matrix(np.exp(mue));
			#returning steering vector
		return steering_v;
		
		
	#function find_eg_v(matrix data_s)
	#computes eigen analysis of data matrix
	#returns eigen vector of if smallest eigen value
	def find_eg_v(self, data):
		
		#create spacial covariance matrix
		if(self.format_s == 2):
			covariance_matrix = (data.getH()*data)/self.number_snapshots; 
		else:
			covariance_matrix = (data*data.getH())/self.number_snapshots;

		#create Eigen-Decomposition of Covariance matrix
		eigen_val, eigen_vec = LA.eigh(covariance_matrix);

		#sort eigen_val and eigen_vec
		idx = eigen_val.argsort()[::-1];
		eigen_val = eigen_val[idx];
		eigen_vec = eigen_vec[:,idx];

		unc_noise_eigen_vec = eigen_vec[:,self.number_elements-1]
		return(unc_noise_eigen_vec);
		

	#function find_music_spectrum()
	#takes data in form of matrix
	#computes music DOA spectrum
	#returns array music_spectrum
	def find_music_spectrum(self):

		data_s = self.Normalize_data(self.data_s)
	
		unc_noise_eigen_vec = self.find_eg_v(self.data_s) 
		
		# music algorithm

		#create music_spectrum array
		music_spectrum = [];

		#fill music_spectrum array
		for i in range(0,len(self.angles)):
			music_spectrum.append((1)/
				((self.complete_response[:,i].getH()* unc_noise_eigen_vec* 
				unc_noise_eigen_vec.getH()* self.complete_response[:,i]).item()));
	
		music_spectrum = np.around(music_spectrum, 4) 
		music_spectrum = np.real(music_spectrum)		#returns only real part os spectrum
		music_spectrum = np.absolute(music_spectrum)
		self.response = music_spectrum
