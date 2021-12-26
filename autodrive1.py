#!/usr/bin/python

# Autodrive 1 - A basic automated driving using the ultrasonic sensors
#   - Drive forward until it gets within a set distance of an object
#   - Look 45 degrees left and right, then turn the direction that is most clear
#	- If both directions show less than the set distance, then back up a bit
#	- If both are equal (within a threshold) then turn the same direction as the last turn (default right)
#
# Dave Hartburn - December 2021
#

# Standard libraries
import time
import json
import RPi.GPIO as GPIO


# Include local pirover library
from piroverlib import piRover


# Define constants
fwSpeed = 50			# Percent forward speed
bwSpeed = 30			# Percent backwards speed (is negated in function, don't make negative here!)
turnSpeed = 50			# Spin rate
fwMinDist = 20			# cm distance to stop when going forward
bwMinDist = 10			# cm distance to stop when going backwards
sonicRead = 0.2			# Interval to wait between sonic sensor readings

backupTime = 2			# Number of seconds to run backwards for
turnTime = 1			# Number of seconds to turn for
quitDist = 4			# Quit if both sensors read less than this distance
panLook = 45			# Amount to look left and right

# Define pin numbers [A, B]
leftPins=[18,12]
rightPins=[13,19]
pantilt=[0,1]		# Servo slots on PCA9685
# Ultrasonic pins (GPIO numbers) are a list of pairs for each sensor, trigger & echo
sonicPins=[ [4,17], [14,15] ]
pushButton=27		# Breadboard pushbutton

# ********* Functions ******************
def backup():
	print("Backing up")
	backing=True
	pirover.fwSpeed(0-bwSpeed)
	endTime=time.time()+backupTime
	while backing:
		d = pirover.getSonic()
		if(d[1]<bwMinDist):
			# Hit minimum distance, stop and end
			pirover.stop()
			backing=False
		if(time.time()>endTime):
			pirover.stop()
			backing=False
		time.sleep(sonicRead)
	print("Done backing up")
	
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
	GPIO.cleanup()
	print("Emergency STOP!!")
	quit()
	
def turn_to_clearest(ab):
	# Function to turn in the direction of the clearest route
	# ab should contain the values of lookAbout() - [l ,r] distances

	# Turn either left or right
	if(ab[0]>=ab[1]):
		# More distance to left, spin left (anti-clockwise)
		print("Left is clear, turning left")
		pirover.spin(-turnSpeed)
	else:
		# More distance to left, spin left (anti-clockwise)
		print("Right is clear, turning right")
		pirover.spin(turnSpeed)
	time.sleep(turnTime)
	pirover.stop()
	
# ********* End of functions ***********


print("AutoDrive 1 started....")
#pirover=piRover(left=leftPins, right=rightPins)
pirover=piRover(left=leftPins, right=rightPins, pantilt=pantilt, sonics=sonicPins)

# Set up button and call back. Not using the button as part of the pirover library, so
# that we can define the emergency stop call back here
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pushButton, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(pushButton, GPIO.RISING, callback=button_callback, bouncetime=100)

drSpeed = fwSpeed		# Start driving forward

# Start running then enter loop, checking positions as we go
pirover.fwSpeed(drSpeed)
runLoop = True
while runLoop:
	# Read ultrasonic sensors
	d = pirover.getSonic()
	print(d)
	if(d[0]<quitDist and d[1]<quitDist):
		runLoop = False
		print("Quitting, both sensors at minimum distance. Stuck?!")

	# Check running direction
	if(drSpeed>0):
		# Running forward
		if(d[0]<fwMinDist):
			print("Reached minimum front distance")
			pirover.stop()
			ab = lookAbout()
			print("Distances read [left, right] are: ",ab)
			# If too close to both, back up
			if(ab[0]<fwMinDist and ab[1]<fwMinDist):
				print("Too close, backing up")
				backup()
				print("Look again")
				ab = lookAbout()
				turn_to_clearest(ab)
			else:
				turn_to_clearest(ab)
			# Start moving again
			pirover.fwSpeed(drSpeed)
	
	time.sleep(sonicRead)
# End of main loop
pirover.stop()


