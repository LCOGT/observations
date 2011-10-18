from django.contrib import admin

class FaulkesSettingsAdmin(admin.ModelAdmin):
    # A handy constant for the name of the alternate database.
    using = 'faulkes'

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super(FalukesSettingsAdmin, self).queryset(request).using(self.using)
        