from django import forms
from datetime import datetime,date
from images.models import Site, Filter

class SearchForm(forms.Form):
    sites = [(s.code, s.name) for s in Site.objects.all()]
    filters = [(f.code, f.name) for f in Filter.objects.all().distinct()]
    sites.append(('','Select a site...'))
    filters.append(('','Select a filter...'))

    query = forms.CharField('Name of astronomical object:',required=False)
    startdate = forms.DateField(required=False)
    enddate = forms.DateField(required=False)
    alldates = forms.BooleanField(required=False)
    #ra = forms.FloatField()
    #dec = forms.FloatField()
    sites = forms.ChoiceField(choices=sites, required=False)
    filters = forms.ChoiceField(choices=filters, required=False)
    exposure = forms.FloatField(widget=forms.TextInput(attrs={'size': '5'}), required=False)
    exposurecondition = forms.ChoiceField(choices=(('gt','greater than'),('lt','less than'),('eq','equals')), required=False)

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
            if data < date(2004,9,1):
                raise forms.ValidationError("Our records only go back to 1 Sept 2004")
            return data
        else:
            return self.cleaned_data['startdate']