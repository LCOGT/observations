# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pipe', '0003_auto_20160411_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proposal',
            name='last_update',
            field=models.DateTimeField(default=datetime.datetime.utcnow),
        ),
    ]
