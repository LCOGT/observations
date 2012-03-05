from django import template
from datetime import datetime

register = template.Library()

def hourstodegrees(value,arg):
	"Converts decimal hours to decimal degrees"
	return value*15

def degreestohours(value):
	"Converts decimal degrees to decimal hours"
	return float(value)/15

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
	"Converts decimal degrees to decimal hours minutes and seconds"
	if not(value):
		return ""
	value = float(value)/15
	d = int(value)
	m = int((value - d)*60)
	s = ((value - d)*3600 - m*60)
	return "%02d:%02d:%05.2f" % (d,m,s)

def niceduration(value):
	if not(value):
		return ""
	if value < 180:
		return str(value)+' seconds'
	elif value < 90*60:
		m = int(value/60)
		s = int(value - m*60)
		if s == 0:
			return str(m)+' minutes'
		else:
			return str(m)+' minutes '+str(s)+' seconds'
	elif value < 86400:
		h = int(value/3600)
		m = int((value-(h*3600))/60)
		if h == 1:
			return '1 hour '+str(m)+' minutes'
		else:
			return str(h)+' hours '+str(m)+' minutes'
	elif value < 2*86400:
		d = int(value/86400)
		h = int((value-(d*86400))/3600)
		if h == 0:
			return '1 day'
		elif h == 1:
			return '1 day 1 hour'
		else:
			return '1 day '+str(h)+' hours'
	elif value < 365.25*86400:
		d = int(value/86400)
		h = int((value-(d*86400))/3600)
		if h == 0:
			return str(d)+' days'
		elif h == 1:
			return str(d)+' days 1 hour'
		else:
			return str(d)+' days '+str(h)+' hours'
	else:
		c = (365.25*86400)
		y = int(value /c)
		d = int((value-y*c)/86400)
		if y == 1:
			return '1 year '+str(d)+' days'
		else:
			return str(y)+' years '+str(d)+' days'
	

def relativetime(value):
	if not(value):
		return ""
	delta = datetime.utcnow()-parsetime(t)
	print delta
	if delta < 60:
		return 'less than a minute ago'
	elif delta < 120:
		return 'about a minute ago'
	elif delta < (45*60):
		return int(delta / 60)+' minutes ago'
	elif delta < (90*60):
		return 'about an hour ago'
	elif delta < (86400):
		h = int(delta / 3600)
		if h == 1:
			return 'about '+h+' hour ago'
		else:
			return 'about '+h+' hours ago'
	elif delta < (2*86400):
		return '1 day ago'
	elif delta < (60*86400):
		return int(delta / 86400)+' days ago'
	elif delta < (365*86400):
		return 'about '+round(delta / (30*86400))+' months ago'
	elif delta < (1.2*365*86400):
		return 'about 1 year ago'
	else:
		h = round(delta / (365.25*86400))
		if h == 1:
			return 'more than a year ago'
		else:
			return 'about '+h+' years ago'

def parsetime(value):
	return datetime(int(value[0:4]),int(value[4:6]),int(value[6:8]),int(value[8:10]),int(value[10:12]),int(value[12:14]))

def datestamp(value):
	if value:
		try:
			dt = parsetime(value)
		except:
			dt = datetime()
	else:
		dt = datetime()
	return dt.strftime("%a %d %B %Y, %H:%M UT");

def isodatestamp(value):
	if value:
		dt = parsetime(value)
	else:
		dt = datetime()
	return dt.strftime("%Y-%M-%DT%H:%M:%S+00:00");



def lowercase(value):
	return value.lower()

def negative(value, arg):
	return round(value)-round(arg)
    
register.filter('degreestohours', degreestohours)
register.filter('hourstodegrees', hourstodegrees)
register.filter('degreestodms', degreestodms)
register.filter('degreestohms', degreestohms)
register.filter('datestamp', datestamp)
register.filter('isodatestamp', isodatestamp)
register.filter('lowercase', lowercase)
register.filter('negative', negative)
register.filter('niceduration', niceduration)
