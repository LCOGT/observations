#
# monkey patch URLNode.render and urlresolvers.reverse,
# so that they are aware of the application PREFIX
#
from django.template.defaulttags import URLNode
import django.core.urlresolvers

URLNode.old_render = URLNode.render
def myrender(self, context):
    from django.conf import settings
    try:
        return settings.PREFIX + self.old_render(context)
    except:
        return self.old_render(context)
URLNode.render = myrender

old_reverse = django.core.urlresolvers.reverse
def myreverse(viewname, urlconf=None, args=None, kwargs=None, prefix=None, current_app=None):
    from django.conf import settings
    try:
        return settings.PREFIX + old_reverse(viewname, urlconf, args, kwargs, prefix, current_app)
    except:
        return old_reverse(viewname, urlconf, args, kwargs, prefix, current_app)
django.core.urlresolvers.reverse = myreverse
