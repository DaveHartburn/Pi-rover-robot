/* HC-SR04 over wheel holder
 * For Pi Rover Robot
  */

$fn=256;

// What to show
showWheel=0;    // Will also show chassis
showSensor=0;
showHolder=1;

rightWheel=1;   // 1 for right wheel, 0 for left

sensorAngle=45;
sensHeight=45;

if(showWheel==1) {
    drawWheelChassis();
}

if(showSensor==1) {
    drawSensor();
}

if(showHolder==1) {
    if(rightWheel==1) {
        sensorHolder();
    } else {
        mirror([1,0,0]) {
            sensorHolder();
        }
    }
}

module sensorHolder() {
    w=45.3+2.4;     // Width of the main unit
    sd=8.6;   // Sensor holder depth
    shh=22;   // Sensor holder height

    plateTh=3;
    plateW=18;
    plateL=23;
    hole=4;     // Screw hole size

    // Sensor holder
    rotate([0,0,180-sensorAngle]) translate([1-w,-3,sensHeight-shh])  {
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
        
        // Draw pole
        translate([w,0,shh-sensHeight]) {
            cube([sd,sd,sensHeight]);
        }
    }
    // Base plate
    translate([-plateW, sd/2-plateL/2-2, 0]) {
        difference() {
            cube([plateW,plateL,plateTh]);
            // Screw holes
            translate([hole,hole,-1]) {
                cylinder(h=plateTh+2, d=hole);
            }
            translate([hole,plateL-hole,-1]) {
                cylinder(h=plateTh+2, d=hole);
            }
        }
    }
}

module drawSensor() {
    translate([0,0,sensHeight]) {
        rotate([-90,0,-sensorAngle]) {
            hcsr04();
        }
    }
}

module drawWheelChassis() {
    // Chassis - very crude
    // Dimensions
    w=60;
    l=100;
    h=12;
    offset=16;  // How much lower is the board to the wheel?
    
    color("Peru") {
        translate([-w,-l/2,-h]) cube([w,l,h]);
    }
    diam=83;
    tyrew=33;
    color("darkgrey") {
        translate([0,0,offset-diam/2]) {
            rotate([0,90,0]) cylinder(d=diam, h=tyrew);
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