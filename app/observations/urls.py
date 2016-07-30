# -*- coding: utf-8 -*-
'''
Observations: Open access archive app for Las Cumbres Observatory Global Telescope Network
Copyright (C) 2014-2015 LCOGT

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from images.views import search, view_group, view_username, index, view_object, \
    view_avm, view_category, view_category_list, view_site, view_telescope, identity, \
    view_observation, view_site_slideshow, view_map
from images.archive import frame_lookup

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


handler500 = 'images.views.server_error'

urlpatterns = [
    url(r'^$', index, name='home'),
    url(r'^search/$',  search,name="search"),
    url(r'^search\.(?P<format>\w+)$',  search,name="search_api"),

    url(r'^recent/$', view_group,{'mode' : 'recent'},name='show_recent'),
    url(r'^recent\.(?P<format>\w+)$', view_group,{'mode' : 'recent'},name='show_recent_json'),
    url(r'^popular/$', view_group,{'mode' : 'popular'},name='show_popular'),
    url(r'^popular\.(?P<format>\w+)$', view_group,{'mode' : 'popular'},name='show_popular'),
    url(r'^trending/$', view_group,{'mode' : 'trending'},name='show_trending'),
    url(r'^trending\.(?P<format>\w+)$', view_group,{'mode' : 'trending'},name='show_trending'),

    url(r'^user/(?P<username>[a-zA-Z0-9_.+-@]+)/?$', view_username,name='show_user'),
    url(r'^user/$', index),
    url(r'^u/(?P<username>\w+)/$', view_username),

    url(r'^object/(?P<object>[a-zA-Z \+\-\.0-9]+)/$', view_object),
    url(r'^object/$', index),
    url(r'^o/(?P<object>[a-zA-Z \+\-\.0-9]+)/$', view_object),

    url(r'^category/(?P<avm>[0-9\.]+)/$', view_avm,name='show_avm'),
    url(r'^category/(?P<category>\w+)/$', view_category,name='category_show'),
    url(r'^category/$', view_category_list,name='category_list'),
    url(r'^c/(?P<avm>[0-9\.]+)/$', view_avm),
    url(r'^c/(?P<category>\w+)/$', view_category),

    url(r'^map/$', view_map),

    url(r'^frame/(?P<frameid>[0-9]+)/$', frame_lookup, name='frame'),
    url(r'^identity/$', identity,name='identity'),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^(?P<code>\w\w\w)/(?P<tel>\w+)/(?P<obs>\d+)/$', view_observation,name='show_rtiobservation'),
    url(r'^(?P<code>\w\w\w)/show/$', view_site_slideshow, name='slideshow_site'),
    url(r'^(?P<code>\w\w\w)/$', view_site, name='show_site'),
    url(r'^telescope/(?P<code>\w\w\w)/(?P<encid>\w+)/(?P<tel>\w+)/$', view_telescope,name='show_telescope'),
    url(r'^(?P<code>\w\w\w)\.(?P<format>\w+)/$', view_site,name='site_api'),
  ]

if not settings.PRODUCTION:
    urlpatterns += staticfiles_urlpatterns()
