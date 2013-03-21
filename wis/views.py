# Create your views here.

from wis.models import Slots, Registrations,EmailMessage, Alerts
from wis.choices import usertypes, USER_TYPES,email_footer,email_sender
from django.utils.encoding import smart_unicode
from django.utils import simplejson
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models import Count, Q
from django.core.mail import send_mail
from django.core import urlresolvers
from django.contrib.admin.models import LogEntry, CHANGE
from datetime import date,timedelta,datetime
from string import replace
import re

def emailtext(request,userid,messid):
    passlist = ('pass1','pass2','pass3')
    ms = EmailMessage.objects.get(id=messid)
    u  = Registrations.objects.get(schoolid=userid)
    if request.POST:
        user = request.POST['uid']
        messid = request.POST['messid']
        sub = "%s :: %s" % (u.teachername,ms.subject)
        footer = email_footer[ms.footer]
        email_from = email_sender[ms.footer]
        if messid in passlist:
            mess = ms.message % (u.teachername,u.schoolid,u.schoolloginname,u.password)
        else:
            mess = ms.message % u.teachername
        mess += footer
        headers = { 'To'            : [u.contactemailaddress] ,
                    'From'          : email_from,
                    'Return-path'   : email_from,
                    'Reply-to'      : email_from,
                    'Content-type'  : 'text/plain; charset=iso-8859-1',
                    'X-Priority'    :'3',
                    'Date'          : datetime.today(),
                    'MIME-Version'  : '1.0' ,}
        send_mail(sub, mess, email_from, [u.contactemailaddress], headers)
        request.user.message_set.create(message="Successfully sent email to %s" % u.teachername)
        return HttpResponseRedirect("../../../")
    else:
        return render_to_response('admin/email_message.html',{'message':ms,'user':u, 'messid':ms.code},context_instance=RequestContext(request))

def slotdetails(request,slotid):
    qs = Slots.objects.get(slotid=slotid)
    return render_to_response('admin/change_form.html',{'queryset':qs})
    
def addcredit(request):
    data = request.POST
    mins = data.get('peakmins','')
    school = request.POST['schoolid']
    message = data.get('reason','')
    if message:
        mess = "Added %s mins : %s" % (mins,message)
    else:
        mess = "Added %s peak mins" % mins
    reg = Registrations.objects.get(schoolid=school)
    reg.peakrtiminsavailable = int(reg.peakrtiminsavailable) + int(mins)
    reg.save()
    LogEntry.objects.log_action(
        user_id         = request.user.pk, 
        content_type_id = '10',
        object_id       = school,
        object_repr     = smart_unicode(reg), 
        action_flag     = CHANGE,
        change_message  = mess
    )
    return HttpResponse('<li>%s</li>' % mess)

def find_slots(request):
    data = request.POST
    if data.get('start',''):
        morning = replace(request.POST['start'],'/','')+"000000"
        morning = replace(morning,' ','')
    else:
        today = date.today()
        morning = today.strftime("%Y%m%d000000")
    if data.get('end',''):
        night = replace(request.POST['end'],'/','')+"235959"
        night = replace(night,' ','')
    else:
        today = date.today()
        night = today.strftime("%Y%m%d235959")
    url = urlresolvers.reverse('admin:wis_slots_changelist')
    sloturl = "%s?start__gte=%s&end__lte=%s" % (url,morning, night)
    return HttpResponseRedirect(sloturl)
    
def show_alerts(request):
  starttime = datetime.utcnow() - timedelta(seconds=7200)
  als = Alerts.objects.filter(alertdatetime__gte=starttime.strftime("%Y%m%d%H%M%S")).order_by('-alertdatetime')
  #als = Alerts.objects.filter(alertdatetime__gte="20100310133000")
  return render_to_response('admin/alerts_history.html',{'alerts':als,'start':datetime.utcnow()},context_instance=RequestContext(request))
  
def update_alerts(request):
    laststamp = request.POST['stamp']
    starttime = datetime.utcnow()
    als = Alerts.objects.filter(alertdatetime__gte=laststamp).order_by('-alertdatetime')
    # Add datetime of last entry in Alerts
    return render_to_response('alerts_update.html',{'alerts':als,'start':starttime})

def slot_search(request):
    data = request.GET
    telnames = [{    'id'    : 1,
                    'code'  : 'FTN',
                    'name'  : 'Faulkes Telescope North',
                },{ 'id'    : 2,
                    'code'  : 'FTS',
                    'name'  : 'Faulkes Telescope South',
                }]
                
    if data:
        callback = request.GET.get('callback','')
        # Sanitise the callback to stop any dodgy Javascript
        callback = re.sub(r"[^\w]",'',callback)
        start = data.get('start','')
        end = data.get('end','')
        tag = data.get('tag','')
        telid = data.get('telid','')
        telname = data.get('telescope','')
        if len(start) == 8:
            # Guess that date format is RTI simple ISO
            s = "%s000000" % start
            s = datetime.strptime(s,'%Y%m%d%H%M%S')
        elif len(start) == 10:
            # Guess that date format is ISO
            s = "%sT00:00:00" % start
            s = datetime.strptime(s,'%Y-%m-%dT%H:%M:%S')
        elif len(start) == 16:
            s = "%s:00" % start
            s = datetime.strptime(s,'%Y-%m-%dT%H:%M:%S')
        elif len(start) == 19:
            s = datetime.strptime(start,'%Y-%m-%dT%H:%M:%S')
        elif len(start) == 20:
            s = datetime.strptime(start,'%Y-%m-%dT%H:%M:%SZ')
        if len(end) == 8:
            # Guess that date format is RTI simple ISO
            e = "%s235959" % end
            e = datetime.strptime(e,'%Y%m%d%H%M%S')
        elif len(end) == 10:
            # Guess that date format is ISO
            e = "%sT23:59:59" % end
            e = datetime.strptime(e,'%Y-%m-%dT%H:%M:%S')
        elif len(end) == 16:
            e = "%s:59" % end
            e = datetime.strptime(e,'%Y-%m-%dT%H:%M:%S')
        elif len(end) == 19:
            e = datetime.strptime(end,'%Y-%m-%dT%H:%M:%S')
        elif len(end) == 20:
            e = datetime.strptime(end,'%Y-%m-%dT%H:%M:%SZ')

        startdate = datetime.strftime(s,'%Y%m%d%H%M%S')
        enddate = datetime.strftime(e,'%Y%m%d%H%M%S')
        print startdate,enddate
        slots = Slots.objects.filter(start__gte=startdate,end__lte=enddate,admincancelled='N',usercancelled='N').order_by('start')
        print slots.count()
        if tag:
            slots = slots.filter(tag=tag)
        if telid or telname:
            if telname:
                telescope = [tel for tel in telnames if tel['code'] == telname.upper()][0]
            if telid:
                try:
                    telescope =  telnames[int(telid)-1]
                except:
                    return HttpResponse("Invalid telescope ID",mimetype='application/javascript')
            slots = slots.filter(telid=telescope['id'])
            tel_list = [telescope]
        else:
            tel_list = telnames
        bookings = []
        for t in tel_list:
            print t
            slottel = slots.filter(telid=t['id'])
            slotlist = []
            if slottel.count() != 0:
                for s in slottel:
                    if s.schoolid.pk == 0:
                        school = 'None'
                    else:
                        school = "%s" % s.schoolid
                    slot = {'start'  : "%sZ" % datetime.strptime(s.start,'%Y%m%d%H%M%S').isoformat(),
                            'end'    : "%sZ" % datetime.strptime(s.end,'%Y%m%d%H%M%S').isoformat(),
                            'booked' : school,
                            'tag'    : s.tag.name,
                            'userid' : s.schoolid.pk
                            }
                    slotlist.append(slot)
            bookings.append({'telescope' : t['name'], 'slots' : slotlist,'code':t['code']})
        if callback:
            resp = callback+"("+simplejson.dumps(bookings,indent=2)+")"
        else:
            resp = simplejson.dumps(bookings,indent=2)
    else:
        resp = "No information supplied"
    return HttpResponse(resp,mimetype='application/javascript')
            

def slots_by_user(request):
    user = request.REQUEST['userid']
    s = Slots.objects.filter(schoolid=user,admincancelled='N',usercancelled='N').order_by('-start')
    return render_to_response('slot_show.html',{'slots':s})
    
def slots_by_month(request):
    data = request.GET
    year = data.get('year','')
    month = data.get('month','')
    if year =='':
        year = date.today().year
    if month =='':
        month = date.today().strftime("%m")
    start = "%s%s01000000" % (year, month)
    end = "%s%s31125959" % (year, month)
    d = {'year':year,'month':month,}
    s = Slots.objects.filter(start__gte=start,end__lte=end,admincancelled='N',usercancelled='N').extra({'start_days':"date(start)"}).values('start_days','telid').annotate(Count('slotid')).order_by('start')
    t = Slots.objects.filter(start__gte=start,end__lte=end,admincancelled='N',usercancelled='N').values('telid').annotate(tot=Count('slotid'))
    return render_to_response('admin/slot_digest.html',
        {'stats':s,'total':t,'date':d},
        context_instance=RequestContext(request)
        )

def top_users(request):
    data = request.GET
    tag = data.get('tag','')
    year = data.get('year','')
    utype = data.get('type','')
    selectt =''
    selectty =''
    if year =='':
        year = date.today().year
    start = "%s0101000000" % year
    end = "%s1231235959" % year
    queryset = Registrations.objects.filter(slots__start__gte=start,slots__end__lte=end, slots__enabled='Y',slots__usercancelled='N',slots__admincancelled='N')
    selecty = "&year=%s" % year
    if tag:
        queryset = queryset.filter(tag=tag)
        selectt ="&tag=%s" % tag
    if utype:
        queryset = queryset.filter(usertype=utype)
        selectty +="&type=%s" % utype
    select = {'type':selectty,
              'tag':selectt,
              'year':selecty}
    years = ('2003','2004','2005','2006','2007','2008','2009','2010')
    r = queryset.values('schoolname','schoolid','tag','usertype').annotate(Count('slots')).order_by('-slots__count')[:20]
    return render_to_response('admin/slot_stats.html',
            {'stats':r,'types':USER_TYPES,'years':years,'s':select,'year':year},
            context_instance=RequestContext(request)
            )

def user_stats(request):
    s = Registrations.objects.filter(accountstatus='active').values('usertype').annotate(Count(tot='schoolid')).order_by('-schoolid__count')
    print simplejson.dumps(s)
    return render_to_response('admin/user_stats.html',{'stats':s},context_instance=RequestContext(request))    
