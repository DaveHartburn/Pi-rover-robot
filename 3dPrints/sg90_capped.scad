$fn=256;

// Library and wrapper function for SG90 servo, allowing fastner on top
// Using modules from https://github.com/ledalert/cadmodel-sg90/blob/master/sg90.scad


//sg90_capped(f=2, r=90);
//sg90_f1_cutout();

module sg90_capped(f=0,r=0) {
    // A SG90 servo with the fastner on top
    // f=1,2 or 3 depending on cap type.
    // r will rotate it
    
    sg90();
    
    translate([5.5,0,22.5+5.6+3.8]) {
        rotate([0,180,r]) {
            if(f==1) sg90_f1();
            if(f==2) sg90_f2();
            if(f==3) sg90_f3();
        }
    }
}

module sg90() {
	color("blue") difference() {
		union() {
			translate([0,0,22.5/2]) cube([22.5,12.2,22.5], center=true);
			translate([0,0,16.75]) cube([32.2,12.2,2], center=true);

			translate([0,0,22.5-1]) {
				hull() {
					translate([-1,0,0]) cylinder(d=5.5, h=4+1);
					translate([1,0,0]) cylinder(d=5.5, h=4+1);
				}

				translate([5.5,0,0]) cylinder(d=11.6, h=4+1);
			}

		}	

		translate([-32.5/2+2,0,16.75-2]) {
			cylinder(d=2, h=2+2);
			translate([-2,0,2]) cube([4,1,2+2], center=true);
		}
		translate([32.5/2-2,0,16.75-2]) {
			cylinder(d=2, h=2+2);
			translate([2,0,2]) cube([4,1,2+2], center=true);
		}
	}
	color("white") translate([5.5,0,22.5-1+4]) {
		difference() {
			cylinder(d=4.8, h=3+1);
			translate([0,0,1]) cylinder(d=2, h=4);
		}
	}
}

module sg90_f1() {
	color("white") difference() {
		union() {
			linear_extrude(height=1.4)
				difference() {
					hull() {
						circle(d=6);
						translate([14,0]) circle(d=4);
					}
					translate([4,0]) for (i=[0:5]) translate([i*2,0]) circle(d=1);
				}
			cylinder(d=6.7, h=3.8);
		}

		//Extend 1mm in each open direction to prevent surfaces from being inside of each other
		translate([0,0,-1]) cylinder(d=2.5, h=3.8+2);
		translate([0,0,-1]) cylinder(d=4.7, h=1+1);	
		translate([0,0,3.8-2+1]) cylinder(d=4.7, h=2+1);	
	}
}

module sg90_f1_cutout(m=0) {
    // More basic version of f1, used to cut out a recess
    // m allows a small margin
	color("white") difference() {
		union() {
			linear_extrude(height=1.4+m)
				difference() {
					hull() {
						circle(d=6+m);
						translate([14,0]) circle(d=4+m);
					}
					//translate([4,0]) for (i=[0:5]) translate([i*2,0]) circle(d=1);
				}
			cylinder(d=6.7+m, h=3.8+m);
		}

		//Extend 1mm in each open direction to prevent surfaces from being inside of each other
	}
}

module sg90_f2() {
	color("white") difference() {
		union() {
			linear_extrude(height=1.4)
				difference() {
					hull() {
						circle(d=6);
						translate([14,0]) circle(d=4);
						translate([-14,0]) circle(d=4);
					}
					for (i=[0:5]) {
						translate([4+i*2,0]) circle(d=1);
						translate([-4-i*2,0]) circle(d=1);
					}
				}
			cylinder(d=6.7, h=3.8);
		}

		//Extend 1mm in each open direction to prevent surfaces from being inside of each other
		translate([0,0,-1]) cylinder(d=2.5, h=3.8+2);
		translate([0,0,-1]) cylinder(d=4.7, h=1+1);	
		translate([0,0,3.8-2+1]) cylinder(d=4.7, h=2+1);	
	}
}

module sg90_f3() {
	color("white") difference() {
		union() {
			linear_extrude(height=1.4)
				difference() {
					union() {
						hull() {
							circle(d=6);
							translate([14,0]) circle(d=4);
						}
						hull() {
							translate([0,-6]) circle(d=3.8);
							translate([0,6]) circle(d=3.8);
						}
						hull() {
							circle(d=7);
							translate([-17,0]) circle(d=4);
						}
					}
					for (i=[0:5]) translate([4+i*2,0]) circle(d=1);					
					for (i=[0:6]) translate([-5-i*2,0]) circle(d=1);
					for (i=[0:1]) {
						translate([0,4+i*2]) circle(d=1);
						translate([0,-4-i*2]) circle(d=1);
					}
				}
			cylinder(d=6.7, h=3.8);
		}

		//Extend 1mm in each open direction to prevent surfaces from being inside of each other
		translate([0,0,-1]) cylinder(d=2.5, h=3.8+2);
		translate([0,0,-1]) cylinder(d=4.7, h=1+1);	
		translate([0,0,3.8-2+1]) cylinder(d=4.7, h=2+1);	
	}
}

module sg90_f3_cutout(m=0) {
    // More basic version of f3, used to cut out a recess
    // m allows a small margin
	color("white") difference() {
		union() {
			linear_extrude(height=1.4+m)
					union() {
						hull() {
							circle(d=6+m);
							translate([14,0]) circle(d=4+m);
						}
						hull() {
							translate([0,-6]) circle(d=3.8+m);
							translate([0,6]) circle(d=3.8+m);
						}
						hull() {
							circle(d=7);
							translate([-17,0]) circle(d=4+m);
						}
					}
			cylinder(d=6.7+m, h=3.8);
		}
	}
}