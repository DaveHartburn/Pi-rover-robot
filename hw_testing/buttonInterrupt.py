#!/usr/bin/python

# Button interrupt test

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

buttonPin=27

quitLimit=5				# Quit when the button has been pressed this many times
pressCount=0

# Set up button pin will internal pull up resistor
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Define interrupt callback
def button_pressed(channel):
	global pressCount, loopRunning
	pressCount+=1
	print("Button pressed {} times".format(pressCount))
	if(pressCount>=quitLimit):
		loopRunning=False
	
	
GPIO.add_event_detect(buttonPin, GPIO.RISING, callback=button_pressed, bouncetime=100)

loopRunning=True
count=0;
startTime=time.time()
while loopRunning:
	runTime=time.time()-startTime
	buttonState=GPIO.input(buttonPin)
	print("Loop running #{}, run time={:.1f} seconds. Button state={}".format(count, runTime, buttonState));
	time.sleep(3)
	count+=1
	
print("Button was pressed {} times, quitting".format(pressCount))
GPIO.cleanup()
