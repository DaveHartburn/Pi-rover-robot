#!/usr/bin/python

# Keyboard drive client
# A very basic client which can send a few simple commands to the
# driveByQueue server, to demonstrate use
# Supply with remote host or remote host:port for a remote connection

import zmq
from zmq.utils.monitor import recv_monitor_message
import time
import sys

context = zmq.Context()
qhost="tcp://localhost:5555"
defport="5555"
connectTimeout=5	# How long to wait before giving up

# Check to see if we have had another host/ip supplied
if(len(sys.argv)==2):
	uin=sys.argv[1]
	# Note, index throws an exception if not found. Have we got a colon/port?
	try:
		# Yes
		if(uin.index(':')):
			qhost="tcp://"+uin
		else:
			print("This should not happen!")
	except:
		# No
		print("No colon")
		qhost="tcp://"+uin+":"+defport

	
# Connect to server
print("Connecting to "+qhost)
socket = context.socket(zmq.REQ)
# Set up a monitor to see if we connect
monitor = socket.get_monitor_socket()
socket.connect(qhost)

# Unable to find documentation on monitor events, however source is at:
# https://github.com/zeromq/pyzmq/blob/main/zmq/utils/constant_names.py
#        'EVENT_CONNECTED', (1)
#        'EVENT_CONNECT_DELAYED', (2)
#        'EVENT_CONNECT_RETRIED', (4)
#        'EVENT_LISTENING', (8)
#        'EVENT_BIND_FAILED', (16)
#        'EVENT_ACCEPTED', (32)
#        'EVENT_ACCEPT_FAILED', (64)
#        'EVENT_CLOSED', (128)
#        'EVENT_CLOSE_FAILED', (256)
#        'EVENT_DISCONNECTED', (512)
#        'EVENT_ALL', (65536)

conQuitTime=time.time()+connectTimeout
conLoop=True
while conLoop:
	zmqstatus = recv_monitor_message(monitor)
	#print(zmqstatus)
	if(zmqstatus['event']==zmq.EVENT_CONNECTED):
		print("Successful connection")
		conLoop=False
	else:
		if(time.time()>conQuitTime):
			print("Timeout: Unable to connect to "+qhost)
			quit()

clientRunning=True
while clientRunning:
	uin = input("Enter command: ")
	#print("You said ", uin)
	if(uin=="exit"):
		# Quit client but do not kill the queue runner
		clientRunning=False
	else:
		byin = bytes(uin, 'utf-8')
		socket.send(byin)
			
		# Wait for response
		rdataJson=socket.recv().decode('utf-8')
		print("Returned data:", rdataJson)
		
		# Quit if we sent quit
		if(uin=="quit"):
			clientRunning=False
