# Servo test. Use gpiozero library to move a sg90 servo

from gpiozero import Servo
from time import sleep
import sys

fact=False		# Default is not to use a GPIO factory
# Check for -f argument
if(len(sys.argv)>1):
	if(sys.argv[1]=="-f"):
		fact=True

if(fact==False):
	print("\n ** To call with a GPIO factory, use '-f'\n")
	servo = Servo(2)
else:
	# See video at https://www.youtube.com/watch?v=_fdwE4EznYo
	# sudo apt install python3-pigpio
	# sudo pigpiod
	
	from gpiozero.pins.pigpio import PiGPIOFactory
	factory=PiGPIOFactory()
	# Comment out if your servo is not turning the full 90, and use the additional settings
	#servo = Servo(2, pin_factory=factory)
	servo = Servo(2, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
	
	

servo.mid()
print("servo mid")
sleep(3)

print("Running through min to max")
for x in range(2):
	print(x)
	servo.min()
	print("servo min")
	sleep(3)

	servo.mid()
	print("servo mid")  
	sleep(3)

	servo.max()
	print("servo max")
	sleep(3)
  
print("Setting particular values")
for x in [-0.33,1,-1,0,-0.5,0.25,-1,0]:
	print("x=",x)
	servo.value=x
	sleep(1.5)

print("Smooth pan")
# Note: range does not allow floats
for y in range(-10,11,1):
	x=y/10
	print("x=",x)
	servo.value=x
	sleep(0.25)
	
servo.mid()
print("Done")
