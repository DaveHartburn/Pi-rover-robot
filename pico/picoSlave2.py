import machine
import time
import _thread
import gc

led=machine.Pin(25, machine.Pin.OUT)

debugOut=True         # Use dprint rather than print, toggle to false for no output
checkSensors=True     # Flag, setting to false will terminate the second thread

# Define hardware
servos=[2,3]    # List of servo pins
servoPWM=[]

# Init uart for serial IO
uart = machine.UART(0, 115200)

# ********* Functions ***************
def sensorThread():
    # Sensor thread - continual loop checking sensors until checkSensors is set to false
    # Currently no sensors attached, toggle onboard LED to show life
    global nextCheck
    global togInterval
    global checkSensors

    nextCheck=0
    togInterval=1000

    dprint("checkSensors={}".format(checkSensors))
    while (checkSensors):
        gc.collect()
        
        if(time.ticks_ms()>nextCheck):
            led.toggle()
            nextCheck=time.ticks_ms()+togInterval
    # End of checkSensors while loop
# End of sensorThread

def dprint(str):
    if(debugOut):
        print(str)
# End of debugPrint

def sleep_nb_ms(t):
    # Use the time tl sleep for t microseconds without blocking
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

# ******** Main code ***********************

# Start sensor checker in new thread
_thread.start_new_thread(sensorThread, ())
# sensorThread()   # Uncomment for single thread/testing

dprint("Start, delay for 5 seconds")
sleep_nb(5)
dprint("Done")

# Initialise servos
for srv in servos:
    dprint("Init servo on pin {}".format(srv))
    p=machine.PWM(machine.Pin(srv))
    p.freq(50)
    servoPWM.append(p)

Angles = [56, 157 ,4 ,89 ,39, 170, 2, 123, 10]
for a in Angles:
    #print("Setting angle ", a);
    setServoAngle(0, a)
    sleep_nb(2)
for pos in range(0,160,2):
    setServoAngle(0, pos)
        
dprint("10 second delay")
sleep_nb(10)
dprint("At end of 10 second delay, done")

# Terminate thread before quitting
checkSensors=False

# No main loop, it often doesn't get this far