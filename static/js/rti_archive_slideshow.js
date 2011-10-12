
function Slideshow(inp){

	this.json = "http://lco3-beta/en/observations/ogg/2m0a.json";
	this.json = "http://lco3-beta/en/observations/user/1323.json";
	this.id = "result";
	this.slideby = 7;
	this.firstload = true;
	this.selected = 0;
	this.delay = 1500;
	this.hideable = true;
	this.loading = false;
	this.pause = 5000;

	if(typeof inp=="object"){
		if(typeof inp.id=="string") this.id = inp.id;
		if(typeof inp.json=="string") this.json = inp.json;
		if(typeof inp.delay=="number") this.delay = inp.delay;
		if(typeof inp.slideby=="number") this.slideby = inp.slideby;
	}
	this.observations = "";

	this.getObservations();
	var _object = this;

	$('body').bind('mousemove',function(e){
		$('#result .scroller, #result .controls').stop().css({opacity:'0.9'});
		clearTimeout(_object.clock);
		_object.readyToHide();
	})
	$(document).bind('keypress',{slides:this},function(e){
		if(!e) e=window.event;
		var code = e.keyCode || e.charCode || e.which || 0;
		if(code == 37) e.data.slides.displayImage(e.data.slides.selected-1)
		else if(code == 39) e.data.slides.displayImage(e.data.slides.selected+1)
		if(code == 37 || code == 39){
			var fromright = ($('#result .thumbnails').outerWidth()/$('#result .thumbnails li').outerWidth());
			var n = (e.data.slides.selected > e.data.slides.observations.length-Math.floor(fromright)) ? e.data.slides.observations.length-Math.floor(fromright) : e.data.slides.selected;
			n = (n < 0) ? 0 : n;
			var left = -(n*$('.thumbnails li').outerWidth());
			$('.thumbnails ul').animate({marginLeft:left+'px'},100);
		}else{
			var character = String.fromCharCode(code).toLowerCase();
			if(character == 's') e.data.slides.stop();	
			else if(character == 'p') e.data.slides.start();
		}
	});
	$('#result').append('<div class="loadingDiv" style="display:none;z-index:2;position:absolute;top:100px;">Loading...</div>');
	$(window).resize(function(){ _object.reposition(); });
}

Slideshow.prototype.reposition = function(){
	var l = (($(window).width()-$(window).height())/2);
	$('#result .controls').css({'right':'0px'});
	$('#result .bigpicture img').css({'height':$(window).height()});
	$('#result .bigpicture').css({'left':l+'px'});
	var w = $(window).width()-($('#result .scrollLeft').outerWidth()+$('#result .scrollRight').outerWidth())-25;
	$('#result .thumbnails').css({width:w+'px'});
	$('#result .info').css({left:l+'px'});
	$('#result .loadingDiv').css({left:'5px',top:'5px'});//:(($(window).height()-$('#result .loadingDiv').outerHeight())/2)+'px'});
}

Slideshow.prototype.start = function(){
	$('#result .scroller, #result .controls').animate({opacity:'0'},500);
	this.startofslide = new Date();
	$('#result .controls .play').hide();
	$('#result .controls .stop').show();
	this.nextSlide();
}

Slideshow.prototype.displayImage = function(sel){
	$('#result .loadingDiv').show();
	this.selectImage(sel);
}

Slideshow.prototype.nextSlide = function(){
	if(this.loading){
		this.slidetimer = setTimeout(function(slides){ slides.nextSlide(); },1000,this);
	}else{
		var now = new Date();
		var tdiff = now.getTime()-this.startofslide.getTime();
		var wait = (this.pause-tdiff);
		if(wait < 100) wait = 100;
		this.slidetimer = setTimeout(function(slides){
			slides.startofslide = new Date();
			slides.selectImage(slides.selected+1);
			var left = -(slides.selected*$('.thumbnails li').outerWidth());
			$('.thumbnails ul').animate({marginLeft:left+'px'},400);
			slides.nextSlide();
		},wait,this);
	}
}

Slideshow.prototype.stop = function(){
	clearTimeout(this.slidetimer);
	$('#result .controls .play').show();
	$('#result .controls .stop').hide();
}

Slideshow.prototype.readyToHide = function(){
	this.clock = setTimeout(function(myslides){
		if(myslides.hideable) $('#result .scroller, #result .controls').animate({opacity:'0'},1000);
	},this.delay,this);
}

Slideshow.prototype.getNext = function(){
	if(typeof this.nextjson=="string") this.getObservations(this.nextjson);
}

Slideshow.prototype.updateObservations = function(){

	this.nextjson = (typeof (this.data.page)=="object" && typeof (this.data.page.next)=="string") ? this.data.page.next : "";
	if(typeof (this.data.live)=="number") setTimeout(function(slides){ slides.getObservations(slides.data.link+'.json'); },this.data.live*1000,this);

	var num = this.observations.length;
	if(typeof this.observations=="object" && typeof (this.data.live)!="number"){
		for(var i = 0 ; i < this.data.observation.length ; i++) this.observations[this.observations.length] = this.data.observation[i];
	}else{
		this.observations = this.data.observation;
	}
	this.desc = this.data.desc;
	if($('#result .thumbnails').length == 0){
		$('#result').append('<div class="info"></div><div class="controls"><div class="play" title="Play"></div><div class="stop" title="Pause"></div><form><radio><input type="radio" name="speed" value="5000" checked /> Slow<br /><input type="radio" name="speed" value="2000" /> Fast</form></div><div class="scroller"><div class="scrollLeft"></div><div class="scrollRight"></div><div class="thumbnails"><ul></ul></div></div>');
		var _object = this;

		$("input[name=speed]").change(function () { _object.pause = $('input[name=speed]:checked').val(); });


		$('#result .play').bind('click',function(){ _object.start(); });
		$('#result .stop').bind('click',function(){ _object.stop(); });
		$('#result .scroller, #result .controls').bind('mouseover',function(e){ _object.hideable = false; }).bind('mouseleave',function(e){ _object.hideable = true; });
		$('#result .scrollLeft').bind('click',function(){
			var shift = (_object.slideby*$('.thumbnails li').outerWidth());
			var left = parseFloat($('.thumbnails ul').css('margin-left'))+shift
			if(left < 0) $('.thumbnails ul').animate({marginLeft:'+='+shift+'px'},400);
			else $('.thumbnails ul').animate({marginLeft:'0px'},400);
		});
		$('#result .scrollRight').bind('click',function(){
			var shift = (_object.slideby*$('.thumbnails li').outerWidth());
			var right = $('.thumbnails ul').outerWidth()+parseFloat($('.thumbnails ul').css('margin-left'))-$('#result .thumbnails').outerWidth()-shift
			if(right < shift && _object.nextjson) _object.getObservations(_object.nextjson);
			if(right+shift > 0) $('.thumbnails ul').animate({marginLeft:'-='+shift+'px'},400);
		});
		$('#result .scrollLeft,#result .scrollRight, #result .play, #result .stop').bind('mousemove',function(){
			$(this).css({cursor:'pointer'});
		});
		w = $(window).width()-($('#result .scrollLeft').outerWidth()+$('#result .scrollRight').outerWidth())-20;
		$('#result .thumbnails').css({width:w+'px'});
	}
	var list = "";
	var _object = this;
	for(var i = 0 ; i < this.observations.length ; i++){
		list += '		<li>\n			<a href="'+this.observations[i]._about+'"><img src="'+this.observations[i].image.thumb+'" title="'+this.observations[i].label+' ('+(i+1)+'/'+this.data.observations+')" class="thumb'+i+'" /></a>\n		</li>\n';
	}
	$('#result .thumbnails ul').html(list);
	for(var i = 0 ; i < this.observations.length ; i++){
		$('img.thumb'+i).bind('click',{num:i},function(e){
			e.stopPropagation();
			e.preventDefault();
			_object.displayImage(e.data.num);
		}).bind('error',function() {
			this.src = "http://lcogt.net/files/imagecache/large/egomez/no-image_120.png";
			this.alt = "Image unavailable";
			this.onerror = "";
			return true;
		});
	}
	$('#result .thumbnails ul').css({width:this.observations.length*$('.thumbnails li').outerWidth()+'px'});
	if(this.firstload){
		if($('#result .intro').length == 0) $('#result').append('<div class="intro"><p>'+this.desc+'</p></div>');
		$('#result .intro').css({'width':($(window).width()/3)+'px'});
		$('#result .intro').css({'left':(($(window).width()-$('#result .intro').outerWidth())/2)+'px','top':(($(window).height()-$('#result .intro').outerHeight())/2)+'px','z-index':3}).delay(3000).fadeOut(500);
		if($('#result .bigpicture').length == 0) $('#result').append('<div class="bigpicture"><img src="'+this.observations[0].image._about+'" /></div>');
		$('#result .bigpicture img').bind('click',{slides:this},function(e){
			location.href = e.data.slides.observations[0]._about
		}).bind('mousemove',function(){ $(this).css({cursor:'pointer'}); }).bind('error',function() {
			this.src = "/files/imagecache/large/egomez/no-image_120.png";
			this.alt = "Image unavailable";
			this.onerror = "";
			return true;
		});
		var obs = this.observations[this.selected];
		$('#result .info').html(_object.getDescription(obs));
		this.firstload = false;
	}
	$('#result .thumbnails ul li').eq(this.selected).find('img').css({'border-color':'white'});
	this.reposition();
}

Slideshow.prototype.getObservations = function(json){
	if(typeof json!="string") json = this.json;
	var _object = this;
	$.ajax({
		dataType: "jsonp", 
		url: json,
		context: _object,
		success: function(data){
			_object.data = data;
			_object.updateObservations();
		}
	});
}

Slideshow.prototype.selectImage = function(sel){
	var fromright = ($('#result .thumbnails').outerWidth()/$('#result .thumbnails li').outerWidth());
	if(sel > this.observations.length-fromright && this.nextjson) this.getObservations(this.nextjson);

	sel = (sel < 0) ? 0 : sel;
	sel = (sel >= this.observations.length) ? 0 : sel;
	this.selected = sel
	var obs = this.observations[this.selected];
	this.loading = true;

	$('#result .thumbnails ul li img').css({'border-color':$('#result .thumbnails ul li img').css('border-color')});	
	$('#result .thumbnails ul li').eq(this.selected).find('img').css({'border-color':'white'});
	$('#result .bigpicture img').attr({
		src: obs.image._about,
		title: obs.label
	}).unbind('click').bind('click',{slides:this},function(e){
		location.href = e.data.slides.observations[e.data.slides.selected]._about
	}).unbind('load').bind('load',{slides:this},function(e){
		e.data.slides.loading = false;
		$('#result .loadingDiv').hide();
	}).bind('error',function() {
		this.src = "/files/imagecache/large/egomez/no-image_120.png";
		this.alt = "Image unavailable";
		this.onerror = "";
		return true;
	});

	$('#result .info').html(this.getDescription(obs));

	// Now we pre-cache the next image
	sel = this.selected+1;
	sel = (sel < 0) ? 0 : sel;
	sel = (sel >= this.observations.length) ? 0 : sel;
	$.preLoadImages(this.observations[sel].image._about);
}

Slideshow.prototype.getDescription = function(obs){
	return '<h1 style="font-size:1em;margin:0px;"><a href="'+obs._about+'">'+obs.label+'</a></h1><p style="margin:0px;padding:0px;font-size:0.8em;">by <a href="'+obs.observer._about+'">'+obs.observer.label+'</a> '+relative_time(new Date(Date.parse(obs.time.creation)))+' using <a href="'+obs.instr._about+'">'+obs.instr.tel+'</a>';

	var str = $('#logo').html()+'<br style="clear:both;"><h1><a href="'+obs._about+'">'+obs.label+'</a></h1><table><tr><td>Observer:</td><td><a href="'+obs.observer._about+'">'+obs.observer.label+'</a></td></tr><tr><td>Date:</td><td>'+obs.time.creation+'</td></tr>';
	if(typeof obs.ra!="undefined"){
		var ra_h = Math.floor(obs.ra/15);
		var ra_m = Math.floor(((obs.ra/15)-ra_h)*60);
		var ra_s = Math.round(((obs.ra/15)-ra_h)*3600 - (ra_m)*60);
		if (ra_h < 10) ra_h = "0"+ra_h;
		if (ra_m < 10) ra_m = "0"+ra_m;
		if (ra_s < 10) ra_s = "0"+ra_s;
		var ra = ra_h+':'+ra_m+':'+ra_s
		var dc_d = Math.floor(obs.dec);
		var dc_m = Math.floor((obs.dec-dc_d)*60);
		var dc_s = Math.round((obs.dec-dc_d)*3600 - (dc_m)*60);
		var sign = (dc_d >= 0) ? "+" : "-";
		if (Math.abs(dc_d) < 10) dc_d = sign+"0"+Math.abs(dc_d);
		if (dc_m < 10) dc_m = "0"+dc_m;
		if (dc_s < 10) dc_s = "0"+dc_s;
		var dec = dc_d+':'+dc_m+':'+dc_s;
		str += '<tr><td>Coordinates:</td><td>'+ra+', '+dec+'</td></tr>';
	}
	str += '<tr><td>Telescope:</td><td><a href="'+obs.instr._about+'">'+obs.instr.tel+'</a></td></tr>';
	return str;
}

function relative_time(parsed_date) {
	var relative_to = (arguments.length > 1) ? arguments[1] : new Date();
	var delta = parseInt((relative_to.getTime() - parsed_date) / 1000);
	//delta = delta - (relative_to.getTimezoneOffset() * 60);
	if (delta < 60) return 'less than a minute ago';
	else if(delta < 120) return 'about a minute ago';
	else if(delta < (45*60)) return (parseInt(delta / 60)).toString() + ' minutes ago';
	else if(delta < (90*60)) return 'about an hour ago';
	else if(delta < (48*60*60)) {
		h = (parseInt(delta / 3600)).toString()
		if(h == 1) return 'about ' + h + ' hour ago';
		else return 'about ' + h + ' hours ago';
	}else return (parseInt(delta / 86400)).toString() + ' days ago';
}

//(function($) {
var cache = [];
// Arguments are image paths relative to the current page.
$.preLoadImages = function() {
	var args_len = arguments.length;
	for (var i = args_len; i--;) {
		var cacheImage = document.createElement('img');
		cacheImage.src = arguments[i];
		cache.push(cacheImage);
	}
}

