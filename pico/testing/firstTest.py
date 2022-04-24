from machine import Pin, Timer
import time

led = Pin(25, Pin.OUT)
ledB = Pin(15, Pin.OUT)
button = Pin(16, Pin.IN, Pin.PULL_DOWN)

timer = Timer()

def blink(timer):
    led.toggle()

timer.init(freq=1, mode=Timer.PERIODIC, callback=blink)

while True:
    if button.value():
        ledB.toggle()
        time.sleep(0.5)