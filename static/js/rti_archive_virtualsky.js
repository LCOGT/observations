var planetarium;

function spinOff(){
	planetarium.az_step = 0;
	if(typeof timer_az!='undefined') clearTimeout(timer_az);
}

window.onload = function(){
	if(typeof lat==="number" && typeof lon=="number"){
		planetarium = new $.virtualsky({id:'starmap',projection:'stereo',latitude:lat,longitude:lon,az:(lat > 0 ? 180 : 0),gridlines_az:true,callback:{mouseenter:spinOff}});
		planetarium.draw();
		planetarium.az_step = -0.1;
		planetarium.moveIt();

		if(typeof json==="string") $.getJSON(json+'?callback=?',function(data) { updatePlanetarium(data); });
	}
}

function updatePlanetarium(data){
	// Zap existing pointers
	planetarium.pointers = [];
	var obs = data.observation;
	for(var i = 0; i < obs.length ; i++){
		relative = relative_time_short(new Date(Date.parse(obs[i].time.creation)))
		a = planetarium.addPointer({'ra':obs[i].ra,'dec':obs[i].dec,'label':obs[i].label+' ('+relative+')','img':obs[i].image.thumb,'url':obs[i].about,credit:obs[i].observer.label,colour:'rgb(255,255,255)'})
	}
	planetarium.draw();
}