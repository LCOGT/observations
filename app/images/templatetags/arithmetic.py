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
from django.template import Library
register = Library()

@register.filter(name='mult')
def mult(value, arg):
    "Multiplies the arg and the value"
    return int(value) * int(arg)
mult.is_safe = False

@register.filter(name='sub')
def sub(value, arg):
    "Subtracts the arg from the value"
    return int(value) - int(arg)
sub.is_safe = False

@register.filter(name='div')
def div(value, arg):
    "Divides the value by the arg"
    return "%.2f" % (float(value) / float(arg))
div.is_safe = False
