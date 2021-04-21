import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from matplotlib import animation
from matplotlib.patches import Ellipse
import mpl_toolkits.mplot3d.art3d as art3d
import matplotlib.gridspec as gridspec
from numpy.ctypeslib import ndpointer
import ctypes as ct
import time
import subprocess
import os
from os import path
from DOA import DOA


# C to python
#receivers = ct.CDLL('./lib.so')



#global variables
angles = (np.arange(-90,90,.1))
radial_V = 0
linear_2D_V = 0
linear_2D_peaks_V = 0
radial_H = 0
linear_2D_H = 0
linear_2D_peaks_H = 0
graph_3D = 0
graph_3D_peaks = 0
ax0_0 = 0
ax0_1 = 0
ax1_0 = 0
ax1_1 = 0

# figure Setup will remain global
fig = plt.figure(figsize=(9,7))
gs0 = fig.add_gridspec(1, 2)
#gs0.update(left=0.06, right=0.94, top = .96, bottom = .08) #need to run on pi to adjust
gs00 = gs0[0].subgridspec(2, 1)
gs01 = gs0[1].subgridspec(2, 1)



#radial Graph setup
def setup_radial():
	global fig
	global ax0_0
	global ax0_1
	
	ax0_0 = fig.add_subplot(gs00[0],projection = 'polar') 	#polar plot vertical
	ax0_1 = fig.add_subplot(gs00[1],projection = 'polar') 	#polar plot horizontal
	
	#Vertical setup
	ax0_0.set_xlabel('Vertical Angle')
	ax0_0.set_rmax(21)
	ax0_0.set(rlim =(0,21))
	ax0_0.set_rticks(np.linspace(0,20,3))
	#ax0_0.set_theta_offset(offset = np.pi/2)
	ax0_0.set_thetamin(90)
	ax0_0.set_thetamax(-90)
	ax0_0.grid(True)
	ax0_0.set_theta_direction(-1)

	#Horizontal setup
	ax0_1.set_xlabel('Horizontal Angle')
	ax0_1.set_rmax(21)
	ax0_1.set(rlim =(0,21))
	ax0_1.set_rticks(np.linspace(0,20,3))
	ax0_1.set_theta_offset(offset = np.pi/2)
	ax0_1.set_thetamin(90)
	ax0_1.set_thetamax(-90)
	ax0_1.grid(True)
	ax0_1.set_theta_direction(1)


#2D line plot setup
def setup_Linear():
	global fig
	global ax1_0
	global ax1_1
	
	ax1_0 = fig.add_subplot(gs01[0])						#2D plot vertical 
	ax1_1 = fig.add_subplot(gs01[1])						#2D plot horizontal
	
	ax1_0.set_xlabel('Angle of Arival')
	ax1_0.set_ylabel('Power')
	ax1_1.set_xlabel('Angle of Arival')
	ax1_1.set_ylabel('Power')


#3D graph setup
def setup_3D():
	
	global ax1_0
	
	ax1_0 = fig.add_subplot(gs01[0:],projection = '3d')		#3D plot
	
	ax1_0.set_xlabel('Horizontal angle')
	ax1_0.set_ylabel('Vertical angle')
	ax1_0.set_zlabel('Power')
	ax1_0.set_zlim(0,20)
	ax1_0.set_ylim(90,-90)
	ax1_0.set_xlim(-90,90)


#findchords(array ms_s1, array heights)
#finds the chords axies needed to create an ellipse object
def findchords(ms_s1, heights):
		
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


#create_ellipses(array ms_1, array ms_2, in res, int offset)
#creates and returns a list of ellipses objects 
#	and corresponding heights of the ellipses
def create_ellipses(ms_1, ms_2, res, offset):
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
	chords_1 = (findchords(ms_2, heights))
	chords_2 = (findchords(ms_1, heights))
	
	ells = []
	ells_h = []
	
	#"""
	#create ellipse based on height and chords found
	for i in range(len(heights)):
		if(len(chords_1[i]) == len(chords_2[i])):
			if(len(chords_1[i]) > 0):
				for j in range(0,len(chords_1[i]),2):
					widt = abs(angles[chords_1[i][j]]-angles[chords_1[i][j+1]])
					heig = abs(angles[chords_2[i][j]]-angles[chords_2[i][j+1]])
					e_center_1 = angles[chords_1[i][j]] + (widt)/2
					e_center_2 = angles[chords_2[i][j]] + (heig)/2
					ells.append(Ellipse((e_center_1,e_center_2),widt,heig))
					ells_h.append(heights[i])
				
	#"""
	return(ells,ells_h)


#start plots
def start_plots_2D():
	global radial_V
	global linear_2D_V
	global linear_2D_peaks_V
	global radial_H
	global linear_2D_H
	global linear_2D_peaks_H
	global ax0_0
	global ax0_1
	global ax1_0
	global ax1_1
	
	radial_V, = ax0_0.plot([],[], 'r', marker = 'o', ls = '')
	linear_2D_V, = ax1_0.plot(angles, np.random.uniform(0,20,len(angles)))
	linear_2D_peaks_V, = ax1_0.plot([],[], 'r', marker = 'x', ls = '')
	radial_H, = ax0_1.plot([],[], 'r', marker = 'o', ls = '')
	linear_2D_H, = ax1_1.plot(angles, np.random.uniform(0,20,len(angles)))
	linear_2D_peaks_H, = ax1_1.plot([],[], 'r', marker = 'x', ls = '')


#start plots
def start_plots_3D():
	global radial_V
	global radial_H
	global graph_3D
	global graph_3D_peaks
	global ax0_0
	global ax0_1
	global ax1_0
	
	
	#graph_3D, = ax1_0.plot([],[],[])
	#graph_3D_peaks, = ax1_0([],[],[])
	
	#ax1_0.set_zlim(0,(mark)+5)
			
	#ax1.plot([], [], [], 'r', marker = 'x') 			#marks peak
	#ax1.plot([],[],[0,0],'r') 							#plots line on H_angle
	#ax1.plot([],[],[0,0],'r')							#plots line on V_angle
	#ax1.plot([],[],[],'r')								#plots vertical line to peak
	
	#plot background 2D
	#ax1.plot(xs = angles,zs = music_spectrum_1, ys = np.linspace(-90,-90,len(angles)))
	#ax1.plot(ys = angles,zs = music_spectrum_2, xs = np.linspace(-90,-90,len(angles)))
	radial_V, = ax0_0.plot([],[], 'r', marker = 'o', ls = '')
	radial_H, = ax0_1.plot([],[], 'r', marker = 'o', ls = '')
	

#setup_program_2D()
def setup_program_2D():
	setup_radial()
	setup_Linear()
	start_plots_2D()


#setup_program_3D()
def setup_program_3D():
	setup_radial()
	setup_3D()
	start_plots_3D()


#testing function
def random():
	return(np.random.uniform(0,20,len(angles)))
	



#Animation function 3D
# not complete need to find a way to update patches
# Will be passed to "animation.FuncAnimation()"
# Will be main event loop. 
# Can create a separate animate for 3d plotting
# Should call BladeRX receive function 
# Then music spectrum then update data on the figures
# def Animate_3D(i):

# 	res_3d = 50 
# 	offset_3d=3

# 	music_spectrum_V = random()	#replace with find_music_spectrum(results)
# 	music_spectrum_H = random()
	
# 	peaks_V,_= find_peaks((music_spectrum_V),height = 0)
# 	peaks_H,_= find_peaks((music_spectrum_H),height = 0)
	
# 	radial_V.set_data(((angles[peaks_V])*np.pi/180),music_spectrum_V[peaks_V])
# 	radial_H.set_data(((angles[peaks_H])*np.pi/180),music_spectrum_H[peaks_H])
	
# 	ells, ells_h = create_ellipses(music_spectrum_V, music_spectrum_H,	
# 												res_3d, offset_3d)

# 	for l in range(len(ells)):
# 		ax1_0.add_patch(ells[l])
# 		art3d.pathpatch_2d_to_3d(ells[l], z=ells_h[l], zdir="z")



# Animation function 2D 
# Will be passed to "animation.FuncAnimation()"
# Will be main event loop. 
# Can create a separate animate for 3d plotting
# Should call BladeRX receive function 
# Then music spectrum then update data on the figures
# def Animate_2D(i):
	
# 	global radial_V
# 	global linear_2D_V
# 	global linear_2D_peaks_V
# 	global radial_H
# 	global linear_2D_H
# 	global linear_2D_peaks_H
# 	#results = receive() 
	
# 	music_spectrum_V = random()	#replace with find_music_spectrum(results)
# 	music_spectrum_H = random()
	
# 	peaks_V,_= find_peaks((music_spectrum_V),height = 0)
# 	peaks_H,_= find_peaks((music_spectrum_H),height = 0)
	
# 	linear_2D_V.set_data(angles,music_spectrum_V)
# 	linear_2D_peaks_V.set_data(angles[peaks_V],music_spectrum_V[peaks_V])
# 	radial_V.set_data(((angles[peaks_V])*np.pi/180),music_spectrum_V[peaks_V])
# 						#np.linspace(3,3,len(peaks)))
# 	linear_2D_H.set_data(angles,music_spectrum_H)
# 	linear_2D_peaks_H.set_data(angles[peaks_H],music_spectrum_H[peaks_H])
# 	radial_H.set_data(((angles[peaks_H])*np.pi/180),music_spectrum_H[peaks_H])
# 						#np.linspace(3,3,len(peaks)))



#setup_program_3D()
#ani = animation.FuncAnimation(fig, Animate_3D, interval=4,repeat=False)

# setup_program_2D()
# ani = animation.FuncAnimation(fig, Animate_2D, interval=4,repeat=False)
# #"""

# plt.show()



#########################################################################


dirname = os.path.dirname(__file__)
master_filename = os.path.join(dirname, 'master.csv')
slave_filename = os.path.join(dirname, 'slave.csv')




"""
Before running the script, you need to install screen, open two terminals and run:

screen -S master
screen -S slave

Then open the bladeRF devices on their respective screen sessions

Screen gives us the ability to send commands to another process, so we use this to send
normal bladeRF commands to the bladeRF-cli program

"""
def openDevices():
    commands = ["screen", "-S", "", "-p", "0", "-X", "stuff", ""]

    master_init_commands = [
        "set frequency rx 2.28G^M",
        "set samplerate rx 6M^M",
        "set clock_out enable^M",
		"set gain rx 50^M",
        "trigger j51-1 tx master^M",
        "trigger j51-1 rx slave^M",
        "rx config file={} format=csv n=2048 channel=1,2 timeout=60s^M".format(master_filename)
    ]

    slave_init_commands = [
        "set frequency rx 2.28G^M",
        "set samplerate rx 6M^M",
        "set clock_sel external^M",
		"set gain rx 50^M",
        "trigger j51-1 rx slave^M",
        "rx config file={} format=csv n=2048 channel=1,2 timeout=60s^M".format(slave_filename)
    ]

    print("Opening and Configuring Master")

    for cmd in master_init_commands:
        commands[2] = "master"
        commands[7] = cmd

        subprocess.call(commands)
        time.sleep(1)

    print("Opening and Configuring Slave")

    for cmd in slave_init_commands:
        commands[2] = "slave"
        commands[7] = cmd

        subprocess.call(commands)
        time.sleep(1)

def receive_rx():
    commands = ["screen", "-S", "", "-p", "0", "-X", "stuff", ""]

    #First Reconfigure the Devices for the master slave
    commands[2] = "master"
    commands[7] = "trigger j51-1 tx master^M"
    subprocess.call(commands)

    commands[2] = "master"
    commands[7] = "trigger j51-1 rx slave^M"
    subprocess.call(commands)

    commands[2] = "slave"
    commands[7] = "trigger j51-1 rx slave^M"
    subprocess.call(commands)

    #Then start both rx processes
    commands[2] = "master"
    commands[7] = "rx start^M"
    subprocess.call(commands)

    commands[2] = "slave"
    commands[7] = "rx start^M"
    subprocess.call(commands)

    #After starting the rx processes, we can send the fire signal from the master device
    commands[2] = "master"
    commands[7] = "trigger j51-1 tx fire^M"
    subprocess.call(commands)

    time.sleep(0.01)

#Use this to open the devices

# openDevices()

# print("Finished Setting Up Devices, ready to receive")
# input()

# receive_rx()

# for i in range(10):
#     print("Receiving File {}".format(i))
#     input()
#     receive_rx(i)


# print("done")




# for i in range(100):

#     receive_rx()

#     if path.exists(master_filename) and path.exists(slave_filename):

#         # print("Path Exists After Receiving")


#         # print("filename is {}".format(master_filename))


#         masterDOA = DOA()

#         slaveDOA = DOA()

#         masterDOA.data_set(filename=master_filename)

#         slaveDOA.data_set(filename=master_filename)

#         dataM = masterDOA.data_s

#         dataS = slaveDOA.data_s

#         # print(np.shape(dataM))

#         print(dataM, end=' ')
#         print(dataS)

#         if path.exists(master_filename) and path.exists(slave_filename):
#             commands = ["rm", "{}".format(master_filename), "{}".format(slave_filename)]
#             subprocess.call(commands)

# else:

#     print("Path Doesnt Exist After Receiving")


# doa.data_set(filename=master_filename)

# print(np.shape(doa.data_s))

# print(doa.data_s)

# if path.exists(master_filename) and path.exists(slave_filename):
#     commands = ["rm", "{}".format(master_filename), "{}".format(slave_filename)]
#     subprocess.call(commands)


######################################

masterDOA = DOA(number_e=2)

slaveDOA = DOA(number_e=2)
# Animation function 2D 
# Will be passed to "animation.FuncAnimation()"
# Will be main event loop. 
# Can create a separate animate for 3d plotting
# Should call BladeRX receive function 
# Then music spectrum then update data on the figures
def Animate_2D(i):
	
	global masterDOA
	global slaveDOA
	global radial_V
	global linear_2D_V
	global linear_2D_peaks_V
	global radial_H
	global linear_2D_H
	global linear_2D_peaks_H
	#results = receive() 

	receive_rx()

	if path.exists(master_filename) and path.exists(slave_filename):

        # print("Path Exists After Receiving")


        # print("filename is {}".format(master_filename))


		

		masterDOA.data_set(filename=master_filename)

		slaveDOA.data_set(filename=slave_filename)

        # dataM = masterDOA.data_s

        # dataS = slaveDOA.data_s

        # print(np.shape(dataM))

        # print(dataM, end=' ')
        # print(dataS)

		if path.exists(master_filename) and path.exists(slave_filename):
			commands = ["rm", "{}".format(master_filename), "{}".format(slave_filename)]
			subprocess.call(commands)

	masterDOA.find_music_spectrum()
	slaveDOA.find_music_spectrum()

	music_spectrum_V = masterDOA.response
	music_spectrum_H = slaveDOA.response

	print(np.shape(music_spectrum_V))
	print(np.shape(music_spectrum_H))
	
	peaks_V,_= find_peaks((music_spectrum_V),height = 0)
	peaks_H,_= find_peaks((music_spectrum_H),height = 0)
	
	linear_2D_V.set_data(angles,music_spectrum_V)
	linear_2D_peaks_V.set_data(angles[peaks_V],music_spectrum_V[peaks_V])
	radial_V.set_data(((angles[peaks_V])*np.pi/180),music_spectrum_V[peaks_V])
						#np.linspace(3,3,len(peaks)))
	linear_2D_H.set_data(angles,music_spectrum_H)
	linear_2D_peaks_H.set_data(angles[peaks_H],music_spectrum_H[peaks_H])
	radial_H.set_data(((angles[peaks_H])*np.pi/180),music_spectrum_H[peaks_H])
						#np.linspace(3,3,len(peaks)))



#setup_program_3D()
#ani = animation.FuncAnimation(fig, Animate_3D, interval=4,repeat=False)
openDevices()

setup_program_2D()
ani = animation.FuncAnimation(fig, Animate_2D, interval=4,repeat=False)
#"""

plt.show()
