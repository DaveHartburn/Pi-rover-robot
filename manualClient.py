#!/usr/bin/python

# Keyboard drive client
# A very basic client which can send a few simple commands to the
# driveByQueue server, to demonstrate use

import zmq
import time

context = zmq.Context()

# Connect to server
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

clientRunning=True
while clientRunning:
	uin = input("Enter command: ")
	print("You said ", uin)
	byin = bytes(uin, 'utf-8')
	socket.send(byin)
		
	# Wait for response
	rdataJson=socket.recv().decode('utf-8')
	print("Returned data:", rdataJson)
	
	# Quit if we sent quit
	if(uin=="quit"):
		clientRunning=False
