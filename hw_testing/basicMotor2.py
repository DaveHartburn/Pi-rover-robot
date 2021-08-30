#!/usr/bin/python

# Basic motor control. Turning the two motor channels back and forward.
# Two 12v motors connected to a Cytron MDD3A. 12v power supply must be used
# This second program uses PWM to control the speed of the motors

# It only controls the one motor

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

# Define pin numbers
M1A=18
M1B=12
M2A=13
M2B=19

# Set up GPIO pins
GPIO.setup(M1A, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(M1B, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(M2A, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(M2B, GPIO.OUT, initial=GPIO.LOW)


print("Starting motor test")
time.sleep(1)

print("Forward")
# Set up PWM channel
pwmA = GPIO.PWM(M1A, 1000)
pwmA.start(0)
for duty in range(0,101):
    pwmA.ChangeDutyCycle(duty)
    time.sleep(0.1)
time.sleep(2)
print("Stopping")
pwmA.stop()

print("Backwards")
pwmA = GPIO.PWM(M1B, 1000)
pwmA.start(0)
for duty in range(0,101):
    pwmA.ChangeDutyCycle(duty)
    time.sleep(0.1)
time.sleep(2)
print("Stopping")
pwmA.stop()

GPIO.output(M1A, GPIO.LOW)
GPIO.output(M1B, GPIO.LOW)
print("Done")
