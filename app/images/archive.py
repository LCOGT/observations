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
import requests
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render

from images.models import Site, Telescope
from images.users import user_look_up

import logging

logger = logging.getLogger('archive')


def get_headers(url):
    auth_data = {'username':settings.ARCHIVE_USER, 'password':settings.ARCHIVE_PASSWORD}
    response = requests.post(url, data = auth_data).json()
    token = response.get('token')
    # Store the Authorization header
    headers = {'Authorization': 'Token {}'.format(token)}
    return headers

def get_latest_data(auth_header='', num_results=30):
    base_url = settings.ARCHIVE_API
    archive_url = '%s?limit=%d&OBSTYPE=EXPOSE&RLEVEL=91' % (base_url, num_results)

    response = requests.get(archive_url, headers=auth_header).json()
    return response

def get_header_data(auth_header='', frameid=None):
    base_url = settings.ARCHIVE_API
    archive_url = '%s%s/headers/' % (base_url, frameid)

    response = requests.get(archive_url, headers=auth_header)
    if response.status_code != 200:
        raise Http404(response.json()['detail'])
    else:
        return response.json()

def recent_observations():
    headers = get_headers(settings.ARCHIVE_TOKEN_URL)
    frames = get_latest_data(auth_header=headers, num_results=6)
    return frames['results']

def get_frame_header(frameid):
    headers = get_headers(settings.ARCHIVE_TOKEN_URL)
    frames = get_header_data(headers, frameid)
    return frames['data']

def frame_lookup(request, frameid):
    frame = get_frame_header(frameid)
    user_id = frame.get('USERID','')
    user = user_look_up([user_id])
    print(user[user_id])
    site = Site.objects.get(code=frame.get('SITEID',''))
    return render(request, 'images/archive_image.html', {'obs': frame, 'observer':user[user_id], 'site':site,'frameid':frameid})
