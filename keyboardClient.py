#!/usr/bin/python

# A client for driveByQueue, allowing the sending of user input commands
# A quick way of testing new/changed commands

import zmq
import time
from getkey import getkey

context = zmq.Context()

# Connect to server
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

clientRunning=True
print("\nUsage:\nW and S for speed up/down")
print("A and D for left and right")
print("Z stop")
print("Q and E spin")
print("X to exit\n")

while clientRunning:
	key = getkey()
	if(key=='w'):
		# Speed up
		msg="chSpeed,10,10"
	elif(key=='s'):
		# Speed down
		msg="chSpeed,-10,-10"
	elif(key=='a'):
		# Left, drop left motor speed
		msg="chSpeed,-10,0"
	elif(key=='d'):
		# Right, drop right motor speed
		msg="chSpeed,0,-10"
	elif(key=='z'):
		msg="stop"
	elif(key=='q'):
		msg="spin,-40"
	elif(key=='e'):
		msg="spin,40"
	elif(key=='x'):
		msg="quit"
		clientRunning=False
	
	#print("Sending ", msg)
	msgbyt=bytes(msg, 'utf-8')	
	socket.send(msgbyt)
	
	# Wait for response
	rdataJson=socket.recv().decode('utf-8')
	print(rdataJson)
