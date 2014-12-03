# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('images.views',
    url(r'^search/$','search',name="search"),
    url(r'^search\.(?P<format>\w+)$','search',name="search"),

    url(r'^recent/$','view_group',{'mode' : 'recent'},name='show_recent'),
    url(r'^recent\.(?P<format>\w+)$','view_group',{'mode' : 'recent'},name='show_recent_json'),
    url(r'^popular/$','view_group',{'mode' : 'popular'},name='show_popular'),
    url(r'^popular\.(?P<format>\w+)$','view_group',{'mode' : 'popular'},name='show_popular'),
    url(r'^trending/$','view_group',{'mode' : 'trending'},name='show_trending'),
    url(r'^trending\.(?P<format>\w+)$','view_group',{'mode' : 'trending'},name='show_trending'),

    url(r'^user/(?P<username>[a-zA-Z\.]+)/$','view_username'),
    url(r'^user/$','index'),
    url(r'^u/(?P<username>[a-zA-Z\.]+)/$','view_username'),

    url(r'^object/(?P<object>[a-zA-Z \+\-\.0-9]+)/$','view_object'),
    url(r'^object/$','index'),
    url(r'^o/(?P<object>[a-zA-Z \+\-\.0-9]+)/$','view_object'),

    url(r'^category/(?P<avm>[0-9\.]+)/$','view_avm',name='show_avm'),
    url(r'^category/(?P<category>\w+)/$','view_category',name='category_show'),
    url(r'^category/$','view_category_list',name='category_list'),
    url(r'^c/(?P<avm>[0-9\.]+)/$','view_avm'),
    url(r'^c/(?P<category>\w+)/$','view_category'),

    url(r'^map/$','view_map'),

    url(r'^identity/$','identity',name='identity'),
    (r'^admin/', include(admin.site.urls)),

    url(r'^(?P<code>\w\w\w)/(?P<tel>\w+)/(?P<obs>\d+)/$','view_observation',name='show_rtiobservation'),
    url(r'^(?P<code>\w\w\w)/show/$','view_site_slideshow', name='slideshow_site'),
    url(r'^(?P<code>\w\w\w)/$','view_site', name='show_site'),
    url(r'^(?P<code>\w\w\w)/(?P<tel>\w+)/$','view_telescope',name='show_telescope'),
    url(r'^(?P<code>\w\w\w)\.(?P<format>\w+)$','view_site',name='site_api'),
    url(r'^$','index', name='home'),
  ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.PRODUCTION:
    urlpatterns += patterns('',
        url(r"^static/(?P<path>.*)$", "django.views.static.serve", {"document_root": settings.STATIC_ROOT, 'show_indexes': True})
    )
