import sys
import os
import threading
from multiprocessing.pool import ThreadPool
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import numpy as np
import csv
import struct
import time
import subprocess
from subprocess import Popen, PIPE, STDOUT
from os import path, remove
from select import epoll, EPOLLIN





def chunked_read(fobj, chunk_bytes=8 * 1024):
    while True:
        data = fobj.read(chunk_bytes)
        if (not data):
            break
        else:
            yield data

def bin2csv(binfile=None, csvfile=None, chunk_bytes=8 * 1024):
    with open(binfile, 'rb') as b:
        with open(csvfile, 'w') as c:
            csvwriter = csv.writer(c, delimiter=',')
            count = 0
            for data in chunked_read(b, chunk_bytes=chunk_bytes):
                count += len(data)
                for i in range(0, len(data), 8):
                    sig_i, = struct.unpack('<h', data[i:i + 2])
                    sig_q, = struct.unpack('<h', data[i + 2:i + 4])
                    sig_i_port2, = struct.unpack('<h', data[i+4:i + 6])
                    sig_q_port2, = struct.unpack('<h', data[i+6:i + 8])
                    csvwriter.writerow([sig_i, sig_q, sig_i_port2, sig_q_port2])


# def initializeBladeRF(master, slave):
#     line = ""
#     while line not == 

def recieve(process1):


    if path.exists("pythonsamp.sc16q11"):
        remove("pythonsamp.sc16q11")



    process1.stdin.write(b"rx start;\n")
    # process1.communicate()
    # p.stdin.flush()

    print("started")

    # process1.stdin.write(b"q\n")
    # process1.stdin.close()
    # process1.wait()

    # finished = False

    while not path.exists("pythonsamp.sc16q11"):
        pass
    

        
    bin2csv(binfile="pythonsamp.sc16q11", csvfile='csvfile.csv')

    
    f = open('csvfile.csv', 'r')

    dataComplex_Port1 = np.zeros(2048, dtype=complex)
    dataComplex_Port2 = np.zeros(2048, dtype=complex)

    n = 0

    # read I, Q - values into memory
    for line in f:
        list = line.split(',')  # two values with comma inbetween
        
        I_Port1 = int(list[0])
        Q_Port1 = int(list[1])
        I_Port2 = int(list[2])
        Q_Port2 = int(list[3])

        dataComplex_Port1[n] = complex(I_Port1, Q_Port1)
        dataComplex_Port2[n] = complex(I_Port2, Q_Port2)

        n += 1

    return np.array([dataComplex_Port1, dataComplex_Port2])


SAMPLE_RATE = 20e6

NUM_SAMPLES = 2048


bin2csv(binfile="master.sc16q11", csvfile='csvfile1.csv')
bin2csv(binfile="slave.sc16q11", csvfile='csvfile2.csv')



f1 = open('csvfile1.csv', 'r')
f2 = open('csvfile2.csv', 'r')


dataComplex_Port1_1 = np.zeros(2048, dtype=complex)
dataComplex_Port2_1 = np.zeros(2048, dtype=complex)

dataComplex_Port1_2 = np.zeros(2048, dtype=complex)
dataComplex_Port2_2 = np.zeros(2048, dtype=complex)

n = 0

# read I, Q - values into memory
for line in f1:
    list = line.split(',')  # two values with comma inbetween
    
    I_Port1 = int(list[0])
    Q_Port1 = int(list[1])
    I_Port2 = int(list[2])
    Q_Port2 = int(list[3])

    dataComplex_Port1_1[n] = complex(I_Port1, Q_Port1)
    dataComplex_Port2_1[n] = complex(I_Port2, Q_Port2)

    n += 1

# read I, Q - values into memory
for line in f2:
    list = line.split(',')  # two values with comma inbetween
    
    I_Port1 = int(list[0])
    Q_Port1 = int(list[1])
    I_Port2 = int(list[2])
    Q_Port2 = int(list[3])

    dataComplex_Port1_2[n] = complex(I_Port1, Q_Port1)
    dataComplex_Port2_2[n] = complex(I_Port2, Q_Port2)

    n += 1


arr1 = np.array([dataComplex_Port1_1, dataComplex_Port2_1])
arr2 = np.array([dataComplex_Port1_2, dataComplex_Port2_2])


# return np.array([dataComplex_Port1, dataComplex_Port2])


# bin2csv(binfile="pythonsamp.sc16q11", csvfile='csvfile.csv')


# f = open('csvfile.csv', 'r')

# dataComplex_Port1 = np.zeros(2048, dtype=complex)
# dataComplex_Port2 = np.zeros(2048, dtype=complex)

# n = 0

# # read I, Q - values into memory
# for line in f:
#     list = line.split(',')  # two values with comma inbetween
    
#     I_Port1 = int(list[0])
#     Q_Port1 = int(list[1])
#     I_Port2 = int(list[2])
#     Q_Port2 = int(list[3])

#     dataComplex_Port1[n] = complex(I_Port1, Q_Port1)
#     dataComplex_Port2[n] = complex(I_Port2, Q_Port2)

#     n += 1

# return np.array([dataComplex_Port1, dataComplex_Port2])


# p = Popen(["konsole", "-e", "bladeRF-cli", "-i"], stdin = PIPE)


# time.sleep(6)

# p.stdin.write(b"Hello\n")

# print("here")

# arr = recieve(p)

freq = 5e9

f = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr1[0]))

f_carrier = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr1[0])) + (freq)

data_fft = (20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(arr1[0]))) / NUM_SAMPLES)) - 20

carrier_data_1 = [np.transpose(f_carrier), data_fft]

plt.figure(1)

plt.plot(, label='SDR 1 Port 1')


f = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr1[1]))

f_carrier = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr1[1])) + (freq)

data_fft = (20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(arr1[1]))) / NUM_SAMPLES)) - 20

carrier_data_2 = [np.transpose(f_carrier), data_fft]

plt.plot(f_carrier, label='SDR 1 Port 2')


f = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr2[0]))

f_carrier = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr2[0])) + (freq)

data_fft = (20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(arr2[0]))) / NUM_SAMPLES)) - 20

carrier_data_1 = [np.transpose(f_carrier), data_fft]

plt.figure(1)

plt.plot(f_carrier, label='SDR 2 Port 1')


f = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr2[1]))

f_carrier = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr2[1])) + (freq)

data_fft = (20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(arr2[1]))) / NUM_SAMPLES)) - 20

carrier_data_2 = [np.transpose(f_carrier), data_fft]

plt.plot(f_carrier, label='SDR 2 Port 2')


plt.legend()

plt.show()

# f = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr[1]))
# f_carrier = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr[1])) + (freq)
# data_fft = (20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(arr[1]))) / NUM_SAMPLES)) - 20
# carrier_data = [np.transpose(f_carrier), data_fft]


# plt.plot(f_carrier, data_fft, label='Port 2')


# plt.xlabel("Frequency (Hz)")

# plt.ylabel("Power (dB)")

# plt.legend()

# plt.show()



# for i in range(20):

#     print(i)


#     arr = recieve(p)
#     f = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr[0]))
#     f_carrier = np.linspace(-0.5 * SAMPLE_RATE, 0.5 * SAMPLE_RATE, len(arr[0])) + (freq)
#     data_fft = (20 * np.log10(np.abs(np.fft.fftshift(np.fft.fft(arr[0]))) / NUM_SAMPLES)) - 20
#     carrier_data = [np.transpose(f_carrier), data_fft]

#     plt.plot(f_carrier, data_fft)

#     plt.draw()

#     plt.pause(0.01)
    

# p.stdin.write(b"q\n")

# p.stdin.close()

# print("Closing BladeRF Devices")
# p.wait()



# master = subprocess.Popen(["bladeRF-cli -d \"*:serial=35d\" -i"], stdin=subprocess.PIPE, stdout = subprocess.PIPE, shell=True)
# slave = subprocess.Popen(["bladeRF-cli -d \"*:serial=cbd\" -i"], stdin=subprocess.PIPE, stdout = subprocess.PIPE, shell=True)




# read_with_timeout(master.stdout)

# time.sleep(3)

# print("Opened BladeRF")

# process.stdin.write(b"rx config file=master.csv format=csv n=2048 channel=1,2 timeout=60s\n")

# time.sleep(3)

# print("Sent Rx config")


# process.stdin.write(b"rx start\n")

# time.sleep(3)
# print("Sent Rx start")






# while not path.exists("master.csv"):
#     pass



# print("Got file, Exiting From BladeRF")


# print("Closing BladeRF")
# time.sleep(3)
# master.stdin.write(b"q\n")


# print("Exited Successfully")










