# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pipe', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 11, 9, 2, 58, 421278)),
        ),
    ]
