# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='filter',
            new_name='filters',
        ),
        migrations.AddField(
            model_name='image',
            name='dateobs',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 11, 9, 6, 30, 324516)),
        ),
    ]
