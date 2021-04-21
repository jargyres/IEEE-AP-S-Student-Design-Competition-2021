#"""
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
from DOA import DOA
from graphing import graphing
import subprocess
import os
from os import path
import python

# C to python
#receivers = ct.CDLL('./lib.so')


#global variables
angles = (np.arange(-90,90,.1))
radial = 0
linear_2D = 0
linear_2D_peaks = 0

# figure Setup will remain global
fig = plt.figure(figsize=(9,7))
gs0 = fig.add_gridspec(1, 2)
gs0.update(left=0.06, right=0.96, top = .94, wspace = .255)
gs00 = gs0[0].subgridspec(2, 1)
gs01 = gs0[1].subgridspec(2, 1)
ax0_0 = fig.add_subplot(gs00[0:],projection = 'polar') 	#polar plot
ax1_0 = fig.add_subplot(gs01[0:])						#2D plot


#radial Graph setup
def setup_radial():
	ax0_0.set_xlabel('Angle of Arival')
	ax0_0.set_rmax(4)
	ax0_0.set(rlim =(0,4))
	ax0_0.set_rticks(np.linspace(0,4,3))
	ax0_0.set_theta_offset(offset = np.pi/2)
	ax0_0.set_thetamin(90)
	ax0_0.set_thetamax(-90)
	ax0_0.grid(True)
	ax0_0.set_theta_direction(-1)


#2D line plot setup
def setup_Linear():
	ax1_0.autoscale(enable = True)
	ax1_0.set_xlabel('Angle of Arival')
	ax1_0.set_ylabel('Power')


#start plots
def start_plots():
	global radial
	global linear_2D
	global linear_2D_peaks
	radial, = ax0_0.plot([],[], 'r', marker = 'o', ls = '')
	linear_2D, = ax1_0.plot(angles, np.random.uniform(0,20,len(angles)),'b')
	linear_2D_peaks, = ax1_0.plot([],[], 'r', marker = 'x', ls = '')


#testing function
def random():
	return(np.random.uniform(0,20,len(angles)))
	

# setup_program()
# 
def setup_program():
	
	setup_radial()
	setup_Linear()
	start_plots()


from analog_control import receive_rx
import time

import adi
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pandas as pd

sdr = adi.FMComms5(uri="ip:analog.local")

# # Configure properties
sdr.rx_lo = int(2.8e9)
sdr.rx_lo_chip_b = int(2.8e9)
sdr.tx_lo = 2000000000
sdr.tx_lo_chip_b = 2000000000
sdr.tx_cyclic_buffer = True
sdr.tx_hardwaregain_chan0 = -30
sdr.tx_hardwaregain_chip_b_chan0 = -30
sdr.gain_control_mode_chan0 = "slow_attack"
sdr.gain_control_mode_chip_b_chan0 = "slow_attack"
sdr.sample_rate = 1000000

setup_program()
masterDOA = DOA(number_e = 4,angle_stp=.1)
# Animation function 
# Will be passed to "animation.FuncAnimation()"
# Will be main event loop. 
# Can create a separate animate for 3d plotting
# Should call BladeRX receive function 
# Then music spectrum then update data on the figures
def Animate(i):
	global masterDOA
	global sdr
	global radial
	global linear_2D
	global linear_2D_peaks

	A = np.matrix(receive_rx(sdr=sdr))

	masterDOA.data_s = A
	masterDOA.format_s = 1

	# python.receive(masterDOA=masterDOA)
	
	masterDOA.find_music_spectrum()
	if(masterDOA.convergence != 1):
		music_spectrum = masterDOA.response

		peaks,_= find_peaks((music_spectrum),height = 0)

		linear_2D.set_data(angles,music_spectrum)
		linear_2D_peaks.set_data(angles[peaks],music_spectrum[peaks])
		radial.set_data(((angles[peaks])*np.pi/180),np.linspace(3,3,len(peaks)))
							#music_spectrum[peaks])




# python.openDevices()

# Animate(1)
# A = receive_rx(sdr=sdr)
# i = 0
ani = animation.FuncAnimation(fig, Animate, interval=4,repeat=False)

plt.show()
