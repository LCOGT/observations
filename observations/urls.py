from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('images.views',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^search/$','search',name='search'),

    url(r'^recent/$','view_group',{'mode' : 'recent'},name='show_recent'),
    url(r'^popular/$','view_group',{'mode' : 'popular'},name='show_popular'),
    url(r'^trending/$','view_group',{'mode' : 'trending'}, name='show_trending'),

    (r'^user/(?P<userid>\d+)/$','view_user'),
    (r'^user/(?P<username>[a-zA-Z\.]+)/$','view_username'),
    (r'^user/$','index'),
    (r'^u/(?P<userid>\d+)/$','view_user'),
    (r'^u/(?P<username>[a-zA-Z\.]+)/$','view_username'),

    (r'^object/(?P<object>[a-zA-Z \+\-\.0-9]+)/$','view_object'),
    (r'^object/$','index'),
    (r'^o/(?P<object>[a-zA-Z \+\-\.0-9]+)/$','view_object'),

    (r'^category/(?P<avm>[0-9\.]+)/$','view_avm'),
    url(r'^category/(?P<category>\w+)/$','view_category', name='category'),
    url(r'^category/$','view_category_list',name='category_list'),
    (r'^c/(?P<avm>[0-9\.]+)/$','view_avm'),
    (r'^c/(?P<category>\w+)/$','view_category'),

    (r'^map/$','view_map'),

    url(r'^identity/$','identity',name='identity'),

    (r'^(?P<code>\w\w\w)/(?P<tel>\w+)/(?P<obs>\d+)/$','view_observation'),
    url(r'^(?P<code>\w\w\w)/show/$','view_site',name='site_view'),
    url(r'^(?P<code>\w\w\w)/(?P<tel>\w+)/$','view_telescope',name='telescope_view'),
    (r'^(?P<code>\w\w\w)/$','view_site'),

    url(r'^$','index', name='home'),
  ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.PRODUCTION:
    urlpatterns += patterns('',
        url(r"^static/(?P<path>.*)$", "django.views.static.serve", {"document_root": settings.STATIC_ROOT, 'show_indexes': True})
    )
