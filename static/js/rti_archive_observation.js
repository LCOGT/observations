var http_request = false;
var lookup_done = true;
var lookup_start = 0;
var filterchange = 0;

if (jQuery) {
	$(document).ready(function(){
		if($('img.observation-image').length == 1){
			obs_img = $('img.observation-image').attr('src');
			$(".observation-metadata ul.filters li a").bind('mouseover',function(){
				clearTimeout(filterchange);
				var col = $(this).attr('title').substring(0,$(this).attr('title').indexOf(' '));
				col = col.toLowerCase();
				if($(this).attr('href').indexOf('.jpg') >= 0){
					$(this).parent().append('<div class="filter_loader">loading</div>');
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
		}
	});
}


function showFilter(col){
	if(col != "red" && col != "green" && col != "blue") col= 'transparent';
	if($('.huefilter').length <= 0) $('.observation-image').before("<div class='huefilter'></div>");
	// Show/hide the hue filter as necessary
	if($('img.observation-image').attr('src') != obs_img) $('.huefilter').show();
	else $('.huefilter').hide();
	$('.huefilter').css({position:'absolute','background-color':col,width:'560px',height:'560px',opacity:'0.2','z-index':2});
}

function encodeURL(str){
	str = encodeURIComponent(str).replace(/!/g, '%21').replace(/'/g, '%27').replace(/\(/g, '%28').  replace(/\)/g, '%29').replace(/\*/g, '%2A'); 
	str = str.replace(/%0A/g, '\n')
	return str
}