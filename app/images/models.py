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
# -*- coding: utf-8 -*-
from django.db import models

from datetime import datetime
import time

wistime_format = "%Y%m%d%H%M%S"

class Site(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=64, blank=True,null=True)
    longitude = models.FloatField(blank=True,null=True)
    latitude = models.FloatField(blank=True,null=True)
    drupalnode = models.IntegerField(blank=True,null=True)
    class Meta:
        db_table  = 'observatory_site'
    def __unicode__(self):
        return self.name

class Telescope(models.Model):
    site = models.ForeignKey(Site)
    code = models.CharField(max_length=4, blank=True, null=True)
    enclosure = models.CharField(max_length=4, blank=True, null=True)
    name = models.CharField(max_length=64,  blank=True, null=True)
    short = models.CharField(max_length=10, blank=True, null=True)
    drupalnode = models.IntegerField(blank=True, null=True)
    class Meta:
        db_table = 'telescope'
    def __unicode__(self):
        return u"%s at %s" % (self.code,self.site)

class Filter(models.Model):
    code = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=64, blank=True, null=True)
    ucd = models.CharField('UCD electromagnetic spectrum identifier',max_length=32, blank=True, null=True)
    class Meta:
        db_table = 'telescope_filter'
    def __unicode__(self):
        return self.name

class Image(models.Model):
    imageid = models.IntegerField(primary_key=True, help_text="Block ID if from ODIN")
    dateobs = models.DateTimeField(default=datetime.utcnow)
    objectname = models.CharField(max_length=100,blank=True,null=True)
    ra = models.FloatField(blank=True,null=True)
    dec = models.FloatField(blank=True,null=True)
    filters = models.CharField(max_length=30, blank=True,null=True)
    exposure = models.FloatField('total exposure time', blank=True,null=True)
    requestids = models.CharField(max_length=50, blank=True,null=True)
    telescope = models.ForeignKey(Telescope)
    filename = models.CharField(max_length=150, blank=True,null=True)
    username = models.CharField(help_text="If processingtype is STIFF this is ODIN username else RTI username", max_length=150, blank=True,null=True)
    observer = models.CharField(max_length=150, blank=True,null=True)
    processingtype = models.CharField(max_length=20, blank=True, null=True)
    instrumentname = models.CharField(max_length=60, blank=True, null=True)
    archive_link = models.CharField(max_length=200,blank=True,null=True)
    class Meta:
        db_table = u'images'
        verbose_name = u'image'
        verbose_name_plural = u'images'
    def __unicode__(self):
        return "%s taken by %s" % (self.objectname, self.observer)

class ObservationStats(models.Model):
    image = models.ForeignKey(Image)
    views = models.IntegerField(null=True, db_column='Views', blank=True,help_text='The number of views that this observation has had')
    weight = models.FloatField(null=True, db_column='Weight', blank=True,help_text='A weight to determine what is currently popular')
    lastviewed = models.DateTimeField(db_column='LastViewed', blank=True,help_text='The time this image was last viewed')
    imageurl = models.URLField(null=True, blank=True)
    moreurl = models.URLField(null=True, blank=True)
    avmcode = models.CharField(max_length=32, db_column='AVMCode', blank=True,help_text='The AVM code for this image. Can contain multiple codes separated by a semi-colon.')
    class Meta:
        verbose_name = u'observation stat'
        verbose_name_plural = u'observation stats'
