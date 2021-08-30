#!/usr/bin/python

# Basic motor control. Turning the two motor channels back and forward.
# Two 12v motors connected to a Cytron MDD3A. 12v power supply must be used

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
GPIO.output(M1A, GPIO.HIGH)
GPIO.output(M2A, GPIO.HIGH)
time.sleep(5)

print("Backwards")
GPIO.output(M1A, GPIO.LOW)
GPIO.output(M1B, GPIO.HIGH)
GPIO.output(M2A, GPIO.LOW)
GPIO.output(M2B, GPIO.HIGH)
time.sleep(5)

print("Both high")
GPIO.output(M1A, GPIO.HIGH)
GPIO.output(M1B, GPIO.HIGH)
GPIO.output(M2A, GPIO.HIGH)
GPIO.output(M2B, GPIO.HIGH)
time.sleep(2)

print("Both low")
GPIO.output(M1A, GPIO.LOW)
GPIO.output(M1B, GPIO.LOW)
GPIO.output(M2A, GPIO.LOW)
GPIO.output(M2B, GPIO.LOW)
time.sleep(2)

print("Done")
