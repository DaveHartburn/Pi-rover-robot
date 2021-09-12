# Pi-rover-robot

Repository for main code, libraries, hardware testing and simulator for a Raspberry Pi based rover robot.

Can I create an autonomous rover robot that can navigate around the garden, tracking it's location with BLE beacons, using a camera and image analysis to detect the lawn edge and other sensors to find and avoid other obsticles around the garden? Originally conceived with the intention of making an automated lawn mower (which may still happen) but the build and automation challenges are far more interesting first.

Blog posts detailing hardware build and software development can be found at https://samndave.org.uk/ourdoc/pi-rover-robot-project/

##piroverlib


The heart of most Python scripts is piroverlib.py. This contains two classes, piRover and pwmMotor.

###piRover class

* init(<list>) : Called with multiple arguments, depending on what hardware is installed
  * name="string"	Give your robot a name
  * left=[a,b]		List of a and b pins for left motor(s)
  * right=[a,b]		List of a and b pins for right motor(s)
* stop() : Instantly stops both motors
* fwFull(sp) : Sets both motors to full speed. sp positive for forward, sp negative for backwards. Zero will perform a stop
* fwSpeed(sp) : Sets both motors to the speed sp
* drive(l,r) : Drives the motors forward by setting the motors to the l & r values
* js(x,y) : Drives the motors according to an analog joystick x and y axis calibrated to -100 to 100
* spin(sp) : Spins the rover on it's axis according to speed. Positive=clockwise

###pwmMotor class

* init(a,b) : Called when new motor object is created with the motor A & B BCM pins
* stopPWM() : Internal use only. Used to stop a running PWM object
* stop() : Instantly stops the motor and disabled PWM on the pin
* full(sp) : Sets the motor to full speed. sp positive for forward, sp negative for backwards. Zero will perform a stop
* setSpeed(sp) : Use PWM to set an analog speed between -100 and 100, with negative being backwards


##To Do


- [] Drivable app over wifi, can we drive anywhere in range of wifi?
- [] Proximity detection. Add to HUD and autonomous driving avoiding obstacles
- [] Directional sensing. Can we detect which direction we are facing and add suitable functions for turn to angle?
- [] Software vs Hardware PWM, power draw and test motor controller power
- [] QR code recognition - act when the camera recognises a QR code
- [] BLE beacon - can it detect a beacon and locate it?
- [] BLE triangulation - what if there were 4 beacons, can we accurately find our location?
