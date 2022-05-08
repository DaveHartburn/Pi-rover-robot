#!/usr/bin/python

# Autodrive 1 - A basic automated driving using the ultrasonic sensors
#   - Drive forward until it gets within a set distance of an object
#   - Look 45 degrees left and right, then turn the direction that is most clear
#	- If both directions show less than the set distance, then back up a bit
#	- If both are equal (within a threshold) then turn the same direction as the last turn (default right)
#
# Modified from original to use sonic sensors and servos on a pico slave device
#
# Dave Hartburn - December 2021
#

# Standard libraries
import time
import json
import RPi.GPIO as GPIO


# Include local pirover library
from piroverlib import piRover

# Array to hold data from the pico
picoData=[]

# Define constants
fwSpeed = 50			# Percent forward speed
bwSpeed = 30			# Percent backwards speed (is negated in function, don't make negative here!)
turnAngle = 50			# Spin rate
fwMinDist = 20			# cm distance to stop when going forward
bwMinDist = 15			# cm distance to stop when going backwards
lMinDist = 15			# cm distance to veer away from left side
rMinDist = 15			# cm distance to veer away from right side
sonicRead = 0.2			# Interval to wait between sonic sensor readings

backupTime = 2			# Number of seconds to run backwards for
turnAngle = 45			# Angle to turn
turnSpeed = 80			# Speed to turn
quitDist = 4			# Quit if both sensors read less than this distance
panLook = 45			# Amount to look left and right

# Define pin numbers [A, B]
leftPins=[18,12]
rightPins=[13,19]

pushButton=27		# Breadboard pushbutton

debugDelay=0		# How much to slow down operations to allow debugging and sense checks

# ********* Functions ******************
def backup():
	print("Backing up")
	backing=True
	pirover.fwSpeed(0-bwSpeed)
	endTime=time.time()+backupTime
	while backing:
		d = rearS=picoData["pico"]["sonics"][3][1]
		if(d<bwMinDist):
			# Hit minimum distance, stop and end
			pirover.stop()
			backing=False
		if(time.time()>endTime):
			pirover.stop()
			backing=False
		time.sleep(sonicRead)
	print("Done backing up")
	time.sleep(debugDelay)
	
def lookAbout():
	# Look both ways and retun distances as pair [left, right]
	global pirover
	sl=1			# Time to sleep between readings
	# Set to middle
	pirover.panAngle("mid")
	# Look left
	pirover.panLeft(panLook)
	time.sleep(sl)
	l=pirover.getSonic(0,4,True)
	# Look right
	pirover.panLeft(panLook*-2)
	time.sleep(sl)
	r=pirover.getSonic(0,4,True)
	
	# Return to middle
	pirover.panAngle("mid")
	return [l[0], r[0]]
	
def button_callback(channel):
	# Call back when the button is pressed. Stop the robot and quit
	global pirover
	pirover.stop()
	pirover.picoDeactivate()
	GPIO.cleanup()
	print("Emergency STOP!!")
	quit()
	
	
# ************ CHANGE THIS, need to take l and r value	
def turn_to_clearest(l, r):
	# Function to turn in the direction of the clearest route
	# l ,r are reported distances

	turn=0
	
	# If left comes back -1, turn right if sensible otherwise turn left
	if(l==-1):
		if(r==-1):
			# No sensible reading, quit
			print("No sonic readings, doing nothing")
			return
		if(r>rMinDist):
			print("No left reading, but right is clear, turning right")
			pirover.turnByHeading(turnAngle, speed=turnSpeed)
		else:
			print("No left reading, and right is not clear, try turning left")
			pirover.turnByHeading(-turnAngle, speed=turnSpeed)
	elif(r==-1):
		if(l>lMinDist):
			print("No right reading, and left is clear, turning left")
			pirover.turnByHeading(-turnAngle, speed=turnSpeed)
		else:
			print("No right reading, and left is not clear, try turning right")
			pirover.turnByHeading(turnAngle, speed=turnSpeed)
	elif(l>=r):
		# More distance to left, spin left (anti-clockwise)
		print("Left is clear, turning left")
		pirover.turnByHeading(-turnAngle, speed=turnSpeed)
	else:
		# More distance to right, spin right (clockwise)
		print("Right is clear, turning right")
		pirover.turnByHeading(turnAngle, speed=turnSpeed)

	time.sleep(debugDelay)
#  End of turn_to_clearest

def tooClose(frontS, leftS, rightS):
	# Return false if no sensor is within minimum distance
	if(frontS>-1 and frontS<fwMinDist):
		print("Front too close")
		return True
	if(leftS>-1 and leftS<lMinDist):
		print("Left too close")
		return True
	if(rightS>-1 and rightS<rMinDist):
		print("Right too close")
		return True
	return False
		
# Testing pico comms, should never be called during normal operation
# Suggest quitting after calling this
def testPico():
	print("Testing pico")
	print("Activate pico")#
	pirover.picoActivate()
	
	# Testing data receive
	for i in range(0,1):
		picoData=pirover.getdata()
		print(picoData)
		time.sleep(1)
	
	print("Testing servos at 30 degrees")
	pirover.panAngle(30)
	pirover.tiltAngle(30)
	time.sleep(2)
	print("Return servos to 90 degrees")
	pirover.panAngle(90)
	pirover.tiltAngle(90)
		
	print("Shutdown pico")
	pirover.picoDeactivate()
# End of testPico
	
	
# ********* End of functions ***********


print("AutoDrive 2 started, using magnetometer and accelerometer....")
#pirover=piRover(left=leftPins, right=rightPins)
pirover=piRover(left=leftPins, right=rightPins, pico=True, magneto=True)

# Set up button and call back. Not using the button as part of the pirover library, so
# that we can define the emergency stop call back here
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pushButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(pushButton, GPIO.RISING, callback=button_callback, bouncetime=100)


# Test mode, comment out
#testPico()
#quit()

# Start the pico processes
pirover.picoActivate()

drSpeed = fwSpeed		# Start driving forward

# Start running then enter loop, checking positions as we go
pirover.fwSpeed(drSpeed)
runLoop = True
errorStopped = False	# Flag if motors were stopped because of error

while runLoop:
	picoData=pirover.getSensorData()
	#print(picoData)
	
	# Get the accelerometer data
	rdata = pirover.getAccel()
	if(rdata["magneto"]["chassisTilt"]>15):
		print(" ** We are tipping up, angle={:0.1f}".format(rdata["magneto"]["chassisTilt"]))
		backup()
		pirover.fwSpeed(drSpeed)
		
	# Pull out data to make references easier.
	# It is possible the data has not been populated yet, use defaults/null values
	
	# Sonics
	try:
		frontS=picoData["pico"]["sonics"][0][1]
		leftS=picoData["pico"]["sonics"][1][1]
		rightS=picoData["pico"]["sonics"][2][1]
		rearS=picoData["pico"]["sonics"][3][1]
	except KeyError:
		frontS=-1
		leftS=-1
		rightS=-1
		rearS=-1
		errorStopped=True
	
	#print(frontS, leftS, rightS)
	
	# If no reading from front, stop
	if(frontS<0):
		print("Stopping, no front sensor reading")
		errorStopped=True
	while(frontS<0):
		
		pirover.stop()
		try:
			frontS=picoData["pico"]["sonics"][0][1]
		except:
			frontS=-1
		time.sleep(0.05)
	# Restart
	#print("Errorstopped=",errorStopped)
	if(errorStopped==True):
		pirover.fwSpeed(drSpeed)
		errorStopped=False
		
	# Stop if too close at and front sensor
	if(tooClose(frontS, leftS, rightS)):
		print("Stopping, object in front at distances (front, left, right) ", frontS, leftS, rightS)
		pirover.stop()
		time.sleep(debugDelay)
	
		
		# Check out left and right distances
		# If too close to both, back up
		if(leftS>-1 and leftS<fwMinDist and rightS>-1 and rightS<fwMinDist):
			print("Too close on both sides, backing up")
			backup()
			# Now turn to the clearest side
			turn_to_clearest(leftS, rightS)
		else:
			# Turn to the clearest side
			turn_to_clearest(leftS, rightS)
		# Return to forward motion
		print("Going forward again")
		pirover.fwSpeed(drSpeed)
			
	# Give a tiny rest
	time.sleep(0.05)
# End of main loop
	

# End of main loop
pirover.stop()
pirover.picoDeactivate()


