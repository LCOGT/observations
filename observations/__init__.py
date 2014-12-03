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
