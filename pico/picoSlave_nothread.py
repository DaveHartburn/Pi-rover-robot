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

# Import libraries
from machine import Pin
import machine
import time
import json

debugOut = True       # Use dprint(str) rather than print(str), set to false to prevent print output

activate = False       # True if actively checking sensors and sending serial data
sendFreq = 250         # How often to send data in ms
sensorFreq = 250       # How often to check sensors in ms
sonicTimeout = 50000    # Timeout in ns

hwData={}             # Build dictionary of hardware data to return current status to Pi
hwData["msg"]=""      # Used to send messages back

# List of attached servos as array, [pin,min angle, max angle, calibrarion angle]
# Leave blank if no servos
servos=[ [2,25,150,-14],    # Pan servo (index 0)
         [3,30,120,0] ]   # Tilt servo (index 1)
servoPWM=[]          # Array of PWM objects for each servo

# List of sonic sensors. Name, triger pin, echo

sonicList= [
    ["front", Pin(4, Pin.OUT), Pin(5, Pin.IN)],
    ["left", Pin(6, Pin.OUT), Pin(7, Pin.IN)],
    ["right", Pin(8, Pin.OUT), Pin(9, Pin.IN)],
    ["rear", Pin(15, Pin.OUT), Pin(14, Pin.IN)]
    ]

# Internal timers
nextSend = 0         # Time of next data send
nextSensor = 0       # Next time to check the sensors


# Internal pin for activity
led=Pin(25, Pin.OUT)

# Initialise the UART
uart = machine.UART(0, 115200)

# ********* Functions *****************
def dprint(str):
    if(debugOut):
        print(str)
# End of debugPrint

def flash(l,n, i):
    # Flash the led l, n times, with an interval i
    for x in range(n*2):
        l.toggle()
        time.sleep(i)
    l.toggle()
    
# UART function
def sendData(str):
    # Sends data over the serial UART
    # Add new line to terminate string
    #print("Sending: ", str)
    uart.write(str+'\n')

def sendhw():
    # Send the hwData array as JSON object
    jsonOut=json.dumps(hwData)
    #dprint(jsonOut)            
    sendData(jsonOut)
     
def receiveData():
    toReturn=[]
    dataIn = ""
    
    while uart.any():
        # In a fast enough loop, this may be called before the string
        # has completed sending. This loop will continue until the incoming
        # data has completed. On exception it will send what string it has
        # so far
        # However if the sender sends data too quickly, then all commands
        # merge into one, construct array "toReturn" and send a list if needed
        rawIn = uart.readline()
        # print(rawIn)
        # print("".join("%02x " % b for b in rawIn))
        
        # Raw data is as a byte stream. Convert
        # Need to use a try/except as control characters may cause an issue
        try:
            dataIn += str(rawIn.decode('utf-8'))
            #print("Incoming :", dataIn)
        except:
            pass
    
    # Split commands on new line
    toReturn=dataIn.split('\n')
    
    #print("Array of commands")
    #print(toReturn)
    return toReturn

# Servo functions
def setServoCycle (obj, pos):
    obj.duty_u16(pos)
    
def setServoAngle (s, a):
    # Check servo is in the range of defined servos
    # Out of range is silently ignored
    if(s<len(servoPWM)):
        # Is fine, check angle is in range and if not adjust
        # to min or max value
        
        if(a<servos[s][1]):
            a=servos[s][1]
        if(a>servos[s][2]):
            a=servos[s][2]
        
        # Updata hardware data array
        hwData["servos"][s]=a

        # Add calibration angle
        a=a+servos[s][3]
        
        d = int(a/180*8000+1000)
        dprint("Angle={}, d={}".format(a,d))
        setServoCycle(servoPWM[s], d)
# End of set servo angle

def changeServoAngle (s, a):
    # Change the angle of servo s by a degrees
    if(s<len(servoPWM)):
        n=hwData["servos"][s]+a
        setServoAngle(s,n)

# Ultrasonic functions
def readSonic(trig, echo):
    # Read the distance from an ultrasonic sensor,
    # return in cm. -1 = error
    
    # Any reading above this value is considered an error
    timeOut=time.ticks_us()+sonicTimeout
    
    callTime=time.ticks_us()
    startTime=callTime    # Set a default value time. We can sometimes get
    stopTime=callTime     # Get a variable not set error
    
    trig.low()
    time.sleep_us(2)   
    trig.high()
    time.sleep_us(5)
    trig.low()
    
    # Save start time
    #print("Waiting for echo to go to zero")
    while (echo.value()==0 and time.ticks_us()<timeOut):
        startTime = time.ticks_us()
    
    # Save end time
    #print("Waiting for echo to go to one")
    while (echo.value()==1 and time.ticks_us()<timeOut):
        stopTime = time.ticks_us()
      
    #print("Echo returned / time out")
    
    if(time.ticks_us()>timeOut):
        # Time out error
        dist=-1
    else:
        elTime=stopTime-startTime
        dist=round((elTime*0.0343)/2,2)

    return dist
# End of readSonic

def readAllSonics():
    i=0
    for s in sonicList:
        d = readSonic(s[1], s[2])
        #dprint("Sonic {}, distance={} cm".format(s[0],d))
        hwData["sonics"][i][1]=d
        i+=1
    #print(hwData)
    
# ******** Main code ******************

dprint("Hello from pico slave")

# Show life
flash(led,3,0.5)

# Initialise servos if present
if(servos==[]):
    dprint("No servos defined")
else:
    # Servos present, create array for servo positions in hwData
    hwData["servos"]=[]
    i=0
    for srv in servos:
        dprint("Init servo on pin {}".format(srv[0]))
        # Create PWM object
        p=machine.PWM(Pin(srv[0]))
        p.freq(50)
        # Add to hwData array
        hwData["servos"].append(90)
        # Add to PWM array
        servoPWM.append(p)
        # Init in mid position
        setServoAngle(i, 90);
        i+=1

# Initialise ultrasonic sensors if present
if(sonicList==[]):
    dprint("No ultrasonics defined")
else:
    # Sonics present, create array for distance readings in hwData
    hwData["sonics"]=[]
    for s in sonicList:
        dprint("Init ultrasonic "+s[0])
        hwData["sonics"].append([s[0], -1])
        
dprint("Initial hwData:")
dprint(hwData)

# Main loop
while True:
    if uart.any():
        # Data present
        incData=receiveData()
        dprint("Data received: ")
        dprint(incData)
        
        # Examin individual messages
        for msg in incData:
            # Break the message into CSV
            csvin=msg.split(',')
            # Take the command off the front
            cmd=csvin.pop(0)
            dprint("Received command "+cmd)
            #dprint(csvin)
            
            # Try and except deals with list index errors due
            # to incorrect arguments
            if(cmd=="quit"):
                break
            elif(cmd=="ping"):
                #sendData("beep")
                hwData["msg"]="beep-"+str(time.time())
            elif(cmd=="panangle"):
                try:
                    setServoAngle(0,int(csvin[0]))
                except:
                    pass
            elif(cmd=="panleft"):
                try:
                    changeServoAngle(0,int(csvin[0]))
                except:
                    pass
            elif(cmd=="tiltangle"):
                try:
                    setServoAngle(1,int(csvin[0]))
                except:
                    pass
            elif(cmd=="tiltup"):
                try:
                    changeServoAngle(1,-int(csvin[0]))
                except:
                    pass
            elif(cmd=="servoangle"):
                try:
                    setServoAngle(int(csvin[0]),int(csvin[1]))
                except:
                    pass
            elif(cmd=="servoleft"):
                try:
                    changeServoAngle(int(csvin[0]),int(csvin[1]))
                except:
                    pass
            elif(cmd=="datarequest"):
               sendhw()
            elif(cmd=="activate"):
                activate=True
                nextSend=0
            elif(cmd=="deactivate"):
                activate=False
        # End of for msg in incData
    # End of if uart.any()
    
        
    # Do we need to check sensors and send data?
    if(activate):
        # Are sensor readings required
        if(nextSensor<time.ticks_ms()):
            readAllSonics()
            nextSensor=time.ticks_ms()+sensorFreq
            
        # Time to send data
        if(nextSend<time.ticks_ms()):
            #dprint("Sending data")
            sendhw()
            nextSend=time.ticks_ms()+sendFreq
            
# End of main loop
           
uart.write("Terminating....\n")
dprint("Completed")