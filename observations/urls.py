from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^rtiadminsite/', include('foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^observations/admin/', include(admin.site.urls)),
    (r'^observations/',include('images.urls')),
    # (r'^rtiadmin/alerts/ajax/$', 'wis.views.update_alerts'),
    # (r'^rtiadmin/alerts/$','wis.views.show_alerts'),
    # (r'^rtiadmin/slots/$','wis.views.find_slots'),
    # (r'^rtiadmin/topusers/$','wis.views.top_users'),
    # (r'^rtiadmin/slotdigest/$','wis.views.slots_by_month'),
    # (r'^rtiadmin/addcredit/$','wis.views.addcredit'),
    # (r'rtiadmin/wis/registrations/(?P<userid>\w+)/email/(?P<messid>\d+)/$','wis.views.emailtext'),
    # (r'rtiadmin/slots/all/$','wis.views.slots_by_user'),
    # (r'rtiadmin/userstats/$','wis.views.user_stats'),
    # #(r'^rtiadmin/slotsearch/(?P<mode>\w+)$','wis.views.slot_search'),
    # (r'^rtiadmin/slotsearch/$','wis.views.slot_search'),
    )

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"%s(?P<path>.*)/$" % settings.MEDIA_URL[1:], "django.views.static.serve", {
            "document_root": settings.MEDIA_ROOT,
        })
    )
