#!/usr/bin/python

# Pan tilt with library

# Enable importing from parent directory
import os, sys, time
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from piroverlib import piRover

# Define pin numbers [A, B]
leftPins=[18,12]
rightPins=[13,19]

print("Starting pan/tilt test with library")
pirover=piRover(left=leftPins, right=rightPins, pantilt=[0,1])

# List of pan angles to run through
pana=[10,120,30,80,120,0,180,40]
for a in pana:
	print("Setting angle to ", a)
	rd=pirover.panAngle(a)
	print(rd)
	time.sleep(1)

# Reset to middle
rd=pirover.panAngle("mid")
print(rd)

# List of tilt angles to run through
tilta=[10,40,20,70,110,170,0]
for a in tilta:
	print("Setting angle to ", a)
	rd=pirover.tiltAngle(a)
	print(rd)
	time.sleep(1)
rd=pirover.tiltAngle("mid")
print(rd)

print("Done")
