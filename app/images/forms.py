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
from django import forms
from datetime import datetime, date
from images.models import Site, Filter


class SearchForm(forms.Form):
    sites = [(s.code, s.name) for s in Site.objects.all()]
    filters = [(f.code, f.name) for f in Filter.objects.all().distinct()]
    sites.append(('', 'Select a site...'))
    filters.append(('', 'Select a filter...'))

    query = forms.CharField(label='Name of astronomical object:', required=False)
    startdate = forms.DateTimeField(required=False)
    enddate = forms.DateTimeField(required=False)
    alldates = forms.BooleanField(required=False)
    sites = forms.ChoiceField(choices=sites, required=False)
    filters = forms.ChoiceField(choices=filters, required=False)
    exposure = forms.FloatField(widget=forms.TextInput(attrs={'size': '5'}), required=False)
    exposurecondition = forms.ChoiceField(choices=(
        ('gt', 'greater than'), ('lt', 'less than'), ('eq', 'equals')), required=False)
    offset = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.fields['startdate'].widget.attrs['placeholder'] = 'YYYY-MM-DD'
        self.fields['enddate'].widget.attrs['placeholder'] = 'YYYY-MM-DD'
        self.fields['startdate'].initial = "2014-04-01"
        self.fields['enddate'].initial = datetime.now().strftime("%Y-%m-%d")
        self.fields['exposurecondition'].initial = 'gt'
        self.fields['alldates'].initial = False

    def clean_startdate(self):
        if self.cleaned_data['startdate']:
            data = self.cleaned_data['startdate']
            if data < datetime(2004, 9, 1):
                raise forms.ValidationError(
                    "Our records only go back to 1 Sept 2004")
            return data
        else:
            return self.cleaned_data['startdate']
