import numpy as np
import time
from DOA import DOA
from graphing import graphing
import subprocess
import os
from os import path
import pandas as pd
from datetime import datetime

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
        "set frequency rx 2.285G^M",
        "set samplerate rx 6M^M",
        "set clock_out enable^M",
        "trigger j51-1 tx master^M",
        "trigger j51-1 rx slave^M",
        "rx config file={} format=csv n=2048 channel=1,2 timeout=60s^M".format(master_filename)
    ]

    slave_init_commands = [
        "set frequency rx 2.285G^M",
        "set samplerate rx 6M^M",
        "set clock_sel external^M",
        "trigger j51-1 rx slave^M",
        "rx config file={} format=csv n=2048 channel=1,2 timeout=60s^M".format(slave_filename)
    ]

    print("Opening and Configuring Master")

    for cmd in master_init_commands:
        commands[2] = "master"
        commands[7] = cmd

        subprocess.call(commands)
        time.sleep(1.3)

    print("Opening and Configuring Slave")

    for cmd in slave_init_commands:
        commands[2] = "slave"
        commands[7] = cmd

        subprocess.call(commands)
        time.sleep(1.3)


def call_bladeRF_Command(cmd, dev):
    commands = ["screen", "-S", "", "-p", "0", "-X", "stuff", ""]

    commands[2] = dev
    commands[7] = cmd

    subprocess.call(commands)
    time.sleep(0.2)


def receive_rx():
    # commands = ["screen", "-S", "", "-p", "0", "-X", "stuff", ""]

    #First Reconfigure the Devices for the master slave
    # commands[2] = "master"
    # commands[7] = "trigger j51-1 tx master^M"
    # subprocess.call(commands)
    call_bladeRF_Command("trigger j51-1 tx master^M", "master")

    # commands[2] = "master"
    # commands[7] = "trigger j51-1 rx slave^M"
    # subprocess.call(commands)
    call_bladeRF_Command("trigger j51-1 rx slave^M", "master")


    # commands[2] = "slave"
    # commands[7] = "trigger j51-1 rx slave^M"
    # subprocess.call(commands)
    call_bladeRF_Command("trigger j51-1 rx slave^M", "slave")


    #Then start both rx processes
    # commands[2] = "master"
    # commands[7] = "rx start^M"
    # subprocess.call(commands)
    call_bladeRF_Command("rx start^M", "master")


    # commands[2] = "slave"
    # commands[7] = "rx start^M"
    # subprocess.call(commands)
    call_bladeRF_Command("rx start^M", "slave")
    

    #After starting the rx processes, we can send the fire signal from the master device
    # commands[2] = "master"
    # commands[7] = "trigger j51-1 tx fire^M"
    # subprocess.call(commands)
    call_bladeRF_Command("trigger j51-1 tx fire^M", "master")

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




def receive(masterDOA = None, slaveDOA = None):

    timeout = time.time() + 1

    receive_rx()



    start_time = datetime.now()
# print(start_time)

# while not buff.endswith('/abc #'):
#     print('waiting')
#     time_delta = datetime.now() - start_time
#     print(time_delta)
#     if time_delta.total_seconds() >= 10:
#         break
    while(True):


        if(masterDOA.data_set(filename1=master_filename, filename2 = slave_filename) == 1):
            break
        else:
            time_delta = datetime.now() - start_time
            if time_delta.total_seconds() >= 1:
                start_time = datetime.now()
                receive_rx()
                continue

    # if path.exists(master_filename) and path.exists(slave_filename):
    #     commands = ["rm", "{}".format(master_filename), "{}".format(slave_filename)]
    #     subprocess.call(commands)

# else:

#     print("Path Doesnt Exist After Receiving")


# doa.data_set(filename=master_filename)

# print(np.shape(doa.data_s))

# print(doa.data_s)

# if path.exists(master_filename) and path.exists(slave_filename):
#     commands = ["rm", "{}".format(master_filename), "{}".format(slave_filename)]
#     subprocess.call(commands)




