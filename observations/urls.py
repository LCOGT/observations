from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^observations/admin/', include(admin.site.urls)),
    (r'^observations/',include('images.urls')),
    )

if settings.DEBUG:
    urlpatterns += patterns("",
        url(r"%s(?P<path>.*)/$" % settings.MEDIA_URL[1:], "django.views.static.serve", {
            "document_root": settings.MEDIA_ROOT,
        })
    )
