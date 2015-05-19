from django.template import Template, Library
from django.contrib.admin.models import LogEntry
from datetime import date, datetime, timedelta
import time
from string import find

register = Library()

@register.filter
def user_type_show(value):
    t = usertypes[value]
    return t
    
@register.filter
def date_full_format(value):
   if value:
       t = datetime(*time.strptime(value, "%Y%m%d%H%M%S")[0:5])
       d = "%s" % t.isoformat(" ")
   else:
        d = u'Not applicable'
   return d

@register.filter
def time_convert(value):
  if value:
      t = datetime(*time.strptime(value, "%Y%m%d%H%M%S")[0:5])
      return "%s" % t.strftime("%H:%M")
  else:
      return u'Not applicable'


@register.filter
def time_format(value):
   return "%s:%s:%s" % (value[8:10],value[10:12],value[12:14])
   
@register.filter
def alert_status(value):
   if value.find("success") <> -1:
      c = "green"
   elif value.find("fail") <> -1:
      c = "red"
   elif value.find("logged out") <> -1:
      c = "orange"
   else:
      c = "normal"
   return "<span class='%s'>%s</span>" % (c,value)
      
   
    
