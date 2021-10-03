#!/usr/bin/python

# Second drive test using Blue Dot joystick
# This time using the piroverlib module
# Used as an initial test for this new module

# Import modules
from bluedot import BlueDot
from signal import pause

# Enable importing from parent directory
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from piroverlib import piRover

# Define pin numbers [A, B]
leftPins=[18,12]
rightPins=[13,19]

print("Starting driving test 3")
pirover=piRover(left=leftPins, right=rightPins)

# Establish blue dot
print("Starting bluedot connection")
bd = BlueDot(cols=2,rows=3)
# Top row, joystick, invisible
bd[1,0].visible=False
# Middle row, gap
bd[0,1].visible=False
bd[1,1].visible=False
# Bottom row, ACW, CW
bd[0,2].color="red"
bd[1,2].color="red"

while True:
    if bd.is_connected:
        break
print("Connected")

# Define functions
def jsMap(i):
    # Takes a value -1 to 1 and maps it to -100 to 100
    j=int(i*100)
    return j

def moveBot(pos):
	# Change colour
    bdJS.color = (255,128,0)
    xin,yin=pos.x, pos.y
    x=jsMap(xin)
    y=jsMap(yin)
    # Send joystick values
    pirover.js(x,y)
	
def acwTurn(pos):
	bdACW.color = (255,200,0)
	d=pos.distance
	p=jsMap(d)
	# Send negative value
	pirover.spin(-p)
	
def cwTurn(pos):
	bdCW.color = (255,200,0)
	d=pos.distance
	p=jsMap(d)
	# Send positive value
	pirover.spin(p)
	
def stop():
	pirover.stop()
	# Restore colours
	bdJS.color = "blue"
	bdCW.color = "red"
	bdACW.color = "red"
    	
# Name the components
bdJS=bd[0,0]    # Joystick
bdACW=bd[0,2]   # Anti-clockwise button
bdCW=bd[1,2]    # clockwise button
bdJS.when_pressed = moveBot
bdJS.when_moved = moveBot

bdACW.when_pressed = acwTurn
bdACW.when_moved = acwTurn

bdCW.when_pressed = cwTurn
bdCW.when_moved = cwTurn

bd.when_released = stop # All buttons stop

pause()
exit(0)
