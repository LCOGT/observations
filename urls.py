from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^rtiadminsite/', include('rtiadminsite.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^observations/',include('rtiadminsite.faulkes.urls')),
    (r'^rtiadmin/alerts/ajax/$', 'rtiadminsite.wis.views.update_alerts'),
    (r'^rtiadmin/alerts/$','rtiadminsite.wis.views.show_alerts'),
    (r'^rtiadmin/slots/$','rtiadminsite.wis.views.find_slots'),
    (r'^rtiadmin/topusers/$','rtiadminsite.wis.views.top_users'),
    (r'^rtiadmin/slotdigest/$','rtiadminsite.wis.views.slots_by_month'),
    (r'^rtiadmin/addcredit/$','rtiadminsite.wis.views.addcredit'),
    (r'rtiadmin/wis/registrations/(?P<userid>\w+)/email/(?P<messid>\d+)/$','rtiadminsite.wis.views.emailtext'),
    (r'rtiadmin/slots/all/$','rtiadminsite.wis.views.slots_by_user'),
    (r'rtiadmin/userstats/$','rtiadminsite.wis.views.user_stats'),
    #(r'^rtiadmin/slotsearch/(?P<mode>\w+)$','rtiadminsite.wis.views.slot_search'),
    (r'^rtiadmin/slotsearch/$','rtiadminsite.wis.views.slot_search'),
    (r'^rtiadmin/', include(admin.site.urls)),
    )

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"%s(?P<path>.*)/$" % settings.MEDIA_URL[1:], "django.views.static.serve", {
            "document_root": settings.MEDIA_ROOT,
        })
    )