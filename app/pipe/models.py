# -*- coding: utf-8 -*-
'''
Observations: Open access archive app for Las Cumbres Observatory Global Telescope Network
Copyright (C) 2014-2015 LCOGT

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''
from django.db import models

from datetime import datetime

class Proposal(models.Model):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=64, blank=True,null=True)
    active = models.BooleanField(default=True)
    last_update = models.DateTimeField(default=datetime.utcnow())

    def __unicode__(self):
        return self.name
