# Multithredded comms test

from machine import Pin
import machine
import time
import _thread
import random
import json

numSensors = 6
sensorData = []
sensorInterval = 500      # Update simulated sensors every half second
checkSensors = True       # Flag - setting to false will terminate second thread

led=Pin(25, Pin.OUT)
uart = machine.UART(0, 115200)
print(uart)

# Sensor thread - this will simulate the sensors by filling
# the array with random values
def sensorThread():
    nextCheck=0    # When to next check the sensors
    while True:
        if(checkSensors==False):
            break
        if(time.ticks_ms()>nextCheck):
            # Update the simulated sensors
            for s in range(numSensors):
                sensorData[s]=random.randint(0,255)
            nextCheck=time.ticks_ms()+sensorInterval
    # End of 'infinite while loop
    # Thread complete, checkSensors set to false
# End of sensorThread

def sendData(str):
    # Sends data over the serial UART
    # Add new line to terminate string
    #print("Sending: ", str)
    uart.write(str+'\n')
    
def receiveData():
    dataIn = ""
    
    while uart.any():
        # In a fast enough loop, this may be called before the string
        # has completed sending. This loop will continue until the incoming
        # data has completed. On exception it will send what string it has
        # so far
        rawIn = uart.readline()
        #print(rawIn)
        # Raw data is as a byte stream. Convert
        # Need to use a try/except as control characters may cause an issue
        try:
            dataIn += str(rawIn.decode('utf-8').strip())
            #print("Incoming :", dataIn)
        except:
            pass
    return dataIn

# ******** Main code *************

# Init the sensor array with zero values
for s in range(numSensors):
    sensorData.append(0)
    
# Start sensor checker in new thread
_thread.start_new_thread(sensorThread, ())
# sensorThread()   # Uncomment for single thread/testing

# Main loop
while checkSensors:
    if uart.any():
        msg=receiveData()
        #print(f"Message received: \"{msg}\"")
        if(msg=="quit"):
            checkSensors=False
        elif(msg=="toggleLED"):
            led.toggle()
            sendData("ack")
        elif(msg=="dataRequest"):
            dataOut=json.dumps(sensorData)
            sendData(dataOut)
uart.write("Terminating....")
print("Completed")
