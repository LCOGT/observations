# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0004_auto_20160411_1111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='dateobs',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 11, 10, 13, 54, 845549)),
        ),
    ]
