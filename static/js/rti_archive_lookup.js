var http_request = false;
var lookup_done = true;
var lookup_start = 0;
var filterchange = 0;

if (jQuery) {
	$(document).ready(function(){
		lookUP('#lookup');
		if($('img.observation-image').length == 1){
			obs_img = $('img.observation-image').attr('src');
			$(".observation-metadata ul.filters li a").bind('mouseover',function(){
				clearTimeout(filterchange);
				var col = $(this).attr('title').substring(0,$(this).attr('title').indexOf(' '));
				if($(this).attr('href').indexOf('.jpg') >= 0){
					$(this).parent().append('<div class="filter_loader">(Loading...)</div>');
					$('.filter_loader').css({'color':'black','display':'inline','margin-left':5});
					$('img.observation-image').attr({'src':$(this).attr('href')}).bind('load',function(){
						showFilter(col);
						$(".filter_loader").remove();
					});
				}
			}).bind('mouseout',function(){
				filterchange = setTimeout(function() { $('img.observation-image').attr({'src':obs_img}); },500);
				$(".filter_loader").remove();
			});
			$(document).keypress(function(e){
				if (!e) e=window.event;
				var code = e.keyCode || e.charCode || e.which || 0;
				if(code != 38 && code != 40 && code != 107 && code != 61 && code != 187 && code != 33){
					var character = String.fromCharCode(code);
					var col = "";
					if(character == 'r' || character == 'R') col = 'red';
					else if(character == 'g' || character == 'G') col = 'green';
					else if(character == 'b' || character == 'B') col = 'blue';
					else if(character == 'v' || character == 'a') col = 'transparent';
					if(col){
						clearTimeout(filterchange);
						var src = ($('a.filter-'+col).length > 0) ? $('a.filter-'+col).attr('href') : obs_img;
						if(src) $('img.observation-image').attr({'src':src}).bind('load',function(){ showFilter(col); });
					}
				}
			});
			$('input.searchbox').val($('input.searchbox').attr('title')).css({'color':'#999'}).focus(function(){
				if($(this).val() == $(this).attr('title')) $(this).val('').css({'color':'black'});
			}).blur(function(){
				if($(this).val() == "") $(this).val($(this).attr('title')).css({'color':'#999'});
			});
		}
		if($('img.observation-image').length > 0){
			// Check for failure to load images and use a dummy image
            imageLoadError('img.observation-image');
		}
		if($('.thumbnail img').length > 0){
            imageLoadError('.thumbnail img');
		}
		if($('.stream img').length > 0){
		    imageLoadError('.stream img');
		}
	});
}

function imageLoadError(el){
    $(el).each(function(){
            // Work	around for error function reporting of file load failure
            this.src = this.src;
            $(this).bind('error',function() {
             	this.src = "http://lcogt.net/files/imagecache/large/egomez/no-image_120.png";
             	this.alt = "Image unavailable";
                    this.onerror = "";
                    return true;
            })
    });
}

function showFilter(col){
	if(col != "red" && col != "green" && col != "blue") col= 'transparent';
	if($('.huefilter').length <= 0) $('.observation-images').prepend("<div class='huefilter'></div>");
	// Show/hide the hue filter as necessary
	if($('img.observation-image').attr('src') != obs_img) $('.huefilter').show();
	else $('.huefilter').hide();
	$('.huefilter').css({position:'absolute','background-color':col,width:'500px',height:'500px',opacity:'0.2'});
}

function getLookUPResults(jData) {

	var valid = /[^A-Za-z0-9]/g;
	var id = '#lookup';

	if(jData == null){
		$(id).html("There was a problem dealing with the search results. Sorry about that.");
		return false;
	}
	var equinox = jData.equinox;
	var target = jData.target;
	var coordsys = jData.coordsys;
	var ra = jData.ra;
	var dec = jData.dec;
	var gal = jData.galactic;
	var category = jData.category;
	var service = jData.service;
	var message = jData.message;
	lookup_done = true;
	if(target.suggestion){
		message = "<a href=\"#\" onClick=\"lookUP(\'"+id+"\',\'"+target.suggestion+"\');\">Did you mean "+target.suggestion+"</a>?";
	}else{
		if(ra){
			var str = ra.decimal+','+dec.decimal;
			message = '<a href="/search/archive?ObName='+target.name+'&DateRange=all&telid=0&filter=A&op=Search&form_id=rti_archive_form" title="Search LCOGT archive for more observations of '+target.name+'">'+target.name+'</a> (<span property="AVM:code" content="'+category.avmcode+'">'+category.avmdesc+'</span>)<br />More <a href="'+service.href+'">information via '+service.name+'</a><br />More <a href="http://www.strudel.org.uk/lookUP/?name='+encodeURL(target.name)+'">information via lookUP</a><br /><a href="http://www.flickr.com/search/?q='+encodeURL(target.name)+'+astrophotography">Astrophotography images on Flickr</a>';
		}
	}
	if(message) $(id).html(message);
	return false;
}

function lookUP(id,object) {
	if(!object) object = $(id).val();
	if(!object && $(id).html()) object = $(id).html();

	if(object){
		$(id).html("Searching...");
		lookup_start = new Date();
		lookup_done = false;
		$.ajaxSetup({async:false,'beforeSend': function(xhr){ if (xhr.overrideMimeType) xhr.overrideMimeType("text/plain"); } });
		// Get the JSON results file
		$.getJSON('http://www.strudel.org.uk/lookUP/json/?name='+encodeURL(object)+'&callback=?', getLookUPResults);
	}
}


function encodeURL(str){
	str = encodeURIComponent(str).replace(/!/g, '%21').replace(/'/g, '%27').replace(/\(/g, '%28').  replace(/\)/g, '%29').replace(/\*/g, '%2A'); 
	str = str.replace(/%0A/g, '\n')
	return str
}