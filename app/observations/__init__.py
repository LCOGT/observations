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
#
# monkey patch urlresolvers.reverse,
# to be aware of the application PREFIX
#

import django.core.urlresolvers

old_reverse = django.core.urlresolvers.reverse
def myreverse(*args, **kwargs):
    from django.conf import settings
    try:
        return settings.PREFIX + old_reverse(*args, **kwargs)
    except:
        return old_reverse(*args, **kwargs)
django.core.urlresolvers.reverse = myreverse
