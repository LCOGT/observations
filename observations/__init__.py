#
# monkey patch URLNode.render so that it is aware of the application PREFIX
#
from django.template.defaulttags import URLNode

URLNode.old_render = URLNode.render

def render(self, context):
    from django.conf import settings
    return settings.PREFIX + self.old_render(context)