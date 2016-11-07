from images.models import Site, Telescope, Filter, Image, ObservationStats, wistime_format
from images.lookups import categories, categorylookup
from images.views import get_sci_fits

from django.views.generic import ListView, DetailView

class ImageDetail(DetailView):

    model = Image

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(ImageDetail, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        # context['book_list'] = Book.objects.all()
        try:
            schoolname = self.object.username
        except:
            schoolname = "Unknown"
        context['observer'] = schoolname
        try:
            filter_obj = Filter.objects.filter(code=self.object.filters)
        except:
            filter_obj = self.object.filters
        context['filters'] = filter_obj
        context['views'] = obs_stats(self.object)
        context['files'] = get_sci_fits(self.object)
        return context

class ImageList(ListView):

    model = Image

def obs_stats(image):
    observation = {}
    try:
        obstats = ObservationStats.objects.filter(image=image)
        if(obstats[0].avmcode != "0.0"):
            observation['avmcode'] = obstats[0].avmcode
            cats = o['avmcode'].split(';')
            observation['avmname'] = ""
            for (counter, c) in enumerate(cats):
                if counter > 0:
                    observation['avmname'] += ";"
                if c in categorylookup:
                    observation['avmname'] += categorylookup[c]
        else:
            observation['avmcode'] = ""
        observation['views'] = obstats[0].views
    except:
        observation['avmcode'] = ""
    return observation
