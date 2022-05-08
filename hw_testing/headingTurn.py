#!/usr/bin/python

# Heading test - various routines to turn based on a heading
# Call with a list of headings on the command line

# Try: ./headingTurn.py 72 114 15 345 290 15

# Enable importing from parent directory
import os, sys, time
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from piroverlib import piRover

# Define pin numbers [A, B]
leftPins=[18,12]
rightPins=[13,19]

pirover=piRover(left=leftPins, right=rightPins, magneto=True)	
	
print("Heading test start")
sys.argv.pop(0)		# Pop off initial command
while(sys.argv!=[]):
	s=sys.argv.pop(0)
	print("Turning to ", s)
	h=int(s)
	pirover.turnToHeading(h,speed=60)
	time.sleep(1)
	
print("Turning clockwise 50 degrees")
pirover.turnByHeading(50)
print("Turning anti-clockwise 50 degrees")
pirover.turnByHeading(-50)

print("Heading test end")

# Encore, see how much the robot tilts
rdata=pirover.getAccel()
print("Testing tilt measurement")
print("Current tilt is {:0.2f}, measure again in 4 seconds".format(rdata["magneto"]["chassisTilt"]))
time.sleep(4)
rdata=pirover.getAccel()
print("Tilt is now {:0.2f}".format(rdata["magneto"]["chassisTilt"]))


# To do
#   Return chassis tilt
