# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Site'
        db.create_table('observatory_site', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('drupalnode', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('images', ['Site'])

        # Adding model 'Telescope'
        db.create_table('telescope', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['images.Site'])),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('short', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('drupalnode', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('images', ['Telescope'])

        # Adding model 'Filter'
        db.create_table('telescope_filter', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, null=True, blank=True)),
            ('ucd', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('images', ['Filter'])

        # Adding model 'Image'
        db.create_table(u'images', (
            ('imageid', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('whentaken', self.gf('django.db.models.fields.CharField')(max_length=42, null=True, blank=True)),
            ('schoolid', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('objectname', self.gf('django.db.models.fields.CharField')(max_length=762, null=True, blank=True)),
            ('ra', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('dec', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('filter', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('exposure', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('requestids', self.gf('django.db.models.fields.CharField')(max_length=762, null=True, blank=True)),
            ('telescope', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['images.Telescope'])),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('rti_username', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('processingtype', self.gf('django.db.models.fields.CharField')(max_length=762, null=True, blank=True)),
            ('instrumentname', self.gf('django.db.models.fields.CharField')(max_length=60, null=True, blank=True)),
            ('archive_link', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
        ))
        db.send_create_signal('images', ['Image'])

        # Adding model 'ObservationStats'
        db.create_table('images_observationstats', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['images.Image'])),
            ('views', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='Views', blank=True)),
            ('weight', self.gf('django.db.models.fields.FloatField')(null=True, db_column='Weight', blank=True)),
            ('lastviewed', self.gf('django.db.models.fields.DateTimeField')(db_column='LastViewed', blank=True)),
            ('imageurl', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('moreurl', self.gf('django.db.models.fields.URLField')(max_length=200, null=True, blank=True)),
            ('avmcode', self.gf('django.db.models.fields.CharField')(max_length=32, db_column='AVMCode', blank=True)),
        ))
        db.send_create_signal('images', ['ObservationStats'])


    def backwards(self, orm):
        # Deleting model 'Site'
        db.delete_table('observatory_site')

        # Deleting model 'Telescope'
        db.delete_table('telescope')

        # Deleting model 'Filter'
        db.delete_table('telescope_filter')

        # Deleting model 'Image'
        db.delete_table(u'images')

        # Deleting model 'ObservationStats'
        db.delete_table('images_observationstats')


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
            'objectname': ('django.db.models.fields.CharField', [], {'max_length': '762', 'null': 'True', 'blank': 'True'}),
            'processingtype': ('django.db.models.fields.CharField', [], {'max_length': '762', 'null': 'True', 'blank': 'True'}),
            'ra': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'requestids': ('django.db.models.fields.CharField', [], {'max_length': '762', 'null': 'True', 'blank': 'True'}),
            'rti_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
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