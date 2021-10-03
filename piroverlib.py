# piroverlib - Main python library for driving my Pi Rover Robot
# Dave Hartburn - September 2021
#

import RPi.GPIO as GPIO
import math
import os

# Use BCM settings, e.g. GPIO19
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# PWM motor class. Not making this an internal class to the main rover class, as it may
# be useful to have this accessible directly. For example if a third motor is added
class pwmMotor():
	# Takes two pins and controls a motor using pwm

	def __init__(self, a, b):
		self.pinA=a
		self.pinB=b
		# Set up GPIO pins
		GPIO.setup(self.pinA, GPIO.OUT, initial=GPIO.LOW)
		GPIO.setup(self.pinB, GPIO.OUT, initial=GPIO.LOW)
		self.speed=0          # 0 off, positive forward, negative reverse
		self.pwm=False     # PWM channel, default value
		self.pwmOn=-1      # -1 if we are not using PWM, otherwise will be the pin being used

	def stopPWM(self):
		# If pwm is running, stop. We are going for direct GPIO HIGH/LOW
		if(self.pwmOn>0):
			self.pwm.stop()
			self.pwmOn=-1

	def stop(self):
		# Instantly set motor to stop
		# Disable PWM if established
		self.stopPWM()
		# Set both pins to low
		GPIO.output(self.pinA, GPIO.LOW)
		GPIO.output(self.pinB, GPIO.LOW)

	def full(self, sp):
		# Run motor at full.
		# Any positive value is forward, any negative is backwards

		# Disable PWM if established
		self.stopPWM()
		if(sp==0):
			self.stop()
		elif(sp>0):
			# Full forward
			GPIO.output(self.pinA, GPIO.HIGH)
			GPIO.output(self.pinB, GPIO.LOW)
			self.speed=100
		else:
			GPIO.output(self.pinA, GPIO.LOW)
			GPIO.output(self.pinB, GPIO.HIGH)
			self.speed=-100
	# End of full()

	def setSpeed(self, sp):
		# Use PWM to set motor to speed sp
		if(sp==0):
			# Called with zero value, stop the motors
			self.stop()
		else:
			# Which pin?
			if(sp>0):
				p=self.pinA
			else:
				p=self.pinB

			# Are we already running pwm on this pin?
			if(self.pwmOn!=p):
				# No running pwm on this pin. Either the motor is stopped, running full
				# or running pwm on the other pin. In all scenarios we need to set both
				# pins to low, stop running PWM instances and set up on the new pin
				self.stop()
				
				self.pwm = GPIO.PWM(p, 1000)
				self.pwm.start(0)
				self.pwmOn=p
			# PWM established, set value
			self.speed=sp
			abssp=abs(sp)
			if(abssp>100):
				abssp=100
			self.pwm.ChangeDutyCycle(abssp)
	# End of speed()
# End of class pwmMotor

class piRover():
	# Class for driving Pi Rover Robot.
	# A two channel motor driven robot. While assembled as a 4WD, motors on each
	# side are wired to the same output, so this class would equally work as a
	# 2WD robot.
	
	name="pirover"		# If you have more than one robot controlled, name them
	
	# Init internals as null/none
	left=None	# Left motor object
	right=None	# Right motor object
	leftPins=None	# List of left motor pins
	rightPins=None	# List of right motor pins
	
	# Track object status as a python dictionary, which is returned after every
	# function call. As other sensors are added, they can be added to the dictionary.
	# We will always have a left and right motor speed.
	rdata = {
		"leftSpeed": 0,
		"rightSpeed": 0,
	}
	
	def __init__(self, **kwargs):
		# Accepts variable arguments detailing what hardware is installed,
		# what pins the motors are connected to etc. A pair of left and right
		# motor pins must be provided.
		# Valid inputs are:
		#   name="string"	Give your robot a name
		#   left=[a,b]		List of a and b pins for left motor(s)
		#   right=[a,b]		List of a and b pins for right motor(s)
		
		# Process input
		for k,v in kwargs.items():
			#print("Input = ", k , v)
			if(k=="name"):
				self.name=v
			elif(k=="left"):
				self.leftPins=v
			elif(k=="right"):
				self.rightPins=v
			elif(k=="load"):
				# We want to track system, create dictionary object
				self.rdata["load"]=0
			elif(k=="wifi"):
				# Monitor wifi rssi and noise
				self.rdata["rssi"]=0
				self.rdata["noise"]=0
				
				
		print("Hello world, I am "+self.name)
		# Sanity check
		if(self.leftPins==None):
			print("Warning: No left pins set")
		else:
			# Init left motor
			self.left=pwmMotor(self.leftPins[0], self.leftPins[1])
			
		if(self.rightPins==None):
			print("Warning: No right pins set")
		else:
			# Init right motor
			self.right=pwmMotor(self.rightPins[0], self.rightPins[1])
	# End of init
	
	def stop(self):
		# Stop both motors
		self.left.stop()
		self.right.stop()
		self.rdata["leftSpeed"]=0
		self.rdata["rightSpeed"]=0
		return self.rdata
		
	def fwFull(self, sp):
		# Both motors full. sp positive=forward, backwards=negative
		self.left.full(sp)
		self.right.full(sp)
		# Return data is 100 for each speed
		if(sp>=0):
			self.rdata["leftSpeed"]=100
			self.rdata["rightSpeed"]=100
		else:
			self.rdata["leftSpeed"]=-100
			self.rdata["rightSpeed"]=-100			
		return self.rdata

	def fwSpeed(self, sp):
		# Both motors at speed sp
		print("Setting both motors at speed ",sp)
		self.left.setSpeed(sp)
		self.right.setSpeed(sp)
		self.rdata["leftSpeed"]=sp
		self.rdata["rightSpeed"]=sp
		return self.rdata
		
	def drive(self, l, r):
		# Sets the left and right motors to speeds set by l and r
		self.left.setSpeed(l)
		self.right.setSpeed(r)
		self.rdata["leftSpeed"]=l
		self.rdata["rightSpeed"]=r
		return self.rdata
	
	def js(self, x, y):
		# Drives the rover according to a joystick x and y axis,
		# where the axis run between -100 and 100

		# Calculate power
		p=int(math.sqrt(x*x + y*y))
		# Map to left and right values
		if(x>=0):
			# Turning right
			r=y
			if(y>=0):
				# Forward right
				l=p # Left motor at power
			else:
				# Back right
				l=-p # Left motor at negative power (reverse)
		else:
			# Turning left
			l=y
			if(y>=0):
				# Forward left
				r=p
			else:
				r=-p
		# End of direction if
		self.drive(l, r)
		self.rdata["leftSpeed"]=l
		self.rdata["rightSpeed"]=r
		return self.rdata
	# End of js
		
	def spin(self, sp):
		# Spins the rover on it's axis according to speed sp.
		# Positive=clockwise
		# For clockwise, left is positive, right negative, send sp, -sp
		# However if we receive a negative value we can sent the same as 
		# -sp on the right becomes --sp which is positive
		self.drive(sp, -sp)
		self.rdata["leftSpeed"]=sp
		self.rdata["rightSpeed"]=-sp
		return self.rdata
			
	def chSpeed(self, l, r):
		# Change the left and right motors by the l and r amount
		self.rdata["leftSpeed"]=self.__addsp(self.rdata["leftSpeed"], l)
		self.rdata["rightSpeed"]=self.__addsp(self.rdata["rightSpeed"], r)
		return self.drive(self.rdata["leftSpeed"], self.rdata["rightSpeed"])
		
	def __addsp(self, x, y):
		# Adds a speed y to a value x and checks if it is in the limits -100 to 100
		z=x+y
		if(z>100):
			z=100
		elif(z<-100):
			z=-100
		return z
		
	# Sensor functions
	def getSensorData(self):
		# Get data from all defined sensors
		for key in self.rdata:
			if(key=="load"):
				self.readLoad()
			if(key=="rssi"):
				self.readWifi()
			
		return self.rdata
	# End of getSensorData
	
	def readLoad(self):
		# Read system load and set dictionary
		d=os.getloadavg()
		self.rdata["load"]=d[0]
	
	def readWifi(self):
		# Returns wifi signal and noise
		st = os.popen('cat /proc/net/wireless | tail -1')
		r = st.read()
		sp=r.split()
		self.rdata["rssi"]=sp[3]
		self.rdata["noise"]=sp[4]
			
# End of class piRover
