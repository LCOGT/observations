from django.db import models
from datetime import datetime
import time
from choices import SCOPE_CHOICES, FOOTER_CHOICES, STATUS_CHOICES, STATE_CHOICES, USER_TYPES, statuschoices, TEL_TWITTER
import urllib
from django.utils import simplejson

wistime_format = "%Y%m%d%H%M%S"

class Alerts(models.Model):
    alertdatetime = models.CharField(max_length=42, blank=False,primary_key=True)
    telescopeid = models.IntegerField(null=True, blank=True, choices=SCOPE_CHOICES)
    alerttype = models.CharField(max_length=150, blank=True)
    alertmessage = models.CharField(max_length=765, blank=True)
    class Meta:
        db_table = u'alerts'
        verbose_name_plural = u'alerts'
    def __unicode__(self):
        t = datetime(*time.strptime(self.alertdatetime , wistime_format)[0:5])
        return "%s" % t.isoformat(" ")

class Timeallocationgroups(models.Model):
    tagid = models.IntegerField(primary_key=True,blank=False)
    name = models.CharField(max_length=30,unique=True)
    bookingcutoffhrs = models.IntegerField(null=True, db_column='bookingCutoffHrs', blank=True) # Field name made lowercase.
    description = models.CharField(max_length=600, blank=True)
    contactname = models.CharField(max_length=90, db_column='contactName', blank=True) # Field name made lowercase.
    contactemail = models.CharField(max_length=90, db_column='contactEmail', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'timeallocationgroups'
        verbose_name_plural = u'time allocation groups'
    def __unicode__(self):
        return self.name

        
class Registrations(models.Model):
    tag = models.ForeignKey(Timeallocationgroups, verbose_name = 'TAG', db_column = 'tag', to_field='name')
    failedlogins = models.IntegerField("failed logins",null=True, blank=True,default='0')
    accountstatus = models.CharField("status",max_length=150, blank=False, choices=STATUS_CHOICES)
    schoolname = models.CharField("organization",max_length=150, blank=False)
    schooladdress1 = models.CharField("address",max_length=150, blank=True)
    schooladdress2 = models.CharField("address 2",max_length=150, blank=True)
    schooladdress3 = models.CharField("county/country",max_length=150, blank=True)
    schoolid = models.IntegerField("user ID",primary_key=True)
    contactemailaddress = models.CharField("email",max_length=150, blank=False)
    teachername = models.CharField("full name",max_length=150, blank=False)
    schoolpostcode = models.CharField("postcode",max_length=30, blank=True)
    contactphonenumber = models.CharField("phone number",max_length=150, blank=True)
    accountcreated = models.CharField("created",max_length=42, blank=True)
    accountupdated = models.CharField("updated",max_length=42, blank=True)
    notes = models.CharField("notes",max_length=765, blank=True)
    dfeeregistrationnumber = models.CharField("school dfES",max_length=150, blank=True)
    dfeeteacheridnumber = models.CharField("teacher DfES",max_length=150, blank=True)
    password = models.CharField(max_length=150)
    schoolloginname = models.CharField("username",max_length=60)
    usertype = models.CharField("user type",max_length=3, blank=True, choices=USER_TYPES)
    peakrtiminsavailable = models.IntegerField("peak mins",null=True, blank=True,default='0')
    offpeakrtiminsavailable = models.IntegerField("off peak mins",null=True, blank=True,default='0')
    offlineminsavailable = models.IntegerField("offline mins",null=True, blank=True,default='0')
    canbooksessionsbefore = models.CharField("book sessions before", max_length=24, blank=True)
    isadminaccount = models.CharField("advanced user",max_length=3, blank=True, choices=STATE_CHOICES, default='N')
    timezone = models.IntegerField(null=True, blank=True,default='0')
    class Meta:
        db_table = u'registrations'
        verbose_name_plural = u'registrations'
    def __unicode__(self):
        return self.schoolname
    def was_published_today(self):
        return self.accountcreated
    def colour_status(self):
       st = statuschoices[self.accountstatus]
       if self.accountstatus == 'deleted' or self.accountstatus == 'rejected':
           colour = 'red'
       elif self.accountstatus == 'suspended' or self.accountstatus == 'applied' or self.accountstatus == 'pending':
           colour = 'orange'
       else:
           colour = 'green'
       return '<span class="%s">%s</span>' % (colour,st)
    colour_status.allow_tags = True
    def save(self):
        if self.accountstatus == 'active' and self.accountcreated == '':
            self.accountcreated = datetime.today().strftime("%Y%m%d%H%M%S")
        self.accountupdated = datetime.today().strftime("%Y%m%d%H%M%S")
        super(Registrations, self).save()
    
        
class Slots(models.Model):
    tag = models.ForeignKey(Timeallocationgroups, db_column='tag', to_field='name')
    start = models.CharField(max_length=42, blank=True)
    end = models.CharField(max_length=42, blank=True)
    schoolid = models.ForeignKey(Registrations, db_column='schoolid',verbose_name="username")
    telid = models.IntegerField("telescope",null=True, blank=True, choices=SCOPE_CHOICES)
    peak = models.CharField("is peak?",max_length=3, blank=True, choices=STATE_CHOICES)
    enabled = models.CharField("enabled?",max_length=3, blank=True, choices=STATE_CHOICES)
    bookeddate = models.CharField("date booked",max_length=42, blank=True)
    cancelleddate = models.CharField("date cancelled",max_length=42, blank=True)
    usercancelled = models.CharField("user cancel",max_length=3, blank=True ,choices=STATE_CHOICES)
    admincancelled = models.CharField("admin cancel",max_length=3, blank=True, choices=STATE_CHOICES)
    cancelreason = models.CharField("cancel reason", max_length=762, blank=True)
    notes = models.CharField(max_length=762, blank=True)
    confirmemailsent = models.CharField("confirmation email?",max_length=3, db_column='confirmEmailSent', blank=True,choices=STATE_CHOICES) # Field name made lowercase.
    reminderemailsent = models.CharField("reminder send?",max_length=3, db_column='reminderEmailSent', blank=True ,choices=STATE_CHOICES) # Field name made lowercase.
    firstdateinweek = models.CharField("start of week",max_length=42, blank=True)
    slotid = models.IntegerField("slot ID",primary_key=True)
    loggedin = models.IntegerField("logged in",null=True, blank=True)
    commandexecuted = models.IntegerField("commands executed",null=True, blank=True)
    imagesreceived = models.IntegerField("images received",null=True, blank=True)
    telescopeclosed = models.IntegerField("close detected",null=True, blank=True)
    refunded = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = u'slots'
        verbose_name_plural = u'observing slots'
    def __unicode__(self):
        return "%s" % self.slotid
    def start_time(self):
        if self.start: 
            t = datetime(*time.strptime(self.start , wistime_format)[0:5])
            return "%s" % t.strftime("%H:%M")
        else:
            return "Error"
    start_time.short_description = 'Start'

    def end_time(self): 
        if self.end:
            t = datetime(*time.strptime(self.end , wistime_format)[0:5])
            return "%s" % t.strftime("%H:%M")
        else:
            return "Error"
    end_time.short_description = 'End'
    def slotstamp(self): 
        if self.start:
            s = datetime(*time.strptime(self.start , wistime_format)[0:5])
            d = "%s" % s.strftime("%a, %d %b %Y")
        else:
            d = "Error"
        return d
    slotstamp.short_description = 'Date'

    def start_date(self): 
        s = datetime(*time.strptime(self.start , wistime_format)[0:5])
        return s
    def end_date(self): 
        s = datetime(*time.strptime(self.end , wistime_format)[0:5])
        return s
    def colour_scope(self):
        tel = SCOPE_CHOICES[self.telid-1][1]
        if self.telid == 1:
            colour = '39f'
        elif self.telid == 2:
            colour = '3c6'
        else:
            colour = '000'
        return '<span style="color: #%s;">%s</span>' % (colour,tel.replace('Faulkes Telescope',''))
    colour_scope.allow_tags = True
    colour_scope.short_description = 'Telescope'

class EmailMessage(models.Model):
    code    = models.CharField("message ID",max_length=5,blank=False)
    title   = models.CharField("title",max_length=50,blank=False)
    subject = models.CharField("email subject", max_length=50,blank=False)
    message = models.CharField("body of message",max_length=1500, blank=False)
    footer  = models.IntegerField("standard footer",null=False,blank=False, choices=FOOTER_CHOICES)
    class Meta:
        db_table = u'message'
        verbose_name_plural = u'system emails'
    def __unicode__(self):
        return self.title

class Settings(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    value = models.CharField(max_length=762, blank=True)
    class Meta:
        db_table = u'settings'
        verbose_name_plural = u'status settings'
        
class StatusUpdate(models.Model):
    telid   = models.IntegerField("telescope",null=False, blank=False, choices=SCOPE_CHOICES)
    created = models.DateTimeField("date created",null=False, blank=False)
    message = models.CharField("body of message",max_length=500, blank=False)
    class Meta:
        db_table = u'statusupdate'
        verbose_name = "status update"
    def __unicode__(self):
        return u'%s' % self.created.isoformat(' ')
        
    def save(self):
        # Retrieve creds from choices.py and send to Twitter
        # Removed until we can fix the issue with OAUTH
        #uname = TEL_TWITTER[self.telid][0]
        #pword = TEL_TWITTER[self.telid][1]
        #twid = squawk(uname,pword,self.message,'update') # Tweet directly from telescope
        #print twid
        #squawk(TEL_TWITTER[0][0],TEL_TWITTER[0][1], '',twid) # Tweet from faulkestel
        
        # Save to faulkes db so it shows up on RTI       
        idname = "TelescopeMessageOfTheDay%s" % self.telid
        status = Settings.objects.filter(name=idname).using("faulkes")
        for s in status:
           s.value = "%s - %s" % (datetime.today().strftime("%H:%M UT %d %b"),self.message)
           s.save()
    
        super(StatusUpdate, self).save()
        
class Schooluri(models.Model):
    usr_id = models.ForeignKey(Registrations,db_column='usr_id')
    uri = models.URLField('URI', blank=True, verify_exists=True,db_column='uri')
    class Meta:
        db_table = u'schooluri'
        verbose_name = u'school uri'
    def __unicode__(self):
        return u'School URI'

def truncate(string,target):
    if len(string) > target:
        return string[:(target-3)] + "..."
    else:
        return string

def squawk(username,password,message,status):
    """Simple post-to-twitter function"""
    message = truncate(message,140) # trim message
    data = urllib.urlencode({"status" : message})
    if status == 'update':
        res = urllib.urlopen("http://%s:%s@api.twitter.com/statuses/%s.json" % (username,password,status), data)
    else:
        res = urllib.urlopen("http://%s:%s@api.twitter.com/statuses/retweet/%s.json" % (username,password,status), data)
    result = simplejson.load(res)
    if result['id']:
        return result['id']
    else:
        return false

        
