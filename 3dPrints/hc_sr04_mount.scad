/* Mount for a HC-SR04 ultrasonic sensor board
 *
 * Designed to slot in and has a longish mount plate as it was
 * designed to attach to the underside of a rover robot
 */

use <sg90_capped.scad>;

$fn=256;

sh=3.5;   // Diam of screw hole
armt=2.4;   // Thickness of arm
arml=55;    // Length of arm
armw=30;    // Width of arm

// What to show
showMount=1;
showSensor=0;

if(showMount==1) {
    usonicMount();
}

if(showSensor==1) {
    translate([46.5,3,24]) {
        rotate([90,180,0]) hcsr04();
    }
}

module usonicMount() {
    // Holds the HC-SR04 ultrasonic sensor
    w=45.3+2.4;     // Width of the main unit
    sd=8.6;   // Sensor holder depth
    shh=22;   // Sensor holder height
    
    // Arm
    cube([w,sd,armt]);  // Gives a solid base, originally holder sat on top of arm
                        // but this required supports for printing. Looks nicer.
                        // Comment out to see
    translate([(w-armw)/2,0,0]) {
        difference() {
            union() {
                cube([armw,arml,armt]);
                // Two prisms to give a little more support, based
                // around the thickness of the arm
                pw=armt*2;
                translate([pw,sd+pw,armt]) {
                    rotate([0,0,180]) raPrismUpright(pw,pw,pw);
                    translate([armw-pw,0,0]) {
                        rotate([0,0,180]) raPrismUpright(pw,pw,pw);
                    }
                }                
            }
            // Cut screw holes
            translate([sh*1.5,sd+armt*2+sh*1.5,-1]) cylinder(h=armt+2,d=sh);
            translate([armw-sh*1.5,sd+armt*2+sh*1.5,-1]) cylinder(h=armt+2,d=sh);
            translate([sh*1.5,arml-sh*1.5,-1]) cylinder(h=armt+2,d=sh);
            translate([armw-sh*1.5,arml-sh*1.5,-1]) cylinder(h=armt+2,d=sh);
        }
    }
    
    // Sensor holder
    translate([0,0,armt]) {
        // Sensor holder
        difference() {
            cube([w,sd,shh]);
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