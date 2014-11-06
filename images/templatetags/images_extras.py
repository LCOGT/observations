from django import template
from datetime import datetime
from images.utils import *

register = template.Library()

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


def lowercase(value):
    return value.lower()

def negative(value, arg):
    return round(value)-round(arg)
    degreestohours,hourstodegreesdegreestodms

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
