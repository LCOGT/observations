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
from images.archive import frame_lookup, recent_observations_page
from images.rti_images import ImageDetail

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


handler500 = 'images.views.server_error'

urlpatterns = [
    url(r'^$', index, name='home'),
    url(r'^search/$',  search,name="search"),

    url(r'^recent/$', recent_observations_page, name='show_recent'),

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
    url(r'^image/(?P<pk>[0-9]+)/$', ImageDetail.as_view(), name='image-detail'),
    url(r'^admin/', include(admin.site.urls)),

  ]

if not settings.PRODUCTION:
    urlpatterns += staticfiles_urlpatterns()
