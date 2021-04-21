import time

import adi
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import pandas as pd

# Create radio
# sdr = adi.FMComms5(uri="ip:analog.local")

# # # Configure properties
# sdr.rx_lo = int(5.8e9)
# sdr.rx_lo_chip_b = int(5.8e9)
# sdr.tx_lo = 2000000000
# sdr.tx_lo_chip_b = 2000000000
# sdr.tx_cyclic_buffer = True
# sdr.tx_hardwaregain_chan0 = -30
# sdr.tx_hardwaregain_chip_b_chan0 = -30
# sdr.gain_control_mode_chan0 = "slow_attack"
# sdr.gain_control_mode_chip_b_chan0 = "slow_attack"
# sdr.sample_rate = 1000000

# Set single DDS tone for TX on one transmitter
# sdr.dds_single_tone(30000, 0.9)

# # Read properties
# fs = int(sdr.sample_rate)
# print("RX LO %s" % (sdr.rx_lo))

# x = sdr.rx()

# plt.psd(x[0], NFFT=1024, Fs=fs, Fc=int(5.8e9))
# plt.psd(x[1], NFFT=1024, Fs=fs, Fc=int(5.8e9))
# plt.psd(x[2], NFFT=1024, Fs=fs, Fc=int(5.8e9))
# plt.psd(x[3], NFFT=1024, Fs=fs, Fc=int(5.8e9))

# plt.show()

# print(np.shape(x))

# print(type(x[0][0]))







# pd.DataFrame(x).to_csv("csvfile.csv", header=None, index=None)

# index = 0

# while(True):

# x = sdr.rx()

# tempReal0 = []
# tempImag0 = []

# tempReal1 = []
# tempImag1 = []

# tempReal2 = []
# tempImag2 = []

# tempReal3 = []
# tempImag3 = []


# for i in range(len(x[0])):

#     tempReal0.append(np.real(x[0][i]))
#     tempImag0.append(np.imag(x[0][i]))


#     tempReal1.append(np.real(x[1][i]))
#     tempImag1.append(np.imag(x[1][i]))

#     tempReal2.append(np.real(x[2][i]))
#     tempImag2.append(np.imag(x[2][i]))

#     tempReal3.append(np.real(x[3][i]))
#     tempImag3.append(np.imag(x[3][i]))

# A = np.array([tempReal0, tempImag0, tempReal1, tempImag1, tempReal2, tempImag2, tempReal3, tempImag3])    

# pd.DataFrame(A).to_csv("csvfile{}.csv".format(index), header=None, index=None)

    # index += 1

    # input()

#cat csvfile.csv | tr -d '(' | tr -d ')' > newcsvfile.csv

# A = pd.read_csv("csvfile0.csv",index_col=False,header=None,engine='c', delimiter=',')
# A = A.to_numpy()

# # print(np.shape(A))
# # print(type(A[0][0]))
# b_data = np.array([[0,0,0,0]])

# for i in range(len(A[0])):
#     num0 = A[0][i] + A[1][i]*1j
#     num1 = A[2][i] + A[3][i]*1j
#     num2 = A[4][i] + A[5][i]*1j
#     num3 = A[6][i] + A[7][i]*1j
    
#     temp_array = np.array([[num0,num1,num2,num3]])

#     b_data = np.concatenate((b_data, temp_array))


# A = np.matrix(np.delete(b_data,0,0))
# print(np.shape(A))

def receive_rx(sdr):

    x = sdr.rx()

    tempReal0 = []
    tempImag0 = []

    tempReal1 = []
    tempImag1 = []

    tempReal2 = []
    tempImag2 = []

    tempReal3 = []
    tempImag3 = []

    temp0 = []
    temp1 = []
    temp2 = []
    temp3 = []

    


    for i in range(len(x[0])):

        # tempReal0.append(np.real(x[0][i]))
        # tempImag0.append(np.imag(x[0][i]))
        temp0.append(x[0][i])
        temp1.append(x[1][i])
        temp2.append(x[2][i])
        temp3.append(x[3][i])


        # tempReal1.append(np.real(x[1][i]))
        # tempImag1.append(np.imag(x[1][i]))

        # tempReal2.append(np.real(x[2][i]))
        # tempImag2.append(np.imag(x[2][i]))

        # tempReal3.append(np.real(x[3][i]))
        # tempImag3.append(np.imag(x[3][i]))

    return np.array([temp0, temp1, temp2, temp3])

    # pd.DataFrame(A).to_csv("csvfile.csv", header=None, index=None)

# index += 1



# f, Pxx_den = signal.periodogram(x[0], fs)
# plt.ylim([1e-7, 1e2])
# plt.xlabel("frequency [Hz]")
# plt.ylabel("PSD [V**2/Hz]")
# plt.show()

# Collect data
# for r in range(20):
#     x = sdr.rx()
#     f, Pxx_den = signal.periodogram(x[0], fs)
#     plt.clf()
#     plt.semilogy(f, Pxx_den)

#     f, Pxx_den = signal.periodogram(x[1], fs)
#     plt.semilogy(f, Pxx_den)

#     f, Pxx_den = signal.periodogram(x[2], fs)
#     plt.semilogy(f, Pxx_den)

#     f, Pxx_den = signal.periodogram(x[3], fs)
#     plt.semilogy(f, Pxx_den)

#     plt.ylim([1e-7, 1e2])
#     plt.xlabel("frequency [Hz]")
#     plt.ylabel("PSD [V**2/Hz]")
#     plt.draw()
#     plt.pause(0.05)
#     time.sleep(0.1)

# plt.show()