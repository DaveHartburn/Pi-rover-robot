# Pi-rover-robot

Repository for main code, libraries, hardware testing and simulator for a Raspberry Pi based rover robot.

Can I create an autonomous rover robot that can navigate around the garden, tracking it's location with BLE beacons, using a camera and image analysis to detect the lawn edge and other sensors to find and avoid other obsticles around the garden? Originally conceived with the intention of making an automated lawn mower (which may still happen) but the build and automation challenges are far more interesting first.

Blog posts detailing hardware build and software development can be found at https://samndave.org.uk/ourdoc/pi-rover-robot-project/


To Do
-----

- Drivable app over wifi, can we drive anywhere in range of wifi?
- Proximity detection. Add to HUD and autonomous driving avoiding obstacles
- Directional sensing. Can we detect which direction we are facing and add suitable functions for turn to angle?
- Software vs Hardware PWM, power draw and test motor controller power
- QR code recognition - act when the camera recognises a QR code
- BLE beacon - can it detect a beacon and locate it?
- BLE triangulation - what if there were 4 beacons, can we accurately find our location?
