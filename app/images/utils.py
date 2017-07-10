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
from datetime import datetime

from django.conf import settings
import requests
from urlparse import urljoin

def tracknum_lookup(tracknum):
    if not tracknum.startswith('0') and len(tracknum) != 10:
        # Avoid sending junk to the API
        return False

    headers = {'Authorization': 'Token {}'.format(settings.PORTAL_TOKEN)}
    url = urljoin(settings.PORTAL_REQUEST_API, tracknum)

    try:
        resp = requests.get(url, headers=headers, timeout=20, verify=ssl_verify)
        data = resp.json()
    except requests.exceptions.InvalidSchema, err:
        data = None
        logger.error("Request call to %s failed with: %s" % (url, err))
    except ValueError, err:
        logger.error("Request {} API did not return JSON: {}".format(url, resp.status_code))
    except requests.exceptions.Timeout:
        logger.error("Request API timed out")
    return data

def l(txt, lnk):
    return "<a href=\"http://lco.global/" + lnk + "\">" + txt + "</a>"

def hourstodegrees(value,arg):
    "Converts decimal hours to decimal degrees"
    if ":" in str(value):
        return value
    return value*15

def degreestohours(value):
    "Converts decimal degrees to decimal hours"
    if ":" in str(value):
        return value
    return float(value)/15

def degreestodms(value):
    "Converts decimal degrees to decimal degrees minutes and seconds"
    if ":" in str(value):
        return value
    try:
        if(value < 0):
            sign = "-"
        else:
            sign = ""
        value = abs(value)
        d = int(value)
        m = int((value - d)*60)
        s = ((value - d)*3600 - m*60)
        return "%s%02d:%02d:%05.2f" % (sign,d,m,s)
    except:
        return ""

def degreestohms(value):
    "Converts decimal degrees to decimal hours minutes and seconds"
    if ":" in str(value):
        return value
    try:
        value = float(value)/15
        d = int(value)
        m = int((value - d)*60)
        s = ((value - d)*3600 - m*60)
        return "%02d:%02d:%05.2f" % (d,m,s)
    except:
        return ""

def dmstodegrees(value):
    if ":" not in str(value):
        return value
    el = value.split(":")
    deg = float(el[0])
    if deg < 0:
        sign = -1.
    else:
        sign = 1
    return deg + sign*float(el[1])/60. + sign*float(el[2])/3600.

def hmstodegrees(value):
    if ":" not in str(value):
        return value
    el = value.split(":")
    return float(el[0])*15 + float(el[1])/60. + float(el[2])/3600.

def hmstohours(value):
    if ":" not in str(value):
        return value
    el = value.split(":")
    return float(el[0]) + float(el[1])/60. + float(el[2])/3600.

def parsetime(value):
    if type(value) == int:
        return datetime(int(value[0:4]),int(value[4:6]),int(value[6:8]),int(value[8:10]),int(value[10:12]),int(value[12:14]))
    else:
        return value

def datestamp(value):
    if value:
        try:
            dt = parsetime(value)
        except:
            dt = datetime()
    else:
        dt = datetime()
    return dt.strftime(settings.DATETIME_FORMAT)

def isodatestamp(value):
    if value:
        dt = parsetime(value)
    else:
        dt = datetime()
    return dt.isoformat("T")

def filter_list():
    return [{'code': 'CC', 'name': 'Air', 'node': 'node/31'},
            {'code': 'RGB', 'name': 'Color', 'node': ""},
            {'code': 'RGB+ND', 'name': "Color + Neutral Density", 'node': ""},
            {'code': 'RGB_ND', 'name': "BVr' +Neutral Dens", 'node': ""},
            {'code': 'Red', 'name': "Red", 'node': ""},
            {'code': 'Green', 'name': "Green", 'node': ""},
            {'code': 'Blue', 'name': "Blue", 'node': ""},
            {'code': 'CA', 'name': 'Hydrogen Alpha', 'node': 'node/51'},
            {'code': 'HB', 'name': "Hydrogen Beta", 'node': "node/53"},
            {'code': 'CO', 'name': 'Oxygen III', 'node': 'node/34'},
            {'code': 'CB', 'name': 'Bessell B', 'node': 'node/36'},
            {'code': 'CV', 'name': "Bessell V", 'node': "node/37"},
            {'code': 'CR', 'name': 'Bessell R', 'node': "node/43"},
            {'code': 'BI', 'name': "Bessell I", 'node': ""},
            {'code': 'CU', 'name': "SDSS u'", 'node': "node/42"},
            {'code': 'SR', 'name': "SDSS r'", 'node': ""},
            {'code': 'CI', 'name': "SDSS i'", 'node': "node/35"},
            {'code': 'NB', 'name': "B +Neutral Dens", 'node': ""},
            {'code': 'NV', 'name': "V +Neutral Dens", 'node': ""},
            {'code': 'SG', 'name': "Sloan g'", 'node': "node/45"},
            {'code': 'SY', 'name': "Pan-STARRS Y", 'node': "node/49"},
            {'code': 'SZ', 'name': "Pan-STARRS Z", 'node': "node/48"},
            {'code': 'SO', 'name': "Solar", 'node': "node/40"},
            {'code': 'SM', 'name': "SkyMap - CaV", 'node': "node/41"},
            {'code': 'OP', 'name': "Opal", 'node': "node/50"},
            {'code': 'D5', 'name': "D51 filter", 'node': ""}]


def filter_props(code):
    f = filter_list()
    try:
        for fs in f:
            if(fs['code'] == code):
                return [fs['name'], fs['node']]
        return ["Unknown", ""]
    except:
        return ["Unknown", ""]


def filter_link(code):
    try:
        props = filter_props(code)
    except:
        return "Unknown"
    if len(props) == 2:
        return l(props[0], props[1])
    else:
        return props[0]


def filter_name(code):
    try:
        props = filter_props(code)
    except:
        return "Unknown"
    return props[0]


def hexangletodec(value):
    value = value.split(":")
    if (int(value[0]) >= 0):
        sign = 1
    else:
        sign = -1
    return (int(value[0]) + (sign * (float(value[1]) / 60) + (float(value[2]) / 3600)))

# Bin the observations by month for the specified number of bins


def binMonths(obs, input, bins):
    now = datetime.utcnow()
    binned = [0 for num in range(bins)]
    values = [{'count': 0, 'year': 0, 'm': 0, 'month': ''}
              for num in range(bins)]
    for num in range(bins):
        m = now.month - num
        values[num]['year'] = now.year + ((m - 1) / 12)
        while m < 1:
            m += 12
        values[num]['month'] = datetime(now.year, m, 1).strftime("%b")
        values[num]['m'] = m
    e = 0
    for o in obs:
        try:
            date = o['dateobs']
        except:
            date = o.dateobs
            e += o.exposure
        month = date.month - 12 * (now.year - date.year)
        m = now.month - month
        if (m < bins):
            binned[m] = binned[m] + 1
            values[m]['count'] = binned[m]
    input['bins'] = values
    input['exposuretime'] = e
    input['binmax'] = max(binned)
    if input['binmax'] == 0:
        input['binmax'] = 1
    return input
