from django import forms
from django.views.decorators.csrf import csrf_protect
from django.utils.encoding import smart_unicode
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, CHANGE
from django.core.mail import send_mail
from django.core import urlresolvers
from rtiadminsite.wis.models import Registrations, Slots, Timeallocationgroups, EmailMessage, Alerts, StatusUpdate, Settings, Schooluri 
from rtiadminsite.faulkes.models import Imagearchive, Filter

from rtiadminsite.wis.choices import SCOPE_CHOICES,email_sender, email_footer
from rtiadminsite.wis.templatetags.extra_options import date_full_format
from django.contrib import admin
from datetime import date
from rtiadminsite.wis.admin_render import ReadOnlyAdminFields, DateTextInput
from string import replace,split, lowercase,rstrip
import random

userlist = ('S','A','C','G','E','M','R','P')

class UpdateForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'cols':'50','rows':'10'}))
class UpdateAdmin(admin.ModelAdmin):
    form = UpdateForm
    list_display = ['created','message','telid']

class EmailForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'cols':'70','rows':'30'}))
class EmailAdmin(admin.ModelAdmin):
    form = EmailForm
    list_display= ['title']

class SchooluriInline(admin.StackedInline):
    model = Schooluri
    max_num = 1

'''
****
Registrations admin section
***
'''

class RegAdminForm(forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea, required=False)
    class Meta:
        model = Registrations
class RegAdmin(admin.ModelAdmin):
  form = RegAdminForm
  search_fields = ['schoolname','schoolloginname','schooladdress3','schoolpostcode']
  list_display  = ['schoolname','teachername','colour_status','schooladdress3','usertype','tag']
  list_filter   = ['accountstatus','tag','usertype']
  inlines       = [SchooluriInline]
  fieldsets     = (
                ('Basic Info',{
                  'fields':('schoolname','teachername','usertype','tag')
                }),
                ('Account Info',{
                'fields' : ('schoolloginname','password','accountstatus','isadminaccount','failedlogins')
                }),
                ('Contact details', {
                'fields' : ('contactemailaddress','schooladdress1','schooladdress2','schooladdress3','schoolpostcode','contactphonenumber','notes')
                }),
                ('Unused Info',{
                'classes' : ('collapse',),
                'fields' : ('offpeakrtiminsavailable','timezone','offlineminsavailable','canbooksessionsbefore','dfeeregistrationnumber','dfeeteacheridnumber')
                })
              )
  actions = ['make_active', 'suspend_user','credit_hour','reject_user','astrosoc_email']
  
  @csrf_protect
  def make_active(self,request,queryset):
    title_list = ('Mr','Mrs','Miss','Ms','Dr')
    strings = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXY23456789'
    ukrtoc = Timeallocationgroups.objects.get(name='UKRTOC')
    for obj in queryset:
        randnum = "".join(random.sample(strings, 8))
        name = replace(obj.teachername,".",'')
        uname = split(name)
        username = ""
        for u in uname:
            if u not in title_list :
                username += "%s." % u
        print username
        obj.schoolloginname = username.rstrip(".")
        obj.password=randnum
        obj.accountstatus='active'
        obj.peakrtiminsavailable='30'
        obj.tag=ukrtoc
        obj.save()
        mess = "%s activated with 30 mins, UKRTOC" % obj.schoolname
        LogEntry.objects.log_action(
            user_id         = request.user.pk, 
            content_type_id = ContentType.objects.get_for_model(obj).pk,
            object_id       = obj.pk,
            object_repr     = smart_unicode(obj), 
            action_flag     = CHANGE,
            change_message  = mess
        )
        ms = EmailMessage.objects.get(code='pass1')
        email_from = email_sender[ms.footer]
        u  = Registrations.objects.get(schoolid=obj.pk)
        mess = ms.message % (u.teachername,u.schoolid,u.schoolloginname,u.password)
        mess += email_footer[ms.footer]
        send_mail(ms.subject, mess,email_from, [u.contactemailaddress])

    message_bit = "%s schools were activated" % len(queryset)
    self.message_user(request, "%s successfully" % message_bit)
  make_active.short_description = "Activate UK school with 30 mins "
  
  def suspend_user(self,request,queryset):
    items = queryset.update(accountstatus='suspended')
    if items == 1:
      message_bit = "1 account was suspended"
    else:
      message_bit = "%s accounts were suspended" % items
    for obj in queryset:
      mess = "%s suspended" % obj.schoolname
      LogEntry.objects.log_action(
          user_id         = request.user.pk, 
          content_type_id = ContentType.objects.get_for_model(obj).pk,
          object_id       = obj.pk,
          object_repr     = smart_unicode(obj), 
          action_flag     = CHANGE,
          change_message  = mess
      )
      ms = EmailMessage.objects.get(code='susp1')
      email_from = email_sender[ms.footer]
      u  = Registrations.objects.get(schoolid=obj.pk)
      mess = ms.message % u.teachername
      mess += email_footer[ms.footer]
      send_mail(ms.subject, mess, email_from,
                   [u.contactemailaddress])
    self.message_user(request,"%s successfully" % message_bit)
  suspend_user.short_description = "Suspend user account"

  def reject_user(self,request,queryset):
    items = queryset.update(accountstatus='rejected')
    if items == 1:
      message_bit = "1 account was rejected"
    else:
      message_bit = "%s accounts were rejected" % items
    for obj in queryset:
      mess = "%s rejected" % obj.schoolname
      LogEntry.objects.log_action(
          user_id         = request.user.pk, 
          content_type_id = ContentType.objects.get_for_model(obj).pk,
          object_id       = obj.pk,
          object_repr     = smart_unicode(obj), 
          action_flag     = CHANGE,
          change_message  = mess
      )
      ms = EmailMessage.objects.get(code='rejc1')
      email_from = email_sender[ms.footer]
      u  = Registrations.objects.get(schoolid=obj.pk)
      mess = ms.message % u.teachername
      mess += email_footer[ms.footer]
      send_mail(ms.subject, mess, email_from,
                   [u.contactemailaddress])
    self.message_user(request,"%s successfully" % message_bit)
  reject_user.short_description = "Reject user application"

  def credit_hour(self,request,queryset):
    for obj in queryset:
       message = "Added 60 mins to %s " % obj.schoolname
       LogEntry.objects.log_action(
           user_id         = request.user.pk, 
           content_type_id = ContentType.objects.get_for_model(obj).pk,
           object_id       = obj.pk,
           object_repr     = smart_unicode(obj), 
           action_flag     = CHANGE,
           change_message  = message
       )
       obj.peakrtiminsavailable = int(obj.peakrtiminsavailable) + 60
       obj.save()
    if len(queryset) == 1:
        message_bit = "1 user credit updated by 60 mins"
    else:
        message_bit = "%s users credit updated by 60 mins" % len(items)
    self.message_user(request,"%s successfully" % message_bit)
  credit_hour.short_description = "Credit user with 60 mins"

  def astrosoc_email(self,request,queryset):
    items = queryset.update(accountstatus='pending')
    ms = EmailMessage.objects.get(code='ASrej') #
    for obj in queryset:
       message = "Astronomical Soc 'more info' email sent to '%s'" % (obj.schoolname)
       LogEntry.objects.log_action(
           user_id         = request.user.pk, 
           content_type_id = ContentType.objects.get_for_model(obj).pk,
           object_id       = obj.pk,
           object_repr     = smart_unicode(obj), 
           action_flag     = CHANGE,
           change_message  = message
       )
       sub  = "%s :: %s" % (obj.teachername,ms.subject)
       mess = ms.message % (obj.teachername )
       mess += email_footer[ms.footer]
       email_from = email_sender[ms.footer]
       send_mail(sub, mess, email_from, [obj.contactemailaddress])
       obj.save()
    if items == 1:
        message_bit = "1 user emailed with custom email"
    else:
        message_bit = "%s users emailed with custom email" % len(items)
    self.message_user(request,"%s successfully" % message_bit)
  astrosoc_email.short_description = "FTP: send Astronomical Soc email"

  
'''
****
Slots admin section
***
'''
class SlotAdmin(admin.ModelAdmin):
    raw_id_fields = ['schoolid',]
    list_display = ['slotstamp','start_time','end_time','get_schoolid','get_org','get_username','get_schoolemail','colour_scope','tag']
    
    ordering = ['start','telid']
    list_filter = ['telid','tag']
    fieldsets = ( 
                ('Editable slot info',{
                  'fields' : ('schoolid','cancelreason','notes')
                }),
            )
    actions = ['unbook_slots','cancel_slot_email','refund_slot_email','custom_ftp_email','ftp_book_slot']
    
# A couple of callables to add extra information in the list display
    def get_username(self, obj):
        return '%s'%(obj.schoolid.schoolloginname)
    get_username.short_description = 'Username'
    def get_org(self, obj):
        return '%s'%(obj.schoolid.schoolname)
    get_org.short_description = 'Organization'
    def get_schoolemail(self,obj):
        return '%s' % (obj.schoolid.contactemailaddress)
    get_schoolemail.short_description = 'Email'
    def get_schoolid(self,obj):
        url = urlresolvers.reverse('admin:wis_registrations_change', args=(obj.schoolid.pk,))
        return '<a href=%s>%s</a>' % (url,obj.schoolid.pk)
    get_schoolid.allow_tags = True
    get_schoolid.short_description = 'School ID'
   
# Make sure the slots list only shows slots which are bookable
    def queryset(self,request):
        qs = super(SlotAdmin,self).queryset(request)
        return qs.filter(admincancelled='N',usercancelled='N',enabled='Y')

# Define actions
    def ftp_book_slot(self,request,queryset):
        items = queryset.update(schoolid='136')
        if items == 1:
            message_bit = "1 slot was changed to account 136 (faulkes)"
        else:
            message_bit = "%s slots were changed to account 136 (faulkes)" % items
        self.message_user(request,"%s successfully" % message_bit)
    ftp_book_slot.short_description = "Book slots to 'Faulkes' account (136)"
    
    def custom_ftp_email(self,request,queryset):
      ms = EmailMessage.objects.get(code='cust1') #
      for obj in queryset:
         message = "FTP custom email sent to '%s'" % (obj.schoolid.schoolname)
         LogEntry.objects.log_action(
             user_id         = request.user.pk, 
             content_type_id = ContentType.objects.get_for_model(obj).pk,
             object_id       = obj.pk,
             object_repr     = smart_unicode(obj), 
             action_flag     = CHANGE,
             change_message  = message
         )
         if obj.schoolid.usertype in userlist:
             sub      = "%s :: %s" % (obj.schoolid.teachername,ms.subject)
             mess = ms.message % (obj.schoolid.teachername,date_full_format(obj.start),SCOPE_CHOICES[obj.telid-1][1] )
             mess += email_footer[ms.footer]
             email_from = email_sender[ms.footer]
             send_mail(sub, mess, email_from, [obj.schoolid.contactemailaddress])
         obj.schoolid.peakrtiminsavailable = int(obj.schoolid.peakrtiminsavailable) + 30
         obj.schoolid.save()
      if len(queryset) == 1:
          message_bit = "1 user emailed with custom email"
      else:
          message_bit = "%s users emailed with custom email" % len(queryset)
      self.message_user(request,"%s successfully" % message_bit)
    custom_ftp_email.short_description = "FTP send customizable email"
        
    def refund_slot_email(self,request,queryset):
      ms = EmailMessage.objects.get(code='slot2') #
      for obj in queryset:
         message = "Slot %s refunded. '%s' notified" % (obj.slotid,obj.schoolid.schoolname)
         LogEntry.objects.log_action(
             user_id         = request.user.pk, 
             content_type_id = ContentType.objects.get_for_model(obj).pk,
             object_id       = obj.pk,
             object_repr     = smart_unicode(obj), 
             action_flag     = CHANGE,
             change_message  = message
         )
         if obj.schoolid.usertype in userlist:
             sub      = "%s :: %s" % (obj.schoolid.teachername,ms.subject)
             mess = ms.message % (obj.schoolid.teachername,date_full_format(obj.start),SCOPE_CHOICES[obj.telid-1][1] )
             mess += email_footer[ms.footer]
             email_from = email_sender[ms.footer]
             send_mail(sub, mess, email_from, [obj.schoolid.contactemailaddress])
         obj.schoolid.peakrtiminsavailable = int(obj.schoolid.peakrtiminsavailable) + 30
         obj.schoolid.save()
      if len(queryset) == 1:
          message_bit = "1 slot was refunded and user emailed"
      else:
          message_bit = "%s slots were refunded and users emailed" % len(items)
      self.message_user(request,"%s successfully" % message_bit)
    refund_slot_email.short_description = "Email user and refund slots" 
 
    def cancel_slot_email(self,request,queryset):
      ms = EmailMessage.objects.get(code='slot1')
      for obj in queryset:
         message = "Slot %s cancelled by admin. '%s' notified" % (obj.slotid,obj.schoolid.schoolname)
         LogEntry.objects.log_action(
             user_id         = request.user.pk, 
             content_type_id = ContentType.objects.get_for_model(obj).pk,
             object_id       = obj.pk,
             object_repr     = smart_unicode(obj), 
             action_flag     = CHANGE,
             change_message  = message
         )
         if obj.schoolid.usertype in userlist:
             sub      = "%s :: %s" % (obj.schoolid.teachername,ms.subject)
             mess = ms.message % (obj.schoolid.teachername,date_full_format(obj.start),SCOPE_CHOICES[obj.telid-1][1] )
             mess += email_footer[ms.footer]
             email_from = email_sender[ms.footer]
             send_mail(sub, mess, email_from, [obj.schoolid.contactemailaddress])
         obj.schoolid.peakrtiminsavailable = int(obj.schoolid.peakrtiminsavailable) + 30
         obj.schoolid.save()
      items = queryset.update(admincancelled='Y')
      if items == 1:
       message_bit = "1 slot was cancelled and user emailed"
      else:
       message_bit = "%s slots were cancelled and users emailed" % items
      self.message_user(request,"%s successfully" % message_bit)
    cancel_slot_email.short_description = "Email user cancelling slots"
    
    def unbook_slots(self,request,queryset):
      # Update History for these entries
      for obj in queryset:
        message = "Slot %s changed from '%s' to not booked" % (obj.slotid,obj.schoolid.schoolname)
        LogEntry.objects.log_action(
            user_id         = request.user.pk, 
            content_type_id = ContentType.objects.get_for_model(obj).pk,
            object_id       = obj.pk,
            object_repr     = smart_unicode(obj), 
            action_flag     = CHANGE,
            change_message  = message
        )
        obj.schoolid.peakrtiminsavailable = int(obj.schoolid.peakrtiminsavailable) + 30
        obj.schoolid.save()
      items = queryset.update(schoolid='0',bookeddate='')
      if items == 1:
        message_bit = "1 slot was changed to not booked"
      else:
        message_bit = "%s slots were changed to not booked" % items
      
      self.message_user(request,"%s successfully" % message_bit)
    unbook_slots.short_description = "Change slots to not booked"

class FaulkesAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.
    using = 'faulkes'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super(FaulkesAdmin, self).queryset(request).using(self.using)
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super(FaulkesAdmin, self).formfield_for_foreignkey(db_field, request=request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super(FaulkesAdmin, self).formfield_for_manytomany(db_field, request=request, using=self.using, **kwargs)

class SettingsAdmin(FaulkesAdmin):
    list_display = ['name','value']
           
class ArchiveAdmin(FaulkesAdmin):
    list_display = ['skyobjectname','schoolloginname','datestamp','telescopeid']

admin.site.register(Imagearchive,ArchiveAdmin)
admin.site.register(Filter)     
admin.site.register(Registrations, RegAdmin)
admin.site.register(Slots, SlotAdmin)
admin.site.register(Timeallocationgroups)
admin.site.register(Alerts)
admin.site.register(EmailMessage,EmailAdmin)
admin.site.register(StatusUpdate, UpdateAdmin)
admin.site.register(Settings,SettingsAdmin)
admin.site.register(Schooluri)
