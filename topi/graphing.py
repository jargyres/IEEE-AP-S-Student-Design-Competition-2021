"""
FileName: graphing.py
##############################
created : Jan 19, 2021 

last edit : 
	date: Mar 3, 2021
	reason: creation
				
lasteditor:
	William Wagner
##############################	
File Description:
	visualization for DOA algorithm
Next Steps:
	-need to determine which axis is which
	-add documentation
	-different cases for multiple peaks ???
	-code testing and timing
	-optimization
	-retest and time
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from matplotlib import animation
from matplotlib.patches import Ellipse
import mpl_toolkits.mplot3d.art3d as art3d
import matplotlib.gridspec as gridspec


class graphing():


	#set_up_plot(string vers)
	#sets up the plot based on 'vers'
	#strings available are '2d' and '3d'
	#can set up a 2d and 3d graph
	#also sets up radial graph
	#2d plot is default
	def __init__(self, vers = '2d', angle_step = .1, num_of_dev = 1):
		self.angle_step = angle_step
		self.fig= plt.figure(figsize=(9,7))
		gs0 = self.fig.add_gridspec(1, 2)
		gs00 = gs0[0].subgridspec(2, 1)
		gs01 = gs0[1].subgridspec(2, 1)
		#self.fig.subplots_adjust(left=.05,right=.98,top=.98,bottom=.1)
		self.angles = (np.arange(-90,90,angle_step))
		
		#radial graphs setup
		if(num_of_dev == 1):
		
			self.axr1 = self.fig.add_subplot(gs00[0:],projection = 'polar' )
			#formatting for radial graph
			self.axr1.set_rmax(4)
			self.axr1.set(rlim =(0,5))
			self.axr1.set_rticks([1,2,3,4])
			self.axr1.set_theta_offset(offset = np.pi/2)
			self.axr1.set_thetamin(90)
			self.axr1.set_thetamax(-90)
			self.axr1.grid(True)
			self.axr1.set_theta_direction(-1)
			
			reciver1 = self.axr1.plot(0,0, c='g', marker = 'x')	#plots point for receiver
			
		elif (num_of_dev == 2):
			self.axr1 = self.fig.add_subplot(gs00[0],projection = 'polar' )
			#formatting for 1st radial graph
			self.axr1.set_rmax(4)
			self.axr1.set(rlim =(0,5))
			self.axr1.set_rticks([1,2,3,4])
			self.axr1.set_xlabel('Horizontal Angle')
			self.axr1.set_theta_offset(offset = np.pi/2)
			self.axr1.set_thetamin(90)
			self.axr1.set_thetamax(-90)
			self.axr1.grid(True)
			self.axr1.set_theta_direction(-1)
			
			self.axr2 = self.fig.add_subplot(gs00[1],projection = 'polar' )
			#formatting for 2nd radial graph
			self.axr2.set_rmax(4)
			self.axr2.set(rlim =(0,5))
			self.axr2.set_rticks([1,2,3,4])
			self.axr2.set_xlabel('Vertical Angle')
			self.axr2.set_thetamin(90)
			self.axr2.set_thetamax(-90)
			self.axr2.grid(True)
			self.axr2.set_theta_direction(1)
			reciver1 = self.axr1.plot(0,0, c='g', marker = 'x')	#plots points for receivers
			reciver2 = self.axr2.plot(0,0, c='g', marker = 'x')
		
		else:
			self.axr1 = self.fig.add_subplot(gs00[0:],projection = 'polar' )
			#formatting for radial graph
			self.axr1.set_rmax(4)
			self.axr1.set(rlim =(0,5))
			self.axr1.set_rticks([1,2,3,4])
			self.axr1.set_theta_offset(offset = np.pi/2)
			self.axr1.set_thetamin(90)
			self.axr1.set_thetamax(-90)
			self.axr1.grid(True)
			self.axr1.set_theta_direction(-1)
		
		
		#2d and 3d plotting setup		
		if vers == '3d':		#3d-plotting
			self.plot_type = 2
			self.ax1 = self.fig.add_subplot(gs01[0:],projection = '3d')
			self.ax1.set_xlabel('Horizontal angle')
			self.ax1.set_ylabel('Vertical angle')
			self.ax1.set_zlabel('Power')
			self.ax1.set_zlim(0,20)
			self.ax1.set_ylim(90,-90)
			self.ax1.set_xlim(-90,90)
		
		else:	#2d-plotting
			self.plot_type = 1	
			if(num_of_dev == 1):
				
				self.ax1_0 = self.fig.add_subplot(gs01[0:])
				self.ax1_0.set_xlabel('Angle of Arival')
				self.ax1_0.set_ylabel('Power')
			
			elif (num_of_dev == 2):
				
				self.ax1_0 = self.fig.add_subplot(gs01[0])
				self.ax1_0.set_xlabel('Horizontal Angle of Arival')
				self.ax1_0.set_ylabel('Power')
				
				self.ax1_1 = self.fig.add_subplot(gs01[1])
				self.ax1_1.set_xlabel('Vertical Angle of Arival')
				self.ax1_1.set_ylabel('Power')
			
			else:
			
				self.ax1_0 = self.fig.add_subplot(gs01[0:])
				self.ax1_0.set_xlabel('Angle of Arival')
				self.ax1_0.set_ylabel('Power')
				
		

	#plots a single iteration of animate()
	def plot_graph(self,vector1 = None , vector2 = None):
		if (vector1 is not None and vector2 is None):
			self.animate_1(0,vector1)
		if (vector1 is None and vector2 is not None):
			self.animate_1(0,vector2)
		if (vector1 is not None and vector2 is not None):
			self.animate_2(music_spectrum_1 = vector1, music_spectrum_2 = vector2, i=0 )
		plt.show()

	#not sure if needed
	#plots a continuous animation of animate() 
	def plot_live_graph(self, vector):	
		ani = animation.FuncAnimation(self.fig, self.animate_1, interval=3, fargs=(0,vector))
		plt.show()


	#create_ellipses(array ms_1, array ms_2, in res, int offset)
	#creates and returns a list of ellipses objects 
	#	and corresponding heights of the ellipses
	def create_ellipses(self,ms_1, ms_2, res, offset):
		#find max height betwween two sets
		peaks1, _ = find_peaks((ms_1), height=0)
		peaks2, _ = find_peaks((ms_2), height=0)
	
		temp1 = ms_1[peaks1[0]]
		temp2 = ms_2[peaks2[0]]
	
		if(temp1 > temp2):
			max_h = temp1
		else:
			max_h = temp2
	
		decre1 = (max_h)/res
		
		#create an arrary of heights to find chords at
		heights = []
		for i in range(res-offset):
			heights.append(i*decre1+offset)

	
		heights = np.around(heights,1)
		
		#create list of chords a specific heights 
		chords_1 = (self.findchords(ms_2, heights))
		chords_2 = (self.findchords(ms_1, heights))
	
		ells = []
		ells_h = []
	
		#"""
		#create ellipse based on height and chords found
		for i in range(len(heights)):
			if(len(chords_1[i]) == len(chords_2[i])):
				if(len(chords_1[i]) > 0):
					for j in range(0,len(chords_1[i]),2):
						widt = abs(self.angles[chords_1[i][j]]-self.angles[chords_1[i][j+1]])
						heig = abs(self.angles[chords_2[i][j]]-self.angles[chords_2[i][j+1]])
						e_center_1 = self.angles[chords_1[i][j]] + (widt)/2
						e_center_2 = self.angles[chords_2[i][j]] + (heig)/2
						ells.append(Ellipse((e_center_1,e_center_2),widt,heig))
						ells_h.append(heights[i])
				
		#"""
		return(ells,ells_h)


	#findchords(array ms_s1, array heights)
	#finds the chords axies needed to create an ellipse object
	def findchords(self,ms_s1, heights):

		
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


#need two animate functions one for a single array and one for 2 arrays

	#animate_1 function is called by animation.FuncAnimation()
	#take index i -is not used 
	#currently only supports one data set and one peak 
	#plots in 2d as default unless set up differently in set_up_plot()
	def animate_1(self, i, music_spectrum, res_3d = 50, offset_3d=3):


		peaks,_= find_peaks((music_spectrum),height = 10)
		#print(music_spectrum[peaks])
		angle_1 = self.angles[peaks]
		music_1 = music_spectrum[peaks]
		#plots signal point in radial graph
		temp = (angle_1)*np.pi/180
		# print(np.shape(temp))
		threearray = np.full(np.shape(temp), 3)
		signal = self.axr1.plot(temp, threearray, c='r', marker = 'o')
	
		if(self.plot_type == 2):	#3d-plotting
			self.ax1.set_zlim(0,(music_1)+5)
			self.ax1.plot(angle_1, angle_1, music_1, 'r', marker = 'x')
			self.ax1.plot([90,int(angle_1)],[int(angle_1), int(angle_1)],[0,0],'r')
			self.ax1.plot([int(angle_1),int(angle_1)],[90, int(angle_1)],[0,0],'r')
			self.ax1.plot([int(angle_1),int(angle_1)],[int(angle_1),int(angle_1)],[0,int(music_1)],'r')
			self.ax1.plot(xs = self.angles,zs = music_spectrum, ys = np.linspace(-90,-90,len(self.angles)))
			self.ax1.plot(ys = self.angles,zs = music_spectrum, xs = np.linspace(-90,-90,len(self.angles)))
			ells, ells_h = self.create_ellipses(music_spectrum, music_spectrum, res_3d, offset_3d)
			for i in range(len(ells)):
				self.ax1.add_patch(ells[i])
				art3d.pathpatch_2d_to_3d(ells[i], z=ells_h[i], zdir="z")

		else:	#2d-plotting
			self.ax1_0.plot(self.angles, music_spectrum, 'g')
			self.ax1_0.plot(angle_1, music_1, 'r', marker = 'x')
		
		#need to figure out witch is vertical and horizontal 
		
	#animate_2 function is called by animation.FuncAnimation()
	#take index i -is not used 
	#currently only supports one data set and one peak 
	#plots in 2d as default unless set up differently in set_up_plot()
	#takes two spectrum responses  
	def animate_2(self, i , music_spectrum_1 = None, music_spectrum_2 = None, res_3d = 50, offset_3d=3):
		
		if(music_spectrum_1 is None or music_spectrum_2 is None):
			return(-1,"requirement not met")
			
		peaks_1,_= find_peaks((music_spectrum_1),height = 0)
		peaks_2,_= find_peaks((music_spectrum_2),height = 0)
		#print(music_spectrum[peaks])
	
		angle_1 = self.angles[peaks_1]
		angle_2 = self.angles[peaks_2]
		music_1 = music_spectrum_1[peaks_1]
		music_2 = music_spectrum_2[peaks_2]
		
		mark = (music_1*(music_1>=music_2)) + (music_2*(music_1<music_2))
		#plots signal point in radial graph
		temp = (self.angles[peaks_1])*np.pi/180
		signal = self.axr1.plot(temp,3, c='r', marker = 'o')
		
		temp = (self.angles[peaks_2])*np.pi/180
		signal = self.axr2.plot(temp,3, c='r', marker = 'o')
		
		
	#either need to not support 2d or make 2 2d graphs
		if(self.plot_type == 2):	#3d-plotting
			self.ax1.set_zlim(0,(mark)+5)
			
			self.ax1.plot(angle_1, angle_2, mark, 'r', marker = 'x')
			self.ax1.plot([90,int(angle_1)],[int(angle_1), int(angle_1)],[0,0],'r')
			self.ax1.plot([int(angle_2),int(angle_2)],[90, int(angle_2)],[0,0],'r')
			self.ax1.plot([int(angle_1),int(angle_1)],[int(angle_2),int(angle_2)],[0,int(mark)],'r')
			self.ax1.plot(xs = self.angles,zs = music_spectrum_1, ys = np.linspace(-90,-90,len(self.angles)))
			self.ax1.plot(ys = self.angles,zs = music_spectrum_2, xs = np.linspace(-90,-90,len(self.angles)))
			ells, ells_h = self.create_ellipses(music_spectrum_1, music_spectrum_2, res_3d, offset_3d)
			for i in range(len(ells)):
				self.ax1.add_patch(ells[i])
				art3d.pathpatch_2d_to_3d(ells[i], z=ells_h[i], zdir="z")

		else:	#2d-plotting
			self.ax1_0.plot(self.angles, music_spectrum_1, 'g')
			self.ax1_0.plot(angle_1, music_1, 'r', marker = 'x')
			
			self.ax1_1.plot(self.angles, music_spectrum_2, 'g')
			self.ax1_1.plot(angle_2, music_2, 'r', marker = 'x')
			
		
		
		