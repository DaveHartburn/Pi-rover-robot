#!/usr/bin/python

# driveByQueue - Listens for input on a lightweight queue and drives the rover
# Essentially a proxy which executes the commands on the queue. Uses ZeroMQ
#
# Dave Hartburn - September 2021

# Standard libraries
import time
import zmq
import json

# Include local pirover library
from piroverlib import piRover

# Enable queue server
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

# Define pin numbers [A, B]
leftPins=[18,12]
rightPins=[13,19]

print("driveByQueue started")
#pirover=piRover(left=leftPins, right=rightPins)
pirover=piRover(left=leftPins, right=rightPins, load=1, wifi=1)

serverRunning=True
rdata={}			# Track responses
rdataJson=""

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
	
	# Remove the message key
	rdata.pop("msg", None)
	
	if(cmdin=="stop"):
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
		if(numargs>=2):
			rdata=pirover.chSpeed(int(csvin[1]),int(csvin[2]))
		else:
			print("Need one argument for fwSpeed, sent: ",message)
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
	elif(cmdin=="getsens"):
		# Return all sensor data
		rdata=pirover.getSensorData()
	elif(message=="quit"):
		serverRunning=False
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
