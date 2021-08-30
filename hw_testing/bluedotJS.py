#!/usr/bin/python

# Initial test using Blue Dot joystick

# https://bluedot.readthedocs.io/en/latest/index.html#
from bluedot import BlueDot

bd = BlueDot()

def jsMap(i):
    # Takes a value -1 to 1 and maps it to -100 to 100
    j=int(i*100)
    return j

while True:
    if bd.is_pressed:
        bd.color = (255, 128, 0)
        xin,yin=bd.position.x, bd.position.y
        x=jsMap(xin)
        y=jsMap(yin)
        print("xin={} -> x={}     :  yin={} -> y={}".format(xin,x,yin,y))
    else:
        bd.color = "blue"
