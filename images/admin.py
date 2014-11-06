from django.contrib import admin
from images.models import *

class ArchiveAdmin(admin.ModelAdmin):
	list_display = ['objectname','rti_username','datestamp','telescope']

admin.site.register(Image,ArchiveAdmin)
admin.site.register(Telescope)
admin.site.register(Site)   
admin.site.register(Filter)       
