# Takes commands from a web page and puts them on
# a queue to be processed

import cgi
import json
import zmq

# Dictionary for return data
indata={}
indata["dave"]=44

# Essential header, we are going to return JSON
print ("Content-Type: application/json\n\n")
#print ("Content-Type: test/html\n\n")

args = cgi.parse()

if "msg" in args:
	msg=args["msg"][0]
	
	# Process the message into a command
	if(msg=="up"):
		cmd="chSpeed,10,10"
	elif(msg=="down"):
		cmd="chSpeed,-10,-10"
	elif(msg=="left"):
		cmd="chSpeed,-5,5"
	elif(msg=="right"):
		cmd="chSpeed,5,-5"
	elif(msg=="stop"):
		cmd="stop"
	elif(msg=="acw"):
		cmd="spin,-40"
	elif(msg=="cw"):
		cmd="spin,40"
	elif(msg=="getsens"):
		cmd="getsens"
	elif(msg=="tup"):
		cmd="tiltUp,5"
	elif(msg=="tdown"):
		cmd="tiltUp,-5"
	elif(msg=="panl"):
		cmd="panLeft,10"
	elif(msg=="panr"):
		cmd="panLeft,-10"
	elif(msg=="pcent"):
		cmd="panCentre"
	else:
		cmd="null"

else:
	# Invalid input, ignore
	msg=""
	cmd="null"

# Act if we have a valid command
if(cmd!="null"):
	context = zmq.Context()

	# Connect to server
	socket = context.socket(zmq.REQ)
	socket.connect("tcp://localhost:5555")		
	cmdbyt=bytes(cmd, 'utf-8')	
	socket.send(cmdbyt)
	
	# Wait for response
	rdataJson=socket.recv().decode('utf-8')
	# Return the raw JSON
	print(rdataJson)
else:
	print("{}");
