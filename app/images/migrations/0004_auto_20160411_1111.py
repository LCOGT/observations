# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0003_auto_20160411_1103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='schoolid',
        ),
        migrations.RemoveField(
            model_name='image',
            name='whentaken',
        ),
        migrations.AlterField(
            model_name='image',
            name='dateobs',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 11, 10, 11, 22, 990816)),
        ),
        migrations.AlterField(
            model_name='image',
            name='imageid',
            field=models.IntegerField(help_text=b'Block ID if from ODIN', serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='username',
            field=models.CharField(help_text=b'If processingtype is STIFF this is ODIN username else RTI username', max_length=150, null=True, blank=True),
        ),
    ]
