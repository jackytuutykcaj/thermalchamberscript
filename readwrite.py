#Thermal Chamber Temperature Control Script
#Author: Jacky Tu
#Date updated: 2022-06-16
#This script has been tested on Thermal Chamber 1(the one by the EMI Tent) and works
#At the time of the making of this script, it is not known if it works on Thermal Chamber 2
#If you are going to use this on Thermal Chamber 1, baudrare is 19200
#If you are going to use this on Thermal Chamber 2, baudrate is 9600
#Negative numbers and decimals are taken into account in this script


#This script is used for reading and writing to the watlow controller that controlls the thermal chamber.

import os
from pymodbus.client.sync import ModbusSerialClient
import sys

#Create ModbusSerialClient
client = ModbusSerialClient(
    method='rtu',#Do not change
    port='COM3',#Make sure this is set correctly
    baudrate=19200,#Make sure this is set correctly
    timeout=1,#Do not change
    parity='N',#Do not change
    stopbits=1,#Do not change
    bytesize=8#Do not change
)

#Test if client can connect
if(client.connect()):
    #If it can try reading the arguments provided
    try:
        fileName = os.path.basename(__file__)
        #readOrWrite is the 1st argument which is either read or write
        readOrWrite = sys.argv[1]
        #If it's read, check for 2nd argument and store it in a variable called read
        if(readOrWrite == 'read'):
            #If 2nd argument is currentTemp, read register(address) 100 for the current temperature value
            if(sys.argv[2] == 'currenttemp'):
                read = client.read_holding_registers(address=100, count=1, unit=1)
            #if 2nd argument is getPoint, read register(address) 300 for the set point value
            elif(sys.argv[2] == 'setpoint'):
                read = client.read_holding_registers(address=300, count=1, unit=1)
            #if 2nd argument is rangehigh, read register(address) 603 for the range high value
            elif(sys.argv[2] == 'rangehigh'):
                read = client.read_holding_registers(address=603, count=1, unit=1)
            #if 2nd argument is rangelow, read register(address) 602 for the range low value
            elif(sys.argv[2] == 'rangelow'):
                read = client.read_holding_registers(address=602, count=1, unit=1)
            #if 2nd argument is a register, read that register(address)
            else:
                read = client.read_holding_registers(address=int(sys.argv[2]), count=1, unit=1)
            #get the first value from variable read and store it in variable data
            data = read.registers[int(0)]
            #Conversion for negative numbers
            if data & (1 << 15): data = data - (1 << 16)
            print('Values are in celcius')
            #Decimals are not returned so you have to divide by 10
            #example.
            #if the current temperature is 12 degrees, the value you will get is 120 so you'll need to divide by 10
            print(data/10, 'degrees')
        #if it's write, check for 2nd argument
        elif(readOrWrite == 'write'):
            #v is the value you want to write
            #a is the register(address) you want to write to

            #if 2nd argument is setPoint, write to register(address) 300 which sets the temperature point
            if(sys.argv[2] == 'setpoint'):
                print('Setting the set point....')
                v = int(float(sys.argv[3]) * 10)
                a = 300
            #if 2nd argument is setHighRange, write to register(address) 603 which sets the high temperature limit
            elif(sys.argv[2] == 'rangehigh'):
                print('Setting the high range....')
                v = int(float(sys.argv[3]) * 10)
                a = 603
            #if 2nd argument is setLowRange, write to register(address) 602 which sets the low temperature limit
            elif(sys.argv[2] == 'rangelow'):
                print('Setting the low range....')
                v = int(float(sys.argv[3]) * 10)
                a = 602
            #Conversion for negative numbers
            if(v < 0):
                v = hex((v + (1 << 64)) % (1 << 64))
                v = int(v[-4:], 16)
            client.write_register(address=a, value=v)
        #If first argument is help
        elif(readOrWrite == 'help'):
            print("The use of this script is mainly for reading and writing to registers.")
            print("All values are in celcius.")
            print("Negative numbers and decimals are already taken into account in this script.\n")
            print(f'To read values: {fileName} read [the value you want to read]')
            print('Available values that can be read: currentTemp, setPoint, highRange, lowRange\n')
            print(f'To write values: {fileName} write [the register you want to write to]')
            print('Available registers you can write to: setPoint, highRange, lowRange')
        #if unknown argument
        else:
            print('Invalid Argument')
            print(f'For help type {fileName} help')
    #if no argument is provided
    except IndexError:
        print('Missing arguments')
        print(f'For help type {fileName} help')
    except ValueError:
        print('Invalid Value or argument')
        print(f'For help type {fileName} help')
    #if connection failed.
else:
    print('Connection failed.')
    print('Check if baudrate, com port is correct and/or cable.')