#!/usr/bin/python

# Basic compass demo, see https://learn.adafruit.com/lsm303-accelerometer-slash-compass-breakout/python-circuitpython

import board
import adafruit_lsm303_accel
import adafruit_lis2mdl
import time
import math

i2c = board.I2C()
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
sensor = adafruit_lis2mdl.LIS2MDL(i2c)

#hardiron_calibration = [[-54.75, 37.199999999999996], [-61.8, 25.2], [-94.64999999999999, -12.45]]
#hardiron_calibration = [[-50.25, 42.449999999999996], [-72.45, 8.25], [-101.25, 4.05]]
#hardiron_calibration = [[-45.9, 43.199999999999996], [-77.55, 10.35], [-119.1, 16.349999999999998]]
hardiron_calibration = [[-54.75, 43.199999999999996], [-77.55, 10.35], [-119.1, 16.349999999999998]]
tiltCompensate = -47

# This will take the magnetometer values, adjust them with the calibrations
# and return a new array with the XYZ values ranging from -100 to 100
def normalize(_magvals):
    ret = [0, 0, 0]
    for i, axis in enumerate(_magvals):
        minv, maxv = hardiron_calibration[i]
        axis = min(max(minv, axis), maxv)  # keep within min/max calibration
        ret[i] = (axis - minv) * 200 / (maxv - minv) + -100
    return ret

zmin=9
zmax=9

while True:
	magvals = sensor.magnetic
	normvals = normalize(magvals)
	print("\033c", end="")
	print("magnetometer: {:.3f}\t{:.3f}\t{:.3f} -> {:.3f}\t{:.3f}\t{:.3f} ".format(
	  magvals[0],magvals[1],magvals[2], normvals[0],normvals[1],normvals[2]))
	  
	mx=normvals[0]
	my=normvals[1]
	mz=normvals[2]
	
	accvals = accel.acceleration
	ax = accvals[0]
	ay = accvals[1]
	az = accvals[2]
	
	tilt = math.atan2((-ax), math.sqrt(ay*ay+az*az)) * 180 / math.pi
	magtilt = int(math.atan2(mz, math.sqrt(mx*mx+my*my)) * 180.0 / -math.pi) + tiltCompensate
	print("accelerometer: {:.3f}\t{:.3f}\t{:.3f}".format(accvals[0],accvals[1],accvals[2]))
	
	# we will only use X and Y for the compass calculations, so hold it level!
	compass_heading = int(math.atan2(normvals[1], normvals[0]) * 180.0 / -math.pi) 
	# compass_heading is between -180 and +180 since atan2 returns -pi to +pi
	# this translates it to be between 0 and 360
	# Minus added before math.pi as original code had east as 270 and west as 90.
	compass_heading += 180

	# Show the heading without calibration
	raw_heading = int(math.atan2(magvals[1], magvals[0]) * 180.0 / -math.pi)
	raw_heading+=180

	# Calculate how much the sensor tilts
	print("Calibrated heading: {}\tRaw Heading: {}\tTilt: {:0.2f}\tMagTilt: {}".format(compass_heading, raw_heading, tilt, magtilt))
	
	if(az<zmin):
		zmin=az
	if(az>zmax):
		zmax=az
	print("Zmin={:0.3f}\tZmax={:0.3f}".format(zmin,zmax))
	time.sleep(0.1)
