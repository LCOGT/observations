# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=20)),
                ('name', models.CharField(max_length=64, null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('last_update', models.DateTimeField(default=datetime.datetime(2016, 4, 7, 15, 25, 40, 335272))),
            ],
        ),
    ]
