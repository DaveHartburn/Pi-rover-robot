#!/usr/bin/python

# Com test - Pi end
# Run this bit on the Pi for basic UART/Serial communication

import serial
import time

# Init serial port and print details
sport = serial.Serial("/dev/ttyS0", 115200)
print(sport)

print("Serial test 1 - Run on the Pi not the Pico")
data="Hello from Pi\n".encode('UTF-8')
sport.write(data)

x = 0
while True:
	# Check for incoming data
	if(sport.in_waiting > 0):
		rawIn = bytearray()
		while (sport.in_waiting > 0):
			# Read until will read until we get a line ending
			rawIn += sport.read_until()
			print('.',end='')
		print("")
		print("Data Received")
		#print(rawIn)
		
		# Raw data is a byte stream, convert
		# Need to use a try/except as control characters may cause an issue
		try:
			dataIn = rawIn.decode('utf-8').strip()
			print("  Incoming :", dataIn)
		except:
			print("Unable to decode")
		
	# Output an incremental counter
	msg = "x = {}\n".format(x)
	print("Sending:",msg,end='')
	data=msg.encode('UTF-8')
	sport.write(data)
	x+=1
	time.sleep(1)
