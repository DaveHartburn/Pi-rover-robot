from machine import Pin
import time

trigPin = Pin(6, Pin.OUT)
echoPin = Pin(7, Pin.IN)

# List of sonic sensors. Name, triger pin, echo

sonicList= [
    ["front", Pin(4, Pin.OUT), Pin(5, Pin.IN)],
    ["left", Pin(6, Pin.OUT), Pin(7, Pin.IN)],
    ["right", Pin(8, Pin.OUT), Pin(9, Pin.IN)],
    ["rear", Pin(15, Pin.OUT), Pin(14, Pin.IN)]
    ]

def readSonic(trig, echo):
    # Read the distance from an ultrasonic sensor,
    # return in cm. -1 = error
    
    maxTime = 50000      # Any reading above this value is considered an error
    timeOut=time.ticks_us()+maxTime
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
        
print("Starting sonic reading")

while True:
    for s in sonicList:
        d = readSonic(s[1], s[2])
        print("Sonic {}, distance={} cm".format(s[0],d))
    time.sleep(1)