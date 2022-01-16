# Pi Rover Robot - Pico slave code
# Dave Hartburn - January 2022
#
# Slave processes for handling various IO functions for the main Pi controller
# Communicates over serial to the Pi.
#
# Connected hardware:
#   GP0,1  - UART Tx and Rx to Pi
#   GP2 - Servo 0, lower pan/tilt
#   GP3 - Servo 1, upper pan/tilt
#
# Incoming command format:
#   ping - Will respond with the string 'beep' - used to test for life
#   quit - stop all execution, a reset will be required to restart
#   dataRequest - Send the data array showing sensor and servo positions


from machine import Pin, PWM
import machine
import time
import _thread
import json

led=Pin(25, Pin.OUT)

debugOut = True    # Use debug(str) rather than print(str), set to false to prevent print output
checkSensors = True       # Flag - setting to false will terminate second thread

# Define hardware
servos=[2,3]         # List of servo pins
servoPWM=[]
servoBits=False

uart = machine.UART(0, 115200)
#print(uart)

#pwm = PWM(Pin(2))
#pwm.freq(50)


# ******** Functions ******************************
# Sensor thread - continual loop until checkSensors is set to false
# Will toggle the onboard LED on each operation to show activity and life
def sensorThread():
    nextCheck=0    # When to next check the sensors
    togInterval=1000   # Just toggle the LED for now
    print("checkSensors=", checkSensors)
    while True:
        if(checkSensors==False):
            break
        if(time.ticks_ms()>nextCheck):
            # No sensors, toggle LED
            led.toggle()
            nextCheck=time.ticks_ms()+togInterval
            
    # End of 'infinite while loop
    # Thread complete, checkSensors set to false
# End of sensorThread

def dprint(str):
    if(debugOut):
        print(str)
# End of debugPrint

def sleep_nb_ms(t):
    # Use the time to sleep for t microseconds without blocking
    # i.e. not using time.sleep()
    endTime=time.ticks_ms()+t
    while endTime>time.ticks_ms():
        pass

def sleep_nb(t):
    # None blocking sleep for t seconds
    sleep_nb_ms(t*1000)
    
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

# **** Servo functions *****
def setServoCycle (obj, pos):
    obj.duty_u16(pos)
    
def setServoAngle (s, a):
    d = int(a/180*8000+1000)
    #print("Angle=",a,"d=",d)
    setServoCycle(servoPWM[s], d)
    
# ******** Main code *************

# Start sensor checker in new thread
_thread.start_new_thread(sensorThread, ())
#sensorThread()   # Uncomment for single thread/testing

sendData("Starting main thread")

print("Testing delay of 5 seconds");
sleep_nb(5)
print("Done")

#Initialise servos
for srv in servos:
    #dprint("Init servo on pin {}".format(srv))
    #p=PWM(Pin(srv))
    #p.freq(50)
    #servoPWM.append(p)
    pass

if servoBits:

    Angles = [56, 157 ,4 ,89 ,39, 170, 2, 123]
    for a in Angles:
        #print("Setting angle ", a);
        setServoAngle(0, a)
        sleep_nb(2)
    for pos in range(0,160,2):
        setServoAngle(0, pos)

print("10 second delay")
sleep_nb(10)
print("At end of delay")

#  
# setServoAngle(0, 45)
# time.sleep(2)
# setServoAngle(0, 90)

# Main loop
while True:
    if uart.any():
        msg=receiveData()
        dprint("Message received: \"{}\"".format(msg))
        if(msg=="quit"):
            checkSensors=False
            break
        if(msg=="ping"):
            sendData("beep")
        elif(msg=="dataRequest"):
            # Return whole data array as JSON
            sendData("null")
            
uart.write("Terminating....\n")
dprint("Completed")

