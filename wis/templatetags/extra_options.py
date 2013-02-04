from django.template import Template, Library
from django.contrib.admin.models import LogEntry
from datetime import date, datetime, timedelta
import time
from wis.models import Registrations, Slots, EmailMessage, StatusUpdate
from wis.choices import *
from string import find

register = Library()

@register.inclusion_tag('admin/status_updates.html')
def status_updates(telid):
    queryset = StatusUpdate.objects.all()
    if telid == 'all':
        queryset = queryset.order_by('-created')[:6]
    else:
        queryset = queryset.filter(telid=telid).order_by('-created')[:5]   
    params = { 'updates' : queryset,
               }
    return params  

@register.inclusion_tag('admin/credit_info.html')
def credit_info(regid):
    history = LogEntry.objects.filter(object_id=regid)
    reg     = Registrations.objects.get(schoolid=regid)
    e       = EmailMessage.objects.all()
    params  = {  'history': history,
                'regid'   : regid,
                'emails'  : e,
                'peakmins': reg.peakrtiminsavailable,
                'updated' : reg.accountupdated,
                'created' : reg.accountcreated,
                'postcode': reg.schoolpostcode,}
    return params

@register.inclusion_tag('slot_info.html')
def slot_info(slotid):
    choices = Slots.objects.get(slotid=slotid)
    params = { 'choices' : choices,
               'slotid'  : slotid, }
    return params

@register.inclusion_tag('user_status.html')
def users_of_status(status):
    choices = Registrations.objects.filter(accountstatus=status)
    params = { 'choices' : choices,
                'status' : status,}
    return params

@register.inclusion_tag('slot_show.html')  
def slots_in_period(datestamp):
    today = 'N'
    if datestamp == 'today':
        d = date.today()
        today = 'Y'
    s = d.strftime('%Y%m%d')+"000000"
    e = d.strftime('%Y%m%d')+"235959"
    message = "Booked slots for:"
    slots = Slots.objects.filter(start__gte=s,end__lte=e).order_by('telid','start')
    return {'slots':slots,'date':d, 'message':message, 'today':today}
 
@register.inclusion_tag('slot_show.html')  
def recent_bookings(nodays):
    today = 'N'
    d = datetime.now()
    dy = d - timedelta(days=nodays)
    s = dy.strftime('%Y%m%d%H%M%S')
    e = d.strftime('%Y%m%d%H%M%S')
    message = "Bookings since:"
    slots = Slots.objects.filter(bookeddate__gte=s,bookeddate__lte=e).order_by('telid','start')
    return {'slots':slots,'date':dy, 'message':message,'today':today}
    
@register.filter
def highlight_scope(value):
    tel = SCOPE_CHOICES[value-1][1]
    if value == 1:
        colour = '39f'
    elif value == 2:
        colour = '3c6'
    return '<span style="color: #%s;">%s</span>' % (colour,tel)

@register.filter
def highlight_scope_short(value):
    tel = SCOPE_CHOICES[value-1][1]
    if value == 1:
        colour = '<span style="color: #39f;">North</span>'
    elif value == 2:
        colour = '<span style="color: #3c6;">South</span>'
    return  colour

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
      
   
    
