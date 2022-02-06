# piroverlib-deprecated functions

# Contains a number of functions that were written and then abandoned.
# The pan/tilt and ultrasonic functions where written before I moved
# those functions to the Pico.

# Do not try to run this file!!

	# Pan tilt defaults
	panStart=83			# Starting position (may not be 100% square)
	tiltStart=90		# Starting position
	panMin=10			# Minimum pan angle
	panMax=170			# Maximum pan angle
	tiltMin=5			# Minimum tilt angle, 0 can strain motor
	tiltMax=110			# Any lower and it hits the ultrasonic

		for k,v in kwargs.items():
			elif(k=="pantilt"):
				# Using the pan tilt camera, import library
				from adafruit_servokit import ServoKit

				self.srvKit = ServoKit(channels=16)
				self.panServo=v[0]
				self.tiltServo=v[1]
				# Use extanded pulse width range
				self.srvKit.servo[self.panServo].set_pulse_width_range(500,2500)
				self.srvKit.servo[self.tiltServo].set_pulse_width_range(500,2500)
				# Set up default angles
				self.srvKit.servo[self.panServo].angle=self.panStart
				self.srvKit.servo[self.tiltServo].angle=self.tiltStart
				# Set up return data
				self.rdata["panAngle"]=self.panStart
				self.rdata["tiltAngle"]=self.tiltStart
			elif(k=="sonics"):
				self.sonics=v
				# Set up return data
				self.rdata["sonicDist"]=[]

		# Initialise ultrasonic sensors (HC-SR04s)
		if(self.sonics!=None):
			# Ultrasonic sensors have been defined, initialise
			for son in self.sonics:
				GPIO.setup(son[0], GPIO.OUT)
				GPIO.setup(son[1], GPIO.IN)
				self.rdata["sonicDist"].append(0)
			
	# End of init

	# Sensor functions
	def getSensorData(self):
		# Get data from all defined sensors
		for key in self.rdata:
			if(key=="load"):
				self.readLoad()
			if(key=="rssi"):
				self.readWifi()
			if(key=="sonicDist"):
				self.getSonic()

	def getSonic(self, n=-1, count=1, verbose=False):
		# Return the value of an ultrasonic sensor or all if n is negative
		# Can optionally supply a count for how many times to check, and return an average
		# Set verbose to true for additional output debugging and to spot outliers.
		
		tbc=0.15		# Time between multiple checks

		rtnList=[]		# Define list for returned data
		if(n<0):
			checkList=self.sonics
		else:
			checkList=[self.sonics[n]]
			
		for son in checkList:
			# Check the sensor
			maxTime=5	# Bomb out if no response before maxTime.
						# Prevents hanging on fault
				
			tr=son[0]
			ec=son[1]
			
			resultList=[]
			for c in range(count):
				# Set trigger to high
				if(verbose):
					print("Checking sensor {}, attempt {}".format(son, c))
					
				GPIO.output(tr, True)
				time.sleep(0.00001)
				GPIO.output(tr, False)
				
				callTime=time.time()	# Record time procedure called
				errTime=callTime+5
				startTime=callTime		# Set a default time, can sometimes think
				stopTime=callTime		# variables have not been set
				
				# Save start time
				while (GPIO.input(ec)==0 and time.time()<errTime):
					startTime=time.time()
					
				# Save echo time
				while (GPIO.input(ec)==1 and time.time()<errTime):
					stopTime=time.time()
					
				if(time.time()>errTime):
					dist=-1
				else:	
					elTime=stopTime-startTime			
					dist=round(elTime*17150,2)
					
				if(verbose):
					print("  Distance returned = ", dist)
				resultList.append(dist)
			# End of sensor check loop
			if(verbose):
				print("Results = ", resultList)
				
			# Calculate average
			av=sum(resultList)/len(resultList)
			if(verbose):
				print("Average = ", av)
			
			# Add distance value to list to be returned
			rtnList.append(av)
		# End of checking sonic loop
		
		# Set the global data
		self.rdata["sonicDist"]=rtnList
		return rtnList
						
		
	def panAngle(self, a):
		# Sets the pan angle and returns the general data set
		
		# Can be called with 'mid' which resets to the default middle position
		if(a=="mid"):
			a=self.panStart
			
		# Do not exceed limits
		if(a<self.panMin):
			a=self.panMin
		if(a>self.panMax):
			a=self.panMax
		self.srvKit.servo[self.panServo].angle=a
		self.rdata["panAngle"]=a
		return self.rdata

	def panLeft(self, a):
		# Pans the camera to the left (or right if a is negative)
		newAng=self.rdata["panAngle"]+a
		self.panAngle(newAng)
		return self.rdata

	def panCentre(self):
		# Centres the pan and the tilt
		self.panAngle(self.panStart)
		self.tiltAngle(self.tiltStart)
		return self.rdata
		
	def tiltAngle(self, a):
		# Sets the tilt angle and returns the general data set
		
		# Can be called with 'mid' which resets to the default middle position
		if(a=="mid"):
			a=self.tiltStart
			
		# Do not exceed limits
		if(a<self.tiltMin):
			a=self.tiltMin
		if(a>self.tiltMax):
			a=self.tiltMax
		self.srvKit.servo[self.tiltServo].angle=a
		self.rdata["tiltAngle"]=a
		return self.rdata

	def tiltUp(self, a):
		# Tilt the camera up by the angle reported
		# Need to flip as 0 is all the way up
		newAng=self.rdata["tiltAngle"]-a
		self.tiltAngle(newAng)
		return self.rdata
