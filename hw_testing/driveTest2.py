#!/usr/bin/python

# First drive test using Blue Dot joystick

# Import modules
from bluedot import BlueDot
import time
import RPi.GPIO as GPIO
import math
from signal import pause

# Use BCM settings, e.g. GPIO19
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Define pin numbers [A, B]
leftPins=[18,12]
rightPins=[13,19]

class pwmMotor():
      # Takes two pins and controls a motor using pwm

      def __init__(self, a, b):
          self.pinA=a
          self.pinB=b
          print(a,type(a),b,type(b))
          # Set up GPIO pins
          GPIO.setup(self.pinA, GPIO.OUT, initial=GPIO.LOW)
          GPIO.setup(self.pinB, GPIO.OUT, initial=GPIO.LOW)
          print("Started new motor instance")
          self.speed=0          # 0 off, positive forward, negative reverse
          self.pwm=False     # PWM channel, default value
          self.pwmOn=-1      # -1 if we are not using PWM, otherwise will be the pin being used

      def stopPWM(self):
          # If pwm is running, stop. We are going for direct GPIO HIGH/LOW
          if(self.pwmOn>0):
              self.pwm.stop()
              self.pwmOn=-1

      def stop(self):
          # Instantly set motor to stop
          # Disable PWM if established
          self.stopPWM()
          # Set both pins to low
          GPIO.output(self.pinA, GPIO.LOW)
          GPIO.output(self.pinB, GPIO.LOW)

      def full(self, sp):
          # Run motor at full.
          # Any positive value is forward, any negative is backwards

          # Disable PWM if established
          self.stopPWM()
          if(sp==0):
              self.stop()
          elif(sp>0):
              # Full forward
              GPIO.output(self.pinA, GPIO.HIGH)
              GPIO.output(self.pinB, GPIO.LOW)
              self.speed=100
          else:
              GPIO.output(self.pinA, GPIO.LOW)
              GPIO.output(self.pinB, GPIO.HIGH)
              self.speed=-100
      # End of full()

      def setSpeed(self, sp):
          # Use PWM to set motor to speed sp
          if(sp==0):
              # Called with zero value, stop the motors
              self.stop()
          else:
              # Which pin?
              if(sp>0):
                  p=self.pinA
              else:
                  p=self.pinB

              # Are we already running pwm on this pin?
              if(self.pwmOn!=p):
                  # No, need to set up pwm
                  if(self.pwmOn!=-1):
                      # Running instance in other direction, kill it
                      self.pwm.stop()
                  self.pwm = GPIO.PWM(p, 1000)
                  self.pwm.start(0)
                  self.pwmOn=p
              # PWM established, set value
              self.speed=sp
              abssp=abs(sp)
              if(abssp>100):
                  abssp=100
              self.pwm.ChangeDutyCycle(abssp)

      # End of speed()

 # End of class pwmMotor

def jsMap(i):
    # Takes a value -1 to 1 and maps it to -100 to 100
    j=int(i*100)
    return j

print("Starting driving test 2")

# Set up motors
left=pwmMotor(leftPins[0], leftPins[1])
right=pwmMotor(rightPins[0], rightPins[1])

# Establish blue dot
print("Starting bluedot connection")
bd = BlueDot(cols=2,rows=3)
# Top row, joystick, invisible
bd[1,0].visible=False
# Middle row, gap
bd[0,1].visible=False
bd[1,1].visible=False
# Bottom row, ACW, CW
bd[0,2].color="red"
bd[1,2].color="red"

while True:
    if bd.is_connected:
        break
print("Connected")

def moveBot(pos):
    bdJS.color = (255,128,0)
    xin,yin=pos.x, pos.y
    x=jsMap(xin)
    y=jsMap(yin)
    # Calculate power
    p=int(math.sqrt(x*x + y*y))
    # Map to left and right values
    if(x>=0):
        # Turning right
        r=y
        if(y>=0):
            # Forward right
            l=p # Left motor at power
        else:
            # Back right
            l=-p # Left motor at negative power (reverse)
    else:
        # Turning left
        l=y
        if(y>=0):
            # Forward left
            r=p
        else:
            r=-p
    # End of direction if
    left.setSpeed(l)
    right.setSpeed(r)
    #print("Left = {}, Right = {}".format(l,r))

def acwTurn(pos):
    bdACW.color = (255,200,0)
    d=pos.distance
    p=jsMap(d)
    # ACW is right forward, left bakwards
    l=-p
    r=p
    left.setSpeed(l)
    right.setSpeed(r)
    #print("Left = {}, Right = {}".format(l,r))


def cwTurn(pos):
    bdCW.color = (255,200,0)
    d=pos.distance
    p=jsMap(d)
    # CW is left forward, right bakwards
    l=p
    r=-p
    left.setSpeed(l)
    right.setSpeed(r)
    #print("Left = {}, Right = {}".format(l,r))


def stop():
    #print("STOP!!!")
    left.stop()
    right.stop()
    bdJS.color = "blue"
    bdCW.color = "red"
    bdACW.color = "red"

# Name the components
bdJS=bd[0,0]    # Joystick
bdACW=bd[0,2]   # Anti-clockwise button
bdCW=bd[1,2]    # clockwise button
bdJS.when_pressed = moveBot
bdJS.when_moved = moveBot

bdACW.when_pressed = acwTurn
bdACW.when_moved = acwTurn

bdCW.when_pressed = cwTurn
bdCW.when_moved = cwTurn

bd.when_released = stop # All buttons stop

pause()
exit(0)

