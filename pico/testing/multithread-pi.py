#!/usr/bin/python

# Multithredded test - the Pi end
# Run this bit on the Pi for basic UART/Serial communication

import serial
import time

runTime=30			# Run for 30 seconds
toggleInt=1  		# Toggle every second
dataInt=1.5 		# Get data every 1.5 seconds

dataTimeOut=5		# Time out after 5 seconds

# Init serial port and print details
sport = serial.Serial("/dev/ttyS0", 115200)
print(sport)

print("Multithreadded test - Run on the Pi not the Pico")

def sendData(msg):
	# Send data
	
	print("Sending:",msg)
	data=msg.encode('UTF-8')
	sport.write(data)

def receiveData():
	# Wait for data or time out
	timeOut=time.time()+dataTimeOut
	dataIn="Error_timeout"
	
	while (time.time()<timeOut):
		if(sport.in_waiting>0):
			# There is data
			#print("There is data waiting")
			rawIn = bytearray()
			while (sport.in_waiting > 0):
				# Read until line ending
				rawIn += sport.read_until()
				#print('.',end='')
				
			# Raw data is a byte stream, convert
			# Need to use a try/except as control characters may cause an issue
			try:
				dataIn = rawIn.decode('utf-8').strip()
				#print("  Incoming :", dataIn)
			except:
				dataIn = "Error_decode"
			# We got something, drop out of loop
			#print("Data received")
			break
	# End of while loop, if a timeout then dataIn will be unchanged
	
	return dataIn
# End of receiveData
			
def send_receiveData(msg):
	# Sends data and waits for a response
	sendData(msg)
	return receiveData()
	
	
endTime=time.time()+runTime
nextToggle=0
nextData=0

while time.time()<endTime:
	if(time.time()>nextToggle):
		rtn=send_receiveData("toggleLED")
		print(rtn)
		nextToggle=time.time()+toggleInt
	if(time.time()>nextData):
		rtn=send_receiveData("dataRequest")
		print(rtn)
		nextData=time.time()+dataInt
# Loop completed, tell the Pico to stop
sendData("quit")
print("Finished")
		
