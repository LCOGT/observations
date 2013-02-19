// This is the Javascript for the RTI "Search Public Archive" form

// A counter to keep track of how many js files we've loaded
var loaded = 0;
var obs_img = '';

// We don't want to do anything until the document is loaded as 
// we have to make sure we have chance to get the rti_path from 
// the document (Drupal includes it after this js file).
$(document).ready(function(){
	// If rti_path still doesn't exist we shall make it empty but not undefined
	if(typeof rti_path=="undefined") rti_path = 'observations/media/';
	// Load the jquery.ui files and check if we've loaded them all

	$('.observer').each(function(){
		var html = $(this).html()
		if(html.length > 13) $(this).html(html.substring(0,11)+"...");
	});

	// If we've loaded all the jquery.ui files we will add the functions
	if(loaded < 3) return true;

	if($('#ObName').length > 0){
		// Add the focus help for the object name field
		$('#ObName').focus();
		show_first_hint();

		$(function(){
			// initialise the "Select date" link
			// associate the link with a date picker
			$("#StartDate-pick").datepicker({
				buttonImage: "/"+rti_path+"/img/calendar.gif",
				buttonImageOnly: true,
				showOn: "button",
				minDate:"01/01/2004",
				maxDate:"+0d",
				onSelect:function(dateText, inst){
					updateSelects(dateText,"edit-StartDate-");
				},
				beforeShow:function(input, inst){
					var d = new Date(
						$("#edit-StartDate-year").val(),
						$("#edit-StartDate-month").val()-1,
						$("#edit-StartDate-day").val()
					);
					$(input).datepicker( "setDate" , d );
				}
			});
			
			$("#EndDate-pick").datepicker({
				buttonImage: "/"+rti_path+"/img/calendar.gif",
				buttonImageOnly: true,
				showOn: "button",
				minDate:"01/01/2004",
				maxDate:"+0d",
				onSelect:function(dateText, inst){
					updateSelects(dateText,"edit-EndDate-");
				},
				beforeShow:function(input, inst){
					var d = new Date(
						$("#edit-EndDate-year").val(),
						$("#edit-EndDate-month").val()-1,
						$("#edit-EndDate-day").val()
					);
					$(input).datepicker( "setDate" , d );
				}
			});
			
			var updateSelects = function (selectedDate,el){
				var selectedDate = new Date(selectedDate);
				$("#"+el+"day option[value=" + selectedDate.getDate() + "]").attr("selected", "selected");
				$("#"+el+"month option[value=" + (selectedDate.getMonth()+1) + "]").attr("selected", "selected");
				$("#"+el+"year option[value=" + (selectedDate.getFullYear()) + "]").attr("selected", "selected");
			}
		});
	}
	if($('#edit-ObName').length > 0){
		$("#edit-ObName").blur(function(){
			// We only want to fire off a request if the name has changed
			if($('#edit-ObName').val() != lookup_query){
				lookup_query = $('#edit-ObName').val()
				rti_archive_lookUP(lookup_query);
			}
		});
	}
})
var lookup_query = "";


function rti_archive_lookUP(val) {
	if(val){
		var el = document.getElementById("lookupresults")
		if(el){
			$('#archive-objecttype-info').show();
			el.innerHTML = "<p style=\"font-size:0.8em;\">Attempting to find details of "+val+"...</p>"
		}
		var headID = document.getElementsByTagName("head")[0];         
		var newScript = document.createElement('script');
		newScript.type = 'text/javascript';
		newScript.src = 'http://www.strudel.org.uk/lookUP/json/?name='+val+'&callback=rti_archive_getLookUPResults';
		headID.appendChild(newScript);
	}
}

function rti_archive_getLookUPResults(jData) {
	if(jData == null){
		alert("There was a problem parsing search results");
		return;
	}
	var equinox = jData.equinox;
	var target = jData.target;
	var coordsys = jData.coordsys;
	var ra = jData.ra
	var dec = jData.dec;
	var gal = jData.galactic;
	var category = jData.category;
	var service = jData.service;
	var image = jData.image;
	var el = document.getElementById("lookupresults")
	if(el){
		if(!ra){
				var str = target.name+" was not found. Are you sure it exists?";
		}else{
			if(target.suggestion){
				var str = target.name+" was not found. Did you mean <a href='#' onClick=\"iDidMean('"+target.suggestion+"')\">"+target.suggestion+"</a>?";
			}else{
				var str = target.name;
				if(category.avmdesc) str += " ("+category.avmdesc+")";
				if(ra && dec){
					if(ra.h < 10 && ra.h.length == 1) ra.h = "0"+ra.h;
					if(ra.m < 10) ra.m = "0"+ra.m;
					if(ra.s < 10) ra.s = "0"+(Math.round(ra.s*10)/10);
					str += " is ";
				}
				if(service.name == "SkyBot") str += "currently ";
				if(ra && dec) str += "at "+ra.h+":"+ra.m+":"+ra.s+", "+dec.d+":"+dec.m+":"+(Math.round(dec.s*100)/100)
				//if(ra && dec) str += " "+equinox+"";
				str += ".";
				angle = (category.avmdesc == "Constellation") ? 45 : 1.25;
				wikizoom = (category.avmdesc == "Constellation") ? 1 : 6;
				//if(service) str += " Find out <a href=\""+service.href+"\">more info about "+target.name+" from "+service.name+"</a>.";
				str += "";
			}
		}
		el.innerHTML = str
	}
}
function iDidMean(object) {
	$('#edit-ObName').val(object)
	rti_archive_lookUP(object);
}
