# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pipe', '0002_auto_20160411_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 11, 10, 13, 54, 848215)),
        ),
    ]
