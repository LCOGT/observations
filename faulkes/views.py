# Create your views here.

from wis.models import Registrations, Schooluri
from faulkes.models import Site, Telescope, Filter, Imagearchive, ObservationStats
from django.utils.encoding import smart_unicode
from django.core import serializers
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.core import urlresolvers
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.admin.models import LogEntry, CHANGE
from datetime import date,timedelta,datetime
from string import replace
from django.utils import simplejson
from email.utils import parsedate_tz
import re
import math
import urllib2

n_per_line = 6
n_per_page = 30
base_url = "http://lcogt.net/observations/"
categorylookup = { '1': 'Planets',
				'1.1':'Planets (Type)',
				'1.1.1':'Terrestrial Planets',
				'1.1.2':'Gas Giant Planets',
				'1.2':'Planets (Feature)',
				'1.2.1':'Planet Surfaces',
				'1.2.1.1':'Mountains',
				'1.2.1.2':'Canyons',
				'1.2.1.3':'Volcanic Surfaces',
				'1.2.1.4':'Surface Impacts',
				'1.2.1.5':'Surface Erosion',
				'1.2.1.6':'Surface Liquid',
				'1.2.1.7':'Surface Ice',
				'1.2.2':'Planetary Atmospheres',
				'1.2.2.1':'Atmospheric Clouds',
				'1.2.2.2':'Storms',
				'1.2.2.3':'Atmospheric Belts',
				'1.2.2.4':'Aurorae',
				'1.3':'Planets (Special Cases)',
				'1.3.1':'Transiting Planets',
				'1.3.2':'Hot Jupiters',
				'1.3.3':'Pulsar Planets',
				'1.4':'Satellites',
				'1.4.1':'Satellites (Feature)',
				'1.4.1.1':'Satellite Surfaces',
				'1.4.1.1.1': 'Mountain',
				'1.4.1.1.2': 'Canyon',
				'1.4.1.1.3': 'Volcanic',
				'1.4.1.1.4': 'Impact',
				'1.4.1.1.5': 'Erosion',
				'1.4.1.1.6': 'Liquid',
				'1.4.1.1.7': 'Ice',
				'1.4.1.2':'Satellite Atmospheres',
				'2': 'Interplanetary Bodies',
				'2.1':'Dwarf Planets',
				'2.2':'Comets',
				'2.2.1':'Comet Nuclei',
				'2.2.2':'Comet Coma',
				'2.2.3':'Comet Tails',
				'2.2.3.1':'Comets (Dust)',
				'2.2.3.2':'Comets (Gas)',
				'2.3':'Asteroids',
				'2.4':'Meteoroids',
				'3': 'Stars',
				'3.1':'Stars (Evolutionary Stage)',
				'3.1.1':'Protostar',
				'3.1.2':'Young Stellar Object',
				'3.1.3':'Main Sequence Star',
				'3.1.4':'Red Giants',
				'3.1.5':'Red Supergiants',
				'3.1.6':'Blue Supergiants',
				'3.1.7':'White Dwarf Stars',
				'3.1.8':'Supernovae',
				'3.1.9':'Neutron Stars',
				'3.1.9.1':'Pulsars',
				'3.1.9.2':'Magnetars',
				'3.1.10':'Black Holes',
				'3.2':'Stars (Type)',
				'3.2.1':'Variable Stars',
				'3.2.1.1':'Pulsating Stars',
				'3.2.1.2':'Irregular Stars',
				'3.2.1.3':'Eclipsing Stars',
				'3.2.1.4':'Flare Stars',
				'3.2.1.5':'Novae',
				'3.2.1.6':'X-Ray Binaries (Star)',
				'3.3':'Stars with Spectral Types',
				'3.3.1':'O Stars',
				'3.3.2':'B Stars',
				'3.3.3':'A Stars',
				'3.3.4':'F Stars',
				'3.3.5':'G Stars',
				'3.3.6':'K Stars',
				'3.3.7':'M Stars',
				'3.3.8':'L Stars',
				'3.3.9':'T Stars',
				'3.4':'Stellar Populations',
				'3.4.1':'Population I Stars',
				'3.4.2':'Population II Stars',
				'3.4.3':'Population III Stars',
				'3.5':'Stellar feature',
				'3.5.1':'Photosphere',
				'3.5.1.1':'Granulation',
				'3.5.1.2':'Sunspot',
				'3.5.2':'Chromosphere',
				'3.5.2.1':'Flare',
				'3.5.2.2':'Facula',
				'3.5.3':'Corona',
				'3.5.3.1':'Prominence',
				'3.6': 'Group of Stars',
				'3.6.1':'Binary Stars',
				'3.6.2':'Triple Stars',
				'3.6.3': 'Multiple Stars',
				'3.6.4': 'Clusters of Stars',
				'3.6.4.1':'Open Clusters',
				'3.6.4.2':'Globular Clusters',
				'3.7':'Circumstellar Material',
				'3.7.1':'Planetary Systems',
				'3.7.2':'Disks',
				'3.7.2.1':'Protoplanetary Disks',
				'3.7.2.2':'Accretion Disks',
				'3.7.2.3':'Debris Disks',
				'3.7.3':'Outflows',
				'3.7.3.1':'Solar Winds',
				'3.7.3.2':'Coronal Mass Ejection',
				'4': 'Nebulae',
				'4.1': 'Nebulae (Type)',
				'4.1.1': 'Interstellar Medium',
				'4.1.2': 'Star Formation',
				'4.1.3': 'Planetary Nebulae',
				'4.1.4': 'Supernova Remnants',
				'4.1.5': 'Jets',
				'4.2': 'Nebulae (Appearance)',
				'4.2.1': 'Emission Nebulae',
				'4.2.1.1':'H II Regions',
				'4.2.2': 'Reflection Nebulae',
				'4.2.2.1':'Light Echo',
				'4.2.3': 'Dark Nebulae',
				'4.2.3.1':'Molecular Clouds',
				'4.2.3.2':'Bok Globules',
				'4.2.3.3':'Proplyds',
				'5': 'Galaxies',
				'5.1':'Galaxies (Type)',
				'5.1.1':'Spiral Galaxies',
				'5.1.2':'Barred Galaxies',
				'5.1.3':'Lenticular Galaxies',
				'5.1.4':'Elliptical Galaxies',
				'5.1.5':'Ring Galaxies',
				'5.1.6':'Irregular Galaxies',
				'5.1.7':'Interacting Galaxies',
				'5.2':'Galaxies (Size)',
				'5.2.1':'Giant Galaxies',
				'5.2.2':'Dwarf Galaxies',
				'5.3':'Galaxies (Activity)',
				'5.3.1':'Galaxies with normal activity',
				'5.3.2':'AGN',
				'5.3.2.1':'Quasars',
				'5.3.2.2':'Seyfert Galaxies',
				'5.3.2.3':'Blazars',
				'5.3.2.4':'Liner Galaxies',
				'5.3.3':'Starburst Galaxies',
				'5.3.4':'Ultraluminous Galaxies',
				'5.4':'Galaxies (Component)',
				'5.4.1':'Bulges',
				'5.4.2':'Bars',
				'5.4.3':'Disks', 
				'5.4.4':'Halos', 
				'5.4.5':'Rings', 
				'5.4.6':'Central Black Holes',
				'5.4.7':'Spiral Arms',
				'5.4.8':'Dust Lanes',
				'5.4.9':'Center Cores',
				'5.5':'Galaxies (Grouping)',
				'5.5.1':'Pair of Galaxies',
				'5.5.2':'Multiple Galaxies',
				'5.5.3':'Galaxy Clusters',
				'5.5.4':'Galaxy Superclusters',
				'6':'Cosmology',
				'6.1':'Cosmology (Morphology)',
				'6.1.1':'Deep Field',
				'6.1.2':'Large-scale Structure',
				'6.1.3':'Cosmic Background',
				'6.2':'Cosmology (Phenomenon)',
				'6.2.2':'Gamma Ray Burst',
				'6.2.3':'Dark Matter',
				'7':'Sky Phenomenon',
				'7.1':'Night Sky',
				'7.1.1':'Constellations',
				'7.1.2':'Asterisms',
				'7.1.3':'Milky Way',
				'7.1.4':'Trails',
				'7.1.4.1':'Meteor Trails',
				'7.1.4.2':'Star Trails',
				'7.1.4.3':'Satellite Trails',
				'7.1.5':'Zodiacal Light',
				'7.1.5.1':'Gegenschein',
				'7.1.5.2':'Night glow',
				}
categories = [
			{ 'link': "planets", 'name': 'Planets', 'avm':1 },
			{ 'link':"interplanetarybodies", 'name': 'Interplanetary Bodies', 'avm':2 },
			{ 'link': "stars", 'name': 'Stars', 'avm':3 },
			{ 'link': "nebulae", 'name': 'Nebulae', 'avm':4},
			{ 'link': "galaxies", 'name': 'Galaxies', 'avm':5 },
			{ 'link': "cosmology", 'name': 'Cosmology', 'avm':6 },
			{ 'link': "sky", 'name': 'Sky Phenomenon', 'avm':7 }]

def index(request):

	sites = Site.objects.all()
	telescopes = Telescope.objects.all()

	obs = Imagearchive.objects.using('faulkes').all().order_by('-whentaken')[:n_per_line]
	latest = build_observations(obs)

	obstats = ObservationStats.objects.all().order_by('-weight')[:n_per_line]
	obs = []
	for o in obstats:
		obs.append(o.imagearchive)
	trending = build_observations(obs)


	obstats = ObservationStats.objects.all().order_by('-views')[:n_per_line]
	obs = []
	for o in obstats:
		obs.append(o.imagearchive)
	popular = build_observations(obs)

	return render_to_response('faulkes/index.html', {'latest':latest,'trending':trending,'popular':popular,'sites':sites,'telescopes':telescopes,'categories':categories}, context_instance=RequestContext(request))
#	return HttpResponseRedirect("../../../")


def view_group(request,mode):
	input = input_params(request)

	sites = Site.objects.all()
	
	if(mode == "recent"):
		try:
			dup = request.GET.get('noduplicates','')
		except:
			dup = '';

		if(dup==''):
			obs = Imagearchive.objects.using('faulkes').order_by('-whentaken')[:n_per_page]
		else:
			obs = Imagearchive.objects.using('faulkes').extra(order_by=['-whentaken'])
			obs.query.group_by = ['schoolid']
			obs = obs[:n_per_page]

		n = obs.count()
		obs = build_observations(obs)
		input['title'] = "Recent Observations from LCOGT"
		input['link'] = 'recent'
		input['live'] = 300
		input['description'] = 'Recent observations from the Las Cumbres Observatory Global Telescope'
	elif(mode=="popular"):
		obstats = ObservationStats.objects.all().order_by('-views')[:n_per_page]
		n = obstats.count()
		obs = []
		for o in obstats:
			obs.append(o.imagearchive)
		obs = build_observations(obs)
		input['title'] = "All-time Most Viewed Observations at LCOGT"
		input['link'] = 'popular'
		input['description'] = 'Most popular observations from the Las Cumbres Observatory Global Telescope'
	elif(mode=="trending"):
		obstats = ObservationStats.objects.all().order_by('-weight')[:n_per_page]
		n = obstats.count()
		obs = []
		for o in obstats:
			obs.append(o.imagearchive)
		obs = build_observations(obs)
		input['title'] = "Trending Observations at LCOGT"
		input['link'] = 'trending'	
		input['description'] = 'Trending observations from the Las Cumbres Observatory Global Telescope'


	input['observations'] = len(obs)
	input['perpage'] = n_per_page

	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		data = {'input':input,'link':input['link'],'obs':obs,'n':len(obs)}
		if input['slideshow']:
			return render_to_response('faulkes/slideshow.html', data,context_instance=RequestContext(request))
		else:
			return render_to_response('faulkes/group.html', data,context_instance=RequestContext(request))


def since(request):
	since = request.GET.get('since','')
	if since != '':
		try:
			sd = parsedate_tz(since)
			sd = "%s%02d%02d%02d%02d%02d" % (sd[0],sd[1],sd[2],sd[3],sd[4],sd[5])
		except:
			sd = ''
	return sd


def search(request):
	input = input_params(request)
	telescopes = Telescope.objects.all()
	now = datetime.now()
	years = range(2004,now.year+1)
	months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
	days = range(1,32)
	ago = now + timedelta(-30)
	form = {'query':request.GET.get('query',''),'category':int(request.GET.get('category',0)),'avm':request.GET.get('avm',''),'daterange':request.GET.get('daterange','all'),'sday':int(request.GET.get('sday',ago.day)),'smon':int(request.GET.get('smon',ago.month)),'syear':int(request.GET.get('syear',ago.year)),'eday':int(request.GET.get('eday',now.day)),'emon':int(request.GET.get('emon',now.month)),'eyear':int(request.GET.get('eyear',now.year)),'telid':int(request.GET.get('telid',0)),'filter':request.GET.get('filter','A'),'user':request.GET.get('user',''),'SR':request.GET.get('SR',''),'RA':request.GET.get('RA',''),'DEC':request.GET.get('DEC',''),'exposure':request.GET.get('exposure',''),'exposurecondition':request.GET.get('exposurecondition','eq'),'expmin':request.GET.get('expmin',''),'expmax':request.GET.get('expmax',''),'since':request.GET.get('since','')}
	obs = []
	if re.search('e.g.',form['query']):
		form['query'] = ''
	

	obs = []
	n = -1
	if input['query']:
		obs = Imagearchive.objects.all()
		if form['query'] != "":
			obs = obs.filter(skyobjectname__iregex=r'(^| )%s([^\w0-9]+|$)' % form['query'])
		if form['telid'] != 0:
			obs = obs.filter(telescopeid=form['telid'])
		if form['filter'] != 'A':
			obs = obs.filter(filter=form['filter'])
		if form['daterange'] != 'all':
			sd = "%s%02d%02d000000" % (form['syear'],form['smon'],form['sday'])
			ed = "%s%02d%02d235959" % (form['eyear'],form['emon'],form['eday'])
			obs = obs.filter(whentaken__gte=sd,whentaken__lte=ed)
		if form['since'] != '':
			sd = since(request)
			if sd != '':
				obs = obs.filter(whentaken__gt=sd)
		if form['user'] != '':
			schools = Registrations.objects.filter(schoolname__icontains=form['user']).values_list('schoolloginname',flat=True)
			obs = obs.filter(schoolloginname__in=list(schools))
		if form['avm']!='':
			avmtemp = re.sub(r"\.","\\.",form['avm'])
			obs = obs.filter(observationstats__avmcode__regex=r'(^|;)%s' % avmtemp)
		else:
			if form['category'] > 0:
				avm = "%s" % form['category']
				obs = obs.filter(observationstats__avmcode__startswith=avm)
		if form['expmin'] != '':
			try:
				form['expmin'] = float(form['expmin'])
				obs = obs.filter(exposuresecs__gt=form['expmin'])
			except:
				form['expmin'] = 0
		if form['expmax'] != '':
			try:
				form['expmax'] = float(form['expmax'])
				obs = obs.filter(exposuresecs__lte=form['expmax'])
			except:
				form['expmax'] = 0

		if form['exposure'] != '':
			try:
				form['exposure'] = float(form['exposure'])
				if(form['exposurecondition']=='gt'):
					obs = obs.filter(exposuresecs__gt=form['exposure'])
				elif(form['exposurecondition']=='lt'):
					obs = obs.filter(exposuresecs__lt=form['exposure'])
				else:
					obs = obs.filter(exposuresecs=form['exposure'])
			except:
				form['exposure'] = 0;

		# Cone search
		if form['SR']!='' and form['RA']!='' and form['DEC']!='':

			try:
				form['SR'] = float(form['SR'])
			except:
				return broken(request,"There was a problem with the search radius you entered. Please make sure that it is provided in decimal degrees.")

			srlimit = 10

			if form['SR'] > srlimit:
				form['SR'] = srlimit

			if form['RA'].find(':') > 0:
				try:
					ra = hexangletodec(form['RA'])*15
				except:
					return broken(request,"There was a problem with the format of the Right Ascension that you entered. Please make sure you either enter the Right Ascension as a decimal number of hours or in the format hh:mm:ss.s.")
			else:
				try:
					ra = float(form['RA'])
				except:
					return broken(request,"There was a problem with the format of the Right Ascension that you entered. It doesn't appear to be a number. Please make sure you either enter the Right Ascension as a decimal number of hours or in the format hh:mm:ss.s.")

			if form['DEC'].find(':') > 0:
				try:
					dec = hexangletodec(form['DEC'])
				except:
					return broken(request,"There was a problem with the format of the declination that you entered. Please make sure you either enter the declination as decimal degrees or in the format dd:mm:ss.s.")
			else:
				try:
					dec = float(form['DEC'])
				except:
					return broken(request,"There was a problem with the format of the declination that you entered. Please make sure you either enter the declination as decimal degrees or in the format dd:mm:ss.s.")

			keepers = []
			cosr = math.cos(math.radians(form['SR']))
			i = 0

			obs = obs.order_by('raval')

			dec1 = math.radians(dec);
			ra1 = math.radians(ra)

			if dec >= 90-srlimit:
				obs = obs.filter(decval__gte=dec-form['SR'])
			elif dec <= -90+srlimit:
				obs = obs.filter(decval__lte=dec+form['SR'])
			else:
				obs = obs.filter(decval__gte=dec-form['SR'],decval__lte=dec+form['SR'])

			for o in obs:
				# Declination separation in degrees
				dDec = math.fabs(o.decval-dec)
				if dDec < form['SR']:
					i = i+1
					ra2 = math.radians(o.raval*15);
					dec2 = math.radians(o.decval)
					dRA = (ra1-ra2)
					cosd = math.fabs(math.sin(dec1)*math.sin(dec2) + math.cos(dec1)*math.cos(dec2)*math.cos(dRA))
					#print i
					if cosd > cosr:
						keepers.append(o.imageid)

			#print keepers
			obs = obs.filter(imageid__in=keepers)

		obs = obs.order_by('-whentaken')

		n = obs.count()

	input['observations'] = n
	input['title'] = "Search Results"
	input['link'] = 'search'
	input['linkquery'] = input['query']
	input['form'] = form
	input['description'] = 'Search results (LCOGT)'
	input['perpage'] = n_per_page
	input['pager'] = build_pager(request,n)
	

	if(n > n_per_page):
		obs = build_observations(obs[input['pager']['start']:input['pager']['end']])
	else:
		obs = build_observations(obs)


	# If they searched for a phrase we will guess what category these observations fit into
	input['avmcode'] = "";
	if(form['query'] != ""):
		prev = "            ";
		# Find shorted AVM code
		for o in obs:
			if(o['avmcode'] and len(o['avmcode']) < len(prev)):
				input['avmcode'] = o['avmcode']
				prev = o['avmcode']
		input['avmcode'] = re.sub(r"\;(.*)$",'',input['avmcode'])
		# If we are at the 4th level we'll step back up to 3rd
		input['avmcode'] = re.sub(r"(\.[0-9]\.[0-9])\.[0-9]$",r"\1",input['avmcode'])
		if(input['avmcode']!=""):
			try:
				input['avmname'] = categorylookup[input['avmcode']]
			except:
				input['avmname'] = "";


	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		if input['slideshow']:
			return render_to_response('faulkes/slideshow.html', {'input':input,'obs':obs,'n':n,'link':input['link']},context_instance=RequestContext(request))
		else:
			return render_to_response('faulkes/search.html', {'input':input,'obs':obs,'categorylookup':categorylookup,'n':n,'filters':filter_list(),'link':input['link'],'pager':input['pager']['html'],'form':form,'telescopes':telescopes,'conditions':[{'value':'gt','text':'greater than'},{'value':'lt','text':'less than'},{'value':'eq','text':'equals'}],'years':years,'months':months,'days':days,'categories':categories},context_instance=RequestContext(request))



def view_site(request,code):
	input = input_params(request)
	sites = Site.objects.exclude(code=code)

	try:
		site = Site.objects.get(code=code)
	except ObjectDoesNotExist:
		return unknown(request)
	
	telescopes = Telescope.objects.filter(site=site)

	obs = []
	n = 0
	if site.code == 'ogg' or site.code == 'coj':
		obs = Imagearchive.objects.filter(telescopeid__in=telescopes.values_list('id',flat=True)).order_by('-whentaken')
		n = obs.count()


	input['observations'] = n
	input['title'] = site.name
	input['link'] = site.code
	input['description'] = 'Observations from telescopes at '+site.name+' (LCOGT)'
	input['perpage'] = n_per_page
	input['pager'] = build_pager(request,n)

	if(n > n_per_page):
		obs = build_observations(obs[input['pager']['start']:input['pager']['end']])
	else:
		obs = build_observations(obs)


	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		data = {'sites':sites,'site':site,'telescopes':telescopes,'n':n,'obs':obs,'input':input,'link':input['link'],'pager':input['pager']['html']}
		if input['slideshow']:
			return render_to_response('faulkes/slideshow.html', data,context_instance=RequestContext(request))
		else:
			return render_to_response('faulkes/site.html', data,context_instance=RequestContext(request))


def view_telescope(request,code,tel):
	input = input_params(request)

	sites = Site.objects.exclude(code=code)
	site = Site.objects.get(code=code)
	try:
		telescope = Telescope.objects.get(site=site,code=tel)
	except ObjectDoesNotExist:
		return unknown(request)

	telescopes = Telescope.objects.filter(site=site).exclude(code=tel)

	obs = []
	n =  0
	if site.code == 'ogg' or site.code == 'coj':
		obs = Imagearchive.objects.filter(telescopeid=telescope.id).order_by('-whentaken')
		n = obs.count()


	input['observations'] = n
	input['title'] = telescope.name
	input['link'] = site.code+'/'+telescope.code
	input['description'] = 'Observations from '+telescope.name+' (LCOGT)'
	input['perpage'] = n_per_page
	input['pager'] = build_pager(request,n)

	if(n > n_per_page):
		obs = build_observations(obs[input['pager']['start']:input['pager']['end']])
	else:
		obs = build_observations(obs)


	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		data = {'telescope': telescope,'sites':sites,'telescopes':telescopes,'n':n,'obs':obs,'input':input,'link':input['link'],'pager':input['pager']['html']}
		if input['slideshow']:
			return render_to_response('faulkes/slideshow.html', data,context_instance=RequestContext(request))
		else:
			return render_to_response('faulkes/telescope.html', data,context_instance=RequestContext(request))


def view_object(request,object):
	input = input_params(request)

	# Remove trailing full-stop
	object = re.sub(r"\.json$","",object)
	object = re.sub(r"\.kml$","",object)
	original = object
	object = object.replace('+', ' ')

	page = int(request.GET.get('page','1'))
	try:
		avmcode = int(request.GET.get('avm',0)[0])	# Only allow the major category to be provided by the user. Should distinguish Jupiter from Ghost of Jupiter
	except:
		avmcode = ''

	# On the first page (HTML version only) we do a lookUP
	if page == 1 and input['doctype'] == "html":
		opener = urllib2.build_opener()
		opener.addheaders = [('Accept', 'application/xml'),
							('Content-Type', 'application/xml'),
							('User-Agent', 'LCOGT/1.0')]
		req = urllib2.Request(url='http://www.strudel.org.uk/lookUP/xml/?name=%s' % original)
		# Allow 3 seconds for timeout
		try:
			f = urllib2.urlopen(req,None,5)
			xml = f.read()
		except:
			return unknown(request)
		service = re.search('service href="([^\"]*)">([^\<]*)<',xml)
		if type(service) == 'NoneType':
			return unknown(request)
		try:
			service = {'name':service.group(2),'url':service.group(1) }
		except:
			return unknown(request)
		raval = re.search('<ra ([^\>]*)>([^\<]*)<',xml)
		if type(raval) == 'NoneType':
			raval = ""
		try:
			raval = float(raval.group(2))
		except:
			raval = 0.0
		decval = re.search('<dec ([^\>]*)>([^\<]*)<',xml)
		if type(decval) == 'NoneType':
			decval = ""
		try:
			decval = float(decval.group(2))
		except:
			decval = 0.0
		if avmcode == '' or avmcode < 1 or avmcode > 7:
			m = re.search('avmcode="([^\"]*)"',xml)
			try:
				avmcode = m.group(1)
				if len(avmcode) > 0:
					cats = avmcode.split(';')
					if len(cats) > 0:
						avmcode = cats[-1]
						if avmcode in categorylookup:
							avm = categorylookup[avmcode]
						else:
							avm = avmcode
					else:
						avm = "Unknown"
						avmcode = ""
				else:
					avm = "Unknown"
					avmcode = ""
			except:
				avm = "Unknown"
				avmcode = ""
		else:
			try:
				avmcode = str(avmcode)
				avm = categorylookup[avmcode]
			except:
				avm = "Unknown"
				avmcode = ""
		object = {'name':object,'raval':raval,'decval':decval,'service':service,'avm':{'name':avm,'code':avmcode}}
	else:
		try:
			avmcode = str(avmcode)
			avm = categorylookup[avmcode]
		except:
			avm = "Unknown"
			avmcode = ""
		object = {'name':object,'avm':{'name':avm,'code':avmcode}}

	try:
		obser = Imagearchive.objects.all().filter(skyobjectname__iregex=r'(^| )%s([^\w0-9]+|$)' % object['name']).order_by('-whentaken')
		# If we have an AVM code we can use it to limit to objects of the correct type
		if object['avm']['code'] != "":
			obser = obser.filter(observationstats__avmcode__regex=r'(^|;)%s' % object['avm']['code'])
		a = obser.values('schoolid').annotate(count=Count('schoolid')).order_by('-count')
		if a:
			try:
				u = Registrations.objects.get(schoolid=a[0]['schoolid'])
			except ObjectDoesNotExist:
				u = ""
			input['mostobservedby'] = {'name':u,'id':a[0]['schoolid'],'count':a[0]['count']}
		else:
			u = ""

	except ObjectDoesNotExist:
		return unknown(request)
	
	
	n = obser.count()

	input['observations'] = n
	input['title'] = object['name']
	input['link'] = 'object/'+original
	input['description'] = 'Observations of '+object['name']+' (LCOGT)'
	input['perpage'] = n_per_page
	input['pager'] = build_pager(request,n,object['avm']['code'])
		
	if(n > n_per_page):
		obs = build_observations(obser[input['pager']['start']:input['pager']['end']])
	else:
		obs = build_observations(obser)

	if page == 1:
		# Bin the observations by month for the past year
		input = binMonths(obser,input,12)

		b = [0,1,2,3,4]
		# Calculate how many in each bin
		ns = [{'label':'Under 1 second','max':1,'observations':0},{'label':'1-10 seconds','min':1,'max':10,'observations':0},{'label':'10-30 seconds','min':10,'max':30,'observations':0},{'label':'30-90 seconds','min':30,'max':90,'observations':0},{'label':'Over 90 seconds','min':90,'observations':0}]
		obser = obser.filter(exposuresecs__gt=1)
		b[0] = n-len(obser);
		obser = obser.filter(exposuresecs__gt=10)
		b[1] = n-b[0]-len(obser)
		obser = obser.filter(exposuresecs__gt=30)
		b[2] = n-b[0]-b[1]-len(obser)
		obser = obser.filter(exposuresecs__gt=90)
		b[3] = n-b[0]-b[1]-b[2]-len(obser)
		b[4] = len(obser)

		for i in range(5):
			ns[i]['observations'] = b[i]

		input['exposure'] = ns
		input['exposuremax'] = max(b)
	else:
		ns = []

	uri = ""
	mostrecent = ""


	if len(obs) > 0:
		mostrecent = relativetime(obs[0]['whentaken'])

	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		data = {'n':n,'input':input,'object':object,'mostrecent':mostrecent,'obs':obs,'link':input['link'],'pager':input['pager']['html'],'uri':uri}
		if input['slideshow']:
			return render_to_response('faulkes/slideshow.html', data,context_instance=RequestContext(request))
		else:
			return render_to_response('faulkes/object.html', data,context_instance=RequestContext(request))


def view_user(request,userid):
	input = input_params(request)

	try:
		u = Registrations.objects.get(schoolid=userid)
	except ObjectDoesNotExist:
		return unknown(request)
	
	#s = Registrations.objects.filter(schoolid=userid)#.values('usertype').annotate(Count(tot='schoolid')).order_by('-schoolid__count')
	#return HttpResponse(simplejson.dumps(s),mimetype='application/javascript')

	obs = Imagearchive.objects.filter(schoolid=userid).order_by('-whentaken')
	n = obs.count()


	input['observations'] = n
	input['title'] = u.schoolname
	input['link'] = 'user/'+userid
	input['description'] = 'Observations by '+u.schoolname+' (LCOGT)'
	input['perpage'] = n_per_page
	input['pager'] = build_pager(request,n)

	if int(request.GET.get('page','1')) == 1:
		# Bin the observations by month for the past year
		input = binMonths(obs,input,24)

	if(n > n_per_page):
		obs = build_observations(obs[input['pager']['start']:input['pager']['end']])
	else:
		obs = build_observations(obs)



	try:
		uri = Schooluri.objects.get(usr_id=u).uri
	except:
		uri = ""

	mostrecent = ""

	if len(obs) > 0:
		mostrecent = relativetime(obs[0]['whentaken'])

	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		data = {'input':input,'user': u.schoolname, 'userid' : userid,'n':n,'start':datestamp_basic(u.accountcreated),'mostrecent':mostrecent,'obs':obs,'link':input['link'],'pager':input['pager']['html'],'uri':uri}
		if input['slideshow']:
			return render_to_response('faulkes/slideshow.html', data,context_instance=RequestContext(request))
		else:
			return render_to_response('faulkes/user.html', data,context_instance=RequestContext(request))


def view_username(request,username):
	input = input_params(request)

	try:
		u = Registrations.objects.get(schoolloginname=username)
	except ObjectDoesNotExist:
		return unknown(request)
	
	obs = Imagearchive.objects.filter(schoolloginname=username).order_by('-whentaken')
	n = obs.count()

	input['observations'] = n
	input['title'] = u.schoolname
	input['link'] = 'user/'+username
	input['description'] = 'Observations by '+u.schoolname+' (LCOGT)'
	input['perpage'] = n_per_page
	input['pager'] = build_pager(request,n)

	if(n > n_per_page):
		obs = build_observations(obs[input['pager']['start']:input['pager']['end']])
	else:
		obs = build_observations(obs)

	try:
		uri = Schooluri.objects.get(usr_id=u).uri
	except:
		uri = ""

	mostrecent = ""

	if len(obs) > 0:
		mostrecent = relativetime(obs[0]['whentaken'])

	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		data = {'user': u.schoolname, 'userid' : u.schoolid,'n':n,'start':datestamp_basic(u.accountcreated),'mostrecent':mostrecent,'obs':obs,'link':input['link'],'pager':input['pager']['html'],'uri':uri}
		if input['slideshow']:
			return render_to_response('faulkes/slideshow.html', data,context_instance=RequestContext(request))
		else:
			return render_to_response('faulkes/user.html', data,context_instance=RequestContext(request))


def view_category_list(request):
	input = input_params(request)

	obs = []
	obs = build_observations(obs)

	if input['doctype'] == "html":
		data = {'categorylookup':categorylookup,'category':categories,'n':0,'obs':obs,'previous':'','next':''}
		return render_to_response('faulkes/categorylist.html', data,context_instance=RequestContext(request))
	else:
		return render_to_response('faulkes/404.html', data,context_instance=RequestContext(request))


def view_category(request,category):
	input = input_params(request)

	found = False
	avm = 0
	for c in categories:
		avm = avm + 1
		if c['link'] == category:
			found = True
			cat = c
			break

	if not(found):
		return unknown(request)

	n = 0
	try:
		obstats = ObservationStats.objects.filter(avmcode__startswith='%s' % avm).order_by('-imagearchive__whentaken')#.order_by('-views')
		n = obstats.count()
	except ObjectDoesNotExist:
		return unknown(request)

	input['observations'] = n
	input['title'] = 'Category: '+categories[avm-1]['name']
	input['link'] = 'category/'+categories[avm-1]['link']
	input['description'] = 'Category: '+categories[avm-1]['name']+' (LCOGT)'
	input['perpage'] = n_per_page
	input['pager'] = build_pager(request,n)


	# Work out the AVM categories above and below the current level
	input = getCategoryLevel(avm,input)

	if(n > n_per_page):
		obstats = obstats[input['pager']['start']:input['pager']['end']]

	obs = []
	for o in obstats:
		obs.append(o.imagearchive)

	obs = build_observations(obs)
	

	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		data = {'input':input,'categories':categories,'category':categories[avm-1]['name'],'n':n,'obs':obs,'link':input['link'],'pager':input['pager']['html']}
		if input['slideshow']:
			return render_to_response('faulkes/slideshow.html', data,context_instance=RequestContext(request))
		else:
			return render_to_response('faulkes/category.html', data,context_instance=RequestContext(request))




def view_avm(request,avm):
	input = input_params(request)

	# Remove trailing full-stop
	avm = re.sub(r"\.$","",avm)
	avmtemp = re.sub(r"\.","\\.",avm)

	n = 0
	obstats = ObservationStats.objects.filter(avmcode__regex=r'(^|;)%s' % avmtemp).order_by('-imagearchive__whentaken')#.order_by('-views')
	n = obstats.count()

	if avm in categorylookup:
		category = categorylookup[avm]
	else:
		category = avm

	input['observations'] = n
	input['title'] = 'Category: '+category
	input['link'] = 'category/'+avm
	input['description'] = 'Category: '+category+' (LCOGT)'
	input['perpage'] = n_per_page
	input['pager'] = build_pager(request,n)

	# Work out the AVM categories above and below the current level
	input = getCategoryLevel(avm,input)

	if(n > n_per_page):
		obstats = obstats[input['pager']['start']:input['pager']['end']]

	obs = []
	for o in obstats:
		obs.append(o.imagearchive)
	obs = build_observations(obs)


	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		data = {'input':input,'categories':categories,'category':category,'n':n,'obs':obs,'link':input['link'],'pager':input['pager']['html']}
		if input['slideshow']:
			return render_to_response('faulkes/slideshow.html', data,context_instance=RequestContext(request))
		else:
			return render_to_response('faulkes/category.html', data,context_instance=RequestContext(request))



def view_map(request):
	input = input_params(request)

	sites = Site.objects.all()
	telescopes = Telescope.objects.all()

	dt = datetime.utcnow() - timedelta(30)
	
	sites = Site.objects.all()
	telescopes = Telescope.objects.all()

	obs = Imagearchive.objects.filter(whentaken__gte=dt.strftime("%Y%m%d%H%M%S")).order_by('-whentaken')
	#print dt.strftime("%Y%m%d%H%M%S")
	n = obs.count()
		

	input['observations'] = 0
	input['title'] = 'Heat Map'
	input['link'] = 'map'
	input['description'] = 'Observations in the past month (LCOGT)'
	input['perpage'] = n_per_page
	input['pager'] = build_pager(request,n)

	ras = []
	dcs = []
	for o in obs:
		ras.append(round(o.raval*15*100)/100)
		dcs.append(round(o.decval*100)/100)

	if input['doctype'] == "json":
		return view_json(request,build_observations_json(obs),input)
	elif input['doctype'] == "kml":
		return view_kml(request,obs,input)
	elif input['doctype'] == "rss":
		return view_rss(request,obs,input)
	else:
		data = {'ras':ras,'dcs':dcs,'link':input['link'],'input':input,'sites':sites,'telescopes':telescopes}
		return render_to_response('faulkes/map.html', data,context_instance=RequestContext(request))



def view_observation(request,code,tel,obs):
	input = input_params(request)

	try:
		telescope = Telescope.objects.get(site=Site.objects.get(code=code),code=tel)
	except ObjectDoesNotExist:
		return unknown(request)

	try:
		obs = Imagearchive.objects.filter(imageid=obs)
	except:
		return broken(request,"There was a problem finding the requested observation in the database.")

	if len(obs) < 1:
		return broken(request,"There was a problem finding the requested observation in the database.")

	# Let's try to work out if this is from a crawler. If not we'll assume a real person.
	BotNames=['alexa', 'appie', 'Ask Jeeves', 'Baiduspider', 'bingbot', 'Butterfly', 'crawler', 'facebookexternalhit', 'FAST', 'Feedfetcher-Google', 'Firefly', 'froogle', 'Gigabot', 'girafabot', 'Googlebot', 'InfoSeek', 'inktomi', 'looksmart', 'Me.dium', 'Mediapartners-Google', 'msnbot', 'NationalDirectory', 'rabaz', 'Rankivabot', 'Scooter', 'Slurp', 'Sogou web spider', 'Spade', 'TechnoratiSnoop', 'TECNOSEEK', 'Teoma', 'TweetmemeBot', 'Twiceler', 'Twitturls', 'URL_Spider_SQL', 'WebAlta Crawler', 'WebBug', 'WebFindBot', 'www.galaxy.com', 'ZyBorg']
	request.is_crawler=False
	try:
		user_agent=request.META.get('HTTP_USER_AGENT',None)
		for botname in BotNames:
			if botname in user_agent:
				request.is_crawler=True
	except:
		user_agent = ''

	# Update stats
	obstats = ObservationStats.objects.filter(imagearchive=obs[0])
	if obstats:
		# Only update the number of views if it isn't a crawler
		if (request.is_crawler):
			addition = 0
		else:
			addition = 1
		obstats[0].views = obstats[0].views + addition
		views = obstats[0].views
		delta = datetime.utcnow()-obstats[0].lastviewed
		# 98 = 2*(7^2) <- where 7 days is the sigma for the Gaussian function exp(-datediff^2/(2*sigma^2))
		# 0.5 = 2*(0.5^2) <- where 0.5 days is the sigma for the Gaussian function
		#print obstats[0].weight*math.exp(-math.pow((delta.seconds)/86400.,2)/98.)
		obstats[0].weight = addition + obstats[0].weight*math.exp(-math.pow((delta.seconds)/86400.,2)/0.5)
		#print obstats[0].weight
		obstats[0].lastviewed = datetime.utcnow()
	else:
		obstats = [ObservationStats(imagearchive=obs[0],views = 1,weight = 1,lastviewed = datetime.utcnow())]
		views = 1
	obstats[0].save()

	obs = build_observations(obs)
	otherobs = get_observation_stream(obs[0])

	# Check for AVM code
	if not(obstats[0].avmcode):
		opener = urllib2.build_opener()
		opener.addheaders = [('Accept', 'application/xml'),
							('Content-Type', 'application/xml'),
							('User-Agent', 'LCOGT/1.0')]
		obj = re.sub(r" ",'\+',obs[0]['object'])
		req = urllib2.Request(url='http://www.strudel.org.uk/lookUP/xml/?name=%s' % obj)
		# Allow 3 seconds for timeout
		try:
			f = urllib2.urlopen(req,None,3)
			xml = f.read()
			m = re.search('avmcode="([^\"]*)"',xml)
			n = re.search('service href="([^\"]*)"',xml)
			if(m):
				try:
					obstats[0].avmcode = m.group(1)
				except ObjectDoesNotExist:
					obstats[0].avmcode = "0.0"
			else:
				obstats[0].avmcode = "0.0"
			if(n):
				obstats[0].moreurl = n.group(1)
			obstats[0].save()
		except:
			obstats[0].avmcode = "0"

	try:
		u = Registrations.objects.get(schoolid=obs[0]['schoolid'])
		tag = u.tag
	except:
		tag='0'

	obs[0]['views'] = views

	if(obstats[0].avmcode!="0" and obstats[0].avmcode!="0.0"):
		cats = obstats[0].avmcode.split(';')
		if len(cats) > 0:
			cats = cats[-1]
		obs[0]['avmcode'] = cats
		if cats in categorylookup:
			obs[0]['avmname'] = categorylookup[cats]
		else:
			obs[0]['avmname'] = obstats[0].avmcode


	if input['doctype'] == "kml":
		input['title'] = 'Observation of '+obs[0]['skyobjectname']
		return view_kml(request,obs,input)


	# Get FITS information only if not a crawler
	if (request.is_crawler):
		filters = []
	else:
		opener = urllib2.build_opener()
		url = 'http://sci-archive.lcogt.net/cgi-bin/oc_search?op-centre=%s&user-id=%s&date=%s&telescope=ft%s' % (tag,obs[0]['schoolloginname'],obs[0]['whentaken'][0:8],obs[0]['telescopeid'])
	
		rids = obs[0]['requestids'].split(',')
		filters = []
		if rids:
			if len(rids) == 3:
				ids = ['b','g','r']
				names = ['Blue','Green','Red']
				#filters = [{ 'id':'b','name': 'Blue','fits':'','img':'' },
				#			{ 'id':'g','name': 'Green','fits':'','img':'' },
				#			{ 'id':'r','name': 'Red','fits':'','img':'' }]
			if len(rids) == 1:
				ids = ['f']
				names = [obs[0]['filter']]
				#filters = [{ 'id':'f','name': obs[0]['filter'],'fits':'','img':'' }]
	
	
			for rid in range(0,len(rids)):
				req = urllib2.Request(url=url+'&obs-id=' + rids[rid])
	
				# Allow 6 seconds for timeout
				try:
					f = urllib2.urlopen(req,None,6)
					xml = f.read()

					jpg = re.search('file-jpg type=\"url\">([^\<]*)<',xml)
					fit = re.search('file-hfit type=\"url\">([^\<]*)<',xml)
					if jpg or fit:
						tmp = {'id':ids[rid],'name':names[rid],'fullname':filter_name(names[rid])}
						if jpg:
							tmp['img'] = jpg.group(1)
						if fit:
							tmp['fits'] = fit.group(1)
						filters.append(tmp)
				except:
					filters[0]['img'] = ""
					filters[0]['fits'] = ""

	obs[0]['filter'] = filter_link(obs[0]['filter'])

	if input['doctype'] == "json":
		#print obs
		return view_json(request,build_observations_json(obs),input)
	return render_to_response('faulkes/observation.html', {'n':1,'telescope': telescope,'obs':obs[0],'otherobs':otherobs,'filters':filters,'base':base_url},context_instance=RequestContext(request))


def get_observation_stream(obs):

	ob = Imagearchive.objects.filter(schoolid=obs['schoolid'])
	o = ob.values()
	num = len(o)

	n = 0
	# Find the index of the current image
	for index, item in enumerate(o):
		if(item['imageid'] == obs['imageid']):
			n = index
			break
	# Find the images in the user's stream to either side
	start = n-3
	end = start+6
	if end > num:
		end = num
	start = end-6
	if start < 0:
		start = 0
	o = build_observations(ob[start:end])

	num = end-start
	otherobs = []
	i = 0
	for item in reversed(o):
		tmp = {'url':item['link_obs'],'thumb':item['thumbnail'],'title':item['skyobjectname'],'date':datestamp(item['whentaken']),'class':''}
		if(i==0):
			tmp['class'] = 'left'
		if(i==num-1):
			tmp['class'] = 'right'
		if(item['imageid']==obs['imageid']):
			tmp['class'] = 'current'
		otherobs.append(tmp)
		i = i+1

	return otherobs



def input_params(request):
	doctype = "html"
	callback = ""
	slideshow = False;

	path = request.path_info.split('/')
	if path[len(path)-1] == "":
		path.pop()
	bits = path[len(path)-1].rsplit('.',1)

	if len(bits) > 1:
		doctype = bits[1]
		path[len(path)-1] = bits[0]

	mimetype = "text/html"

	# If the user has requested a particular mime type we'll use that
	#try:
	#	reqtype = request.META.get('CONTENT_TYPE', 'text/html')
	#	if reqtype == 'application/json':
	#		doctype = 'json'
	#	elif reqtype == 'application/vnd.google-earth.kml+xml':
	#		doctype = 'kml'
	#	elif reqtype == 'application/xml':
	#		doctype = 'rss'
	#	elif reqtype == 'application/rdf+xml':
	#		doctype = 'rdf'
	#	else:
	#		doctype = 'html'
	#except:
	#	reqtype = ''

	if doctype == 'json':
		callback = request.GET.get('callback','')
		# Sanitise the callback to stop any dodgy Javascript
		callback = re.sub(r"[^\w]",'',callback)
		mimetype = 'application/json'
	elif doctype == 'kml':
		mimetype = 'application/vnd.google-earth.kml+xml'
	elif doctype == 'rss':
		mimetype = 'application/xml'
	elif doctype == 'rdf':
		mimetype = 'application/rdf+xml'
		
	if path[len(path)-1] == "show":
		slideshow = True

	query = request.META.get('QUERY_STRING', '')
	

	return {'doctype':doctype,'mimetype':mimetype,'callback':callback,'path':path,'slideshow':slideshow,'query':query}


def getCategoryLevel(avm,input):

	# Work out the AVM categories above and below the current level
	input['avmup'] = []
	input['avmdn'] = []

	if(avm):
		avm = str(avm)
		avmup = avm
		if(re.search(r"\.",avmup)):
			while(re.search(r"\.",avmup)):
				avmup = re.sub(r"\.[0-9]$","",avmup)
				try:
					nm = categorylookup[avmup]
				except:
					nm = "";
				input['avmup'].insert(0,{'code':avmup,'name':nm})
		for c in categorylookup:
			if(re.match(avm,c)):
				print avm,c
			if(re.match(avm,c) and c != avm and len(c)==len(avm)+2):
				input['avmdn'].append({'code':c,'name':categorylookup[c]})

	return input



def build_observations(obs):

	observations = []

	if not(obs):
		return obs

	for ob in obs:
		o = {}

		try:
			o['user'] = Registrations.objects.get(schoolid=ob.schoolid)
		except:
			o['user'] = "Unknown"

		try:
			o['schoolname'] = o['user'].schoolname
		except:
			o['schoolname'] = "Unknown"

		try:
			obstats = ObservationStats.objects.filter(imagearchive=ob)
			if(obstats[0].avmcode!="0.0"):
				o['avmcode'] = obstats[0].avmcode
				cats = o['avmcode'].split(';')
				o['avmname'] = "";
				for (counter,c) in enumerate(cats):
					if counter > 0:
						o['avmname'] += ";"
					if c in categorylookup:
						o['avmname'] += categorylookup[c]
			else:
				o['avmcode'] = ""
			o['views'] = obstats[0].views
		except:
			o['avmcode'] = ""

		o['imageid'] = ob.imageid
		o['imagetype'] = ob.imagetype
		o['whentaken'] = ob.whentaken
		o['schoolid'] = ob.schoolid
		o['bestofimage'] = ob.bestofimage
		o['skyobjectname'] = ob.skyobjectname
		o['raval'] = ob.raval*15
		o['decval'] = ob.decval
		o['filter'] = ob.filter
		o['filterprops'] = filter_props(ob.filter)
		o['exposuresecs'] = ob.exposuresecs
		o['defaultexpsecs'] = ob.defaultexpsecs
		o['skyobjecttype'] = ob.skyobjecttype
		o['requestids'] = ob.requestids
		o['telescopeid'] = ob.telescopeid
		o['mosaicpatterncode'] = ob.mosaicpatterncode
		o['hasthumbnail'] = ob.hasthumbnail
		o['imagesequenceid'] = ob.imagesequenceid
		o['filename'] = ob.filename
		o['schoolloginname'] = ob.schoolloginname
		o['processingtype'] = ob.processingtype
		o['indexnames'] = ob.indexnames
		o['instrumentname'] = ob.instrumentname
		o['telescope'] = Telescope.objects.filter(id=int(o['telescopeid']))[0]
		o['fitsfiles'] = "";
		if o['filename'].startswith('NoImage'):
			o['fullimage_url'] = "http://lcogt.net/sites/default/themes/lcogt/images/missing_large.png"
			o['thumbnail'] = "http://lcogt.net/sites/default/themes/lcogt/images/missing.png"
		else:
			o['fullimage_url'] = "http://rti.lcogt.net/observations/%s/%s/%s/%s-%s.jpg" % (o['whentaken'][0:4],o['whentaken'][4:6],o['whentaken'][6:8],o['filename'][0:-4],o['telescopeid'])
			o['thumbnail'] = o['fullimage_url'][0:-4]+"_120.jpg"
		o['license'] = "http://creativecommons.org/licenses/by-nc/2.0/deed.en_US"
		o['licenseimage'] = 'cc-by-nc.png'
		o['credit'] = "Image taken with "+o['telescope'].name+" operated by Las Cumbres Observatory Global Telescope Network"
		# Change the credit if prior to 11 Oct 2005
		if int(o['whentaken']) < int("20051011000000"):
			o['credit'] = "Provided to Las Cumbres Observatory under license from the Dill Faulkes Educational Trust";
		o['userid'] = o['schoolid']
		o['link_obs'] = o['telescope'].site.code+"/"+o['telescope'].code+"/"+str(o['imageid']);
		o['link_site'] = o['telescope'].site.code;
		o['link_tel'] = o['link_site']+"/"+o['telescope'].code;
		o['link_user'] = "user/"+str(o['userid']);
		o['object'] = re.sub(r" ?\([^\)]*\)",'',o['skyobjectname'])	# Remove brackets
		o['object'] = re.sub(r"/\s\s+/", ' ', o['object'])		# Remove redundant whitespace
		o['object'] = re.sub(r"[^\w\-\+0-9 ]/i",'',o['object'])	# Remove non-useful characters

		if len(obs) > 0 and o['schoolid']:
			observations.append(o)
			

	return observations

# n = total number of observations
# page = the current page
def build_pager(request,n,avm=''):
	if(n < n_per_page):
		return { 'next': '','prev':'','html':'','page':0 }
	else:

		page = int(request.GET.get('page','1'))

		qstring = request.META.get('QUERY_STRING','')
		m = re.search('page=', qstring)
		if not(m):
			if qstring=='':
				qstring = 'page=1'
			else:
				qstring = qstring+'&page=1'

		if avm != '':
			m = re.search('avm=', qstring)
			if not(m):
				if qstring=='':
					qstring = 'avm=%s' % str(avm)
				else:
					qstring = qstring+'&avm=%s' % str(avm)
			qstring = re.sub(r"avm=[^\&]+",'avm=%s' % str(avm),qstring)

		start = 1
		if page > start+4:
			start = page-4
		final = int(math.ceil(n/n_per_page)+1)
		end = final + 1
		if end-start > 10:
			end = start + 10
		output = ""
		c = 0
		prev = re.sub(r"page=\d+",'page=%s' % (page-1),qstring)
		if page-1 < 1:
			prev = ''
		next = re.sub(r"page=\d+",'page=%s' % (page+1),qstring)
		if page+1 > final:
			next = ''

		for i in range(start,end):
			if c > 0:
				output = output + " "
			qstring = re.sub(r"page=\d+",'page=%s' % i,qstring)
			if(i==page):
				output = output+"<a href=\"?%s\" class=\"current\">%s</a> " % (qstring,i)
			else:
				output = output+"<a href=\"?%s\">%s</a> " % (qstring,i)
			c = c+1
		if start > 1:
			qstring = re.sub(r"page=\d+",'page=1',qstring)
			output = "<a href=\"?%s\">&laquo; first</a> ... %s" % (qstring,output)
		if end < final:
			qstring = re.sub(r"page=\d+",'page=%s' % int(final),qstring)
			output = output + "... <a href=\"?%s\">last &raquo;</a>" % qstring
		sobs = (page-1)*n_per_page
		eobs = sobs + n_per_page
		if eobs > n:
			eobs = n
		return { 'next':next,'prev':prev,'html':output,'start': sobs,'end':eobs,'page':page }


def build_observations_json(obs):
	if len(obs) > 1:
		observations = []
	elif len(obs) == 0:
		return ""

	for o in obs:
		if not('telescope' in o):
			tel = Telescope.objects.filter(id=o['telescopeid'])
			o['telescope'] = tel[0]

		o['fitsfiles'] = "";
		try:
			filter = filter_props(o['filter'])
		except:
			filter = ["Unknown"]
		ob = {
			"about" : base_url+o['link_obs'],
			"label" : o['skyobjectname'],
			"observer" : {
				"about" : base_url+o['link_user'],
				"label" : re.sub(r"\"",'',o['schoolname'])
			},
			"image" : {
				"about" : o['fullimage_url'],
				"label" : "Image",
				"fits" : o['fitsfiles'],
				"thumb" : o['thumbnail']
			},
			"ra" : o['raval'], 
			"dec" : o['decval'],
			"filter" :  {
				"name" : re.sub(r"\"",'',filter[0]),
			},
			"instr" : {
				"about" : base_url+o['link_tel'],
				"tel" : re.sub(r"\"",'',o['telescope'].name)
			},
			#"views" : o['views'],
			"time" : {
				"creation" : datestamp(o['whentaken'])
			},
			"exposure": o['exposuresecs'],
			"credit" : {
				"about" : o['license'],
				"label" : o['credit']
			}
		}
		if len(filter)==2:
			ob['filter']['about'] = "http://lcogt.net/"+filter[1]
		if 'schooluri' in o:
			ob['observer']['school'] = re.sub(r"\"",'',o['schooluri'])
		if 'avmcode' in o and o['avmcode']!="":
			ob['avm'] = { "code": o['avmcode'], }
		if 'avmname' in o and o['avmname']!="":
			ob['avm']['name'] = o['avmname']
		if 'views' in o:
			ob['views'] = o['views']

		if len(obs) > 1:
			observations.append(ob)
		elif len(obs) == 1:
			observations = ob
	return observations


def view_json(request,obs,config):
	
	response = {
		"message" : "This is a beta release of LCOGT JSON. The format may change so any applications you build using this may need updating in the future.",
		"date" : datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"),
		"observation" : obs
	}
	if 'description' in config:
		response["desc"] = config['description']
	if 'link' in config:
		response["link"] = base_url+config['link']
	if 'title' in config:
		response["title"] = config['title']
	if 'pager' in config:
		if 'next' in config['pager'] or 'previous' in config['pager']:
			response["page"] = {}
			#print config
			if 'previous' in config['pager'] and config['pager']['previous']!='':
				response["page"]["previous"] = response["link"]+".json?"+str(config['pager']['previous'])
			if 'next' in config['pager'] and config['pager']['next']!='':
				response["page"]["next"] = response["link"]+".json?"+str(config['pager']['next'])
	if 'observations' in config:
		response["observations"] = config['observations']
	if 'live' in config:
		response["live"] = config['live']
	if 'exposure' in config:
		response["exposure"] = config['exposure']
	
	s = simplejson.dumps(response, indent=1,sort_keys=True)
	output = '\n'.join([l.rstrip() for l in  s.splitlines()])
	if 'callback' in config and config['callback'] != "":
		output = config['callback']+"("+output+")"
	return HttpResponse(output,mimetype=config['mimetype'])
	


def view_kml(request,obs,config):

	if not('title' in config):
		config['title'] = 'LCOGT'

    output = '<?xml version="1.0" encoding="UTF-8"?>\n'
    output += '<kml xmlns="http://earth.google.com/kml/2.2" hint="target=sky">\n'
    output += '<Document>\n'
    output += '	<name>'+config['title']+'</name>\n'
    output += '	<Style id="observation">\n'
    output += '		<LabelStyle>\n'
    output += '			<color>00ffffff</color>\n'
    output += '		</LabelStyle>\n'
    output += '	</Style>\n'
    try:
        schoolname = o['user'].schoolname
    except:
        schoolname = 'unknown'

    for o in obs:
    	output += '	<Placemark>\n'
    	output += '		<name>'+o['skyobjectname']+'</name>\n'
    	output += '		<description><![CDATA[\n'
    	output += '			<p>Observed by <a href="'+base_url+o['link_user']+'.kml">'+schoolname+'</a> on '+datestamp(o['whentaken'])+' with <a href="'+base_url+o['link_tel']+'.kml">'+o['telescope'].name+'</a>.<br /><a href="'+o['link_obs']+'"><img src="'+o['thumbnail']+'" /></a></p>\n'
    	output += '			<p>Data from <a href="http://lcogt.net/">LCOGT</a></p>\n'
    	output += '		]]></description>\n'
    	output += '		<LookAt>\n'
    	output += '			<longitude>'+str(o['raval'] - 180)+'</longitude>\n'
    	output += '			<latitude>'+str(o['decval'])+'</latitude>\n'
    	output += '			<altitude>0</altitude>\n'
    	output += '			<range>20000</range>\n'
    	output += '			<tilt>0</tilt>\n'
    	output += '			<heading>0</heading>\n'
    	output += '		</LookAt>\n'
    	output += '		<Point>\n'
    	output += '			<coordinates>'+str(o['raval'] - 180)+','+str(o['decval'])+',0</coordinates>\n'
    	output += '		</Point>\n'
    	output += '		<styleUrl>#observation</styleUrl>\n'
    	output += '	</Placemark>\n'

    output += '</Document>\n'
    output += '</kml>\n'

    return HttpResponse(output,mimetype=config['mimetype'])

	
def view_rss(request,obs,config):

    if not('title' in config):
        config['title'] = 'LCOGT'
    try:
        schoolname = o['user'].schoolname
    except:
        schoolname = 'unknown'

    output = '<?xml version="1.0" encoding="utf-8" ?>\n'
    output += '<rss version="2.0">\n'
    output += '<channel>\n'
    output += '	<title>'+config['title']+'</title>\n'
    output += '	<link>'+base_url+config['link']+'</link>\n'
    output += '	<description>'+config['description']+'</description>\n'
    output += '	<language>en-gb</language>\n'
    output += '	<pubDate>'+datestamp('')+'</pubDate>\n'
    output += '	<lastBuildDate>'+datestamp('')+'</lastBuildDate>\n'
    output += '	<docs>http://blogs.law.harvard.edu/tech/rss</docs>\n'
    output += '	<generator>RedDragon (cwl)</generator>\n'
    output += '	<copyright>Las Cumbres Observatory Global Telescope Network</copyright>\n'

    for o in obs:
    	output += '	<item>\n'
    	output += '		<title>'+o['skyobjectname']+'</title>\n'
    	output += '		<description><![CDATA[<a href="'+base_url+o['link_user']+'">'+schoolname+'</a> took an image of '+o['skyobjectname']+' ('+degreestohms(o['raval'])+', '+degreestodms(o['decval'])+') with <a href="'+base_url+o['link_tel']+'">'+o['telescope'].name+'</a>.]]></description>\n'
    	output += '		<link>'+base_url+o['link_obs']+'</link>\n'
    	output += '		<pubDate>'+datestamp(o['whentaken'])+'</pubDate>\n'
    	output += '	</item>\n'

    output += '</channel>\n'
    output += '</rss>\n'

    return HttpResponse(output,mimetype=config['mimetype'])
	

def relativetime(value):
	delta = datetime.utcnow()-parsetime(value)

	if(delta.days > 1.2*365):
		h = int(round(delta.days/365.25))
		if h==1:
			return 'more than a year ago'
		else:
			return 'about %s years ago' % h
	elif delta.days > 60:
		return 'about %s months ago' % int(delta.days/30)
	elif delta.days >= 2:
		return "%s days ago" % int(round(delta.days+delta.seconds/86400.0))
	elif delta.seconds+(delta.days*86400) > (86400):
		return '1 day ago'
	elif delta.seconds > (5400):
		h = round(delta.seconds / 3600)
		return 'about %s hours ago' % h
	elif delta.seconds > (2700):
		return 'about an hour ago'
	elif delta.seconds > (120):
		return 'about %s minutes ago' % round(delta.seconds/60)
	elif delta.seconds > (60):
		return 'about a minute ago'
	else:
		return 'less than a minute ago'


def parsetime(value):
	return datetime(int(value[0:4]),int(value[4:6]),int(value[6:8]),int(value[8:10]),int(value[10:12]),int(value[12:14]))

def degreestodms(value):
	"Converts decimal degrees to decimal degrees minutes and seconds"
	if not(value):
		return ""
	if(value < 0):
		sign = "-"
	else:
		sign = ""
	value = abs(value)
	d = int(value)
	m = int((value - d)*60)
	s = ((value - d)*3600 - m*60)
	return "%s%02d:%02d:%05.2f" % (sign,d,m,s)

def degreestohms(value):
	"Converts decimal degrees to decimal degrees minutes and seconds"
	value = float(value)/15
	d = int(value)
	m = int((value - d)*60)
	s = ((value - d)*3600 - m*60)
	return str(d)+':'+str(m)+':'+"{0:05.2f}".format(s)

def datestamp(value):
	if value:
		dt = datetime(int(value[0:4]),int(value[4:6]),int(value[6:8]),int(value[8:10]),int(value[10:12]),int(value[12:14]))
	else:
		dt = datetime.today()
	return dt.strftime("%a, %d %b %Y %H:%M:%S +0000");

def datestamp_basic(value):
	if value:
		dt = datetime(int(value[0:4]),int(value[4:6]),int(value[6:8]),int(value[8:10]),int(value[10:12]),int(value[12:14]))
	else:
		dt = datetime.today()
	return dt.strftime("%a, %d %b %Y");


def l(txt,lnk):
	return "<a href=\"http://lcogt.net/"+lnk+"\">"+txt+"</a>";

def filter_list():
	return [ {'code':'CC', 'name':'Air', 'node': 'node/31'},
			{'code':'RGB', 'name':'Color', 'node': ""},
			{'code':'RGB+ND', 'name':"Color + Neutral Density", 'node': ""},
			{'code':'RGB_ND', 'name':"BVr' +Neutral Dens", 'node': ""},
			{'code':'Red', 'name':"Red", 'node': ""},
			{'code':'Green', 'name':"Green", 'node': ""},
			{'code':'Blue', 'name':"Blue", 'node': ""},
			{'code':'CA', 'name':'Hydrogen Alpha', 'node': 'node/51'},
			{'code':'HB', 'name':"Hydrogen Beta", 'node': "node/53"},
			{'code':'CO', 'name':'Oxygen III', 'node': 'node/34'},
			{'code':'CB', 'name':'Bessell B', 'node': 'node/36'},
			{'code':'CV', 'name':"Bessell V", 'node': "node/37"},
			{'code':'CR', 'name':'Bessell R', 'node': "node/43"},
			{'code':'BI', 'name':"Bessell I", 'node': ""},
			{'code':'CU', 'name':"SDSS u'", 'node': "node/42"},
			{'code':'SR', 'name':"SDSS r'", 'node': ""},
			{'code':'CI', 'name':"SDSS i'", 'node': "node/35"},
			{'code':'NB', 'name':"B +Neutral Dens", 'node': ""},
			{'code':'NV', 'name':"V +Neutral Dens", 'node': ""},
			{'code':'SG', 'name':"Sloan g'", 'node': "node/45"},
			{'code':'SY', 'name':"Pan-STARRS Y", 'node': "node/49"},
			{'code':'SZ', 'name':"Pan-STARRS Z", 'node': "node/48"},
			{'code':'SO', 'name':"Solar", 'node': "node/40"},
			{'code':'SM', 'name':"SkyMap - CaV", 'node': "node/41"},
			{'code':'OP', 'name':"Opal", 'node': "node/50"},
			{'code':'D5', 'name':"D51 filter", 'node': ""}]

def filter_props(code):
	f = filter_list();
	try:
		for fs in f:
			if(fs['code'] == code):
				return [fs['name'],fs['node']]
		return ["Unknown",""]
	except:
		return ["Unknown",""]

def filter_link(code):
	try:
		props = filter_props(code)
	except:
		return "Unknown"
	if len(props) == 2:
		return l(props[0],props[1])
	else:
		return props[0]

def filter_name(code):
	try:
		props = filter_props(code)
	except:
		return "Unknown"
	return props[0]


def hexangletodec(value):
	value = value.split(":")
	if (int(value[0]) >= 0):
		sign = 1
	else :
		sign = -1
	return (int(value[0])+(sign*(float(value[1])/60)+(float(value[2])/3600)))


def observation_URL(tel,obs):
	telescope = telescope_details(tel)
	return telescope.site+'/'+telescope.code+"/"+obs

# Bin the observations by month for the specified number of bins
def binMonths(obs,input,bins):
	now = datetime.utcnow()
	binned = [0 for num in range(bins)]
	values = [{'count':0,'year':0,'m':0,'month':''} for num in range(bins)]
	for num in range(bins):
		m = now.month - num
		values[num]['year'] = now.year+((m-1)/12)		
		while m < 1:
			m += 12
		values[num]['month'] = datetime(now.year, m, 1).strftime("%b")
		values[num]['m'] = m
	e = 0
	for o in obs:
		try:
			date = parsetime(o['whentaken'])
		except:
			date = parsetime(o.whentaken)
			e += o.exposuresecs
		month = date.month - 12*(now.year-date.year)
		m = now.month-month
		if (m < bins):
			binned[m] = binned[m] + 1
			values[m]['count'] = binned[m]
	input['bins'] = values
	input['exposuretime'] = e
	input['binmax'] = max(binned)
	if input['binmax'] == 0:
		input['binmax'] = 1
	return input

def unknown(request):
    return render_to_response('faulkes/404.html', context_instance=RequestContext(request))

def broken(request,msg):
    return render_to_response('faulkes/500.html', {'msg':msg}, context_instance=RequestContext(request))

