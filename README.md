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
|  * load=1		|	Return load values with data |
|  * wifi=1		|	Return wifi RSSI and noise with data |
|  * button=p       | Defines a pushbutton attached to pin p |
|  * pico=True      | Use a pico slave for functions such as ultrasonic and pan/tilt mount |
|  * magneto=True	| Use a LSM303AGR magnetometer for heading info |
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
| getSonic(n) | Returns the ultrasonic distance value for a specific sensor or all if n is negative/missing |
| panAngle(a) | Sets the pan angle to a |
| panLeft(a) | Pans the camera to the left (or right if a is negative) |
| panCentre(a) | Sets the camera pan and tilt to centre (default positions) |
| tiltAngle(a) | Sets the tilt angle to a |
| tiltUp(a) | Tilts the camera up by angle a (down if a is negative) |
| getButton() | Returns the state of the pushbutton (0=pressed) |
| LSM303AGR Functions: | |
| magNormalise(m) | Internal function to normalise to calibrated values |
| getHeading([a, i]) | Get heading and chassis tilt, optional a attempts with interval i |
| turnToHeading(h, [s, f]) | Turn to a heading h, with speed s and force direction (1,-1) optional |

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
| getsonic | [n]    | Get only the ultrasonic sensors with key sonicDist. Option to supply specific sensor number |
| quit	| None	| Quit the server |

## GPIO Wiring ##

Direct GPIO connections
 
| Pin# | Value | Connection| Pin# | Value | Connection |
| - | - | - | - | - | - |
| 1 | 3V3 | Breadboard 3.3v | 2 | 5V | Breadboard 5v |
| 3 | GPIO2 (SDA1, I2C) | PCA9685 | 4 | 5V | - |
| 5 | GPIO3 (SCL1, I2C) | PCA9685 | 6 | GND | Breadboard GND |
| 7 | GPIO4 | Front US trig | 8 | GPIO14 | Rear US trig |
| 9 | GND | - | 10 | GPIO15 | Rear US echo |
| 11 | GPIO17 | Front US echo | 12 | GPIO18 | MDD3A M1A |
| 13 | GPIO27 | Pushbutton | 14 | GND | - |
| 15 | GPIO22 | - | 16 | GPIO23 | - |
| 17 | 3V3 | - | 18 | GPIO24 | - |
| 19 | GPIO10 | - | 20 | GND | - |
| 21 | GPIO9 | - | 22 | GPIO25 | - |
| 23 | GPIO11 | - | 24 | GPIO8 | - |
| 25 | GND | - | 26 | GPIO7 | - |
| 27 | GPIO0 | - | 28 | GPIO1 | - |
| 29 | GPIO5 | - | 30 | GND | - |
| 31 | GPIO6 | - | 32 | GPIO12 | MDD3A M1B |
| 33 | GPIO19 | MDD3A M2A | 34 | GND | - |
| 35 | GPIO19 | MDD3A M2B | 36 | GPIO16 | - |
| 37 | GPIO26 | - | 38 | GPIO20 | - |
| 39 | GND | - | 40 | GPIO21 | - |

## Pi Pico Wiring ##

 | Pin# | Value | Connection | Pin# | Value | Connection |
 | - | - | - | - | - | - |
 | 1 | GP0 (UART0 Tx) | Pi Serial Rx (GPIO 15) | 40 | VBUS | - |
 | 2 | GP1 (UART0 Rx) | Pi Serial Tx (GPIO 14) | 39 | VSYS | - |
 | 3 | GND | Breadboard GND | 38 | GND | - |
 | 4 | GP2 | Servo 0, lower pan/tilt | 37 | 3v3_EN | - |
 | 5 | GP3 | Servo 1, upper pan/tilt | 36 | 3V3(OUT) | - |
 | 6 | GP4 | - | 35 | ADC_VREF | - |
 | 7 | GP5 | - | 34 | GP28 | - |
 | 8 | GND | - | 33 | GND | - |
 | 9 | GP6 | - | 32 | GP27 | - |
 | 10 | GP7 | - | 31 | GP26 | - |
 | 11 | GP8 | - | 30 | RUN | Pushbutton to GND |
 | 12 | GP9 | - | 29 | GP22 | - |
 | 13 | GND | - | 28 | GND | - |
 | 14 | GP10 | - | 27 | GP21 | - |
 | 15 | GP11 | - | 26 | GP20 | - |
 | 16 | GP12 | - | 25 | GP19 | - |
 | 17 | GP13 | - | 24 | GP18 | - |
 | 18 | GND | - | 23 | GND | - |
 | 19 | GP14 | - | 22 | GP17 (I2C0 SCL) | - |
 | 20 | GP15 | - | 21 | GP16 (I2C0 SDA) | - |
 
## To Do


- [x] Drivable app over wifi, can we drive anywhere in range of wifi?
- [] Proximity detection. Add to HUD and autonomous driving avoiding obstacles
- [] Directional sensing. Can we detect which direction we are facing and add suitable functions for turn to angle?
- [] Software vs Hardware PWM, power draw and test motor controller power
- [] QR code recognition - act when the camera recognises a QR code
- [] BLE beacon - can it detect a beacon and locate it?
- [] BLE triangulation - what if there were 4 beacons, can we accurately find our location?
