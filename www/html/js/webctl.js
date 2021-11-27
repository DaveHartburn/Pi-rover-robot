/* webctl javascript. Used to call the cgi-functions for driving
 * and to keep the display data updated.
 * 
 * We set the active and inactive class on keypress, then if we use keyboard
 * it gives a nice visual effect
 */

window.addEventListener("keydown", keypress);
window.addEventListener("keyup", keypress);

function keypress(e) {
	//console.log("Keypress...."+e.code);
	console.log("Key="+e.key)
	switch(e.key) {
		case 'w': clickButton('b_up', e.type); break;
		case 's': clickButton('b_down', e.type); break;
		case 'a': clickButton('b_left', e.type); break;
		case 'd': clickButton('b_right', e.type); break;
		case 'z': clickButton('b_stop', e.type); break;
		case 'q': clickButton('b_acw', e.type); break;
		case 'e': clickButton('b_cw', e.type); break;
		case 'i': clickButton('b_tup', e.type); break;
		case 'k': clickButton('b_tdown', e.type); break;
		case 'j': clickButton('b_panl', e.type); break;
		case 'l': clickButton('b_panr', e.type); break;
		case ' ': clickButton('b_pcent', e.type); break;
	}	
}

function clickButton(b, type) {
	// Simulate a button press
	btn=document.getElementById(b);
	if(type=="keydown") {
		// Click down
		btn.click();
		btn.setAttribute("class", "active-class");
	} else {
		// Return the style to inactive
		btn.setAttribute("class", "inactive-class");
	}
}

function monitorSensors() {
	// Update the data table on a regular basis (1 second)
	
	// Make call to cgi script
	var xhttp=new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if(this.readyState==4 && this.status==200) {
			// Got a response
			//console.log(this.responseText);
			popDataout(this.responseText);
		}
	}
	xhttp.open("POST", "/cgi-bin/webToQueue.py", true);
	xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttp.send("msg=getsens");	
		
	// Call ourselves again
	setTimeout(monitorSensors, 1000);
}
		
function webctlButtonPress(but) {
	// On button press, make a direct call to the cgi-script
	// and process output
	
	//console.log(but);
	
	// Make call to cgi script
	var xhttp=new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if(this.readyState==4 && this.status==200) {
			// Got a response
			//console.log(this.responseText);
			popDataout(this.responseText);
		}
	}
	xhttp.open("POST", "/cgi-bin/webToQueue.py", true);
	xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttp.send("msg="+but);	
}

function popDataout(d) {
	// Fill the data out pane with the JSON contents of D
	
	//console.log(d)
	if(d.length<6) {
		// Empty/rubbish data, ignore rather than overwrite
		return;
	}
	delm=document.getElementById("dataout");
	
	data=JSON.parse(d)
	output="<table id='datatable'>";
	// Take any returned data and put it in a table. Don't worry about
	// what the data is
	for(var key in data){
		output+="<tr><td class='key'>"+key+"</td><td class='value'>"+data[key]+"</td></tr>";
	}
	
	output+="</table>"
	delm.innerHTML=output;
}

