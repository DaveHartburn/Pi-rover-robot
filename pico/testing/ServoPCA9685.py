# pca9685 servo test - using Kevin McAleer library https://github.com/kevinmcaleer/pca9685_for_pico
import time
from machine import Pin
from pca9685 import PCA9685
from servo import Servos

led = Pin(25, Pin.OUT)


sda = Pin(0)
scl = Pin(1)
id = 0
i2c = I2C(id=id, sda=sda, scl=scl)

pca = PCA9685(i2c=i2c)

for x in range(1,50):
    print(x)
    led.toggle()
    time.sleep(0.5)