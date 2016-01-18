// This is the Javascript for the RTI "Search Public Archive" form

// A counter to keep track of how many js files we've loaded
var loaded = 0;
var obs_img = '';
var search = '';

$(document).ready(function(){

	// Check for failure to load images and use a dummy image
	if($('img.observation-image').length > 0) imageLoadError('img.observation-image');
	if($('.thumb-img img').length > 0) imageLoadError('.thumb-img img');
	if($('.stream img').length > 0) imageLoadError('.stream img');

	if($('input.searchbox').length > 0){
		$('input.searchbox').val($('input.searchbox').attr('title')).css({'color':'#999'}).focus(function(){
			if($(this).val() == $(this).attr('title')) $(this).val('').css({'color':'black'});
		}).blur(function(){
			if($(this).val() == "") $(this).val($(this).attr('title')).css({'color':'#999'});
		});
		search = $('input.searchbox').closest('form').attr('action');
	}
	$(".closeable").prepend('<div style="float:right;" class="closer"><a href="#" class="close" title="Close">&times;</a></div>');
	$(".closeable a.close").click(function(e){
		e.preventDefault();
		// Check parents, grandparents or great-grandparents.
		if($(this).parent().hasClass('closeable')) el = $(this).parent()
		else if($(this).parent().parent().hasClass('closeable')) el = $(this).parent().parent()
		else if($(this).parent().parent().parent().hasClass('closeable')) el = $(this).parent().parent().parent()
		if(el) el.slideUp("slow")
	});

	formatObservations();

	$(document).on('click','.more-info-hint',function(event){
		var li = $(this).closest('.thumb');
		var idx = $(this).attr('id');
		idx = parseInt(idx.substring(idx.lastIndexOf('-')+1));
		var img = li.find('img').attr('src');
		var link = li.find('a').attr('href');
		var observer = li.find('.observer').attr('title');

		if($('.show-details').size() == 0) $('body').append('<div class="show-details"><div class="show-details-inner"></div></div>');
		var img = img.replace("_120.jpg","_150.jpg");
		var img_full = img.replace("_120.jpg",".jpg");
		$('.show-details-inner').html('<div class="show-details-close">&times;</div><a href="'+link+'" title="Click for full size version"><img src="'+img+'" style="width:150px;height:150px;" /></a>'+$('.observation-results .more-info').eq(idx).html()+'<div class="observer">Observer: <a href="'+$('a.observer').eq(idx).attr('href')+'">'+observer+'</a></div>');
		centreDiv('.show-details');
		if ($('.show-details').is(':visible')) $('.show-details').fadeOut("fast");
		else $('.show-details').fadeIn("fast");
		$('.show-details-close').bind("click",function(){
			$('.show-details').fadeOut("fast");
		});
		return false;
	})


	var lastUpdated = new Date(); //'Fri, 27 Apr 2012 11:22:53 +0000');

	// ****** disabling look for new observations ****
	//var timer = setInterval(updateObservations,60000);

	// Get new observations
	function updateObservations(){
		if($(".observation-results").length < 1) clearInterval(timer);
		$(".observation-results").each(function(index) {
			if($(this).attr('data-json')){
				var _obj = $(this);
				var url = $(this).attr('data-json');
				url += (_obj.attr('data-update')=="add" ? (url.indexOf('?') < 0 ? '?' : '&')+'since='+lastUpdated.toGMTString() : "");
				$.ajax({
					url: url,
					dataType: "jsonp",
					success: function(data){
						lastUpdated = new Date();
						var str = lastUpdated.toGMTString();
						if($('.time').length > 0) $('.time').html('Updated <time datetime="'+str+'" title="'+str+'">'+str.substring(5,str.indexOf('GMT'))+'UTC</time>');
						if(data == null) return;
						if(typeof data.observation==="object" && !data.observation.length) data.observation = [data.observation]

						if(data.observation.length > 0){
							var d = new Date(data.observation[0].time.creation);
							if($('.mostrecent').length > 0){
								$('.mostrecent').html('<time datetime="'+d.toGMTString()+'" title="'+d.toGMTString()+'">'+d.toLocaleString()+'</time>');
								updateTime($('.mostrecent time'));
							}
							// What is the maximum size of the list?
							var n = (_obj.attr('data-max')) ? parseInt(_obj.attr('data-update')) : 30;
							if(n < 1 || typeof n!=="number") n = 30;
							// Build the new observations to add
							var out = "";
							for(var i = 0; i < data.observation.length ; i++) out += makeObservation(data.observation[i]);
							// Add or replace
							if(_obj.attr('data-update')=="add") _obj.prepend(out);
							else _obj.html(out);
							imageLoadError(_obj.find('img'));
							// Remove the "lastcol" class and list items that are beyond the limit
							_obj.find('li').removeClass('lastcol').slice(n).remove();
							_obj.find('li:nth-child(6n)').addClass('lastcol');
							// Add the more info links etc
							formatObservations();
						}
						if(typeof updatePlanetarium==="function") updatePlanetarium(data);
					}
				});
			}
		});
	}

	function addMoreInfoHint(el,index){
		if(el.find('.more-info-hint').length == 0){
			var d = el.find('time').attr('datetime');
			var r = relative_time_short(d);
			if(!r) r = "Info";
			el.find('.thumb-img').append('<a href="#" class="more-info-hint" id="more-info-hint-'+index+'" title="Quick info"><time datetime="'+d+'">'+r+'</time></a>');
			$("#more-info-hint-"+index).fadeIn(1000);
		}
	}

	function formatObservations(){
		// Javascript for results thumbnails
		$(".observation-results .thumb").each(function(index) {
			addMoreInfoHint($(this),index);
		});
	}
	function makeObservation(o){
		var d = o.time.creation;
		d = d.replace('+0000','UT');
		var out = "";
		out += '<li class="onecol">';
		out += '	<div class="thumb" about="'+o.about+'">';
		out += '		<span class="thumbnail"><a href="'+o.about+'"><img src="'+o.image.thumb+'" alt="'+o.label+'" /></a></span>';
		out += '		<div class="thumb-caption"><div class="title ellipsis" property="UCD:obs" title="'+o.label+'">'+o.label+'</div><div class="ellipsis">By <a href="'+o.observer.about+'" class="observer" title="'+o.observer.label+'" property="UCD:obs.observer">'+o.observer.label+'</a></div></div>';
		out += '		<div class="more-info">';
		out += '			<div class="name">Title: <a href="'+search+'?query='+o.label+'" property="dc:title">'+o.label+'</a></div>';
		out += '			<div class="position">'+formatPosition(o.ra,o.dec)+'<br /><span style="font-size:0.7em;">(View coordinates in <a href="http://server1.wikisky.org/v2?ra='+o.ra+'&amp;de='+o.dec+'&amp;zoom=6&amp;img_source=astrophoto">Wikisky</a> or <a href="http://www.worldwidetelescope.org/wwtweb/goto.aspx?object=ViewShortcut&amp;ra='+o.ra+'&amp;dec='+o.dec+'&amp;zoom=3">WorldWideTelescope</a>)</span></div>';
		out += '			<div class="telescope">Telescope: <a href="'+o.instr.about+'">'+o.instr.tel+'</a></div>';
		out += '			<div class="filter">Filter: <a href="'+o.filter.about+'" title="'+o.filter.name+'">'+o.filter.name+'</a></div>';
		out += '			<div class="exposure">Exposure: '+o.exposure+' s (total)</div>';
		out += '			<time datetime="'+o.time.creation+'">Date: '+d+'</time>';
		out += '		</div>';
		out += '	</div>';
		out += '</li>';
		return out;
	}
	function updateTime(el){
		var attr = (el.attr('datetime')) ? el.attr('datetime') : el.attr('title');
		if(!attr) return;
		var txt = relative_time_short(attr);
		if(txt) el.html(txt);
	}
	function updateTimes(el){
		if(typeof el!=="object") el = $('.more-info-hint time');
		el.each(function(i){ updateTime($(this)); });
	}
	ticker = setInterval(updateTimes,30000);

});

function tryImageAgain(t){
	// Get the value of the original URL
	var orig = $(t).attr('data-src');
	if(orig){
		// Set the source again and work around any caching
		t.src = orig+"?"+Math.random();
		console.log(t.src);
		imageLoadError(t);
	}
}

function imageLoadError(el){
	$(el).each(function(){
		// Work	around for error function reporting of file load failure
		this.src = this.src;
		$(this).off('error').on('error',function() {
			var tryagain = (!$(this).attr('data-src')) ? true : false;
			// Store the original URL
			$(this).attr('data-src',this.src);
			this.src = "http://lcogt.net/files/no-image_120.png";
			this.alt = "Image unavailable";
			this.onerror = "";
			if(tryagain) var timeout = setTimeout(tryImageAgain,30000,this);
			return true;
		});
	});
}

centreDiv = function(el){
	var wide = $(window).width();
	var tall = $(window).height();
	$(el).css({left:(wide-$(el).outerWidth())/2,top:($(window).scrollTop()+(tall-$(el).outerHeight())/2)});
}

function formatPosition(ra,dec){
	ra /= 15;
	var ra_h = parseInt(ra);
	var ra_m = parseInt((ra-ra_h)*60);
	var ra_s = ((ra-ra_h-ra_m/60)*3600).toFixed(2);
	if(ra_h < 10) ra_h = "0"+ra_h;
	if(ra_m < 10) ra_m = "0"+ra_m;
	if(ra_s < 10) ra_s = "0"+ra_s;
	var dec_sign = (dec >= 0) ? "" : "-";
	var dec_d = parseInt(Math.abs(dec));
	var dec_m = parseInt((Math.abs(dec)-dec_d)*60);
	var dec_s = ((Math.abs(dec)-dec_d-dec_m/60)*3600).toFixed(2);
	if(Math.abs(dec_d) < 10) dec_d = "0"+dec_d;
	if(dec_m < 10) dec_m = "0"+dec_m;
	if(dec_s < 10) dec_s = "0"+dec_s;
	return 'RA: '+ra_h+':'+ra_m+':'+ra_s+', Dec: '+dec_sign+dec_d+':'+dec_m+':'+dec_s+'';
}

// Function to check if a date is valid - to avoid NaNs
function isValidDate(d) {
	if ( Object.prototype.toString.call(d) !== "[object Date]" )
		return false;
	return !isNaN(d.getTime());
}

// pd = parsed date
function relative_time_short(pd) {
	var relative_to = (arguments.length > 1) ? arguments[1] : new Date();
	pd = new Date(pd);
	if(!isValidDate(pd)) return "";
	var dt = parseInt((relative_to.getTime() - pd) / 1000);
	if (dt < 60) return 'seconds ago';
	else if(dt < 120) return 'a minute ago';
	else if(dt < (60*60)) return (parseInt(dt / 60)).toString() + ' minutes ago';
	else if(dt < (48*60*60)) {
		h = (parseInt(dt / 3600)).toString()
		if(h == 1) return 'an hour ago';
		else return ''+ h + ' hours ago';
	}else if(dt < (30*86400)) {
		return (parseInt(dt / 86400)).toString() + ' days ago';
	}else{
		var mons = new Array('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec');
		y = pd.getYear()+'';
		if(y.length < 4) y = (y-0+1900);
		if(dt < (180*86400)) return pd.getDate()+' '+mons[pd.getMonth()];
		else return pd.getDate()+' '+mons[pd.getMonth()]+' '+y;
	}
}
