#!/usr/bin/python

# Ultrasonic Sensors using pirover library
# Will also use pan/tilt but may not call anything

import os, sys, time
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from piroverlib import piRover

# Define pin numbers [A, B]
leftPins=[18,12]
rightPins=[13,19]

# Ultrasonic pins (GPIO numbers) are a list of pairs for each sensor, trigger & echo
sonicPins=[ [4,17], [14,15] ]

print("Starting ultrasonic test with library")
pirover=piRover(left=leftPins, right=rightPins, pantilt=[0,1], sonics=sonicPins)

while True:
	# Test both direct call to the ultrasonic and the entire data return
	r=pirover.getSonic()
	print(r)
	rd=pirover.getSensorData()
	print(rd)
	time.sleep(1)
