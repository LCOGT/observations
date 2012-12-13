// This is the Javascript for the RTI "Search Public Archive" form

// A counter to keep track of how many js files we've loaded
var loaded = 0;
var obs_img = '';

$(document).ready(function(){

	// Check for failure to load images and use a dummy image
	if($('img.observation-image').length > 0) imageLoadError('img.observation-image');
	if($('.thumbnail img').length > 0) imageLoadError('.thumbnail img');
	if($('.stream img').length > 0) imageLoadError('.stream img');

	if($('input.searchbox').length > 0){
		$('input.searchbox').val($('input.searchbox').attr('title')).css({'color':'#999'}).focus(function(){
			if($(this).val() == $(this).attr('title')) $(this).val('').css({'color':'black'});
		}).blur(function(){
			if($(this).val() == "") $(this).val($(this).attr('title')).css({'color':'#999'});
		});
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

	// Javascript for results thumbnails
	$(".observation-results li").each(function(index) {
		var d = $(this).find('time').attr('datetime');
		var r = relative_time_short(new Date(d));
		$(this).find('.thumbnail a').after('<a href="" class="more-info-hint" id="more-info-hint-'+index+'" title="Quick info"><time datetime="'+d+'">'+r+'</time></a>')

		$("#more-info-hint-"+index).fadeIn(1000).bind('click',{idx:index,img:$(this).find('img').attr('src'),link:$(this).find('a').attr('href'),observer:$(this).find('.observer').attr('title')},function(event){
			if($('.show-details').size() == 0) $('body').append('<div class="show-details"></div>');
			var img = event.data.img.replace("_120.jpg","_150.jpg");
			var img_full = event.data.img.replace("_120.jpg",".jpg");
			$('.show-details').html('<div class="show-details-close">&times;</div><a href="'+event.data.link+'" title="Click for full size version"><img src="'+img+'" style="width:150px;height:150px;" /></a>'+$('.observation-results li .more-info').eq(event.data.idx).html()+'<div class="observer">Observer: <a href="'+$('a.observer').eq(event.data.idx).attr('href')+'">'+event.data.observer+'</a></div>');
			centreDiv('.show-details');
			if ($('.show-details').is(':visible')) $('.show-details').fadeOut("fast");
			else $('.show-details').fadeIn("fast");
			$('.show-details-close').bind("click",function(){
				$('.show-details').fadeOut("slow");
			});
			return false;
		})
	});

	function updateTime(el){
		var attr = (el.attr('datetime')) ? el.attr('datetime') : el.attr('title');
		if(!attr) return;
		var d = new Date(attr);
		if(d) el.html(relative_time_short(d));
	}
	function updateTimes(el){
		if(typeof el!=="object") el = $('.more-info-hint time');
		el.each(function(i){ updateTime($(this)); });
	}
	ticker = setInterval(updateTimes,30000);

	$(".observation-results li .observer").each(function(){
		var html = $(this).html()
		if(html.length > 13) $(this).html(html.substring(0,11)+"...");
	});
	$(".observation-results li .title").each(function(){
		var html = $(this).html()
		if(html.length > 17) $(this).html(html.substring(0,15)+"...");
	});


});

function imageLoadError(el){
	$(el).each(function(){
			// Work	around for error function reporting of file load failure
			this.src = this.src;
			$(this).bind('error',function() {
				this.src = "http://lcogt.net/files/no-image_120.png";
				this.alt = "Image unavailable";
				this.onerror = "";
				return true;
			})
	});
}

centreDiv = function(el){
	var wide = $(window).width();
	var tall = $(window).height();
	$(el).css({left:(wide-$(el).outerWidth())/2,top:($(window).scrollTop()+(tall-$(el).outerHeight())/2)});
}

// pd = parsed date
function relative_time_short(pd) {
	var relative_to = (arguments.length > 1) ? arguments[1] : new Date();
	var dt = parseInt((relative_to.getTime() - pd) / 1000);
	if (dt < 60) return 'seconds ago';
	else if(dt < 120) return 'a minute ago';
	else if(dt < (45*60)) return (parseInt(dt / 60)).toString() + ' minutes ago';
	else if(dt < (90*60)) return 'an hour ago';
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