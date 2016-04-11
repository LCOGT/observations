# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0002_auto_20160411_1006'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='rti_username',
            new_name='username',
        ),
        migrations.AddField(
            model_name='telescope',
            name='enclosure',
            field=models.CharField(max_length=4, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='dateobs',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 11, 10, 2, 56, 644584)),
        ),
    ]
