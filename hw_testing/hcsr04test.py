#!/usr/bin/python

# HC-SR04 ultra sonic test
# Perform distance measurements to a single ultrasonic sensor

# Usage: hcsr04test.py [-e pin] [-t pin] [-v]
# Where -e and -t override the default trigger and echo pins
# -v verbose / debug

import RPi.GPIO as GPIO
import time
import sys

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Default pins
HC_TRIG=4
HC_ECHO=17

verbose=False

def debug(str):
	if(verbose):
		print(str)
		
# Parse input arguments
sys.argv.reverse()
sys.argv.pop() # Dump first element
while(sys.argv!=[]):
	elm=sys.argv.pop()
	if(elm=="-t"):
		HC_TRIG=int(sys.argv.pop())
		print("Trigger pin set as", HC_TRIG)
	elif(elm=="-e"):
		HC_ECHO=int(sys.argv.pop())
		print("Echo pin set as", HC_ECHO)
	elif(elm=="-v"):
		verbose=True
	else:
		print("Unknown argument", elm)
		
print("Init sensor, trigger =", HC_TRIG, ", echo =", HC_ECHO)

# Set GPIO pints
GPIO.setup(HC_TRIG, GPIO.OUT)
debug("Trigger set")
GPIO.setup(HC_ECHO, GPIO.IN)
debug("Echo set")

# Allow sensor to settle
GPIO.output(HC_TRIG,False)
debug("Settling")
time.sleep(2)


		
def hcsr04dist(tr, ec):
	# Reads and returns the distance from a HC-SR04 sensor
	maxTime=5		# Bomb out if no response before maxTime
					# Prevents hanging on fault
	
	debug("Reading distance")
	# Trigger to high
	GPIO.output(tr, True)
	time.sleep(0.00001)
	GPIO.output(tr, False)
	
	callTime=time.time()	# Record time procedure called
	errTime=callTime+5
	startTime=callTime		# Set a default time, can sometimes think
	stopTime=callTime		# variables have not been set
	
	debug("Getting start time")
	# Save start time
	while (GPIO.input(ec)==0 and time.time()<errTime):
		startTime=time.time()
		
	debug("Getting stop time")
	# Save echo time
	while (GPIO.input(ec)==1 and time.time()<errTime):
		stopTime=time.time()
		
	if(time.time()>errTime):
		debug("Error: Send error value (negative)");
		return -1
		
	elTime=stopTime-startTime
	
	dist=round(elTime*17150,2)
	
	return dist
	
while True:
	dist=hcsr04dist(HC_TRIG, HC_ECHO)
	print("Distance =",dist)
	time.sleep(0.5)
