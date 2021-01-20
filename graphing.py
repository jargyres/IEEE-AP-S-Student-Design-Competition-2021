"""
FileName: graphing.py
##############################
created : Jan 19, 2021 

last edit : 
	date: Jan 19, 2021
	reason: creation
				
lasteditor:
	William Wagner
##############################	
File Description:
	visualization for DOA algorithm
Next Steps:
	-code testing and timing
	-optimization
	-retest and time
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
#from mpl_toolkits.mplot3d import axes3d
from matplotlib import animation
#from matplotlib import cm
from matplotlib.patches import Ellipse
#from matplotlib.text import TextPath
#from matplotlib.transforms import Affine2D
import mpl_toolkits.mplot3d.art3d as art3d



#plotting


class graphing():


	#set_up_plot(string vers)
	#sets up the plot based on 'vers'
	#strings available are '2d' and '3d'
	#can set up a 2d and 3d graph
	#also sets up radial graph
	#2d plot is default
	def __init__(self, vers = '2d', vector = 0, angle_step = .1):
		self.angle_step = angle_step
		self.response = vector
		self.fig= plt.figure()
		self.angles = (np.arange(-90,90,angle_step))
		
		#radial graph
		#"""
		self.ax = self.fig.add_subplot(1,2,1,projection = 'polar' )

		#formatting for radial graph
		self.ax.set_rmax(4)
		self.ax.set(rlim =(0,5))
		self.ax.set_rticks([1,2,3,4])
		self.ax.set_theta_offset(offset = np.pi/2)
		self.ax.set_thetamin(90)
		self.ax.set_thetamax(-90)
		self.ax.grid(True)
		self.ax.set_theta_direction(-1)
		#"""
		
		if vers == '3d':		#3d-plotting
			self.plot_type = 2
			self.ax1 = self.fig.add_subplot(1,2,2,projection = '3d')
			self.ax1.set_xlabel('horizontal angle')
			self.ax1.set_ylabel('vertical angle')
			self.ax1.set_zlabel('Power')
			self.ax1.set_zlim(0,20)
			self.ax1.set_ylim(-90,90)
			self.ax1.set_xlim(90,-90)
		
		else:		#2d-plotting
			self.plot_type = 1
			self.ax1= self.fig.add_subplot(1,2,2)
			self.ax1.set_xlabel('Angle of Arival')
			self.ax1.set_ylabel('Power')


		reciver = self.ax.plot(0,0, c='g', marker = 'x')	#plots point for receiver
	

	#plots a single iteration of animate()
	def plot_graph(self):
		self.animate(0)
		plt.show()

	
	#plots a continuous animation of animate() 
	def plot_live_graph(self):	
		ani = animation.FuncAnimation(self.fig, self.animate, interval=3,)
		plt.show()


	#create_ellipses(array ms_1, array ms_2, in res, int offset)
	#creates and returns a list of ellipses objects 
	#	and corresponding heights of the ellipses
	def create_ellipses(self,ms_1, ms_2, res, offset):
	
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
	
		chords_1 = (self.findchords(ms_2, heights))
		chords_2 = (self.findchords(ms_1, heights))
	
		ells = []
		ells_h = []
	
		#"""
		for i in range(len(heights)):
			if(len(chords_1[i]) == len(chords_2[i])):
				if(len(chords_1[i]) > 0):
					for j in range(0,len(chords_1[i]),2):
						widt = abs(self.angles[chords_1[i][j+1]]-self.angles[chords_1[i][j]])
						heig = abs(self.angles[chords_2[i][j+1]]-self.angles[chords_2[i][j]])
						e_center_1 = (widt)/2
						e_center_2 = (heig)/2
						ells.append(Ellipse((e_center_1,e_center_2),widt,heig))
						ells_h.append(heights[i])
				
		#"""
		return(ells,ells_h)


	#findchords(array ms_s1, array heights)
	#finds the chords axies needed to create an ellipse object
	def findchords(self,ms_s1, heights):

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


	#animate function is called by animation.FuncAnimation()
	#take index i -is not used 
	#currently only supports one data set and one peak 
	#plots in 2d as default unless set up differently in set_up_plot()
	def animate(self,i):

		music_spectrum = self.response
		peaks,_= find_peaks((music_spectrum),height = 11)
	
	
		#plots signal point
		temp = (self.angles[peaks])*np.pi/180
		signal = self.ax.plot(temp,2, c='r', marker = 'o')
	
		if(self.plot_type == 2):	#3d-plotting
			ells, ells_h = self.create_ellipses(music_spectrum, music_spectrum, 50, 3)
			for i in range(len(ells)):
				self.ax1.add_patch(ells[i])
				art3d.pathpatch_2d_to_3d(ells[i], z=ells_h[i], zdir="z")

		else:	#2d-plotting
			self.ax1.plot(self.angles, music_spectrum, 'g')
			self.ax1.plot(self.angles[peaks], music_spectrum[peaks], 'r', marker = 'x')
		
		
		
		
		
		