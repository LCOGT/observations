from django import template
from datetime import datetime

register = template.Library()

def hourstodegrees(value,arg):
	"Converts decimal hours to decimal degrees"
	if ":" in str(value):
		return value
	return value*15

def degreestohours(value):
	"Converts decimal degrees to decimal hours"
	if ":" in str(value):
		return value
	return float(value)/15

def degreestodms(value):
	"Converts decimal degrees to decimal degrees minutes and seconds"
	if ":" in str(value):
		return value
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
	if ":" in str(value):
		return value
	if not(value):
		return ""
	value = float(value)/15
	d = int(value)
	m = int((value - d)*60)
	s = ((value - d)*3600 - m*60)
	return "%02d:%02d:%05.2f" % (d,m,s)

def dmstodegrees(value):
	if ":" not in str(value):
		return value
	el = value.split(":")
	deg = float(el[0])
	if deg < 0:
		sign = -1.
	else:
		sign = 1
	return deg + sign*float(el[1])/60. + sign*float(el[2])/3600.

def hmstodegrees(value):
	if ":" not in str(value):
		return value
	el = value.split(":")
	return float(el[0])*15 + float(el[1])/60. + float(el[2])/3600.

def hmstohours(value):
	if ":" not in str(value):
		return value
	el = value.split(":")
	return float(el[0]) + float(el[1])/60. + float(el[2])/3600.

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
	delta = datetime.utcnow()-parsetime(value)

	if(delta.days > 1.2*365):
		h = int(round(delta.days/365.25))
		if h==1:
			return 'a year ago'
		else:
			return '%s years ago' % h
	elif delta.days > 60:
		return '%s months ago' % int(delta.days/30)
	elif delta.days >= 2:
		return "%s days ago" % int(round(delta.days+delta.seconds/86400.0))
	elif delta.seconds+(delta.days*86400) > (86400):
		return '1 day ago'
	elif delta.seconds > (5400):
		h = round(delta.seconds / 3600)
		return '%d hours ago' % h
	elif delta.seconds > (2700):
		return 'an hour ago'
	elif delta.seconds > (120):
		return '%s minutes ago' % round(delta.seconds/60)
	elif delta.seconds > (60):
		return 'a minute ago'
	else:
		return 'less than a minute ago'

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
	return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00");



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
register.filter('relativetime', relativetime)
register.filter('parsetime', parsetime)
register.filter('hmstohours', hmstohours)
register.filter('hmstodegrees',hmstodegrees)
register.filter('dmstodegrees',dmstodegrees)
