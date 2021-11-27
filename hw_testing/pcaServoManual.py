#!/usr/bin/python

# Servo test using PCA9685 16 channel servo driver
# Servos connected to 0 and 1

# Built following Adafruit guide: https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi
# sudo pip3 install adafruit-circuitpython-servokit

from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

endprog=False

print("Enter commands:")
print("  servo x : Change the servo number (default 0)")
print("  a       : Change current servo to angle (integer) a")
print("  quit    : Quit program")

# Set default servo
s=0
kit.servo[s].set_pulse_width_range(500,2500)

while endprog==False:
	# Get user input
	uin=input("servo[{}]: ".format(s))
	if(uin=="quit"):
		endprog=True
	elif(uin.startswith("servo")):
		print("Changing servo")
		# Break up the string
		sp=uin.split()
		s=int(sp[1])
		kit.servo[s].set_pulse_width_range(500,2500)
		print("Servo changed to", s)
	elif(uin.isdigit()):
		a=int(uin)
		print("Set angle on servo {} to {}".format(a, s))
		kit.servo[s].angle=a
	else:
		print("Unknown input")
		
