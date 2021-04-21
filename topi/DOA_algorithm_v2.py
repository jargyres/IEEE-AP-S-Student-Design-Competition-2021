"""
FileName: DOA_algorithm_v2.py
##############################
created : Oct 26, 2020 
last edit : 
	date: Dec 7, 2020
	reason: updated 3d graphing  
			clean up code
			set everything into functions
			
lasteditor:
	William Wagner
##############################	
File Description:
	direction of arrival Music Algorithm with plotting 
Next Steps:
	-create classes
	-code testing and timing
	-live plotting is not testing
	-optimization
	-retest and time
problems:
	-need to have something for when no peaks are avaliable

"""

#imports
#"""
import numpy as np
from numpy.lib import scimath as SM
from numpy import linalg as LA
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from mpl_toolkits.mplot3d import axes3d
from matplotlib import animation
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib import cm
import random
import time
from matplotlib.patches import Ellipse
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D
import mpl_toolkits.mplot3d.art3d as art3d
import timeit as Tit
# import datas_s
# import b_data
#"""

#global-variables

#"""
#need to add angles to setup globals

power = [1];                                #Power level of incoming signals

plot_type = 0;								#plot type, setup in set_up plot()

data_s = 0									#initialize global variable of data 
												#is set in data_set()
ax1 = 0
ax = 0											
	#set up in set_up_globals()
number_elements = 0;                        #Number of array elements
number_snapshots = 0;  		            	#Number of snapshots received
separation_distance = 0;                  	#Distance between elements in wavelengths
noise_variance = 0;                       	#Noise Variance
angles = (np.arange(-90,90,1));				#array of angles from -90 - 90, step of .1
number_signals = 0;       					#Total number of signals
#calculate the complete spectrum response, this does not change
#used in find_music_spectrum()
complete_response =0;
format_s = 2;							#tells find_eg_v() how to calculate covariances											
#"""


#set_up_plot(string vers)
#sets up the plot based on 'vers'
#strings available are '2d' and '3d'
#can set up a 2d and 3d graph
#also sets up radial graph
#2d plot is default
def set_up_plot(vers = '2d'):
	#create plot for graph
	global plot_type
	global ax1
	global ax
	fig = plt.figure()

	#radial graph
	#"""
	ax = fig.add_subplot(1,2,1,projection = 'polar' )

	#formatting for radial graph
	ax.set_rmax(4)
	ax.set(rlim =(0,5))
	ax.set_rticks([1,2,3,4])
	ax.set_theta_offset(offset = np.pi/2)
	ax.set_thetamin(90)
	ax.set_thetamax(-90)
	ax.grid(True)
	ax.set_theta_direction(-1)
	#"""
		
	if vers == '3d':		#3d-plotting
		plot_type = 2
		ax1 = fig.add_subplot(1,2,2,projection = '3d')
		ax1.set_xlabel('horizontal angle')
		ax1.set_ylabel('vertical angle')
		ax1.set_zlabel('Power')
		ax1.set_zlim(0,20)
		ax1.set_ylim(-90,90)
		ax1.set_xlim(90,-90)
		
	else:		#2d-plotting
		plot_type = 1
		ax1= fig.add_subplot(1,2,2)
		ax1.set_xlabel('Angle of Arival')
		ax1.set_ylabel('Power')


	reciver = ax.plot(0,0, c='g', marker = 'x')	#plots point for receiver
	

#plots a single iteration of animate()
def plot_graph():
	animate(0)
	plt.show()

	
#plots a continuous animation of animate() 
def plot_live_graph():	
	ani = animation.FuncAnimation(fig, animate, interval=3,)
	plt.show()


#data_set(int t)
#set which data set is going to be used
#pulls data from datas_s.py and b_data.py
# 1-1024	format 1
# 2-10		format 1 
# 3-4		format 1
# 4-512		format 2
# all else defaults to 1024	format 1
def data_set(t = 1):
		global data_s
		global format_s
		if t == 1:
			data_s = datas_s.data_U #1024 snapshots
			format_s = 1

		elif t == 2:
			data_s = datas_s.data_T #10 snapshots
			format_s = 1

		elif t == 3:
			data_s = datas_s.data_s #4 snapshots
			format_s = 1
		
		elif t == 4:
			data_s = b_data.blade_data
			format_s = 2
			
		else:
			data_s = datas_s.data_U #1024 snapshots
			format_s = 1


#create_ellipses(array ms_1, array ms_2, in res, int offset)
#creates and returns a list of ellipses objects 
#	and corresponding heights of the ellipses
def create_ellipses(ms_1, ms_2, res, offset):
	
	peaks1, _ = find_peaks((ms_1), height=10)
	peaks2, _ = find_peaks((ms_2), height=10)
	
	temp1 = ms_1[peaks1[0]]
	temp2 = ms_2[peaks2[0]]
	
	if(temp1 > temp2):
		max_h = temp1
	else:
		max_h = temp2
	
	decre1 = (max_h)/res
	
	heights = []
	for i in range(res-offset):
		heights.append(i*decre1+offset)

	
	heights = np.around(heights,1)
	
	chords_1 = (findchords(ms_2, heights))
	chords_2 = (findchords(ms_1, heights))
	
	ells = []
	ells_h = []
	
	#"""
	for i in range(len(heights)):
		if(len(chords_1[i]) == len(chords_2[i])):
			if(len(chords_1[i]) > 0):
				for j in range(0,len(chords_1[i]),2):
					widt = abs(angles[chords_1[i][j+1]]-angles[chords_1[i][j]])
					heig = abs(angles[chords_2[i][j+1]]-angles[chords_2[i][j]])
					e_center_1 = (widt)/2
					e_center_2 = (heig)/2
					ells.append(Ellipse((e_center_1,e_center_2),widt,heig))
					ells_h.append(heights[i])
				
	#"""
	return(ells,ells_h)


#mesh(matrix a, matrix b)
#collapses two nxn meshed matrixes into a single nxn matrix 
#by taking the lowest values
#returns a nxn matrix
#not currently being used
def mesh_2(a,b):
	c = []
	row, col = a.shape
	#print(a.shape)
	for i in range(row):
		c.append([])
		for j in range(col):
			c[i].append(a[i][j]*(a[i][j]<b[i][j])+b[i][j]*(a[i][j]>b[i][j]))
	c = np.array(c)
	return(c)


#findchords(array ms_s1, array heights)
#finds the chords axies needed to create an ellipse object
def findchords(ms_s1, heights):

	#peaks1, _ = find_peaks((ms_s1), height=10)
	ms_s1 = np.around(ms_s1,2)		
	
	chords = []
	list_of_dels = []
	
	#creates list of lists for chords 
	for i in range(len(heights)):
		chords.append([])
	
	#adds points to chords list
	for i in range(ms_s1.size):
		temp = ms_s1[i]
		for j in range(len(heights)):
			if ((temp > (heights[j]-.4)) and (temp < (heights[j]))):
				chords[j].append(i)
				break;
			if (temp < heights[j]-.4): 
				break;
	
	#creates a list of chords to delete
	#"""		
	for i in range(len(chords)):		
		for j in range(len(chords[i])):
			if(len(chords[i])>2):
				if(chords[i][j] == (chords[i][j-1]+1)):
					list_of_dels.append((i,j))
				
	for i in reversed(range(len(list_of_dels))):			
		a1,a2 = list_of_dels[i]
		del chords[a1][a2]
	
	#"""
	
	#removes the first index [0]
	#when length is odd 
	#"""
	list_of_dels.clear()
	
	for i in range(len(chords)):	
		if((len(chords[i])%2) != 0):
			list_of_dels.append((i,0))
	
	for i in reversed(range(len(list_of_dels))):			
		a1,a2 = list_of_dels[i]
		del chords[a1][a2]
	#"""				
	
	return(chords)


#function Normalize_data(matrix data_s)
#normalizes data for use in algorithm
#return data matrix normalized
def Normalize_data(data_s):
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
def steering(doa_signals):
		#mue of steering vector
	mue = (np.arange(number_elements).reshape((number_elements,1)));
	mue = -1j*2*np.pi*separation_distance*mue*np.sin((doa_signals)*np.pi/180);
	steering_v = np.matrix(np.exp(mue));
		#returning steering vector
	return steering_v;


#function find_eg_v(matrix data_s)
#computes eigen analysis of data matrix
#returns eigen vector of if smallest eigen value
def find_eg_v(data_s):
	#create spacial covariance matrix
	global format_s
	
	if(format_s == 2):
		covariance_matrix = (data_s.getH()*data_s)/number_snapshots; 
	else:
		covariance_matrix = (data_s*data_s.getH())/number_snapshots;

	#create Eigen-Decomposition of Covariance matrix
	eigen_val, eigen_vec = LA.eigh(covariance_matrix);

	#sort eigen_val and eigen_vec
	idx = eigen_val.argsort()[::-1];
	eigen_val = eigen_val[idx];
	eigen_vec = eigen_vec[:,idx];

	unc_noise_eigen_vec = eigen_vec[:,number_elements-1]
	return(unc_noise_eigen_vec);

#sets_up_globals(int number_e, int number_s, int seperation_d,
#									int noise_v, float angle_stp)
#defaults number_e = 4, 
#		number_s = 1024, 
#		separation_d = 0.5, 
#		noise_v = 0.4
#		angle_stp = .1
def set_up_globals(number_e = 4, number_s = 1024, 
					separation_d = 0.5, noise_v = 0.4, angle_stp = .1):
					
	global number_elements			#Number of array elements
	global number_snapshots			#Number of snapshots received
	global separation_distance	#Distance between elements in wavelengths
	global noise_variance			#Noise Variance
	#calculate the complete spectrum response, this does not change
	#used in find_music_spectrum()
	global complete_response
	global angles
	global number_signals
	
	angles = (np.arange(-90,90,angle_stp))
	number_elements = number_e;
	number_snapshots = number_s;
	separation_distance = separation_d;
	noise_variance = noise_v;
	complete_response = steering(angles);
	number_signals = len(angles)

#function find_music_spectrum()
#takes data in form of matrix
#computes music DOA spectrum
#returns array music_spectrum
def find_music_spectrum(data_s):

	global complete_response;
	data_s = Normalize_data(data_s)
	
	unc_noise_eigen_vec = find_eg_v(data_s) 
	
	# music algorithm

	#create music_spectrum array
	music_spectrum = [];

	#fill music_spectrum array
	for i in range(0,len(angles)):
		music_spectrum.append((1)/
			((complete_response[:,i].getH()* unc_noise_eigen_vec* 
			unc_noise_eigen_vec.getH()* complete_response[:,i]).item()));
	
	music_spectrum = np.around(music_spectrum, 4) 
	music_spectrum = np.real(music_spectrum)		#returns only real part os spectrum
	music_spectrum = np.absolute(music_spectrum)
	return(music_spectrum)


#animate function is called by animation.FuncAnimation()
#take index i -is not used 
#currently only supports one data set and one peak 
#plots in 2d as default unless set up differently in set_up_plot()
def animate(i):
	global plot_type
	global angles
	global data_s
	global signal
	
	music_spectrum = find_music_spectrum(data_s)
	peaks,_= find_peaks((music_spectrum),height = 11)
	
	
	#plots signal point
	temp = (angles[peaks])*np.pi/180
	signal = ax.plot(temp,2, c='r', marker = 'o')
	
	if(plot_type == 2):	#3d-plotting
		ells, ells_h = create_ellipses(music_spectrum, music_spectrum, 50, 3)
		for i in range(len(ells)):
			ax1.add_patch(ells[i])
			art3d.pathpatch_2d_to_3d(ells[i], z=ells_h[i], zdir="z")

	else:	#2d-plotting
		ax1.plot(angles, music_spectrum, 'g')
		ax1.plot(angles[peaks], music_spectrum[peaks], 'r', marker = 'x')
		

