/* Pan/tilt camera mount for Pi Rover robot
 * Also includes a mount for a HC-SR04 ultrasonic sensor board
 *
 * Some insperation taken from https://www.thingiverse.com/thing:350229
 */

use <sg90_capped.scad>;

$fn=256;

// What to show
showBasePlate=1;
showBasePlateUpper=0;
showLowerBody=0;        // There is no upper body!
showCamArm=0;

// Hardware
showLowerServo=0;
showSensor=0;
showUpperServo=0;

if(showBasePlate==1) {
    basePlate();
}
if(showBasePlateUpper==1) {
    color("cyan") basePlateUpper();
}

if(showLowerBody==1) {
    color("lime") lowerBody();
}

if(showCamArm==1) {
    translate([38,-26,44]) {
        color("orange") camArm();
    }
}

if(showLowerServo==1) {
    translate([5.5,0,32.8]) {
        rotate([0,180,0]) sg90_capped(3);
    }
}

if(showSensor==1) {
    translate([26,-13,32.6]) {
        rotate([90,180,0]) hcsr04();
    }
}

if(showUpperServo==1) {
    translate([7.3,0,44.3]) {
        rotate([180,-90,0]) sg90_capped(f=1,r=-90);
    }
}

module basePlate() {
    w=45;
    d=26;
    h=3;
    
    hole=3;
    ho=3;   // Hole offset from edges
    difference() {
        translate([-w/2, -d/2, 0]) cube([w,d,h]);
    
        translate([0,0,0.8]) sg90_f3_cutout(m=1);
        
        // Mounting holes
        translate([-w/2,-d/2,-1]) {
            translate([ho,ho,0]) cylinder(d=hole,h=h+2);
            translate([ho,d-ho,0]) cylinder(d=hole,h=h+2);
            translate([w-ho,ho,0]) cylinder(d=hole,h=h+2);
            translate([w-ho,d-ho,0]) cylinder(d=hole,h=h+2);
        }
        // Hole for screw driver
        translate([0,0,-1]) cylinder(h=h+2,d=5);
        
       
    }
}

module basePlateUpper() {
    // Used to clamp the servo fixing into place
    
    // Sizes must match base plate above
    w=45;
    d=26;
    h=1.6;
    lh=2.2; // Height of lower base
    
    hole=3;
    ho=3;   // Hole offset from edges
    difference() {
        translate([-w/2, -d/2, lh]) cube([w,d,h]);
    
        // Mounting holes
        translate([-w/2,-d/2,lh-1]) {
            translate([ho,ho,0]) cylinder(d=hole,h=h+2);
            translate([ho,d-ho,0]) cylinder(d=hole,h=h+2);
            translate([w-ho,ho,0]) cylinder(d=hole,h=h+2);
            translate([w-ho,d-ho,0]) cylinder(d=hole,h=h+2);
        }
        // Servo fixing centre
        translate([0,0,lh-1]) cylinder(d=7.5,h=h+2);
    }
}    

module lowerBody() {
    // Holds the lower servo and ultrasonic sensor
    // Reminder, sg9 main body 22.5x12.2
    // Screw mounts stick out 5mm, bottom of them 7mm down
    
    sh=1.2;   // Diam of screw hole
    translate([-12,-7.2,11]) {
        difference() {
            cube([35,14.4,22]);
            
            // Cut out for main body
            translate([6,0.65,-1]) cube([23.2,13,24]);
            
            // Body with screw mounts
            translate([1,0.65,-1]) cube([33.2,13,8]);
            
            // Screw holes
            translate([3.3,7.2,0]) cylinder(d=sh,h=20);
            translate([35-3.3,7.2,0]) cylinder(d=sh,h=20);
            // For upper servo
            translate([22,7.2,19]) {
                rotate([0,90,0]) cylinder(d=sh,h=20);
            }
            
        }
        // Sensor holder
        sd=8.6;   // Sensor holder depth
        shh=22;   // Sensor holder height
        translate([-7.3-1.2,-sd,0]) {
            difference() {
                cube([45.3+2.4,sd,shh]);
                // slot
                translate([1,-1,1.2]) cube([45.3+0.4,5,shh+1]);
                translate([2,3,1.2]) cube([45.3+0.4-2,4.4,shh+5]);
            }
            // Retaining supports
            translate([0,0,1]) cube([18,1,2]);
            translate([30,0,1]) cube([17,1,2]);
            translate([1,0,0]) cube([1,1,shh]);
            translate([45.3+0.4,0,0]) cube([1,1,shh]);
        }
        // Second servo, on top of first
        translate([35-16.5,0,22]) {
            difference() {
                cube([16.5,14.4,28]);
                // Cut out for main body
                translate([-1,0.65,-1]) cube([23.2,13,24]);
                // Upper screw hole, the lower is in 
                // the lower section
                translate([3.3,7.2,25.6]) {
                    rotate([0,90,0]) cylinder(d=sh,h=20);
                }
               
            }
        }
    }
}


module camArm() {
    // Side arm, attaches to servo
    aw=12;  // Arm width
    ath=6;  // Arm thickness, fairly thick to take a small screw
    arml=46;    // Arm length
    difference() {
        union() {
            translate([0,arml,aw/2]) {
                rotate([0,90,0]) cylinder(d=aw,h=ath);
            }
            cube([ath,arml,aw]);
        }
        translate([2,arml,aw/2]) rotate([90,0,-90]) sg90_f1_cutout(m=0.8);
    }
    hlen=55; // Horizontal arm length
    th=2;   // Arm thickness (height)
    d=8;   // Depth
    translate([-hlen,0,th]) {
        
        // Plate to mount Pi camera to
        // See: https://www.raspberrypi-spy.co.uk/2013/05/pi-camera-module-mechanical-dimensions/
        lip=1.2;    // 1.2mm lip around the edge
        marg=0.4;   // Margin
        difference() {
            cube([25+lip*2+marg,2,24+lip*2+marg]);
            // Cut out for module
            translate([lip,1,lip]) {
                cube([25+marg,2,24+marg]);
            }
            // Cut out for screw holes, move to top left corner
            translate([lip+marg/2,-1,lip+marg/2+24]) {
                // Top left
                translate([2,0,-2]) rotate([-90,0,0]) cylinder(d=2.2,h=10);
                // Top right
                translate([2+21,0,-2]) rotate([-90,0,0]) cylinder(d=2.2,h=10);
                // Bottom left
                translate([2,0,-2-12.5]) rotate([-90,0,0]) cylinder(d=2.2,h=10);
                // Bottom right
                translate([2+21,0,-2-12.5]) rotate([-90,0,0]) cylinder(d=2.2,h=10);
           }
           // Cut out for camera module
           translate([lip+8.5,-1,lip+6.5]) cube([8+marg,10,8+marg]);
        }
        // Horizontal arm
        translate([0,0,-th]) {
            difference() {
                cube([hlen,d,th]);
                // Slot for cable
                translate([(25+lip*2+marg-18)/2,4,-1]) cube([18,2,th*3]);
            }
            // Fill in between servo arm and front horizontal arm
            translate([lip*2+marg+25,0,0]) {
                cube([hlen-(lip*2+marg+25),th,aw]);
                translate([hlen-(lip*2+marg+25),0,0]) {
                    rotate([0,0,90]) raPrism(d,d,aw);
                }
            }
            // Triangles to add more strength
            translate([lip,d,th]) rotate([0,0,180]) raPrismUpright(lip,d,20);
            translate([lip*2+marg+25,d,th]) rotate([0,0,180]) raPrismUpright(lip,d,20);
        }
    }
}

module hcsr04() {
    // Draws a HC-SR04 sensor module
    w=45.3;
    h=20.3;
    d=1.6;
    hole=1.5;
    ho=1.3; // Hole offset (same in X and Y);
    srdiam=16;
    difference() {
        color("darkblue") cube([w,h,d]);
        // Cut holes
        translate([ho,ho,-1]) cylinder(d=hole, h=d+2);
        translate([ho,h-ho,-1]) cylinder(d=hole, h=d+2);
        translate([w-ho,ho,-1]) cylinder(d=hole, h=d+2);
        translate([w-ho,h-ho,-1]) cylinder(d=hole, h=d+2);
    }
    // Sender and receiver
    translate([9,10,d]) color("silver") cylinder(d=16, h=12);
    translate([w-9,10,d]) color("silver") cylinder(d=16, h=12);
    // Oscillator
    ow=9.8;
    oh=3.4;
    od=2.5;
    color("silver") translate([19.5,17.9,d]) {
        hull() {
            cylinder(d=oh,h=od);
            translate([6.6,0,0]) cylinder(d=oh,h=od);
        }
    }
    
    // Pins
    translate([17.5,0,-2.4]) {
        color("black") cube([10.4,2.4,2.4]);
        for(i=[0:3]) {
            translate([1.1+i*2.54,1.1,-1.6]) {
                color("silver") {
                    cube([0.6,0.6,1.6]);
                    translate([0,-6.9,0]) cube([0.6,7.5,0.6]);
                }
            }
        }
    }
}

module raPrism(x,y,z) {
    // Draws a right angle prism on it's side
    polyhedron(
        points=[
            [0,0,0],    // 0
            [0,0,z],    // 1
            [x,0,z],    // 2
            [x,0,0],    // 3
            [0,y,z],    // 4
            [0,y,0]     // 5
        ], faces=[
            [0,1,2,3],  // Front face along X axis
            [5,4,1,0],  // Side face along Y axis
            [5,3,2,4],  // Side diagonal
            [1,4,2],    // Top triangle
            [0,3,5]     // Bottom triangle
        ]
    );
}
module raPrismUpright(x,y,z) {
    // Draws an upright right angle prism, flat back to the rear
    polyhedron(
        points=[
            [0,0,0],    // 0
            [0,y,0],    // 1
            [x,y,0],    // 2
            [x,0,0],    // 3
            [0,y,z],    // 4
            [x,y,z]     // 5
        ], faces=[
            [3,2,1,0],  // Base
            [2,5,4,1],  // Back
            [0,4,5,3],  // sloped front
            [0,1,4],    // left side
            [3,5,2]     // right side
        ]
    );
}
