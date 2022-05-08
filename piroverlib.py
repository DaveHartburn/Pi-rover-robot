# piroverlib - Main python library for driving my Pi Rover Robot
# Dave Hartburn - September 2021
#

import RPi.GPIO as GPIO
import math
import os
import time
import serial
from threading import Thread
import json

# Required for LSM303AGR
import board
import adafruit_lsm303_accel
import adafruit_lis2mdl

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

	buttonPin=None	# Pin for a push button
	picoSlave=False	# True or false if you have a Pi Pico as a slave device
	sport=None		# Set as serial port device
	picoTimeout=3000	# Timeout serial comms after 3 seconds
	activated=False	# False if pico slave is not activated
	magneto=False	# No magnetomoeter
		
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
		#	load=1			Return load values with data
		#	wifi=1			Return wifi RSSI and noise with data
		
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
			elif(k=="button"):
				self.buttonPin=v
				# Set up button pin will internal pull up resistor
				GPIO.setup(self.buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			elif(k=="pico"):
				# We have a pico slave. Encode other hardware directly onto it.
				# Dynamic via this library is far too complicated!
				self.picoSlave=True
				# Init serial point
				#print("Init serial port")
				self.sport = serial.Serial("/dev/ttyS0", 115200)
				#print(self.sport)
			elif(k=="magneto"):
				# Use a LSM303AGR magnetometer for heading info, connected via I2C
				self.magneto=True

		# End of argument processing / setup		
				
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
			
		# Set up magnetometer
		if(self.magneto==True):
			print("Setting up magnetometer")
			# Init I2C
			self.i2c = board.I2C()
			self.accel = adafruit_lsm303_accel.LSM303_Accel(self.i2c)
			self.magsens = adafruit_lis2mdl.LIS2MDL(self.i2c)
			# Run lis2mdl_calibrate for hardiron_calibration array
			self.hardiron_calibration = [[-54.75, 43.199999999999996], [-77.55, 10.35], [-119.1, 16.349999999999998]]
			# Set up return data
			self.rdata["magneto"]={}
			self.rdata["magneto"]["raw"]=[]
			self.rdata["magneto"]["heading"]=-255		# -255 is an error state
			self.rdata["magneto"]["accelraw"]=[]
			self.rdata["magneto"]["chassisTilt"]=-255
	# End of init

	def getdata(self):
		# Return the data array
		return self.rdata
		
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
		# Get data from all local defined sensors (not Pico)
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
		return d
	
	def readWifi(self):
		# Returns wifi signal and noise
		st = os.popen('cat /proc/net/wireless | tail -1')
		r = st.read()
		sp=r.split()
		self.rdata["rssi"]=sp[3]
		self.rdata["noise"]=sp[4]
		return [sp[3], sp[4]]

		
	def getButton(self):
		# Return the state of the push button
		return GPIO.input(self.buttonPin)
		
	# Serial functions
	def sendToPico(self, msg):
		# Send over serial port to pico
		# Terminate msg with new line
		msg+='\n'
		data=msg.encode('UTF-8')
		self.sport.write(data)
		
	def checkSerial(self):
		# Check if there is data in the serial queue
		if(self.sport.in_waiting>0):
			return True
		else:
			return False
		
	def getFromPico(self):
		# Receive from pico or timeout
		sport=self.sport
		timeoutTime=time.time()+self.picoTimeout
		if(sport.in_waiting>0):
			rawIn = bytearray()
			dataIn = ""
			while (sport.in_waiting > 0 and time.time()<timeoutTime):
				# Read until we get a line ending
				rawIn += sport.read_until()
			
				# Raw data is a byte stream, convert
				# Need to use a try/except as control characters may cause an issue
				try:
					dataIn = rawIn.decode('utf-8').strip()
					#print("  Incoming :", dataIn)
				except:
					print("Unable to decode")
					print(rawIn)
					return ""
			return dataIn

		else:
			# Queue was empty, return empty string
			return ""
	# End of getFromPico
		
	def picoRthread(self):
		# Pico receive thread. Will sit in a loop waiting for serial data from the Pico
		# Then add it to the main data array
		# Also sends activate to the Pico to start it's loop
		self.activated=True
		
		# Start pico loop
		self.sendToPico("activate")
		
		# Set to activated 
		while self.activated:
			# Check for serial input
			if(self.sport.in_waiting>0):
				dataIn = self.getFromPico()
				#print("** Got data **")
				#print(dataIn)
				if(dataIn!=""):					
					# dataIn is a string, convert to JSON
					# May be garbage
					try:
						jsonIn = json.loads(dataIn)
						#print(jsonIn)
						# Add timestamp
						jsonIn["timestamp"]=time.time()
						self.rdata["pico"]=jsonIn
						#print("Whole JSON structure");
						#print(self.rdata)
						#print("Left speed", self.rdata["leftSpeed"]);
						#print("Pico ", self.rdata["pico"]);
						#print("Pico timestamp", self.rdata["pico"]["timestamp"]);
					except:
						print("Error decoding JSON");
					
			time.sleep(0.05)
			
		print("picoRthread ended")		
	# End of picoRthread

	def picoActivate(self):
		# Starts the picoRthread
		print("Activating pico and starting thread")
		picoThread = Thread(target=self.picoRthread)
		picoThread.daemon = True
		picoThread.start()
		
	def picoDeactivate(self):
		# Sends deactivate to the pico and stops the thread by setting activated to false
		self.activated=False
		# Don't try to deactivate if no pico slave. Do not give error message as this may be called from driveByQueue
		# and have no pico defined
		if(self.picoSlave):
			self.sendToPico("deactivate")

	def picoCmd(self,cmd,arg):
		# Sends a pico command with a single argument
		cmdOut="{},{}".format(cmd,arg)
		self.sendToPico(cmdOut)
		
	# Pan/tilt functions
	def panAngle(self, a):
		# Sets the pan angle
		if(a=="mid"):
			angle=90
		else:
			angle=a
		self.picoCmd("panangle",angle)
		return self.rdata
		
	def panLeft(self, a):
		self.picoCmd("panleft",a)
		return self.rdata
		
	def tiltAngle(self, a):
		# Sets the tilt angle
		if(a=="mid"):
			angle=90
		else:
			angle=a
		self.picoCmd("tiltangle",angle)
		return self.rdata
		
	def tiltUp(self, a):
		self.picoCmd("tiltup",a)
		return self.rdata

	# *** LSM303AGR, accelerometer and magnetometer functions ****
	def magNormalize(self, _magvals):
		# Normalise heading readings
		ret = [0, 0, 0]
		for i, axis in enumerate(_magvals):
			minv, maxv = self.hardiron_calibration[i]
			axis = min(max(minv, axis), maxv)  # keep within min/max calibration
			ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
		return ret

	def getHeading(self, attempts=1, interval=0.01):
		# Get magnetometer heading. -255 is an error
		# Also returns tilt, via rdata settings
		# By default will just try once, but can have multiple attempts
		# for greater accuracy
		totalH=0
		for i in range(1,attempts+1):
			#print("Getting heading, attempt", i)
			magvals = self.magsens.magnetic
			normvals = self.magNormalize(magvals)
			#print("magnetometer: %s -> %s" % (magvals, normvals))

			# we will only use X and Y for the compass calculations, so hold it level!
			compass_heading = int(math.atan2(normvals[1], normvals[0]) * 180.0 / -math.pi)
			# compass_heading is between -180 and +180 since atan2 returns -pi to +pi
			# this translates it to be between 0 and 360
			# Minus added before math.pi as original code had east as 270 and west as 90.
			compass_heading += 180

			#print("Calibrated heading: {}".format(compass_heading))			
			totalH+=compass_heading
			
			# Don't sleep on last attempt
			if(i!=attempts):
				time.sleep(interval)
		
		# Compute average
		h=totalH/attempts
		self.rdata["magneto"]["raw"]=normvals
		self.rdata["magneto"]["heading"]=round(h,1)
			
		return self.rdata

	def turnToHeading(self, heading, speed=30, fdir=0):
		# Turn to the heading, 'heading' using default or specified turning speed
		# By default it will turn the shortest direction, but it can be forced 
		# with fdir=1 for clockwise or -1 for anti-clockwise
		#print("Turning to heading {}, speed {} and force direction status {}".format(heading, speed, fdir))
		self.getHeading()
		initHead=self.rdata["magneto"]["heading"]
		# Is the direction forced?
		if(fdir!=0):
			# Yes
			direct=fdir
		else:
			# No, calculate bearing difference
			headDiff=((((initHead-heading)%360)+540)%360)-180

			#print("Change in heading", headDiff)
			if(headDiff<0):
				direct=1
			else:
				direct=-1
		#print("Turning to {} from {} (difference {}) in direction {} (1=CW)".format(heading,initHead,headDiff,direct))
		turnSpeed=speed*direct		# Will turn negative if -1
		#time.sleep(2)

		# Start spin
		self.spin(turnSpeed)
		while(self.stillMagTurning(self.rdata["magneto"]["heading"],direct,heading)):
			self.getHeading()
			# Be nice
			time.sleep(0.001)
		self.stop()
		
		return self.rdata
		# *** End of LSM303AGR functions
	
	def stillMagTurning(self, now, direct, targ):
		# Return true if we should still turn. There are a number of different scenarios
		# Turning clockwise?
		if(direct==1):
			# Turning clockwise to a greater angle
			# If we are on a heading over 180 and the target is less than 180, keep turning
			if(now>180 and targ<180):
				return True
			# Not crossing the 0/360 line, keep turning if needed
			if(now<targ):
				return True
		else:
			# Turning anticlockwise to a smaller angle
			# If we are on a heading less than 180 and the target is over 180, keep turning
			if(now<180 and targ>180):
				return True
			# Not crossing the 0/360 line, keep turning if needed
			if(now>targ):
				return True
		return False
		
	def turnByHeading(self, ang, speed=30):
		# Turn by speficied angle
		self.getHeading()
		h=self.rdata["magneto"]["heading"]+ang
		if(h>360):
			h-=360
		if(h<0):
			h+=360
		self.turnToHeading(h, speed=speed)
		
	def getAccel(self):
		# Return data from the accelerometer, including calculations for tilt (pitch)
		accvals = self.accel.acceleration
		ax = accvals[0]
		ay = accvals[1]
		az = accvals[2]
	
		# Perform calculations
		tilt = math.atan2((-ax), math.sqrt(ay*ay+az*az)) * 180 / math.pi
		
		# Set into array
		self.rdata["magneto"]["accelraw"]=accvals
		self.rdata["magneto"]["chassisTilt"]=tilt
		return self.rdata
		
# End of class piRover
