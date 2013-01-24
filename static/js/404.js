$(document).ready(function(){
	fourOfour({'about':'http://rti.lcogt.net/observations/2011/10/10/process-2174-1.jpg','thumb':'http://rti.lcogt.net/observations/2011/10/10/process-2174-1_120.jpg'}, 'http://lcogt.net/observations/search?query=NGC+404', { 'about' : '', 'label': ''});
	$.ajax({
		url: "http://lcogt.net/observations/search.json?query=NGC+404&filter=RGB",
		dataType: "jsonp",
		success: function(data){
			if(data == null) return;
			if(typeof data.observation==="object" && !data.observation.length) data.observation = [data.observation];
			if(data.observation.length > 0){
				fourOfour(data.observation[0].image, data.observation[0].about, data.observation[0].observer);
			}
		}
	});
	$(window).resize(function(){
		four0fourResize();
	});
});
function four0fourResize(){
	//$('#main').css({'min-height':($('#main').outerWidth()*0.8 + $('#navigation').closest('.row').outerHeight())+"px","background-position":"0 "+$('#navigation').closest('.row').outerHeight()+"px"});
	var nh = $('#navigation').closest('.row').outerHeight();
	var h = $('#main').outerWidth()*0.8 + nh;
	$('#main').css({'min-height':parseInt(h)+"px","background-position":"0 "+($(window).width() > 400 ? "center" : nh+"px")});
}
function fourOfour(img,url,observer){
	$('#main').css({ "background":"url('"+($(window).width() > 400 ? img.about : img.thumb)+"')","background-size": "100% auto" });
	if($('.404msg').length == 0) $('.rowfirst p').append('<span class="404msg"></span>');
	$('.404msg').html(' Meanwhile, here\'s an observation of <a href="http://lcogt.net/observations/search?query=NGC+404" class="404link">NGC 404</a> taken by <a href="'+observer.about+'">'+observer.label+'</a> using our network.');
	$('a.404link').attr('href',url);
	$('#main, h1').css({'color':'white'});
	$('.404msg a').css({'color':'#dee8ff'});
	four0fourResize();
}