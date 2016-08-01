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
from datetime import date, timedelta, datetime
from django.conf import settings
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.sites.models import Site as DjSite
from django.core import serializers, urlresolvers
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db import connections
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.utils.encoding import smart_unicode
from email.utils import parsedate_tz
from images.forms import SearchForm
from images.models import Site, Telescope, Filter, Image, ObservationStats, wistime_format
from images.utils import parsetime, dmstodegrees, hmstodegrees, hmstohours, datestamp, \
    filter_list, filter_props, filter_link, filter_name, hexangletodec, l, binMonths
from images.archive import recent_observations, search_archive, get_auth_headers, \
    search_archive_data
from images.lookups import categories, categorylookup
from images.users import user_look_up, look_up_org_names
from string import replace
import json
import math
import re
import requests
import logging

logger = logging.getLogger('images')

n_per_line = 6
n_per_page = 18
base_url = "http://lcogt.net/observations/"

def server_error(request):
    # one of the things 'render' does is add 'STATIC_URL' to
    # the context, making it available from within the template.
    response = render(request, '500.html')
    response.status_code = 500
    return response


def index(request):

    sites = Site.objects.all()
    telescopes = Telescope.objects.all()

    latest = recent_observations()

    obstats = ObservationStats.objects.all().order_by('-weight')[:n_per_line]
    obs = []
    for o in obstats:
        obs.append(o.image)
    trending = build_observations(obs)

    obstats = ObservationStats.objects.all().order_by('-views')[:n_per_line]
    obs = []
    for o in obstats:
        obs.append(o.image)
    popular = build_observations(obs)

    return render(request, 'images/index.html', {'latest': latest,
                                                    'trending': trending,
                                                    'popular': popular,
                                                    'sites': sites,
                                                    'telescopes': telescopes,
                                                    'categories': categories})


def view_group(request, mode, format=None):
    input = input_params(request)
    sites = Site.objects.all()

    if(mode == "recent"):
        obs = build_recent_observations(n_per_page)
        input['title'] = "Recent Observations from LCOGT"
        input['link'] = 'recent'
        input['live'] = 300
        input[
            'description'] = 'Recent observations from the Las Cumbres Observatory Global Telescope'
    elif(mode == "popular"):
        obstats = ObservationStats.objects.all().order_by(
            '-views')[:n_per_page]
        n = obstats.count()
        obs = []
        for o in obstats:
            obs.append(o.image)
        obs = build_observations(obs)
        input['title'] = "All-time Most Viewed Observations at LCOGT"
        input['link'] = 'popular'
        input[
            'description'] = 'Most popular observations from the Las Cumbres Observatory Global Telescope'
    elif(mode == "trending"):
        obstats = ObservationStats.objects.all().order_by(
            '-weight')[:n_per_page]
        n = obstats.count()
        obs = []
        for o in obstats:
            obs.append(o.image)
        obs = build_observations(obs)
        input['title'] = "Trending Observations at LCOGT"
        input['link'] = 'trending'
        input[
            'description'] = 'Trending observations from the Las Cumbres Observatory Global Telescope'

    input['observations'] = len(obs)
    input['perpage'] = n_per_page

    if input['doctype'] == "json" or format == 'json':
        return view_json(request, build_observations_json(obs), input)
    elif input['doctype'] == "kml":
        return view_kml(request, obs, input)
    elif input['doctype'] == "rss":
        return view_rss(request, obs, input)
    else:
        data = {'input': input, 'link': input[
            'link'], 'obs': obs, 'n': len(obs)}
        if input['slideshow']:
            return render_to_response('images/slideshow.html', data, context_instance=RequestContext(request))
        else:
            return render_to_response('images/group.html', data, context_instance=RequestContext(request))


def since(request):
    since = request.GET.get('since', '')
    if since != '':
        try:
            sd = parsedate_tz(since)
            sd = "%s%02d%02d%02d%02d%02d" % (
                sd[0], sd[1], sd[2], sd[3], sd[4], sd[5])
        except:
            sd = ''
    return sd


def search_rtiarchive(form):
    obs = []
    n = -1
    obs = Image.objects.all()
    if form['query']:
        query_string = form['query'].replace('(','').replace(')','')
        obs = obs.filter(
            objectname__iregex=r'(^| )%s([^\w0-9]+|$)' % query_string)
    if form['sites'] in ('ogg', 'coj'):
        obs = obs.filter(telescope__site__code=form['sites'])
    if form['filters']:
        obs = obs.filter(filter=form['filters'])
    if form['startdate'] and form['enddate']:
        obs = obs.filter(dateobs__gte=form['startdate'], dateobs__lte=form['enddate'])
    if form['enddate']:
        obs = obs.filter(dateobs__lte=form['enddate'])
    if form['exposure']:
        try:
            form['exposure'] = float(form['exposure'])
            if(form['exposurecondition'] == 'gt'):
                obs = obs.filter(exposuresecs__gt=form['exposure'])
            elif(form['exposurecondition'] == 'lt'):
                obs = obs.filter(exposuresecs__lt=form['exposure'])
            else:
                obs = obs.filter(exposuresecs=form['exposure'])
        except:
            form['exposure'] = 0

    obs = obs.order_by('-dateobs')
    return obs


def search(request, format=None):
    page_data = input_params(request)
    if not request.GET:
        form = SearchForm()
        return render(request, 'images/search.html', {'form': form})
    else:
        #page_data ={}
        form = SearchForm(request.GET)
        if form.is_valid():
            lastobs = request.GET.get('lastobs', None)
            if lastobs:
                if "T" in lastobs:
                    lastobs = datetime.strptime(lastobs, "%Y-%m-%dT%H:%M:%S")
                else:
                    try:
                        lastobs = datetime.strptime(lastobs, "%Y%m%d%H%M%S")
                    except:
                        lastobs = datetime.utcnow()
                form.cleaned_data['enddate'] = lastobs
            elif not form.cleaned_data['enddate']:
                form.cleaned_data['enddate'] = datetime.utcnow()
            obs, n, onlyrti, offset = fetch_observations(form.cleaned_data, lastobs)
            page_data['offset'] = offset
            page_data['onlyrti'] = onlyrti
            page_data['lastobs'] = lastobs
            page_data['description'] = 'Search results (LCOGT)'
            page_data['searchstring'] = request.GET.get('query', None)

            if page_data['doctype'] == "json" or format == 'json':
                return view_json(request, build_observations_json(obs), page_data)
            elif page_data['doctype'] == "kml":
                return view_kml(request, obs, page_data)
            elif page_data['doctype'] == "rss":
                return view_rss(request, obs, page_data)
            else:
                page_data['n'] = n
                if n == 0:
                    page_data['form'] = form
                elif obs['archive']:
                    page_data['firstobs'] = obs['archive'][0]['DATE_OBS']
                elif obs['rti'] and not obs['archive']:
                    page_data['firstobs'] = obs['rti'][0]['dateobs']

                page_data['obs'] = obs
                if page_data['slideshow']:
                    return render(request, 'images/slideshow.html', page_data)
                else:
                    return render(request, 'images/search.html', page_data)
        else:
            return render(request, 'images/search.html', {'form': form})


def fetch_observations(data, lastobs):
    obs = {'archive' : [], 'rti' : []}
    onlyrti = False
    rti_n = 0
    # earliest_obs = search_include_framedb(data['query'])
    offset = data.get('offset', 0)
    if not offset:
        offset = 0
    new_offset = offset+30
    if not data['enddate'] or data['enddate'] > datetime(2014, 4, 1):
        obs_archive  = search_archive(data, offset)
        if obs_archive:
            obs['archive'] = obs_archive['results']
            total_n = obs_archive['count']

    if len(obs['archive']) < n_per_page:
        # Fetch RTI images
        rti_obs = search_rtiarchive(data)
        rti_n = rti_obs.count()
        rti_obs = rti_obs[offset:new_offset]

        obs['rti'] = build_observations(rti_obs)
        total_n = len(obs['archive']) + rti_n
    if total_n == rti_n:
        onlyrti = True
    if obs['archive']:
        lastobs = obs['archive'][-1]['DATE_OBS']
    elif obs['rti'] and not obs['archive']:
        lastobs = obs['rti'][-1]['dateobs']
    else:
        lastobs = None
    return obs, total_n, onlyrti, new_offset


def search_include_framedb(objectname):
    query = "/find?tagid__in=LCOEPO,FTP&limit=1&order_by=date_obs&object_name=%s" % objectname
    details = framedb_lookup(query)
    if details:
        return details[0]['date_obs']
    else:
        return None


def get_site_data(code):
    # Store the TAG IDs in a config not here
    qstring = "SITEID=%s&limit=30&OBSTYPE=EXPOSE&RLEVEL=91" % (code)
    headers = get_auth_headers(settings.ARCHIVE_TOKEN_URL)
    obs = search_archive_data(qstring, headers)

    data = {'n': obs['count'],
            'obs': obs['results']}
    return data


def view_site(request, code, format=None):
    # Check we have a valid site
    if Site.objects.filter(code=code).count() == 0:
        raise Http404
    input = input_params(request)
    data = get_site_data(code)
    obs = data['obs']
    site = Site.objects.get(code=code)
    input['observations'] = len(obs)
    input['title'] = site.name
    input['link'] = site.code
    input['description'] = 'Observations from telescopes at ' + \
        site.name + ' (LCOGT)'
    input['perpage'] = n_per_page
    if input['doctype'] == "json" or format == 'json':
        return view_json(request, build_observations_json(obs), input)
    elif input['doctype'] == "kml" or format == 'kml':
        return view_kml(request, obs, input)
    elif input['doctype'] == "rss" or format == 'rss':
        return view_rss(request, obs, input)
    else:
        data['sites'] = Site.objects.all()
        data['site'] = site
        data['telescopes'] = Telescope.objects.filter(site=site)
        return render(request, 'images/site.html', data)


def view_site_slideshow(request, code, format=None):
    if code:
        site = Site.objects.get(code=code)
        return render(request, 'images/slideshow.html', {'site': site})
    else:
        return Http404


def old_view_site(request, code):
    input = input_params(request)
    sites = Site.objects.exclude(code=code)

    try:
        site = Site.objects.get(code=code)
    except ObjectDoesNotExist:
        return unknown(request)

    telescopes = Telescope.objects.filter(site=site)

    obs = []
    n = 0
    if site.code == 'ogg' or site.code == 'coj':
        obs = Image.objects.filter(
            telescope__in=telescopes.values_list('id', flat=True)).order_by('-obsdate')
        n = obs.count()

    input['observations'] = n
    input['title'] = site.name
    input['link'] = site.code
    input['description'] = 'Observations from telescopes at ' + \
        site.name + ' (LCOGT)'
    input['perpage'] = n_per_page
    input['pager'] = build_pager(request, n)

    if(n > n_per_page):
        obs = build_observations(
            obs[input['pager']['start']:input['pager']['end']])
    else:
        obs = build_observations(obs)

    if input['doctype'] == "json":
        return view_json(request, build_observations_json(obs), input)
    elif input['doctype'] == "kml":
        return view_kml(request, obs, input)
    elif input['doctype'] == "rss":
        return view_rss(request, obs, input)
    else:
        data = {'sites': sites, 'site': site, 'telescopes': telescopes, 'n': n, 'obs':
                obs, 'input': input, 'link': input['link'], 'pager': input['pager']['html']}
        if input['slideshow']:
            return render_to_response('images/slideshow.html', data, context_instance=RequestContext(request))
        else:
            return render_to_response('images/site.html', data, context_instance=RequestContext(request))


def view_telescope(request, code, tel, encid):
    input = input_params(request)

    sites = Site.objects.exclude(code=code)
    site = Site.objects.get(code=code)
    try:
        telescope = Telescope.objects.get(site=site, code=tel, enclosure=encid)
    except ObjectDoesNotExist:
        return unknown(request)

    telescopes = Telescope.objects.filter(site=site).exclude(code=tel)

    obs = []
    n = 0
    if site.code == 'ogg' or site.code == 'coj':
        obs = Image.objects.filter(
            telescope=telescope.id).order_by('-dateobs')
        n = obs.count()

    input['observations'] = n
    input['title'] = telescope.name
    input['link'] = site.code + '/' + telescope.code
    input['description'] = 'Observations from ' + telescope.name + ' (LCOGT)'
    input['perpage'] = n_per_page
    input['pager'] = build_pager(request, n)

    if(n > n_per_page):
        obs = build_observations(
            obs[input['pager']['start']:input['pager']['end']])
    else:
        obs = build_observations(obs)

    if input['doctype'] == "json":
        return view_json(request, build_observations_json(obs), input)
    elif input['doctype'] == "kml":
        return view_kml(request, obs, input)
    elif input['doctype'] == "rss":
        return view_rss(request, obs, input)
    else:
        data = {'telescope': telescope, 'sites': sites, 'telescopes': telescopes, 'n': n,
                'obs': obs, 'input': input, 'link': input['link'], 'pager': input['pager']['html']}
        if input['slideshow']:
            return render_to_response('images/slideshow.html', data, context_instance=RequestContext(request))
        else:
            return render_to_response('images/telescope.html', data, context_instance=RequestContext(request))


def view_object(request, object):
    input = input_params(request)

    # Remove trailing full-stop
    object = re.sub(r"\.json$", "", object)
    object = re.sub(r"\.kml$", "", object)
    original = object
    object = object.replace('+', ' ')

    page = int(request.GET.get('page', '1'))
    try:
        # Only allow the major category to be provided by the user. Should
        # distinguish Jupiter from Ghost of Jupiter
        avmcode = int(request.GET.get('avm', 0)[0])
    except:
        avmcode = ''

    # On the first page (HTML version only) we do a lookUP
    if page == 1 and input['doctype'] == "html":
        headers = {'Accept': 'application/xml',
                   'Content-Type': 'application/xml',
                   'User-Agent' : 'LCOGT/1.0'}
        url='http://lcogt.net/lookUP/xml/?name=%s' % original
        # Allow 3 seconds for timeout
        try:
            f = requests.get(url, timeout=5, headers=headers)
            xml = f.content
        except:
            return unknown(request)
        service = re.search('service href="([^\"]*)">([^\<]*)<', xml)
        if type(service) == 'NoneType':
            return unknown(request)
        try:
            service = {'name': service.group(2), 'url': service.group(1)}
        except:
            return unknown(request)
        ra = re.search('<ra ([^\>]*)>([^\<]*)<', xml)
        if type(ra) == 'NoneType':
            ra = ""
        try:
            ra = float(ra.group(2))
        except:
            ra = 0.0
        dec = re.search('<dec ([^\>]*)>([^\<]*)<', xml)
        if type(dec) == 'NoneType':
            dec = ""
        try:
            dec = float(dec.group(2))
        except:
            dec = 0.0
        if avmcode == '' or avmcode < 1 or avmcode > 7:
            m = re.search('avmcode="([^\"]*)"', xml)
            try:
                avmcode = m.group(1)
                if len(avmcode) > 0:
                    cats = avmcode.split(';')
                    if len(cats) > 0:
                        avmcode = cats[-1]
                        if avmcode in categorylookup:
                            avm = categorylookup[avmcode]
                        else:
                            avm = avmcode
                    else:
                        avm = "Unknown"
                        avmcode = ""
                else:
                    avm = "Unknown"
                    avmcode = ""
            except:
                avm = "Unknown"
                avmcode = ""
        else:
            try:
                avmcode = str(avmcode)
                avm = categorylookup[avmcode]
            except:
                avm = "Unknown"
                avmcode = ""
        object = {'name': object, 'ra': ra, 'dec': dec,
                  'service': service, 'avm': {'name': avm, 'code': avmcode}}
    else:
        try:
            avmcode = str(avmcode)
            avm = categorylookup[avmcode]
        except:
            avm = "Unknown"
            avmcode = ""
        object = {'name': object, 'avm': {'name': avm, 'code': avmcode}}

    try:
        obser = Image.objects.all().filter(
            objectname__iregex=r'(^| )%s([^\w0-9]+|$)' % object['name']).order_by('-dateobs')
        # If we have an AVM code we can use it to limit to objects of the
        # correct type
        if object['avm']['code'] != "":
            obser = obser.filter(
                observationstats__avmcode__regex=r'(^|;)%s' % object['avm']['code'])
        a = obser.values('username')
        if a:
            u = user_look_up(a[0]['username'])
            input['mostobservedby'] = {
                'name': u, 'id': a[0]['username'], 'count': a[0]['count']}
        else:
            u = ""

    except ObjectDoesNotExist:
        return unknown(request)

    n = obser.count()

    input['observations'] = n
    input['title'] = object['name']
    input['link'] = 'object/' + original
    input['description'] = 'Observations of ' + object['name'] + ' (LCOGT)'
    input['perpage'] = n_per_page
    input['pager'] = build_pager(request, n, object['avm']['code'])

    if(n > n_per_page):
        obs = build_observations(
            obser[input['pager']['start']:input['pager']['end']])
    else:
        obs = build_observations(obser)

    if page == 1:
        # Bin the observations by month for the past year
        input = binMonths(obser, input, 12)

        b = [0, 1, 2, 3, 4]
        # Calculate how many in each bin
        ns = [{'label': 'Under 1 second', 'max': 1, 'observations': 0}, {'label': '1-10 seconds', 'min': 1, 'max': 10, 'observations': 0}, {'label': '10-30 seconds', 'min':
                                                                                                                                            10, 'max': 30, 'observations': 0}, {'label': '30-90 seconds', 'min': 30, 'max': 90, 'observations': 0}, {'label': 'Over 90 seconds', 'min': 90, 'observations': 0}]
        obser = obser.filter(exposure__gt=1)
        b[0] = n - len(obser)
        obser = obser.filter(exposure__gt=10)
        b[1] = n - b[0] - len(obser)
        obser = obser.filter(exposure__gt=30)
        b[2] = n - b[0] - b[1] - len(obser)
        obser = obser.filter(exposure__gt=90)
        b[3] = n - b[0] - b[1] - b[2] - len(obser)
        b[4] = len(obser)

        for i in range(5):
            ns[i]['observations'] = b[i]

        input['exposure'] = ns
        input['exposuremax'] = max(b)
    else:
        ns = []

    uri = ""
    mostrecent = ""

    if len(obs) > 0:
        mostrecent = obs[0]['dateobs']

    if input['doctype'] == "json":
        return view_json(request, build_observations_json(obs), input)
    elif input['doctype'] == "kml":
        return view_kml(request, obs, input)
    elif input['doctype'] == "rss":
        return view_rss(request, obs, input)
    else:
        data = {'n': n, 'input': input, 'object': object, 'mostrecent': mostrecent,
                'obs': obs, 'link': input['link'], 'pager': input['pager']['html'], 'uri': uri}
        if input['slideshow']:
            return render_to_response('images/slideshow.html', data, context_instance=RequestContext(request))
        else:
            return render_to_response('images/object.html', data, context_instance=RequestContext(request))


def view_username(request, username):
    input = input_params(request)

    u = user_look_up(username)
    org_name = u.get(username, 'Unknown')

    obs = Image.objects.filter(username=username).order_by('-dateobs')
    if obs:
        org_name = obs[0].observer
    n = obs.count()

    input['observations'] = n
    input['title'] = org_name
    input['link'] = 'user/' + username
    input['description'] = 'Observations by ' + org_name + ' (LCOGT)'
    input['perpage'] = n_per_page
    input['pager'] = build_pager(request, n)

    if(n > n_per_page):
        obs = build_observations(
            obs[input['pager']['start']:input['pager']['end']])
    else:
        obs = build_observations(obs)

    try:
        uri = Schooluri.objects.get(usr_id=u).uri
    except:
        uri = ""

    mostrecent = ""

    if len(obs) > 0:
        mostrecent = obs[0]['dateobs']

    if input['doctype'] == "json":
        return view_json(request, build_observations_json(obs), input)
    elif input['doctype'] == "kml":
        return view_kml(request, obs, input)
    elif input['doctype'] == "rss":
        return view_rss(request, obs, input)
    else:
        data = {'user': org_name, 'n': n, 'mostrecent': mostrecent, 'obs': obs,
                'link': input['link'], 'pager': input['pager']['html'], 'uri': uri}
        if input['slideshow']:
            return render_to_response('images/slideshow.html', data, context_instance=RequestContext(request))
        else:
            return render_to_response('images/user.html', data, context_instance=RequestContext(request))


def view_category_list(request):
    input = input_params(request)

    obs = []
    obs = build_observations(obs)

    if input['doctype'] == "html":
        data = {'categorylookup': categorylookup, 'category': categories,
                'n': 0, 'obs': obs, 'previous': '', 'next': ''}
        return render_to_response('images/categorylist.html', data, context_instance=RequestContext(request))
    else:
        return render_to_response('404.html', data, context_instance=RequestContext(request))


def view_category(request, category):
    input = input_params(request)

    found = False
    avm = 0
    for c in categories:
        avm = avm + 1
        if c['link'] == category:
            found = True
            cat = c
            break

    if not(found):
        return unknown(request)

    n = 0
    try:
        obstats = ObservationStats.objects.filter(avmcode__startswith='%s' % avm).order_by(
            '-image__dateobs')  # .order_by('-views')
        n = obstats.count()
    except ObjectDoesNotExist:
        return unknown(request)

    input['observations'] = n
    input['title'] = 'Category: ' + categories[avm - 1]['name']
    input['link'] = 'category/' + categories[avm - 1]['link']
    input['description'] = 'Category: ' + \
        categories[avm - 1]['name'] + ' (LCOGT)'
    input['perpage'] = n_per_page
    input['pager'] = build_pager(request, n)

    # Work out the AVM categories above and below the current level
    input = getCategoryLevel(avm, input)

    if(n > n_per_page):
        obstats = obstats[input['pager']['start']:input['pager']['end']]

    obs = []
    for o in obstats:
        obs.append(o.image)

    obs = build_observations(obs)

    if input['doctype'] == "json":
        return view_json(request, build_observations_json(obs), input)
    elif input['doctype'] == "kml":
        return view_kml(request, obs, input)
    elif input['doctype'] == "rss":
        return view_rss(request, obs, input)
    else:
        data = {'input': input, 'categories': categories, 'category': categories[
            avm - 1]['name'], 'n': n, 'obs': obs, 'link': input['link'], 'pager': input['pager']['html']}
        if input['slideshow']:
            return render_to_response('images/slideshow.html', data, context_instance=RequestContext(request))
        else:
            return render_to_response('images/category.html', data, context_instance=RequestContext(request))


def view_avm(request, avm):
    input = input_params(request)

    # Remove trailing full-stop
    avm = re.sub(r"\.$", "", avm)
    avmtemp = re.sub(r"\.", "\\.", avm)

    n = 0
    obstats = ObservationStats.objects.filter(avmcode__regex=r'(^|;)%s' % avmtemp).order_by(
        '-image__dateobs')  # .order_by('-views')
    n = obstats.count()

    if avm in categorylookup:
        category = categorylookup[avm]
    else:
        category = avm

    input['observations'] = n
    input['title'] = 'Category: ' + category
    input['link'] = 'category/' + avm
    input['description'] = 'Category: ' + category + ' (LCOGT)'
    input['perpage'] = n_per_page
    input['pager'] = build_pager(request, n)

    # Work out the AVM categories above and below the current level
    input = getCategoryLevel(avm, input)

    if(n > n_per_page):
        obstats = obstats[input['pager']['start']:input['pager']['end']]

    obs = []
    for o in obstats:
        obs.append(o.image)
    obs = build_observations(obs)

    if input['doctype'] == "json":
        return view_json(request, build_observations_json(obs), input)
    elif input['doctype'] == "kml":
        return view_kml(request, obs, input)
    elif input['doctype'] == "rss":
        return view_rss(request, obs, input)
    else:
        data = {'input': input, 'categories': categories, 'category': category,
                'n': n, 'obs': obs, 'link': input['link'], 'pager': input['pager']['html']}
        if input['slideshow']:
            return render_to_response('images/slideshow.html', data, context_instance=RequestContext(request))
        else:
            return render_to_response('images/category.html', data, context_instance=RequestContext(request))


def view_map(request):
    input = input_params(request)

    sites = Site.objects.all()
    telescopes = Telescope.objects.all()

    dt = datetime.utcnow() - timedelta(30)

    sites = Site.objects.all()
    telescopes = Telescope.objects.all()

    obs = Image.objects.filter(
        dateobs__gte=dt).order_by('-dateobs')
    n = obs.count()

    input['observations'] = 0
    input['title'] = 'Heat Map'
    input['link'] = 'map'
    input['description'] = 'Observations in the past month (LCOGT)'
    input['perpage'] = n_per_page
    input['pager'] = build_pager(request, n)

    ras = []
    dcs = []
    for o in obs:
        ras.append(round(o.ra * 15 * 100) / 100)
        dcs.append(round(o.dec * 100) / 100)

    # if input['doctype'] == "json":
    #     return view_json(request,build_observations_json(obs),input)
    # elif input['doctype'] == "kml":
    #     return view_kml(request,obs,input)
    # elif input['doctype'] == "rss":
    #     return view_rss(request,obs,input)
    # else:
    data = {'ras': ras, 'dcs': dcs, 'link': input[
        'link'], 'input': input, 'sites': sites, 'telescopes': telescopes}
    return render_to_response('images/map.html', data, context_instance=RequestContext(request))


def view_observation(request, code, tel, obs):
    input = input_params(request)

    try:
        telescope = Telescope.objects.get(
            site=Site.objects.get(code=code), code=tel)
    except ObjectDoesNotExist:
        return unknown(request)

    try:
        obs = Image.objects.filter(imageid=obs)
    except:
        return broken(request, "There was a problem finding the requested observation in the database.")

    if len(obs) < 1:
        return broken(request, "There was a problem finding the requested observation in the database.")

    # Let's try to work out if this is from a crawler. If not we'll assume a
    # real person.
    BotNames = ['alexa', 'appie', 'Ask Jeeves', 'Baiduspider', 'bingbot', 'Butterfly', 'crawler', 'facebookexternalhit', 'FAST', 'Feedfetcher-Google', 'Firefly', 'froogle', 'Gigabot', 'girafabot', 'Googlebot', 'InfoSeek', 'inktomi', 'looksmart', 'Me.dium', 'Mediapartners-Google',
                'msnbot', 'NationalDirectory', 'rabaz', 'Rankivabot', 'Scooter', 'Slurp', 'Sogou web spider', 'Spade', 'TechnoratiSnoop', 'TECNOSEEK', 'Teoma', 'TweetmemeBot', 'Twiceler', 'Twitturls', 'URL_Spider_SQL', 'WebAlta Crawler', 'WebBug', 'WebFindBot', 'www.galaxy.com', 'ZyBorg']
    request.is_crawler = False
    try:
        user_agent = request.META.get('HTTP_USER_AGENT', None)
        for botname in BotNames:
            if botname in user_agent:
                request.is_crawler = True
    except:
        user_agent = ''

    # Update stats
    obstats = ObservationStats.objects.filter(image=obs[0])
    if obstats:
        # Only update the number of views if it isn't a crawler
        if (request.is_crawler):
            addition = 0
        else:
            addition = 1
        obstats[0].views = obstats[0].views + addition
        views = obstats[0].views
        delta = datetime.utcnow() - obstats[0].lastviewed
        # 98 = 2*(7^2) <- where 7 days is the sigma for the Gaussian function exp(-datediff^2/(2*sigma^2))
        # 0.5 = 2*(0.5^2) <- where 0.5 days is the sigma for the Gaussian function
        # obstats[0].weight*math.exp(-math.pow((delta.seconds)/86400.,2)/98.)
        obstats[0].weight = addition + obstats[0].weight * \
            math.exp(-math.pow((delta.seconds) / 86400., 2) / 0.5)
        obstats[0].lastviewed = datetime.utcnow()
    else:
        obstats = [ObservationStats(
            image=obs[0], views=1, weight=1, lastviewed=datetime.utcnow())]
        views = 1
    obstats[0].save()

    obs = build_observations(obs)
    otherobs = get_observation_stream(obs[0])

    # Check for AVM code
    if not(obstats[0].avmcode):
        headers = {'Accept': 'application/xml',
                   'Content-Type': 'application/xml',
                   'User-Agent' : 'LCOGT/1.0'}
        url='http://lcogt.net/lookUP/xml/?name=%s' % obs
        try:
            f = requests.get(url, timeout=5, headers=headers)
            xml = f.content
            m = re.search('avmcode="([^\"]*)"', xml)
            n = re.search('service href="([^\"]*)"', xml)
            if(m):
                try:
                    obstats[0].avmcode = m.group(1)
                except ObjectDoesNotExist:
                    obstats[0].avmcode = "0.0"
            else:
                obstats[0].avmcode = "0.0"
            if(n):
                obstats[0].moreurl = n.group(1)
            obstats[0].save()
        except:
            obstats[0].avmcode = "0"

    tag = '0'

    obs[0]['views'] = views

    if(obstats[0].avmcode != "0" and obstats[0].avmcode != "0.0"):
        cats = obstats[0].avmcode.split(';')
        if len(cats) > 0:
            cats = cats[-1]
        obs[0]['avmcode'] = cats
        if cats in categorylookup:
            obs[0]['avmname'] = categorylookup[cats]
        else:
            obs[0]['avmname'] = obstats[0].avmcode

    if input['doctype'] == "kml":
        input['title'] = 'Observation of ' + obs[0]['objectname']
        return view_kml(request, obs, input)

    # Get FITS information only if not a crawler
    if (request.is_crawler):
        filters = []
    else:
        params = {'tag': tag,
                  'username': obs[0]['username'],
                  'requestids': obs[0]['requestids'],
                  'dateobs': obs[0]['dateobs'],
                  'telescope': obs[0]['telescope'],
                  'filter': obs[0]['filter']}
        filters = get_sci_fits(params)

    if input['doctype'] == "json":
        return view_json(request, build_observations_json(obs), input)
    return render(request,'images/observation.html', {'n': 1,
                                                          'telescope': telescope,
                                                          'obs': obs[0],
                                                          'otherobs': otherobs,
                                                          'filters': filters,
                                                          'base': base_url,
                                                          'framedb_obs': False})


def get_sci_fits(params):
    telids = {'ogg': 1, 'coj': 2}
    telid = telids.get(params['telescope'].site.code, '')
    url = 'http://sci-archive.lcogt.net/cgi-bin/oc_search?op-centre=UKRTOC&user-id=%s&date=%s&telescope=ft%s' % (
        params['username'], params['dateobs'], telid)
    rids = params['requestids'].split(',')
    filters = []
    if rids:
        if len(rids) == 3:
            ids = ['b', 'g', 'r']
            names = ['Blue', 'Green', 'Red']
            # filters = [{ 'id':'b','name': 'Blue','fits':'','img':'' },
            #           { 'id':'g','name': 'Green','fits':'','img':'' },
            #           { 'id':'r','name': 'Red','fits':'','img':'' }]
        if len(rids) == 1:
            ids = ['f']
            names = [params['filter']]
            #filters = [{ 'id':'f','name': obs[0]['filter'],'fits':'','img':'' }]

        for rid in range(0, len(rids)):
            sci_url = '%s&obs-id=%s' % (url, rids[rid])

            # Allow 6 seconds for timeout
            try:
                f = requests.get(url=sci_url, timeout=6)
                xml = f.content

                jpg = re.search('file-jpg type=\"url\">([^\<]*)<', xml)
                fit = re.search('file-hfit type=\"url\">([^\<]*)<', xml)
                if jpg or fit:
                    tmp = {'id': ids[rid], 'name': names[rid],
                           'fullname': filter_name(names[rid])}
                    if jpg:
                        tmp['img'] = jpg.group(1)
                    if fit:
                        tmp['fits'] = fit.group(1)
                    filters.append(tmp)
            except:
                filters.append({'img': '', 'fits': ''})
    return filters

def get_framedb_fits(obs):
    '''
    return a download link to the observation along with the filter name
    First it checks if the data is in Archive and if not returns a framedb link
    '''
    date = obs["date_obs"][0:10]
    url = get_archive_fits(
        obs['origname'], date, obs['propid'], obs['tracknum'], obs['reqnum'])
    img = "http://data.lcogt.net/thumbnail/%s/?height=1000&width=1000&label=0" % obs[
        'origname'][:-5]
    if not url:
        url = 'http://data.lcogt.net/download/frame/%s' % obs['origname']
    filter_info = {
        'id': obs['reqnum'],
        'name': obs['filter_name'],
        'fullname': obs['filter_name'],
        'img': img,
        'fits': url
    }
    # Make an array to match the format returned by RTI/sci-archive
    filters = [filter_info]
    return filters

def get_archive_fits(origname, date, propid, tracknum, reqnum):
    qstring = "&propid=%s&selcols=filehand,tracknum,reqnum&mission=lcogt&constraints=(date_obs+between+to_date('%s 00:01','YYYY-MM-DD HH24:MI')+and+to_date('%s 23:59','YYYY-MM-DD HH24:MI')+and+tracknum+in+('%s'))" % (
        propid, date, date, tracknum)
    lookup_url = ARCHIVE_API + qstring.replace(" ", "%20")
    try:
        resp = requests.get(lookup_url, timeout=10)
    except:
        return False
    text = resp.content
    vals = [x.strip() for x in text.split(
        "\n") if x[:1] != '\\' and x[:1] != '' and x[:1] != '|']
    files = [v.split()[0] for v in vals]
    filename = origname[:-9]
    datafile = [f for f in files if filename in f]
    if datafile:
        return dl_url + datafile[0]
    else:
        return False


def get_observation_stream(obs):

    ob = Image.objects.filter(username=obs['username'])
    o = ob.values()
    num = len(o)

    n = 0
    # Find the index of the current image
    for index, item in enumerate(o):
        if(item['imageid'] == obs['imageid']):
            n = index
            break
    # Find the images in the user's stream to either side
    start = n - 3
    end = start + 6
    if end > num:
        end = num
    start = end - 6
    if start < 0:
        start = 0
    o = build_observations(ob[start:end])

    num = end - start
    otherobs = []
    i = 0
    for item in reversed(o):
        tmp = {'url': item['link_obs'], 'thumb': item['thumbnail'], 'title': item[
            'objectname'], 'date': item['dateobs'], 'class': ''}
        if(i == 0):
            tmp['class'] = 'left'
        if(i == num - 1):
            tmp['class'] = 'right'
        if(item['imageid'] == obs['imageid']):
            tmp['class'] = 'current'
        otherobs.append(tmp)
        i = i + 1

    return otherobs


def input_params(request):
    doctype = "html"
    callback = ""
    slideshow = False

    path = request.path_info.split('/')
    if path[len(path) - 1] == "":
        path.pop()
    bits = path[len(path) - 1].rsplit('.', 1)

    if len(bits) > 1:
        doctype = bits[1]
        path[len(path) - 1] = bits[0]

    mimetype = "text/html"

    # If the user has requested a particular mime type we'll use that
    # try:
    #   reqtype = request.META.get('CONTENT_TYPE', 'text/html')
    #   if reqtype == 'application/json':
    #       doctype = 'json'
    #   elif reqtype == 'application/vnd.google-earth.kml+xml':
    #       doctype = 'kml'
    #   elif reqtype == 'application/xml':
    #       doctype = 'rss'
    #   elif reqtype == 'application/rdf+xml':
    #       doctype = 'rdf'
    #   else:
    #       doctype = 'html'
    # except:
    #   reqtype = ''

    if doctype == 'json':
        callback = request.GET.get('callback', '')
        # Sanitise the callback to stop any dodgy Javascript
        callback = re.sub(r"[^\w]", '', callback)
        mimetype = 'application/json'
    elif doctype == 'kml':
        mimetype = 'application/vnd.google-earth.kml+xml'
    elif doctype == 'rss':
        mimetype = 'application/xml'
    elif doctype == 'rdf':
        mimetype = 'application/rdf+xml'

    if path[len(path) - 1] == "show":
        slideshow = True

    query = request.META.get('QUERY_STRING', '')
    url_path = DjSite.objects.get_current().domain

    return {'doctype': doctype, 'mimetype': mimetype, 'callback': callback, 'path': path, 'slideshow': slideshow, 'query': query, 'site_path': url_path}


def getCategoryLevel(avm, input):

    # Work out the AVM categories above and below the current level
    input['avmup'] = []
    input['avmdn'] = []

    if(avm):
        avm = str(avm)
        avmup = avm
        if(re.search(r"\.", avmup)):
            while(re.search(r"\.", avmup)):
                avmup = re.sub(r"\.[0-9]$", "", avmup)
                try:
                    nm = categorylookup[avmup]
                except:
                    nm = ""
                input['avmup'].insert(0, {'code': avmup, 'name': nm})
        for c in categorylookup:
            if(re.match(avm, c) and c != avm and len(c) == len(avm) + 2):
                input['avmdn'].append({'code': c, 'name': categorylookup[c]})

    return input

def recent_frames(proposal_id, datestamp=None, num_frames=10):
    '''
    Use Archive API to get most recent data images
    proposal_id - ID of the proposal being searched
    timestamp [optional] - date and time to search from
    num_frames [optional] - number of frames to return
    '''
    url =settings.ARCHIVE_API + 'frames/?PROPID={}&RLEVEL=90'.format(proposal_id)
    if timestamp:
        url +='&start={}'.format(timestamp)
    headers = {'Authorization': 'Token {}'.format(settings.ARCHIVE_API_TOKEN)}
    response = requests.get(url,headers=headers).json()
    if len(response['results']) > 0:
        return response['results']
    else:
        return []

def frame_by_basename(basename):
    '''
    Use Archive API to get the frame corresponding to supplied basename
    '''

    headers = {'Authorization': 'Token {}'.format(settings.ARCHIVE_API_TOKEN)}
    response = requests.get(
        settings.ARCHIVE_API + 'frames/?BASENAME={}'.format(basename),
        headers=headers
    ).json()
    if len(response['results']) > 0:
        result = response['results'][0]
        frame ={
            'id': result['id'],
            'url': result['url'],
            'filename': result['filename']
        }
    return frame

def tracknum_lookup(tracknum):
    if not tracknum.startswith('0') and len(tracknum) != 10:
        # Avoid sending junk to the API
        return False
    try:
        client = requests.session()
        login_data = dict(username='dthomas+guest@lcogt.net', password='guest')
        # Because we are sending log in details it has to go over SSL
        data_url = 'https://lcogt.net/observe/service/request/get/userrequest/%s' % tracknum
        resp = client.post(data_url, data=login_data, timeout=20)
        data = resp.json()
    except:
        return False
    return data

def build_recent_observations(num):
    observations = []
    recent_obs = []
    # Store the TAG IDs in a config not here
    qstring = "/find?tagid__in=LCOEPO,FTP&limit=%s&order_by=-date_obs&full_header=1" % int(
        num)
    observations = framedb_lookup(qstring)
    if observations:
        org_names = collate_org_names(observations)
        recent_obs = build_framedb_observations(observations, org_names)
    else:
        recent_obs = []
    return recent_obs


def identity(request):
    '''
    Main function for looking up the origname, tracking number or organization's observations.
    Then passes all the meta data that observations need to be displayed either as a group or on a single page
    '''
    origname = request.GET.get('origname', '')
    tracknum = request.GET.get('tracknum', '')
    org_name = request.GET.get('org_name', '')
    query = '/find?full_header=1'
    if origname:
        query += '&origname=%s&annotate_best_reduction=1' % origname
    if tracknum:
        query += '&tracknum__in=%s' % tracknum
    observation = framedb_lookup(query)
    org_names = collate_org_names(observation)
    if not observation:
        # return broken(request,"There was a problem finding the requested
        # observation in the database.")
        return render(request,'404.html')
    if len(observation) == 1:
        obs = build_framedb_observations(observation, org_names)
        filters = get_fits(origname)
        try:
            site = Site.objects.get(code=observation[0]['siteid'])
        except Exception, e:
            logger.error(e, observation[0]['site'])
            site = None
        return render(request,'images/identity_detail.html', {'n': 1,
                                                              'site': site,
                                                              'obs': obs[0],
                                                              'filters': filters,
                                                              'framedb_obs': True})
    else:
        obs = build_framedb_observations(observation, org_names)
        if len(org_names) > 1:
            info = {
                'title': "Recent observations",
                'link': '',
                'description': 'Recent observations from Las Cumbres Observatory Global Telescope Network',
                'perpage': 36
            }
        elif len(org_names) == 1:
            name = org_names.items()[0][1]
            info = {
                'title': "Recent %s observations" % name,
                'link': '',
                'description': 'Recent observations taken by %s using Las Cumbres Observatory Global Telescope Network' % name,
                'perpage': 36
            }
        data = {'input': info, 'link': info['link'], 'obs': obs, 'n': len(obs)}
        return render(request, 'images/group.html', data)

def get_fits(origname):
    filters = []
    origname = origname[0:31]
    url =settings.ARCHIVE_API + 'frames/?basename={}'.format(origname)
    headers = {'Authorization': 'Token {}'.format(settings.ARCHIVE_API_TOKEN)}
    try:
        response = requests.get(url,headers=headers).json()
    except ValidError:
        return []
    for datum in response['results']:
        filter_params = {
                'fits': datum['url'],
                'fullname' : filter_name
                }
        filters.append(filter_params)
    return filters


def build_framedb_observations(observations, org_names=None):
    '''
    Translate response from framedb to the format Observations wants to display
    '''
    from images.utils import dmstodegrees, hmstodegrees
    obs_list = []
    encl = {'doma': 'Dome A', 'domb': 'Dome B', 'domc': 'Dome C',
            'clma': '', 'aqwa': 'Aqawan A', 'aqwb': 'Aqawan B'}
    telid = {'1m0a': '1-meter', '2m0a': '2-meter',
             '0m4a': '0.4-meter', '0m4b': '0.4-meter'}
    reduction = {'10.0': 'Quicklook image',
                 '90.0': 'Final quality', '00.0': 'Uncalibrated image'}
    if observations:
      numobs = len(observations)
    else:
      numobs = 0
    for o in observations:
        id_name = o['origname'].split('.')[0]
        thumbnail = "http://data.lcogt.net/thumbnail/%s/?height=150&width=150&label=0" % id_name
        large_img = "http://data.lcogt.net/thumbnail/%s/?height=560&width=560&label=0" % id_name
        try:
            if o['telid'] != '2m0a':
                telname = "%s in %s" % (telid[o['telid']], encl[o['encid']])
            else:
                telname = telid[o['telid']]
            site = Site.objects.get(code=o['siteid'])
        except:
            telname = ''
            site = ''
        if o['object_name']:
            # Remove brackets
            obj = re.sub(r" ?\([^\)]*\)", '', o['object_name'])
            # Remove redundant whitespace
            obj = re.sub(r"/\s\s+/", ' ', obj)
            # Remove non-useful characters
            obj = re.sub(r"[^\w\-\+0-9 ]/i", '', obj)
        else:
            obj = "Unknown"
        try:
            filter_name = Filter.objects.get(code=o['filter_name'])
        except:
            filter_name = o['filter_name']
        params = {
                  'instrumentname': o['detector'],
                  'objectname': o['object_name'],
                  'object': obj,
                  'thumbnail': thumbnail,
                  'hasthumbnail': True,
                  'dateobs': datetime.strptime(o['date_obs'], "%Y-%m-%d %H:%M:%S"),
                  'telescope': o['telid'],
                  'license': "http://creativecommons.org/licenses/by-nc/2.0/deed.en_US",
                  'credit': "Image taken with %s telescope at Las Cumbres Observatory Global Telescope Network, %s node" % (o['telid'], site.name if hasattr(site, 'name') else 'unknown'),
                  'licenseimage': 'cc-by-nc.png',
                  'filter': filter_name,
                  'filterprops': filter_name,
                  'telescope': telname,
                  'site': site,
                  'exposure': o['exptime'],
                  'ra': hmstodegrees(o['ra']),
                  'dec': dmstodegrees(o['dec']),
                  'fullimage_url': large_img,
                  'fits_view_url': "%s#%s/%s/%s" % (settings.FITS_VIEWER_URL, o['propid'], o['day_obs'], o['origname']),
                  'origname': o['origname']
                  }
        if org_names:
            params['user'] = org_names.get(o['tracknum'], 'Unknown')
        else:
            params['user'] = "Unknown"
        try:
            params['reduction'] = reduction.get(
                str(o['annotate_best_reduction']), '')
        except:
            params['reduction'] = 'Unknown'
        if numobs == 1:
            avm = avm_from_lookup(params['object'])
            if avm:
                params['avmname'] = avm['desc']
                params['avmcode'] = avm['code']
        obs_list.append(params)
    return obs_list


def find_username_tracknum(nums):
    '''On supplying a list of tracking numbers this will return a dictionary with tracking number keys and user id values'''
    #     o['user'] = Registrations.objects.get(schoolid=ob.schoolid)
    # except:
    #     o['user'] = "Unknown"
    return "Unknown"


def avm_from_lookup(objectname):
    ''' Use LookUP to find the AVM code and description for an object based on its name.
        Eventually we will store this unless this is the first time we view the object
    '''
    objectname = objectname.strip()
    obj = "+".join(objectname.split(" "))
    lookup_url = "http://lcogt.net/lookUP/json/?name=%s&callback=lk" % obj
    try:
        resp = requests.get(lookup_url, timeout=10)
        if not resp:
            return None
    except:
        return None
    obj = json.loads(resp.content[3:-3])
    try:
        if obj['category']['avmcode']:
            params = {
                'code': obj['category']['avmcode'],
                'desc': obj['category']['avmdesc'],
            }
        else:
            return None
    except:
        return None
    return params

def build_observations(obs):

    observations = []

    if not(obs):
        logger.error("build_observations: No observations provided")
        return obs

    for ob in obs:
        o = {}

        try:
            o['user'] = ob.observer
        except:
            o['user'] = "Unknown"

        try:
            o['schoolname'] = ob.observer
        except:
            o['schoolname'] = "Unknown"
        try:
            filter_obj = Filter.objects.get(code=ob.filters)
        except:
            filter_obj = ob.filters

        try:
            obstats = ObservationStats.objects.filter(image=ob)
            if(obstats[0].avmcode != "0.0"):
                o['avmcode'] = obstats[0].avmcode
                cats = o['avmcode'].split(';')
                o['avmname'] = ""
                for (counter, c) in enumerate(cats):
                    if counter > 0:
                        o['avmname'] += ";"
                    if c in categorylookup:
                        o['avmname'] += categorylookup[c]
            else:
                o['avmcode'] = ""
            o['views'] = obstats[0].views
        except:
            o['avmcode'] = ""

        o['imageid'] = ob.imageid
        o['dateobs'] = ob.dateobs
        o['objectname'] = ob.objectname
        o['ra'] = ob.ra * 15
        o['dec'] = ob.dec
        o['filter'] = filter_obj
        o['exposure'] = ob.exposure
        o['requestids'] = ob.requestids
        o['telescope'] = ob.telescope
        o['site'] = ob.telescope.site
        o['filename'] = ob.filename
        o['username'] = ob.username
        o['processingtype'] = ob.processingtype
        o['instrumentname'] = ob.instrumentname
        o['fitsfiles'] = ""
        if o['filename'].startswith('NoImage'):
            o['fullimage_url'] = "http://lcogt.net/sites/default/themes/lcogt/images/missing_large.png"
            o['thumbnail'] = "http://lcogt.net/sites/default/themes/lcogt/images/missing.png"
        else:
            o['fullimage_url'] = "http://lcogt.net/files/rtisba/faulkes-rti/imagearchive/%s/%s/%s/%s.jpg" % (
                o['dateobs'].year, o['dateobs'].strftime('%m'), o['dateobs'].strftime('%d'), o['filename'][0:-4])
            o['thumbnail'] = o['fullimage_url'][0:-4] + "_120.jpg"
        o['license'] = "http://creativecommons.org/licenses/by-nc/2.0/deed.en_US"
        o['licenseimage'] = 'cc-by-nc.png'
        o['credit'] = "Image taken with " + o['telescope'].name + \
            " operated by Las Cumbres Observatory Global Telescope Network"
        # Change the credit if prior to 11 Oct 2005
        if o['dateobs'] < datetime(2005,10,11):
            o['credit'] = "Provided to Las Cumbres Observatory under license from the Dill Faulkes Educational Trust"
        o['link_obs'] = reverse('show_rtiobservation', kwargs={'code': o[
                                'telescope'].site.code, 'tel': o['telescope'].code, 'obs': o['imageid']})
        o['link_site'] = o['telescope'].site.code + '/'
        o['link_tel'] = o['link_site'] + "/" + o['telescope'].code + '/'
        o['link_user'] = "user/" + str(o['username']) + '/'
        # Remove brackets
        o['object'] = re.sub(r" ?\([^\)]*\)", '', o['objectname'])
        # Remove redundant whitespace
        o['object'] = re.sub(r"/\s\s+/", ' ', o['object'])
        # Remove non-useful characters
        o['object'] = re.sub(r"[^\w\-\+0-9 ]/i", '', o['object'])
        observations.append(o)
    return observations


# n = total number of observations
# page = the current page
def build_pager(request, n, avm=''):
    if(n < n_per_page):
        return {'next': '', 'prev': '', 'html': '', 'page': 0}
    else:

        page = int(request.GET.get('page', '1'))

        qstring = request.META.get('QUERY_STRING', '')
        m = re.search('page=', qstring)
        if not(m):
            if qstring == '':
                qstring = 'page=1'
            else:
                qstring = qstring + '&page=1'

        if avm != '':
            m = re.search('avm=', qstring)
            if not(m):
                if qstring == '':
                    qstring = 'avm=%s' % str(avm)
                else:
                    qstring = qstring + '&avm=%s' % str(avm)
            qstring = re.sub(r"avm=[^\&]+", 'avm=%s' % str(avm), qstring)

        start = 1
        if page > start + 4:
            start = page - 4
        final = int(math.ceil(n / n_per_page) + 1)
        end = final + 1
        if end - start > 10:
            end = start + 10
        output = ""
        c = 0
        prev = re.sub(r"page=\d+", 'page=%s' % (page - 1), qstring)
        if page - 1 < 1:
            prev = ''
        next = re.sub(r"page=\d+", 'page=%s' % (page + 1), qstring)
        if page + 1 > final:
            next = ''

        for i in range(start, end):
            if c > 0:
                output = output + " "
            qstring = re.sub(r"page=\d+", 'page=%s' % i, qstring)
            if(i == page):
                output = output + \
                    "<a href=\"?%s\" class=\"current\">%s</a> " % (qstring, i)
            else:
                output = output + "<a href=\"?%s\">%s</a> " % (qstring, i)
            c = c + 1
        if start > 1:
            qstring = re.sub(r"page=\d+", 'page=1', qstring)
            output = "<a href=\"?%s\">&laquo; first</a> ... %s" % (
                qstring, output)
        if end < final:
            qstring = re.sub(r"page=\d+", 'page=%s' % int(final), qstring)
            output = output + "... <a href=\"?%s\">last &raquo;</a>" % qstring
        sobs = (page - 1) * n_per_page
        eobs = sobs + n_per_page
        if eobs > n:
            eobs = n
        return {'next': next, 'prev': prev, 'html': output, 'start': sobs, 'end': eobs, 'page': page}


def build_observations_json(obs):
    if len(obs) > 1:
        observations = []
    elif len(obs) == 0:
        return ""

    for o in obs:
        if not('telescope' in o):
            tel = Telescope.objects.filter(id=o['telescope'])
            o['telescope'] = tel[0]

        o['fitsfiles'] = ""
        try:
            filter = filter_props(o['filter'])
        except:
            filter = ["Unknown"]
        if o.get('origname',''):
            page_url = reverse('identity') + "?origname="+o['origname']
        else:
            page_url = o.get('link_obs','')
        ob = {
            "about": page_url,
            "label": o['objectname'],
            "observer": {
                "about": '',  # base_url+o['link_user'],
                "label": o['user']
            },
            "image": {
                "about": o['fullimage_url'],
                "label": "Image",
                "fits": o['fitsfiles'],
                "thumb": o['thumbnail']
            },
            "ra": o['ra'],
            "dec": o['dec'],
            "filter":  {
                "name": re.sub(r"\"", '', filter[0]),
            },
            "time": {
                "creation": o['dateobs'].isoformat()
            },
            "exposure": o['exposure'],
            "credit": {
                "about": o['license'],
                "label": o['credit']
            }
        }

        if len(obs) > 1:
            observations.append(ob)
        elif len(obs) == 1:
            observations = ob
    return observations


def view_json(request, obs, config):

    response = {
        "message": "This is a beta release of LCOGT JSON. The format may change so any applications you build using this may need updating in the future.",
        "date": datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"),
        "observation": obs
    }
    if 'description' in config:
        response["desc"] = config['description']
    if 'link' in config:
        response["link"] = base_url + config['link']
    if 'title' in config:
        response["title"] = config['title']
    if 'pager' in config:
        if 'next' in config['pager'] or 'previous' in config['pager']:
            response["page"] = {}
            # print config
            if 'previous' in config['pager'] and config['pager']['previous'] != '':
                response["page"]["previous"] = response["link"] + \
                    ".json?" + str(config['pager']['previous'])
            if 'next' in config['pager'] and config['pager']['next'] != '':
                response["page"]["next"] = response["link"] + \
                    ".json?" + str(config['pager']['next'])
    if 'observations' in config:
        response["observations"] = config['observations']
    if 'live' in config:
        response["live"] = config['live']
    if 'exposure' in config:
        response["exposure"] = config['exposure']

    s = json.dumps(response, indent=1, sort_keys=True)
    output = '\n'.join([l.rstrip() for l in s.splitlines()])
    if 'callback' in config and config['callback'] != "":
        output = config['callback'] + "(" + output + ")"
    return HttpResponse(output, content_type='application/json')


def view_kml(request, obs, config):

    if not('title' in config):
        config['title'] = 'LCOGT'

    output = '<?xml version="1.0" encoding="UTF-8"?>\n'
    output += '<kml xmlns="http://earth.google.com/kml/2.2" hint="target=sky">\n'
    output += '<Document>\n'
    output += ' <name>' + config['title'] + '</name>\n'
    output += ' <Style id="observation">\n'
    output += '     <LabelStyle>\n'
    output += '         <color>00ffffff</color>\n'
    output += '     </LabelStyle>\n'
    output += ' </Style>\n'
    try:
        schoolname = o['user'].schoolname
    except:
        schoolname = 'unknown'

    for o in obs:
        if type(o['telescope']) == type('a'):
            telname = o['telescope']
        else:
            telname = o['telescope'].name
        output += ' <Placemark>\n'
        output += '     <name>' + o['objectname'] + '</name>\n'
        output += '     <description><![CDATA[\n'
        output += '         <p>Observed by ' + schoolname + ' on ' + o['dateobs'].isoformat() + ' with <a href="' + base_url + o.get('link_tel','') + '.kml">' + telname + '</a>.<br /><a href="' + o.get('link_obs','') + '"><img src="' + o.get('thumbnail','') + '" /></a></p>\n'
        output += '         <p>Data from <a href="http://lcogt.net/">LCOGT</a></p>\n'
        output += '     ]]></description>\n'
        output += '     <LookAt>\n'
        output += '         <longitude>' + \
            str(o['ra'] - 180) + '</longitude>\n'
        output += '         <latitude>' + str(o['dec']) + '</latitude>\n'
        output += '         <altitude>0</altitude>\n'
        output += '         <range>20000</range>\n'
        output += '         <tilt>0</tilt>\n'
        output += '         <heading>0</heading>\n'
        output += '     </LookAt>\n'
        output += '     <Point>\n'
        output += '         <coordinates>' + \
            str(o['ra'] - 180) + ',' + str(o['dec']) + ',0</coordinates>\n'
        output += '     </Point>\n'
        output += '     <styleUrl>#observation</styleUrl>\n'
        output += ' </Placemark>\n'

    output += '</Document>\n'
    output += '</kml>\n'

    return HttpResponse(output, content_type=config['mimetype'])


def view_rss(request, obs, config):

    if not('title' in config):
        config['title'] = 'LCOGT'

    return render(request, 'images/rss.xml', {'config': config, 'obs': obs}, content_type=config['mimetype'])




def datestamp_basic(value):
    if value:
        dt = datetime(int(value[0:4]), int(value[4:6]), int(value[6:8]), int(
            value[8:10]), int(value[10:12]), int(value[12:14]))
    else:
        dt = datetime.today()
    return dt.strftime("%a, %d %b %Y")


def observation_URL(tel, obs):
    telescope = telescope_details(tel)
    return telescope.site + '/' + telescope.code + "/" + obs


def unknown(request):
    return render_to_response('404.html', context_instance=RequestContext(request))


def broken(request, msg):
    return render_to_response('500.html', {'msg': msg}, context_instance=RequestContext(request))
