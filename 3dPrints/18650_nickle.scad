/* 18650 holder with nickel strip.
 * The Flexing Battery holder with a slot cut out and grips
 * https://www.thingiverse.com/thing:456900
 *
 * Download the SCAD file for this and save it is flexbatter_lib.scad
 *
 * Not doing this as a remix as multiple cells are made from the same holder
 * butted up to each other. We need to add grips to the outsides
 */

use <flexbatter_lib.scad>

bat=2;   // Number of batteries
stripW=8;   // Width of strip
stripT=0.2; // Thickness of strip

// The sizes calculated for a single cell by flexbatter
holdSize=[67.74, 22.88, 17.16];
// Move battery holder to origin. The spring remains in negative X,
// but this is useful as we can make our slot at x=0
translate([0,holdSize.y/2,0]) {
    // Cut out slot at spring
    cw=stripW+1;    // Give a margin
    ct=stripT+0.4;
    ch=4.5;           // Manually defined height of cut out
    difference() {
        flexbatter18650(n=bat);
        // - end
        translate([0,-holdSize.y,ch]) {
            cube([ct,holdSize.y*(bat+1),cw]);
        }
        // + end
        translate([65,-holdSize.y,ch]) {
            cube([ct,holdSize.y*(bat+1),cw]);
        }
    }
}

// Add strip grips, move down the holder a little
translate([15,0,0]) stripGrip(r=1);
translate([65-27,0,0]) stripGrip(r=1);
translate([15,holdSize.y*bat-(1.2*(bat-1)),0]) stripGrip(r=0);
translate([65-27,holdSize.y*bat-(1.2*(bat-1)),0]) stripGrip(r=0);

module stripGrip(r=1) {
    // Grips or handles to tuck the end of the nickel strips into
    // r=1, right side, r=0, left side
    gap=1+stripT;
    t=1.2;    // Thickness of the grip top (the bottom goes to the base for easy printing)
    s=1.2;  // Thickness of the grip side
    l=8;    // Length of grip (how far down the side)
    ch=4.5;  // How high we have done the cut out
    
    translate([0,r*-(gap+s),0]) {
        difference() {
            cube([l,gap+s,ch+stripW+1+t]);
            if(r==1) {
                translate([-1,s,ch]) cube([l+2,gap,stripW]);
            } else {
                translate([-1,0,ch]) cube([l+2,gap,stripW]);
            }
        }
    }
}