#!/usr/bin/python

# Basic motor control. Turning the two motor channels back and forward.
# Two 12v motors connected to a Cytron MDD3A. 12v power supply must be used
# This third program introduces a class for the motors and allows us to
# independently control the speed of each motor

# From the docs:
#  IN A     IN B     Motor
#  Low      Low      Break
#  HIGH     Low      Forward
#  Low      HIGH     Reverse
#  HIGH     HIGH     Break

# Wiring:
# M1A - GPIO 18 (pin 12 PWM 0)
# M1B - GPIO 12 (pin 32 PWM 0)
# GND - GND (any, e.g. pin 39) - they must share a common ground
# M2A - GPIO 13 (pin 33 PWM 1)
# M2B - GPIO 19 (pin 35 PWM 1)

# Import modules
import time
import RPi.GPIO as GPIO

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
              self.pwm.ChangeDutyCycle(abs(sp))
      # End of speed()

 # End of class pwmMotor



print("Starting motor test")
time.sleep(1)

# Set up motors
left=pwmMotor(leftPins[0], leftPins[1])
right=pwmMotor(rightPins[0], rightPins[1])


print("Forward")
left.full(100)
right.full(100)
time.sleep(2)
left.stop()
right.stop()
time.sleep(1)

print("Reverse")
left.full(-100)
right.full(-100)
time.sleep(2)
left.stop()
right.stop()
time.sleep(1)

for x in range(-100,101,20):
    print('Speed = {}'.format(x))

    left.setSpeed(x)
    right.setSpeed(x)
    time.sleep(1)
time.sleep(1)
left.stop()
right.stop()
time.sleep(1)

print("Left forward 80%, right backwards 40%")
left.setSpeed(80)
right.setSpeed(-20)
time.sleep(6)
left.stop()
right.stop()

print("Done")
#
