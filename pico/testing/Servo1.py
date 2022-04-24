from machine import Pin, PWM
from time import sleep

pwm = PWM(Pin(0))
pwm.freq(50)

def setServoCycle (pos):
    pwm.duty_u16(pos)
    sleep(0.01)
    
def setServoAngle (a):
    d = int(a/180*8000+1000)
    print("Angle=",a,"d=",d)
    setServoCycle(d)



for x in range (1,2):
    for pos in range(0,180,2):
        setServoAngle(pos)
    for pos in range(180,0,-2):
        setServoAngle(pos)
        
Angles = [56, 157 ,4 ,89 ,39, 170, 2, 123]
for a in Angles:
    setServoAngle(a)
    sleep(2)
for pos in range(0,180,2):
    setServoAngle(pos)
    
print("Done")