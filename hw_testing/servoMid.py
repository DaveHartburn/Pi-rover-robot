#!/usr/bin/python

# Sets a servo on the specified pin to the middle position(or default)

# Usage: servoTest.py [-f] [-p n] [-e]
#  -f : Force pin factory, ensure you sudo gpiod
#  -p n : Use pin n, rather than default
#  -e : Use extended pulse range

from gpiozero import Servo
from time import sleep
import sys

pin=17		# Default pin
svalue=0	# Servo position/value

fact=False		# Default is not to use a GPIO factory
extpulse=False	# Use standard pulse width or extended

# Parse gpio arguments
sys.argv.reverse()
sys.argv.pop()	# Dump first element
while(sys.argv!=[]):
	elm=sys.argv.pop()
	if(elm=="-f"):
		fact=True
		print("Using factory")
	if(elm=="-p"):
		pin=int(sys.argv.pop())
		print("New pin", pin)
	if(elm=="-e"):
		extpulse=True
		print("Using extended pulse")
	if(elm=="-v"):
		svalue=float(sys.argv.pop())
		print("Forcing servo to", svalue)
	
# Check for -f argument
if(len(sys.argv)>1):
	if(sys.argv[1]=="-f"):
		fact=True

if(fact==False):
	print("\n ** To call with a GPIO factory, use '-f'\n")
	if(extpulse==True):
		servo = Servo(pin, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
	else:
		servo = Servo(pin)
else:
	# See video at https://www.youtube.com/watch?v=_fdwE4EznYo
	# sudo apt install python3-pigpio
	# sudo pigpiod
	
	from gpiozero.pins.pigpio import PiGPIOFactory
	factory=PiGPIOFactory()
	# Comment out if your servo is not turning the full 90, and use the additional settings
	if(extpulse==True):
		servo = Servo(pin, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
	else:
		servo = Servo(pin, pin_factory=factory)
	
	
print("Setting to value ", svalue)
servo.value=svalue
print("done")
