#!/usr/bin/python

# Servo test using PCA9685 16 channel servo driver
# Servos connected to 0 and 1

# Built following Adafruit guide: https://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi
# sudo pip3 install adafruit-circuitpython-servokit

from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

servoList=[0,1]
angleList=[0,45,90,110,160,180,90,0]
for s in servoList:
	print("Servo ", s)
	kit.servo[s].set_pulse_width_range(500,2500)
	for a in angleList:
		print("  angle =", a)
		kit.servo[s].angle=a
		time.sleep(1)
	# Slow pan
	print("Panning...")
	for x in range(0,180):
		kit.servo[s].angle=x
		time.sleep(0.05)
	print("Park in middle position")
	kit.servo[s].angle=90
		
