#
# monkey patch urlresolvers.reverse,
# to be aware of the application PREFIX
#

import django.core.urlresolvers

old_reverse = django.core.urlresolvers.reverse
def myreverse(viewname, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None):
    from django.conf import settings
    try:
        return settings.PREFIX + old_reverse(viewname, urlconf, args, kwargs, prefix, current_app)
    except:
        return old_reverse(viewname, urlconf, args, kwargs, prefix, current_app)
django.core.urlresolvers.reverse = myreverse
