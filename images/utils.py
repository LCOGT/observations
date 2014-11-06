from datetime import datetime

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
    return datetime(int(value[0:4]),int(value[4:6]),int(value[6:8]),int(value[8:10]),int(value[10:12]),int(value[12:14]))

def datestamp(value):
    if value:
        try:
            dt = parsetime(value)
        except:
            dt = datetime()
    else:
        dt = datetime()
    return dt.strftime("%a %d %B %Y, %H:%M UT");

def isodatestamp(value):
    if value:
        dt = parsetime(value)
    else:
        dt = datetime()
    return dt.strftime("%Y-%m-%dT%H:%M:%S+00:00");