# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=20, null=True, blank=True)),
                ('name', models.CharField(max_length=64, null=True, blank=True)),
                ('ucd', models.CharField(max_length=32, null=True, verbose_name=b'UCD electromagnetic spectrum identifier', blank=True)),
            ],
            options={
                'db_table': 'telescope_filter',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('imageid', models.IntegerField(serialize=False, primary_key=True)),
                ('whentaken', models.CharField(max_length=42, null=True, blank=True)),
                ('schoolid', models.IntegerField(null=True, blank=True)),
                ('objectname', models.CharField(max_length=100, null=True, blank=True)),
                ('ra', models.FloatField(null=True, blank=True)),
                ('dec', models.FloatField(null=True, blank=True)),
                ('filter', models.CharField(max_length=30, null=True, blank=True)),
                ('exposure', models.FloatField(null=True, verbose_name=b'total exposure time', blank=True)),
                ('requestids', models.CharField(max_length=50, null=True, blank=True)),
                ('filename', models.CharField(max_length=150, null=True, blank=True)),
                ('rti_username', models.CharField(max_length=150, null=True, blank=True)),
                ('observer', models.CharField(max_length=150, null=True, blank=True)),
                ('processingtype', models.CharField(max_length=20, null=True, blank=True)),
                ('instrumentname', models.CharField(max_length=60, null=True, blank=True)),
                ('archive_link', models.CharField(max_length=200, null=True, blank=True)),
            ],
            options={
                'db_table': 'images',
                'verbose_name': 'image',
                'verbose_name_plural': 'images',
            },
        ),
        migrations.CreateModel(
            name='ObservationStats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('views', models.IntegerField(help_text=b'The number of views that this observation has had', null=True, db_column=b'Views', blank=True)),
                ('weight', models.FloatField(help_text=b'A weight to determine what is currently popular', null=True, db_column=b'Weight', blank=True)),
                ('lastviewed', models.DateTimeField(help_text=b'The time this image was last viewed', db_column=b'LastViewed', blank=True)),
                ('imageurl', models.URLField(null=True, blank=True)),
                ('moreurl', models.URLField(null=True, blank=True)),
                ('avmcode', models.CharField(help_text=b'The AVM code for this image. Can contain multiple codes separated by a semi-colon.', max_length=32, db_column=b'AVMCode', blank=True)),
                ('image', models.ForeignKey(to='images.Image')),
            ],
            options={
                'verbose_name': 'observation stat',
                'verbose_name_plural': 'observation stats',
            },
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=3)),
                ('name', models.CharField(max_length=64, null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('drupalnode', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'observatory_site',
            },
        ),
        migrations.CreateModel(
            name='Telescope',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=4, null=True, blank=True)),
                ('name', models.CharField(max_length=64, null=True, blank=True)),
                ('short', models.CharField(max_length=10, null=True, blank=True)),
                ('drupalnode', models.IntegerField(null=True, blank=True)),
                ('site', models.ForeignKey(to='images.Site')),
            ],
            options={
                'db_table': 'telescope',
            },
        ),
        migrations.AddField(
            model_name='image',
            name='telescope',
            field=models.ForeignKey(to='images.Telescope'),
        ),
    ]
