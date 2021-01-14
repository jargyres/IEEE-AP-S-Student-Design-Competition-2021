import DOA_algorithm_v2 as DA
import time
import numpy as np
from scipy.signal import find_peaks

#finding time in nano seconds of process 

set = 1		#witch data set to use#
snap = 1024		#number of snapshots to use
ele = 4			#number of elements

DA.data_set(set)
DA.set_up_plot(vers = '3d')


DA.set_up_globals(angle_stp = 1, number_e = ele, number_s = snap)
A = time.time_ns()
DA.find_music_spectrum(DA.data_s)
B = time.time_ns()
print(B-A)



DA.set_up_globals(angle_stp = .75, number_e = ele, number_s = snap)
A = time.time_ns()
DA.find_music_spectrum(DA.data_s)
B = time.time_ns()
print(B-A)



DA.set_up_globals(angle_stp = .5, number_e = ele, number_s = snap)
A = time.time_ns()
DA.find_music_spectrum(DA.data_s)
B = time.time_ns()
print(B-A)



DA.set_up_globals(angle_stp = .25, number_e = ele, number_s = snap)
A = time.time_ns()
DA.find_music_spectrum(DA.data_s)
B = time.time_ns()
print(B-A)


"""
DA.set_up_globals(angle_stp = .1, number_e = ele, number_s = snap)
A = time.time_ns()
DA.find_music_spectrum(DA.data_s)
B = time.time_ns()
print(B-A)
"""

DA.plot_graph()