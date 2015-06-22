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
'''# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Image.observer'
        db.add_column(u'images', 'observer',
                      self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Image.observer'
        db.delete_column(u'images', 'observer')


    models = {
        'images.filter': {
            'Meta': {'object_name': 'Filter', 'db_table': "'telescope_filter'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'ucd': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'})
        },
        'images.image': {
            'Meta': {'object_name': 'Image', 'db_table': "u'images'"},
            'archive_link': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'dec': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'exposure': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'filter': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'imageid': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'instrumentname': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True', 'blank': 'True'}),
            'objectname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'observer': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'processingtype': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'ra': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'requestids': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'rti_username': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'schoolid': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'telescope': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['images.Telescope']"}),
            'whentaken': ('django.db.models.fields.CharField', [], {'max_length': '42', 'null': 'True', 'blank': 'True'})
        },
        'images.observationstats': {
            'Meta': {'object_name': 'ObservationStats'},
            'avmcode': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_column': "'AVMCode'", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['images.Image']"}),
            'imageurl': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'lastviewed': ('django.db.models.fields.DateTimeField', [], {'db_column': "'LastViewed'", 'blank': 'True'}),
            'moreurl': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'views': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'Views'", 'blank': 'True'}),
            'weight': ('django.db.models.fields.FloatField', [], {'null': 'True', 'db_column': "'Weight'", 'blank': 'True'})
        },
        'images.site': {
            'Meta': {'object_name': 'Site', 'db_table': "'observatory_site'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'drupalnode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'})
        },
        'images.telescope': {
            'Meta': {'object_name': 'Telescope', 'db_table': "'telescope'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'drupalnode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'short': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['images.Site']"})
        }
    }

    complete_apps = ['images']