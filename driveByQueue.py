#!/usr/bin/python

# driveByQueue - Listens for input on a lightweight queue and drives the rover
# Essentially a proxy which executes the commands on the queue. Uses ZeroMQ
#
# Dave Hartburn - September 2021

# Standard libraries
import time
import zmq
import json
import sys

# Include local pirover library
from piroverlib import piRover

# Enable queue server
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

# Define pin numbers [A, B]
leftPins=[18,12]
rightPins=[13,19]
pantilt=[0,1]		# Servo slots on PCA9685
# Ultrasonic pins (GPIO numbers) are a list of pairs for each sensor, trigger & echo
sonicPins=[ [4,17], [14,15] ]

print("driveByQueue started")
#pirover=piRover(left=leftPins, right=rightPins)
pirover=piRover(left=leftPins, right=rightPins, pico=True)

serverRunning=True
rdata={}			# Track responses
rdataJson=""

# Check for command line arguments
# Initially can only send a '-a' to activate pico on start
if(len(sys.argv) > 1):
	if(sys.argv[1]=="-a"):
		print("Activating pico on start")
		pirover.picoActivate()
# End of argument processing

# Loop for input
while serverRunning:
	#  Wait for next request from client
	message = socket.recv().decode('utf-8')
	#print(f"Received request: {message}")
	
	# Break into CSV. Assume input is in sensible format
	csvin=message.split(',')
	# Check what command has been sent, csvin[0] should be the command
	# Make case insensitive
	cmdin=csvin[0].lower()
	numargs=len(csvin)-1		# Number of arguments supplied
	
	# Blank the internal message 
	#rdata["msg"]=""
	
	if(cmdin=="getdata"):
		# Get the latest data from the library
		rdata=pirover.getdata()
	elif(cmdin=="stop"):
		rdata=pirover.stop()
	elif(cmdin=="fwfull"):
		if(numargs>=1):
			rdata=pirover.fwFull(int(csvin[1]))
		else:
			print("Need one argument for fwfull, sent: ",message)
	elif(cmdin=="fwspeed"):
		if(numargs>=1):
			rdata=pirover.fwSpeed(int(csvin[1]))
		else:
			print("Need one argument for fwSpeed, sent: ",message)
	elif(cmdin=="chspeed"):
		if(numargs>=1):
			rdata=pirover.chSpeed(int(csvin[1]),int(csvin[2]))
		else:
			print("Need two arguments for chSpeed, sent: ",message)
	elif(cmdin=="drive"):
		if(numargs>=1):
			rdata=pirover.drive(int(csvin[1]),int(csvin[2]))
		else:
			print("Need two arguments for drive, sent: ",message)
	elif(cmdin=="js"):
		if(numargs>=1):
			rdata=pirover.js(int(csvin[1]),int(csvin[2]))
		else:
			print("Need two arguments for js, sent: ",message)
	elif(cmdin=="spin"):
		if(numargs>=1):
			rdata=pirover.spin(int(csvin[1]))
		else:
			print("Need one argument for spin, sent: ",message)
	elif(cmdin=="panangle"):
		if(numargs>=1):
			if(csvin[1]=="mid"):
				rdata=pirover.panAngle("mid")
			else:
				rdata=pirover.panAngle(int(csvin[1]))
		else:
			print("Need one argument for panangle, self: ", message)
	elif(cmdin=="panleft"):
		if(numargs>=1):
			rdata=pirover.panLeft(int(csvin[1]))
		else:
			print("Need one argument for panleft, self: ", message)
	elif(cmdin=="tiltangle"):
		if(numargs>=1):
			if(csvin[1]=="mid"):
				rdata=pirover.tiltAngle("mid")
			else:
				rdata=pirover.tiltAngle(int(csvin[1]))
		else:
			print("Need one argument for tiltangle, self: ", message)
	elif(cmdin=="tiltup"):
		if(numargs>=1):
			rdata=pirover.tiltUp(int(csvin[1]))
		else:
			print("Need one argument for tiltup, self: ", message)
	elif(cmdin=="getsens"):
		# Return all sensor data
		rdata=pirover.getSensorData()
	elif(cmdin=="getsonic"):
		# Just get sonic data, may be just one sensor
		if(numargs>=1):
			rdata["sonicDist"]=pirover.getSonic(int(csvin[1]))
		else:
			# No argument, get all ultrasonic sensors
			rdata["sonicDist"]=pirover.getSonic()
	elif(cmdin=="sendpico"):
		# Send a command to the pico
		# Collapse the CSV, removing the command off the front first
		csvin.pop(0)
		str=",".join(csvin)
		pirover.sendToPico(str)
	elif(cmdin=="checkserial"):
		# Return true or false if there is data in the queue
		# Use for testing, thread should check regularly
		print("Checking the serial buffer")
		s=pirover.checkSerial()
		print(s)
	elif(cmdin=="getpico"):
		# Gets data from the pico
		# Use for testing, thread should check regularly
		d=pirover.getFromPico()
		print(d)
	elif(cmdin=="activate"):
		# Activate the pico loop and serial receive thread
		pirover.picoActivate()
	elif(cmdin=="deactivate"):
		pirover.picoDeactivate()
	elif(message=="quit"):
		serverRunning=False
		# Also shutdown pico
		pirover.picoDeactivate()
		rdata["msg"]="Quit"
	else:
		print("Unknown command "+csvin[0])
		rdata["msg"]="Unknown command"
		
	# Produce JSON from the returned data, which we always reply with
	rdataJson=json.dumps(rdata)
	#print(rdataJson)
	byt=bytes(rdataJson, 'utf-8')
	socket.send(byt)
	
# End of serverRunning loop / main loop
