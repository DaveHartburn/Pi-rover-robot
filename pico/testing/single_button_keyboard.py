# Requires CircuitPython, not MicroPython
# HCI support was needed

import board
import digitalio
import time
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

kbd = Keyboard(usb_hid.devices)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

butA = digitalio.DigitalInOut(board.GP1)
butA.switch_to_input(pull=digitalio.Pull.UP)

rptRate=0.25

while True:
    if(butA.value==False):
        led.value = not led.value
        kbd.press(Keycode.SHIFT)
        time.sleep(rptRate)
    else:
        kbd.release(Keycode.SHIFT)
    
    

