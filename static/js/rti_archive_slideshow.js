// LCOGT Slideshow module
// Last updated 2 January 2012
function Slideshow(inp){

	this.json = "";
	this.id = "result";
	this.slideby = 7;
	this.firstload = true;
	this.selected = 0;
	this.delay = 1500;
	this.hideable = true;
	this.loading = false;
	this.pause = 5000;
	this.running = false;

	if(typeof inp=="object"){
		if(typeof inp.id=="string") this.id = inp.id;
		if(typeof inp.json=="string") this.json = inp.json;
		if(typeof inp.delay=="number") this.delay = inp.delay;
		if(typeof inp.slideby=="number") this.slideby = inp.slideby;
	}
	this.observations = "";

	this.getObservations();
	$('#'+this.id).html('');

	$('body').bind('mousemove',{slides:this},function(e){
		ss = e.data.slides;
		$('#'+ss.id+' .scroller, #'+ss.id+' .controls').stop().css({opacity:'0.9'});
		clearTimeout(ss.clock);
		ss.readyToHide();
	})
	$(document).bind('keypress',{slides:this},function(e){
		if(!e) e=window.event;
		ss = e.data.slides;
		var code = e.keyCode || e.charCode || e.which || 0;
		if(code == 37) ss.displayImage(e.data.slides.selected-1)
		else if(code == 39) ss.displayImage(ss.selected+1)
		if(code == 37 || code == 39){
			var fromright = ($('#'+ss.id+' .thumbnails').outerWidth()/$('#'+ss.id+' .thumbnails li').outerWidth());
			var n = (ss.selected > ss.observations.length-Math.floor(fromright)) ? ss.observations.length-Math.floor(fromright) : ss.selected;
			n = (n < 0) ? 0 : n;
			var left = -(n*$('.thumbnails li').outerWidth());
			$('.thumbnails ul').animate({marginLeft:left+'px'},100);
		}else{
			if(code == 32) ss.toggle();
			else{
				var character = String.fromCharCode(code).toLowerCase();
				if(character == 's') ss.stop();	
				else if(character == 'p') ss.start();
				else if(character == 'i') ss.toggleInfo();
			}
		}
	});
	$('#'+this.id).append('<div class="loadingDiv" style="display:none;z-index:2;position:absolute;top:100px;">Loading...</div>');
	$(window).bind('resize',{s:this},function(e){ e.data.s.reposition(); });
}

Slideshow.prototype.reposition = function(){
	var l = (($(window).width()-$(window).height())/2);
	$('#'+this.id+' .controls').css({'right':'0px'});
	$('#'+this.id+' .bigpicture img').css({'height':$(window).height()});
	$('#'+this.id+' .bigpicture').css({'padding-left':l+'px'});
	var w = $(window).width()-($('#'+this.id+' .scrollLeft').outerWidth()+$('#'+this.id+' .scrollRight').outerWidth())-25;
	$('#'+this.id+' .thumbnails').css({width:w+'px'});
	$('#'+this.id+' .info').css({left:l+'px'});
	$('#'+this.id+' .loadingDiv').css({left:'5px',top:'5px'});
}
Slideshow.prototype.toggle = function(){
	if(this.running) this.stop();
	else this.start();
}
Slideshow.prototype.toggleInfo = function(){
	$('#'+this.id+' .info').fadeToggle();
}
Slideshow.prototype.start = function(){
	this.running = true;
	$('#'+this.id+' .scroller, #'+this.id+' .controls').animate({opacity:'0'},500);
	$('#logo').fadeOut();
	$('#'+this.id+' .controls .play').hide();
	$('#'+this.id+' .controls .stop').show();
	this.startofslide = new Date();
	this.nextSlide();
}
Slideshow.prototype.stop = function(){
	this.running = false;
	clearTimeout(this.slidetimer);
	$('#'+this.id+' .controls .play').show();
	$('#'+this.id+' .controls .stop').hide();
	$('#logo').fadeIn();
}

Slideshow.prototype.displayImage = function(sel){
	$('#'+this.id+' .loadingDiv').show();
	this.selectImage(sel);
	//this.panAndZoom();
}

Slideshow.prototype.panAndZoom = function(inp){
	w = $(window).width();
	h = $(window).height();
	if(!inp) inp = { };
	inp.x1 = inp.x1 || 0.5;
	inp.x2 = inp.x2 || 0.5;
	inp.y1 = inp.y1 || 0.5;
	inp.y2 = inp.y2 || 0.5;
	inp.z1 = inp.z1 || w/h;
	inp.z2 = inp.z2 || 1.5*w/h;
	inp.t = inp.t || 5000;
	var l1 = (inp.z1*(w-h)/2);
	var l2 = ((w-h*inp.z2)/2);
	$('#'+this.id+' .bigpicture').css({'padding-left':'0px','overflow':'hidden','width':w+'px','height':h+'px','left':'0px','top':'0px'})
	$('#'+this.id+' .bigpicture img').css({'left':l1+'px','width':(h*inp.z1)+'px','height':(h*inp.z1)+'px'}).animate({'left':l2+'px','width':($(window).height()*inp.z2)+'px','height':($(window).height()*inp.z2)+'px'},inp.t);
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

Slideshow.prototype.readyToHide = function(){
	this.clock = setTimeout(function(myslides){
		if(myslides.hideable) $('#'+myslides.id+' .scroller, #'+myslides.id+' .controls').animate({opacity:'0'},1000);
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
	if($('#'+this.id+' .thumbnails').length == 0){
		$('#'+this.id).append('<div class="info" style="display:none;"></div><div class="controls"><div class="play" title="Play"></div><div class="stop" title="Pause"></div><form><radio><input type="radio" name="speed" value="5000" checked /> Slow<br /><input type="radio" name="speed" value="2000" /> Fast</form></div><div class="scroller"><div class="scrollLeft"></div><div class="scrollRight"></div><div class="thumbnails"><ul></ul></div></div>');

		$("input[name=speed]").bind('change',{s:this},function(e){ e.data.s.pause = $('input[name=speed]:checked').val(); });
		$('#'+this.id+' .play').bind('click',{s:this},function(e){ e.data.s.start(); });
		$('#'+this.id+' .stop').bind('click',{s:this},function(e){ e.data.s.stop(); });
		$('#'+this.id+' .scroller, #'+this.id+' .controls').bind('mouseover',{s:this},function(e){ e.data.s.hideable = false; }).bind('mouseleave',{s:this},function(e){ e.data.s.hideable = true; });
		$('#'+this.id+' .scrollLeft').bind('click',{slides:this},function(e){
			var shift = (e.data.slides.slideby*$('.thumbnails li').outerWidth());
			var left = parseFloat($('.thumbnails ul').css('margin-left'))+shift
			if(left < 0) $('.thumbnails ul').animate({marginLeft:'+='+shift+'px'},400);
			else $('.thumbnails ul').animate({marginLeft:'0px'},400);
		});
		$('#'+this.id+' .scrollRight').bind('click',{slides:this},function(e){
			ss = e.data.slides;
			var shift = (ss.slideby*$('.thumbnails li').outerWidth());
			var right = $('.thumbnails ul').outerWidth()+parseFloat($('.thumbnails ul').css('margin-left'))-$('#result .thumbnails').outerWidth()-shift
			if(right < shift && ss.nextjson) ss.getObservations(ss.nextjson);
			if(right+shift > 0) $('.thumbnails ul').animate({marginLeft:'-='+shift+'px'},400);
		});
		$('#'+this.id+' .scrollLeft,#'+this.id+' .scrollRight, #'+this.id+' .play, #'+this.id+' .stop').bind('mousemove',function(){
			$(this).css({cursor:'pointer'});
		});
		w = $(window).width()-($('#'+this.id+' .scrollLeft').outerWidth()+$('#'+this.id+' .scrollRight').outerWidth())-20;
		$('#'+this.id+' .thumbnails').css({width:w+'px'});
	}
	var list = "";
	for(var i = 0 ; i < this.observations.length ; i++) list += '		<li>\n			<a href="'+this.observations[i].about+'"><img src="'+this.observations[i].image.thumb+'" title="'+this.observations[i].label+' ('+(i+1)+'/'+this.data.observations+')" class="thumb'+i+'" /></a>\n		</li>\n';
	$('#'+this.id+' .thumbnails ul').html(list);
	for(var i = 0 ; i < this.observations.length ; i++){
		$('img.thumb'+i).bind('click',{num:i,slides:this},function(e){
			e.stopPropagation();
			e.preventDefault();
			e.data.slides.displayImage(e.data.num);
		}).bind('error',function() {
			this.src = "http://lcogt.net/sites/default/themes/lcogt/images/missing.png";
			this.alt = "Image unavailable";
			this.onerror = "";
			return true;
		});
	}
	$('#'+this.id+' .thumbnails ul').css({width:this.observations.length*$('.thumbnails li').outerWidth()+'px'});
	if(this.firstload){
		if($('#'+this.id+' .intro').length == 0) $('#'+this.id).append('<div class="intro"><p>'+this.desc+'</p></div>');
		$('#'+this.id+' .intro').css({'width':($(window).width()/3)+'px'});
		$('#'+this.id+' .intro').css({'left':(($(window).width()-$('#'+this.id+' .intro').outerWidth())/2)+'px','top':(($(window).height()-$('#'+this.id+' .intro').outerHeight())/2)+'px','z-index':3}).delay(3000).fadeOut(500);
		if($('#'+this.id+' .bigpicture').length == 0) $('#'+this.id).append('<div class="bigpicture"><a href="'+this.observations[0].about+'"><img src="'+this.observations[0].image.about+'" /></div></a>');
		$('#'+this.id+' .bigpicture img').bind('mousemove',function(){ $(this).css({cursor:'pointer'}); }).bind('error',function() {
			this.src = "http://lcogt.net/sites/default/themes/lcogt/images/missing_large.png";
			this.alt = "Image unavailable";
			this.onerror = "";
			return true;
		});
		var obs = this.observations[this.selected];
		$('#'+this.id+' .info').html(this.getDescription(obs));
		this.firstload = false;
	}
	$('#'+this.id+' .thumbnails ul li').eq(this.selected).find('img').css({'border-color':'white'});
	this.reposition();
}

Slideshow.prototype.getObservations = function(json){
	if(typeof json!="string") json = this.json;
	if(!json) return this;
	$.ajax({
		dataType: "jsonp", 
		url: json,
		context: this,
		success: function(data){
			this.data = data;
			this.updateObservations();
		}
	});
}

Slideshow.prototype.selectImage = function(sel){
	var fromright = ($('#'+this.id+' .thumbnails').outerWidth()/$('#'+this.id+' .thumbnails li').outerWidth());
	if(sel > this.observations.length-fromright && this.nextjson) this.getObservations(this.nextjson);

	sel = (sel < 0) ? 0 : sel;
	sel = (sel >= this.observations.length) ? 0 : sel;
	this.selected = sel
	var obs = this.observations[this.selected];
	this.loading = true;

	$('#'+this.id+' .thumbnails ul li img').css({'border-color':$('#'+this.id+' .thumbnails ul li img').css('border-color')});	
	$('#'+this.id+' .thumbnails ul li').eq(this.selected).find('img').css({'border-color':'white'});
	$('#'+this.id+' .bigpicture a').attr('href',this.observations[this.selected].about);

	$('#'+this.id+' .bigpicture img').attr({
		src: obs.image.about,
		title: obs.label
	}).unbind('load').bind('load',{slides:this},function(e){
		e.data.slides.loading = false;
		$('#'+e.data.slides.id+' .loadingDiv').hide();
	}).bind('error',function() {
		this.src = "http://lcogt.net/sites/default/themes/lcogt/images/missing_large.png";
		this.alt = "Image unavailable";
		this.onerror = "";
		return true;
	});

	$('#'+this.id+' .info').html(this.getDescription(obs));

	// Now we pre-cache the next image
	sel = this.selected+1;
	sel = (sel < 0) ? 0 : sel;
	sel = (sel >= this.observations.length) ? 0 : sel;
	$.preLoadImages(this.observations[sel].image.about);
}

Slideshow.prototype.getDescription = function(obs){
	html = '<h1><a href="'+obs.about+'">'+obs.label+'</a></h1>'
	if(obs.avm && obs.avm.name){
		codes = obs.avm.code.split(';');
		names = obs.avm.name.split(';');
		html += '<p class="avm">';
		for(c = 0 ; c < codes.length ; c++){
			if(c > 0) html += "/"
			html += '<a href="http://lcogt.net/observations/category/'+codes[c]+'" title="Object type">'+names[c]+'</a>'
		}
		html += '</p>';
	}
	html += '<p class="telescope"><a href="'+obs.instr.about+'" title="Telescope">'+obs.instr.tel+'</a></p>'
	html += '<p class="exposure"><span title="Exposure">'+obs.filter+' '+obs.exposure+' seconds</span></p>'
	html += '<p class="date"><span title="Date">'+relative_time(new Date(Date.parse(obs.time.creation)))+'</span></p>'
	html += '<p class="observer"><a href="'+obs.observer.about+'" title="Observer">'+obs.observer.label+'</a></p>';
	return html;
}

// pd = parsed date
function relative_time(pd) {
	var relative_to = (arguments.length > 1) ? arguments[1] : new Date();
	var dt = parseInt((relative_to.getTime() - pd) / 1000);
	if (dt < 60) return 'less than a minute ago';
	else if(dt < 120) return 'about a minute ago';
	else if(dt < (45*60)) return (parseInt(dt / 60)).toString() + ' minutes ago';
	else if(dt < (90*60)) return 'about an hour ago';
	else if(dt < (48*60*60)) {
		h = (parseInt(dt / 3600)).toString()
		if(h == 1) return 'about ' + h + ' hour ago';
		else return 'about ' + h + ' hours ago';
	}else if(dt < (30*86400)) {
		return (parseInt(dt / 86400)).toString() + ' days ago';
	}else{
		var mons = new Array('January','February','March','April','May','June','July','August','September','October','November','December');
		y = pd.getYear()+'';
		if(y.length < 4) y = (y-0+1900);
		h = pd.getHours();
		if(h < 10) h = "0"+h;
		m = pd.getMinutes();
		if(m < 10) m = "0"+m;
		if(dt < (360*86400)) return pd.getDate()+' '+mons[pd.getMonth()]+' ('+h+':'+m+')';
		else return pd.getDate()+' '+mons[pd.getMonth()]+' '+y+' ('+h+':'+m+')';
	}
}
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