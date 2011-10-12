from django.db import models

from rtiadminsite.wis.choices import *
from datetime import datetime
import time

wistime_format = "%Y%m%d%H%M%S"

class Site(models.Model):
	code = models.CharField(primary_key=True, max_length=3, db_column='Code', blank=True)
	name = models.CharField(max_length=64, db_column='Name', blank=True)
	longitude = models.FloatField(null=True, db_column='Longitude', blank=True)
	latitude = models.FloatField(null=True, db_column='Latitude', blank=True)
	drupalnode = models.IntegerField(null=True, db_column='DrupalNode', blank=True)
	class Meta:
	    app_label = 'faulkes'
	    db_table  = 'observatory_site'

class Telescope(models.Model):
	id = models.IntegerField(primary_key=True, null=True, db_column='ID', blank=True,help_text='A numerical ID for the telescope')
	site = models.ForeignKey(Site)
	code = models.CharField(max_length=4, db_column='Code', blank=True)
	name = models.CharField(max_length=64, db_column='Name', blank=True)
	short = models.CharField(max_length=10, db_column='Short', blank=True)
	drupalnode = models.IntegerField(null=True, db_column='DrupalNode', blank=True)
	class Meta:
	    app_label = 'faulkes'
	    db_table = 'telescope'

class Filter(models.Model):
	code = models.CharField(primary_key=True, max_length=10, db_column='Code', blank=True)
	name = models.CharField(max_length=64, db_column='Name', blank=True)
	drupalnode = models.IntegerField(null=True, db_column='DrupalNode', blank=True)
	centralwavelength = models.FloatField('The central wavelength in nm',null=True, db_column='CentralWavelength', blank=True)
	bandpass = models.FloatField('The bandpass in nm',null=True, db_column='Bandpass', blank=True)
	ucd = models.CharField('UCD electromagnetic spectrum identifier',max_length=32, db_column='UCD', blank=True)
	class Meta:
	    app_label = 'faulkes'
	    db_table = 'telescope_filter'

class Imagearchive(models.Model):
    imageid = models.IntegerField(primary_key=True, db_column='ImageID') # Field name made lowercase.
    imagetype = models.CharField(max_length=30, db_column='ImageType', blank=True) # Field name made lowercase.
    whentaken = models.CharField(max_length=42, db_column='WhenTaken', blank=True) # Field name made lowercase.
    schoolid = models.IntegerField(null=True, db_column='SchoolID', blank=True) # Field name made lowercase.
    bestofimage = models.CharField(max_length=3, db_column='BestOfImage', blank=True) # Field name made lowercase.
    skyobjectname = models.CharField(max_length=762, db_column='SkyObjectName', blank=True) # Field name made lowercase.
    raval = models.FloatField(null=True, db_column='RaVal', blank=True) # Field name made lowercase.
    decval = models.FloatField(null=True, db_column='DecVal', blank=True) # Field name made lowercase.
    filter = models.CharField(max_length=30, blank=True)
    exposuresecs = models.FloatField(null=True, db_column='ExposureSecs', blank=True) # Field name made lowercase.
    defaultexpsecs = models.FloatField(null=True, db_column='DefaultExpSecs', blank=True) # Field name made lowercase.
    skyobjecttype = models.CharField(max_length=3, db_column='SkyObjectType', blank=True) # Field name made lowercase.
    requestids = models.CharField(max_length=762, blank=True)
    telescopeid = models.IntegerField(null=True, db_column='TelescopeId', blank=True,choices=SCOPE_CHOICES) # Field name made lowercase.
    mosaicpatterncode = models.IntegerField(null=True, db_column='MosaicPatternCode', blank=True) # Field name made lowercase.
    hasthumbnail = models.CharField(max_length=3, db_column='HasThumbnail', blank=True) # Field name made lowercase.
    imagesequenceid = models.IntegerField(null=True, db_column='imageSequenceId', blank=True) # Field name made lowercase.
    filename = models.CharField(max_length=150, db_column='Filename', blank=True) # Field name made lowercase.
    schoolloginname = models.CharField(max_length=762, blank=True)
    processingtype = models.CharField(max_length=762, blank=True)
    indexnames = models.CharField(max_length=762, blank=True)
    instrumentname = models.CharField(max_length=60, db_column='instrumentName', blank=True) # Field name made lowercase.
    class Meta:
        db_table = u'imagearchive'
        verbose_name = u'image archive'
        verbose_name_plural = u'image archive'
        app_label = 'faulkes'
    def datestamp(self): 
        if self.whentaken:
            s = datetime(*time.strptime(self.whentaken , wistime_format)[0:5])
            d = "%s" % s.strftime("%a, %d %b %Y")
        else:
            d = "Error"
        return d

class ObservationStats(models.Model):
	imagearchive = models.ForeignKey(Imagearchive)
	views = models.IntegerField(null=True, db_column='Views', blank=True,help_text='The number of views that this observation has had')
	weight = models.FloatField(null=True, db_column='Weight', blank=True,help_text='A weight to determine what is currently popular')
	lastviewed = models.DateTimeField(db_column='LastViewed', blank=True,help_text='The time this image was last viewed')
	imageurl = models.URLField(blank=True)
	moreurl = models.URLField(blank=True)
	avmcode = models.CharField(max_length=32, db_column='AVMCode', blank=True,help_text='The AVM code for this image. Can contain multiple codes separated by a semi-colon.')


class Posdebug(models.Model):
    postime = models.CharField(max_length=42, blank=True)
    sent = models.CharField(max_length=3, blank=True)
    posdata = models.TextField(blank=True)
    posid = models.CharField(max_length=36, blank=True)
    class Meta:
        db_table = u'posdebug'
        app_label = 'faulkes'


class Settings(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    value = models.CharField(max_length=762, blank=True)
    class Meta:
        db_table = u'settings'
        app_label = 'faulkes'
