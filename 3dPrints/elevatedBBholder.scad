/* Elevated breadboard holder
 * Dave Hartburn - January 2022
 * Used to hold three breadboards in an elevated position
 * above my Pi Rover robot (for development)
 *
 * The total width for 3 boards is greater than the width
 * of the wheels, so I need to account for this when positioning the stands
 */
$fn=256;


bbsize=[54,82,9];   // Size, excluding locking tabs
numBoards=3;
elevation=50;
supportTh=3;        // How thick to make main bit the boards rest on
maxLegWidth=140;    // Width of gap between wheels, do not make wider
footScrewHole=3.5;

showBoards=1;
boardsWidth=bbsize.x*numBoards;
echo("Total width = ", boardsWidth, "mm");

if(showBoards==1) {
    translate([0,0,elevation]) {
        draw_breadboards(numBoards);
    }
}

// Supporting board
translate([0,0,elevation-supportTh]) {
    difference() {
        cube([boardsWidth, bbsize.y,supportTh]);
        // Cut out strips so it is not completely solid
        strips=3;
        stripWidth=12;
        xedge=12;
        gap=(bbsize.y-(stripWidth*strips))/(strips+1);
        for(i = [1:strips]) {
            translate([xedge,gap*i+stripWidth*(i-1),-1]) {
                //cube([boardsWidth-xedge*2,gap,supportTh+2]);
                stadium(boardsWidth-xedge*2,gap,supportTh+2);
            }
        }     
    }
}
// Legs
legx=10;
legy=10;
// This code will fail if boards are narrower than min leg
xoffset=(boardsWidth-maxLegWidth)/2;
echo("xoffset=", xoffset);
translate([xoffset,0,0]) leg(1,legx,legy,elevation-supportTh);
translate([xoffset,bbsize.y-legy,0]) leg(2, legx,legy,elevation-supportTh);
translate([boardsWidth-legx-xoffset,bbsize.y-legy,0]) leg(3, legx,legy,elevation-supportTh);
translate([boardsWidth-legx-xoffset,0,0]) leg(4, legx,legy,elevation-supportTh);


module leg(pos,x,y,h) {
    // Produces a square leg with a foot and supports
    // pos is clockwise from 1 where 1 is the front left corner
    p=pos-1;
    f=5;    // Fraction of x to make triangular supports
    translate([x*floor(p/2),y*ceil(p%1.5),0]) {
        rotate([0,0,-90*p]) {
            cube([x,y,h]);
            // Triangular supports
            translate([x,0,h]) {
                rotate([-90,0,0]) raPrism(x,x,x/f);
            }
            translate([x/f,y,h]) {
                rotate([-90,0,90]) raPrism(x,x,x/f);
            }
        }
        // Foot
        translate([-x*floor(p/2),-y+y*ceil(p%1.5),0]) {
            difference() {
                cube([x,y+1,2]);
                translate([x/2,y/2,-1]) {
                    cylinder(d=footScrewHole, h=4);
                }
            }
        }

    }
}

module breadboard() {
    // Shows a sinle bit of standard size breadboard
    color("white") {
        difference() {
            cube(bbsize);
            // Remove middle dip to give a bit more feature
            dip=3;
            translate([bbsize.x/2-dip/2, -1, bbsize.z-dip]) {
                cube([dip,bbsize.y+2,dip+1]);
            }
        } 
        // Locking tabs - short edge
        for(x = [0:2]) {
            translate([4.5+x*22,-0.7,0]) cylinder(d=2.2,h=4.65);
        }
        // Long edge
        translate([-0.7,13.8,0]) cylinder(d=2.2,h=4.65);
        translate([-0.7,bbsize.y-13.8,0]) cylinder(d=2.2,h=4.65);
    }
    
    // Add a couple of surface features to make it a little more
    // interesting
    translate([1.5,10,bbsize.z]) {
        color("blue") cube([0.5,bbsize.y-20,0.1]);
    }
    translate([bbsize.x-8,10,bbsize.z]) {
        color("blue") cube([0.5,bbsize.y-20,0.1]);
    }
    translate([8,10,bbsize.z]) {
        color("red") cube([0.5,bbsize.y-20,0.1]);
    }
    translate([bbsize.x-1.5,10,bbsize.z]) {
        color("red") cube([0.5,bbsize.y-20,0.1]);
    }
}

module draw_breadboards(x) {
    // Draws x breadboards side by side
    for(y = [0:x-1]) {
        translate([y*bbsize.x,0,0]) {
            breadboard();
        }
    }
}
module stadium(x,y,z) {
    // Make a stadium/oblong shape with the two x ends rounded
    translate([y/2,y/2,0]) cylinder(h=z,d=y);
    translate([y/2,0,0]) cube([x-y,y,z]);
    translate([x-y/2,y/2,0]) cylinder(h=z,d=y);

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