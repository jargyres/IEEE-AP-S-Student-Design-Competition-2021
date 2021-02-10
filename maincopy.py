
import time
import numpy as np
from scipy.signal import find_peaks

import graphing
import DOA

A = time.time_ns()



B = time.time_ns()
print(B-A)

test = DOA.DOA(number_e = 2)
graphingtest = graphing.graphing(vers = '2d', angle_step = test.angle_step)
"""
A = time.time_ns()
test.data_set(filename = 'master.csv')
test.find_music_spectrum()
graphingtest.plot_graph(vector = test.response)
B = time.time_ns()
print(B-A)

#
#

graphingtest = graphing.graphing(vers = '2d', angle_step = test.angle_step)
A = time.time_ns()
test.data_set(filename = 'master1.csv')
test.find_music_spectrum()
graphingtest.plot_graph(vector = test.response)
B = time.time_ns()
print(B-A)

#
#

graphingtest = graphing.graphing(vers = '2d', angle_step = test.angle_step)
A = time.time_ns()
test.data_set(filename = 'master2.csv')
test.find_music_spectrum()
graphingtest.plot_graph(vector = test.response)
B = time.time_ns()
print(B-A)

#
"""
#"""


graphingtest = graphing.graphing(vers = '2d', angle_step = test.angle_step)
A = time.time_ns()
test.data_set(filename = 'bluetooth.csv')
test.find_music_spectrum()
graphingtest.plot_graph(vector = test.response)
B = time.time_ns()
print(B-A)
#"""
#
#
"""
test.data_set(filename = 'slave1.csv')
test.find_music_spectrum()
graphingtest = graphing.graphing(vers = '2d', vector = test.response, angle_step = test.angle_step)
graphingtest.plot_graph()

test.data_set(filename = 'slave2.csv')
test.find_music_spectrum()
graphingtest = graphing.graphing(vers = '2d', vector = test.response, angle_step = test.angle_step)
graphingtest.plot_graph()
#"""