#Thermal Chamber Temperature Ramping Script
#Author: Jacky Tu
#Date updated: 2022-06-16
#This script has been tested on Thermal Chamber 1(the one by the EMI Tent) and works

#At the time of the making of this script, it is not known if it works on Thermal Chamber 2. This
#script was made because we could not figure out if the watlow controller came with this capability.

#If you are going to use this on Thermal Chamber 1, baudrare is 19200
#If you are going to use this on Thermal Chamber 2, baudrate is 9600


#This script is used for simulating ramping on the thermal chamber

import sys
from pymodbus.client.sync import ModbusSerialClient
import time

#Create ModbusSerialClient
client = ModbusSerialClient(
    method='rtu',#Don't change
    port='COM3',#Make sure this is set correctly
    baudrate=19200,#Make sure this is set correctly
    timeout=1,#Don't change
    parity='N',#Don't change
    stopbits=1,#Don't change
    bytesize=8#Don't change
)

LINE_CLEAR = '\x1b[2K'
LINE_UP = '\033[1A'

#This function reads the temperature of the thermal chamber
def readTemp():
    read = client.read_holding_registers(address=100, count=1, unit=1)
    data = read.registers[int(0)]
    if data & (1 << 15): data = data - (1 << 16)
    print(f'Current Temperature is {data/10} degress')
    time.sleep(1)
    print(LINE_UP, end=LINE_CLEAR)
    return data/10

#This function sets the temperature point of the thermal chamber
def writeSetPoint(target):
    v = int(float(target) * 10)
    if(v < 0):
        v = hex((v + (1 << 64)) % (1 << 64))
        v = int(v[-4:], 16)
    client.write_register(address=300, value=v)

#Test if client can connect
if(client.connect()):
    try:
        startTemp = float(sys.argv[1])#Starting temperature
        endTemp = float(sys.argv[2])#Ending temperature
        tempDif = float(sys.argv[3])#Temperature difference
        cycles = float(sys.argv[4])#Cycles
        interval = float(sys.argv[5])#Interval between each ramp(seconds)
        startingCycle = 1#Don't change
        ready = True#Don't change
        currentTemp = startTemp#Don't change
        target = startTemp#Don't change

        #If the starting temperature is greater than the ending temperature, set the temperature
        #difference to negative of itself(It will ramp down at the start). If not it will ramp up at the start.
        if startTemp > endTemp:
            tempDif = tempDif * -1
    
        #Setup for ramping
        print('Current parameters:')
        print(f'Starting temperature: {startTemp} degress')
        print(f'Ending temperature: {endTemp} degrees')
        print(f'Temperature difference: {tempDif} degrees')
        print(f'Cycles: {cycles}')
        print(f'Interval time: {interval} seconds')
        print('Setting up initial temperature....')
        print('Checking current temperature....')
        #Check the current temperature if it matches the starting temperature
        #If it doesn't match, set the temperature point to the starting temperature
        data = readTemp()
        if(data != startTemp):
            print(f'Setting temperature to {startTemp} degrees....')
            writeSetPoint(startTemp)
            ready = False
    
        #When the current temperature is in range of the starting temperature,
        #proceed to ramping
        while(ready == False):
            time.sleep(1)
            data = readTemp()
            if(data < startTemp + 0.2 and data > startTemp - 0.2):
                print('Ready to proceed to ramping')
                ready = True
            
        print(f'Cycling between {startTemp} degrees and {endTemp} degrees')
        #Loop until the startingCycle variable equals the cycles variable
        while(startingCycle <= cycles):
            print(f'Cycle {startingCycle} started')
            print('Ramping starting....')
            print('Ramping in progress....')
            #while the target temperature does not equal the ending temperature
            while target != endTemp:
                #Set the temperature target
                target = target + tempDif
                #set the temperature point to the target
                writeSetPoint(target)
                #If tempDif is positive, it is ramping up
                #If it is negative, it is ramping down
                if(tempDif < 0):
                    print(f'Ramping down to {target} degrees')
                else:
                    print(f'Ramping up to {target} degrees')

                #Continously read the current temperature until the current temperature
                #is in range of the targe temperature
                while ((currentTemp > target + 0.2 or currentTemp < target - 0.2)):
                    currentTemp = readTemp()
        
                #After it reaches the target temperature, it will loop until it starts the timer
                print(f'Starting timer of {interval} seconds before next ramp')
                i = interval
                while i >= 0:
                    print(f'{i} seconds until next ramp')
                    time.sleep(1)
                    print(LINE_UP, end=LINE_CLEAR)
                    i -= 1

            #After it reaches the ending temperature, tempDif is set to negative of itself and will ramp
            #towards the starting temperature
            tempDif = tempDif * -1
            while target != startTemp:
                #Set the temperature target
                target = target + tempDif
                #set the temperature point to the target
                writeSetPoint(target)
                #If tempDif is positive, it is ramping up
                #If it is negative, it is ramping down
                if(tempDif < 0):
                    print(f'Ramping down to {target} degrees')
                else:
                    print(f'Ramping up to {target} degrees')

                #Continously read the current temperature until the current temperature
                #is in range of the targe temperature
                while ((currentTemp > target + 0.2 or currentTemp < target - 0.2)):
                    currentTemp = readTemp()
            
                print(f'Starting timer of {interval} seconds before next ramp')
                i = interval
                while i >= 0:
                    print(f'{i} seconds until next ramp')
                    time.sleep(1)
                    print(LINE_UP, end=LINE_CLEAR)
                    i -= 1

            tempDif = tempDif * -1
            #Loop until it reaches the last cycle
            print(f'Cycle {startingCycle} finished')
            startingCycle = startingCycle + 1
        print('Cycling finished')
        print('Setting temperature to ambient')
        writeSetPoint(22)
    except IndexError:
        print('Missing arguments')
    except ValueError:
        print('Invalid Value or argument')
    #if connection failed.
else:
    #If connection failed
    print('Connection failed.')
    print('Check if baudrate, com port is correct and/or cable.')