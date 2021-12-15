#!/usr/bin/python

# HC-SR04 ultrasonic radar, using libraries built for Pi Rover Robot project
# Uses pygame for a graphical display
# Dave Hartburn - December 2021

# Run remotely with X forwarding or connect to rover remotely with IP/hostname as an argument
# It can be quite stuttery with X forwarding

# ** driveByQueue.py must be started to give the script something to talk to **

import pygame
import time
import math
import zmq
from zmq.utils.monitor import recv_monitor_message
import sys
import json

context = zmq.Context()
qhost="tcp://localhost:5555"
defport="5555"
connectTimeout=5	# How long to wait before giving up

MAXdist=50				# Maximum distance to show on radar
OBJECT_TTL=6			# How many seconds to live for, before fading from screen

# Define colours
BG=(0,0,25)				# Background
LINECOL=(200,200,200)	# Lines for the radar plot
SWEEPCOL=(0,225,100)	# Sweep colour
OBJCOL=(200,0,0)		# Colour of found object

# Define window size
WIDTH=900
MARG=40			# Margin around screen to not draw in
RADIUS=int((WIDTH-(MARG*2))/2)
HEIGHT=RADIUS+MARG*2
# Origin
OX=int(WIDTH/2)
OY=HEIGHT-MARG


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
		qhost="tcp://"+uin+":"+defport


# Connect to server
print("Connecting to "+qhost)
socket = context.socket(zmq.REQ)
# Set up a monitor to see if we connect
monitor = socket.get_monitor_socket()
socket.connect(qhost)

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

# Start pygame and create window
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("Ultrasonic RADAR")
# Init fonts
pygame.font.init()
labelFontHeight = 14
labelFont = pygame.font.Font('freesansbold.ttf',labelFontHeight)

sweepList=[]	# Maintain list of sweep objects at deminishing brightness
sweepLw=10		# Line width of sweep object
radObjList=[]	# Maintain a list of objects found on the radar


# ********* Classes *******************************
class sweepObject():
	# The sweep arm of the radar, which for effect shows a decreasing shade of the primary colour
	def __init__(self,angle,colour,max):
		self.angle=angle
		self.colour=colour
		self.alpha=1
		self.max=max
		self.life=0			# Start with life = zero. The queue processor should remove by the time we hit max
		# Calculate x and y offset (distance from radar origin)
		self.xoff=int(RADIUS*math.cos(math.radians(self.angle)))
		self.yoff=int(RADIUS*math.sin(math.radians(self.angle)))

	def update(self):
		self.life+=1
		# Weaken the colour
		self.alpha-=0.005
		# You can't use a true alpha, fudge it by blending the background colour with the foreground
		self.colour=(int(self.colour[0]*self.alpha)+int(BG[0]*(1-self.alpha)),
		             int(self.colour[1]*self.alpha)+int(BG[1]*(1-self.alpha)),
		             int(self.colour[2]*self.alpha)+int(BG[2]*(1-self.alpha)))
# End of sweepObject class

class radarObject():
	# Shows an object on the radar

	# Init with an angle and a distance to that object
	def __init__(self,angle,dist):
		self.angle=angle
		self.dist=dist
		self.origCol=OBJCOL
		self.crTime=time.time()
		self.ttl=OBJECT_TTL
		self.dieTime=self.crTime+self.ttl
		#print("RADAR object created", angle, dist,self.crTime)

	def draw(self, surf):
		# Draws the object on the surface, relative to the origin ox,oy

		# Time to die?
		if(time.time()>self.dieTime):
			return -1
		else:
			#print("Drawing", self.angle, self.dist)
			r=(self.dist/MAXdist)*RADIUS
			x=OX-int(math.cos(math.radians(self.angle))*r)
			y=OY-int(math.sin(math.radians(self.angle))*r)
			# Calculate colour, what percent to show?
			leftFrac=(self.dieTime-time.time())/self.ttl
			col=(int(self.origCol[0]*leftFrac),
					  int(self.origCol[1]*leftFrac),
					  int(self.origCol[2]*leftFrac))
			pygame.draw.circle(surf, col, (x,y), 5)
			return 0

# End of radarObject class

# ********* End of classes ************************

# ********* Functions *****************************
def drawScreen():
	# Main screen drawing function

	# Plot radar display lines
	# Radar is a semi-circle depicting 180 degrees

	# Calculate radius

	maxAng=180	# Maximum range of angle
	angGap=30	# Interval to mark out angles. Sould be a fraction of 180
	lw=2		# Width of the line
	numArcs=4	# How many division arcs


	maxAngRad=math.radians(maxAng)
	angGapRad=math.radians(angGap)

	screen.fill(BG)

	# To visualise display area
	# pygame.draw.rect(screen, (255,0,0), (MARG,MARG,WIDTH-MARG*2, HEIGHT-MARG*2), 3)
	# Draw the sweep objects
	for sw in sweepList:
		sw.update()
		pygame.draw.line(screen, sw.colour, (OX, OY), (OX-sw.xoff, OY-sw.yoff), sweepLw)

	# Draw the radar object blobs
	# The [:] makes a copy of the list and allows us to delete as we go
	for robj in radObjList[:]:
		d=robj.draw(screen)
		if(d==-1):
			radObjList.remove(robj)

	# Marker lines
	a=0
	while a<=maxAngRad:
		# Calculate end points
		ex=OX-int(RADIUS*math.cos(a))
		ey=OY-int(RADIUS*math.sin(a))

		da=math.ceil(math.degrees(a))

		pygame.draw.line(screen, LINECOL, (OX, OY), (ex, ey), lw)

		# Angle label
		lab = labelFont.render(str(da), 1, LINECOL)
		if(da<90):
			screen.blit(lab,(ex-15,ey-labelFontHeight))
		else:
			screen.blit(lab,(ex+5,ey-labelFontHeight))

		a+=angGapRad

	# Arcs
	arcGap=int(RADIUS/numArcs)
	distJump=int(MAXdist/numArcs)		# Distances to show on each arc
	distGap=distJump
	for x in range(arcGap,RADIUS+1,arcGap):
		pygame.draw.arc(screen, LINECOL, (MARG+RADIUS-x,MARG+RADIUS-x,x*2,x*2), 0, maxAngRad+0.01, lw)
		lab=labelFont.render(str(distGap)+"cm", 1, LINECOL)
		screen.blit(lab,(MARG+RADIUS+5, MARG+RADIUS-x+int(labelFontHeight/2)))
		distGap+=distJump


	pygame.display.flip()

# End of drawScreen()


# ********* End of Functions **********************

drawScreen()
sweepAngle=0
sweepStep=1
maxSweeps=60
while True:
	# Send angle to camera mount
	cmd="panangle,"+str(sweepAngle)
	#print(cmd)
	byin = bytes(cmd, 'utf-8')
	socket.send(byin)

	# Wait for response
	rdataJson=socket.recv().decode('utf-8')
	#print("Returned data:", rdataJson)

	# Get sonic reading
	#print("Get sonic reading")
	byin = bytes("getsonic,0", 'utf-8')
	socket.send(byin)

	# Wait for response
	rdataJson=socket.recv().decode('utf-8')
	#print("Returned sensor data:", rdataJson)
	rdata=json.loads(rdataJson)
	d=rdata["sonicDist"][0]
	a=rdata["panAngle"]
	#print("dist=",d)
	if(d<=MAXdist):
		# This is a distance we are interested in, create a new radar object
		robj=radarObject(a, d)
		radObjList.append(robj)

	# Remove last sweep object, if over max number
	if(len(sweepList)==maxSweeps):
		sweepList.pop(0)


	# Add new sweep object
	sObj=sweepObject(sweepAngle, SWEEPCOL, maxSweeps)
	sweepList.append(sObj)

	drawScreen()
	sweepAngle+=sweepStep
	# Check limits and 'bounce'
	if(sweepAngle<0 or sweepAngle>180):
		sweepAngle-=sweepStep*2
		sweepStep=sweepStep*-1

	#time.sleep(0.01)

pygame.quit()
