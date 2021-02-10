#subprocess library to open and pass new commands to the bladeRF-cli programs we need to run the SDR
from subprocess import Popen, PIPE, STDOUT
import time
import sys
from os import path, remove
import os


class bladeRFControl_master():

    def __init__(self):

        #the device with 35d must be the master becuause the clkout on "35d" is connected to clkin on "cbd"
        self.master_process = Popen(['bladeRF-cli', '-d', '*:serial=35d','-s','mastercommands', '-i'], stdin=PIPE, stdout=PIPE)
       
        time.sleep(4)
        print("Master Opened")
        #give it some time to open the device and load the commands
        #we need to wait because we can't set the external clock on the slave until the master is already outputting a clock signal
        


    def PrepareReceive(self):

        self.sendBladeRFCommand("rx start;", "master",waitTime=1)

        print("Rx Started")

        time.sleep(3)



    def recieve(self):

        print("Sending Trigger")

        self.sendBladeRFCommand("trigger j51-1 tx fire", "master", waitTime=1)

        print("Done Receiving")



    def sendBladeRFCommand(self, command, device, waitTime=0):

        commandBytes = bytes(command + "\n", 'utf-8')

        self.master_process.stdin.write(commandBytes)



    def printBladeRFCommand(self, command, device):


        commandBytes = bytes(command + "\n", 'utf-8')

        if device == "master":
            self.master_process.stdin.write(commandBytes)
            while True:
                line = self.master_process.stdout.readline()
                if line != 'bladeRF>':
                    print(line.strip())
                else:
                    break
    

    def closeDevices(self):
        
        print("Closing BladeRFs")

        self.sendBladeRFCommand("q", "master")
        time.sleep(5)
        print("Closed Device Successfully")


class bladeRFControl_slave():

    def __init__(self):


        self.slave_process = Popen(['bladeRF-cli', '-d', '*:serial=cbd', '-s', 'slavecommands', '-i'], stdin=PIPE, stdout=PIPE)
        time.sleep(4)
        print("Slave Opened")
        # same thing, give it some time to open and load commands
        

    def PrepareReceive(self):

        self.sendBladeRFCommand("rx start;", "slave",waitTime=1)
        time.sleep(3)
        print("Rx Started")

       
    def sendBladeRFCommand(self, command, device, waitTime=0):

        commandBytes = bytes(command + "\n", 'utf-8')

        self.slave_process.stdin.write(commandBytes)

        if waitTime != 0:
            time.sleep(waitTime)

            
    def closeDevices(self):
        
        print("Closing BladeRFs")

        self.sendBladeRFCommand("q", "slave")
        time.sleep(5)
        print("Closed Devices Successfully")



"""
master = bladeRFControl_master()
slave = bladeRFControl_slave()


master.PrepareReceive()
slave.PrepareReceive()

master.recieve()

master.closeDevices()
slave.closeDevices()
#"""