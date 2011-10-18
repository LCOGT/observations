#!/usr/bin/env python
import sys, os, re, urllib2, datetime, random
from datetime import datetime, timedelta, date
from rtiadminsite.faulkes.models import ObservationStats, Imagearchive

import MySQLdb

# Start connection
db = MySQLdb.connect(user="root", passwd="", db="lco3_5", host="127.0.0.1")

sql_objects = "SELECT img_id,when_taken,weight,last_viewed,img_url,views from rti_stats_observations"
obj = db.cursor()
obj.execute(sql_objects)

i = 0
for o in obj:
    obs1 = ObservationStats.objects.filter(imagearchive__imageid=o[0])
    if obs1:
        obs = obs1[0]
        obs.weight=o[2]
        obs.lastviewed= o[3]
        obs.imageurl= o[4]
        obs.views= o[5]
        obs.save()
    else:
        obs = ObservationStats(imagearchive=Imagearchive.objects.get(imageid=o[0]),
                                weight=o[2],
                                lastviewed= o[3],
                                imageurl= o[4],
                                views= o[5])
    obs.save()
    print "Saved %s (%s) with %s views" % (i,obs.imagearchive.imageid,obs.views)
    i = i+1
    
    
'''imagearchive = models.ForeignKey(Imagearchive)
views = models.IntegerField(null=True, db_column='Views', blank=True,help_text='The number of views that this observation has had')
weight = models.FloatField(null=True, db_column='Weight', blank=True,help_text='A weight to determine what is currently popular')
lastviewed = models.DateTimeField(db_column='LastViewed', blank=True,help_text='The time this image was last viewed')
imageurl = models.URLField(blank=True)
moreurl = models.URLField(blank=True)
avmcode = models.CharField(max_length=32, db_column='AVMCode', blank=True,help_text='The AVM code for this image. Can contain multiple codes separated by a semi-colon.')'''
