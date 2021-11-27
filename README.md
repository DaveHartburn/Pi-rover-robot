# Pi-rover-robot

Repository for main code, libraries, hardware testing and simulator for a Raspberry Pi based rover robot.

Can I create an autonomous rover robot that can navigate around the garden, tracking it's location with BLE beacons, using a camera and image analysis to detect the lawn edge and other sensors to find and avoid other obsticles around the garden? Originally conceived with the intention of making an automated lawn mower (which may still happen) but the build and automation challenges are far more interesting first.

Blog posts detailing hardware build and software development can be found at https://samndave.org.uk/ourdoc/pi-rover-robot-project/

## piroverlib


The heart of most Python scripts is piroverlib.py. This contains two classes, piRover and pwmMotor.

### piRover class

| Function | Details |
| ------- | ------- |
| init(<list>) | Called with multiple arguments (below), depending on what hardware is installed |
|  * name="string"	| Give your robot a name |
|  * left=[a,b]		| List of a and b pins for left motor(s) |
|  * right=[a,b]	|	List of a and b pins for right motor(s) |
|  *	load=1		|	Return load values with data |
|  *	wifi=1		|	Return wifi RSSI and noise with data |
|  * pantilt=[p,t] |	Pan tilt camera connected to a PCA9685, which servo slots are they in |
| stop() | Instantly stops both motors |
| fwFull(sp) | Sets both motors to full speed. sp positive for forward, sp negative for backwards. Zero will perform a stop |
| fwSpeed(sp) | Sets both motors to the speed sp |
| drive(l,r) | Drives the motors forward by setting the motors to the l & r values |
| js(x,y) | Drives the motors according to an analog joystick x and y axis calibrated to -100 to 100 |
| spin(sp) | Spins the rover on it's axis according to speed. Positive=clockwise |
| chSpeed(l,r) | Change the left and right motors by the l and r amount |
| getSensorData() | Returns data from all defined sensors |
| readLoad() | Returns only the current load |
| readWifi() | Returns wifi signal and noise levels as a list/tuple |
| panAngle(a) | Sets the pan angle to a |
| panLeft(a) | Pans the camera to the left (or right if a is negative) |
| panCentre(a) | Sets the camera pan and tilt to centre (default positions) |
| tiltAngle(a) | Sets the tilt angle to a |
| tiltUp(a) | Tilts the camera up by angle a (down if a is negative) |

### pwmMotor class

| Function | Details |
| -------- | ------- |
| init(a,b) | Called when new motor object is created with the motor A & B BCM pins |
| stopPWM() | Internal use only. Used to stop a running PWM object |
| stop() | Instantly stops the motor and disabled PWM on the pin |
| full(sp) | Sets the motor to full speed. sp positive for forward, sp negative for backwards. Zero will perform a stop |
| setSpeed(sp) | Use PWM to set an analog speed between -100 and 100, with negative being backwards |

### driveByQueue
 
driveByQueue.py is an interface which implements a ZMQ queue and accepts a simple text command language. It directly calls functions in piroverlib.py, allowing one or more applications to send commands to the rover (or read sensor data), without having to run multiple piRoverLibs which may conflict. This aids web interface driving and also allows remote control.

Commands are supplied as a comma seperated list and it is quite sensitive to formatting.
 
e.g. "`chspeed,10,-10`" will increase the left motor by 10% while decreasing the right motor by 10%.
 
| Command	| Arguments	| Function |
| ------- | --------- | -------- |
| stop	| None	| Stop |
| fwfull	| speed | positive or negative integer	Both motors forward or reverse at full power |
| fwspeed	| speed | -100 to 100	Sets both motors to speed |
| chspeed |	l, r	| Value to change speed of left and right motor |
| drive	| l, r	| Set absolute values for left and right motor |
| js	| x,y | Values between -100 and 100, send x and y joystick values |
| spin	| speed | -100 to 100,	Spin clockwise (positive) or anti-clockwise at given speed |
| panangle | a or 'mid' | Sets the pan angle or sets to centre |
| panleft | a | Pans the camera to the left (or right if a is negative) |
| pancentre | a | Sets the camera pan and tilt to centre (default positions) |
| tiltAngle | a | Sets the tilt angle to a |
| tiltUp | a | Tilts the camera up by angle a (down if a is negative) |
| getsens |	None	| Return all sensor data |
| quit	| None	| Quit the server |

## To Do


- [x] Drivable app over wifi, can we drive anywhere in range of wifi?
- [] Proximity detection. Add to HUD and autonomous driving avoiding obstacles
- [] Directional sensing. Can we detect which direction we are facing and add suitable functions for turn to angle?
- [] Software vs Hardware PWM, power draw and test motor controller power
- [] QR code recognition - act when the camera recognises a QR code
- [] BLE beacon - can it detect a beacon and locate it?
- [] BLE triangulation - what if there were 4 beacons, can we accurately find our location?
