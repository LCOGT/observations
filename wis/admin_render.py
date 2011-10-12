from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode
from django.utils import datetime_safe
from datetime import datetime
import re

class ReadOnlyWidget(forms.Widget):
    def __init__(self, original_value, display_value):
        self.original_value = original_value
        self.display_value = display_value

        super(ReadOnlyWidget, self).__init__()

    def render(self, name, value, attrs=None):
        if self.display_value is not None:
            return unicode(self.display_value)
        return unicode(self.original_value)

    def value_from_datadict(self, data, files, name):
        return self.original_value

class ReadOnlyAdminFields(object):
    def get_form(self, request, obj=None):
        form = super(ReadOnlyAdminFields, self).get_form(request, obj)
        if hasattr(self, 'readonly'):
            for field_name in self.readonly:
                if field_name in form.base_fields:
                    if hasattr(obj, 'get_%s_display' % field_name):
                        display_value = getattr(obj, 'get_%s_display' % field_name)()
                    else:
                        display_value = None
                    form.base_fields[field_name].widget = ReadOnlyWidget(getattr(obj, field_name, ''), display_value)
                    form.base_fields[field_name].required = False
        return form
        

class DateTextInput(forms.TextInput):
    def render(self, name, value, attrs=None):
        print name
        if value:
          s = datetime.strptime(value,"%Y%m%d%H%M%S")
          display = s.strftime("%H:%M %a, %d %b %Y") # + "<input type=hidden id='id_%s' name='%s' value='%s' />" % (name,name,value)
        else:
            display = "None"
        return display



