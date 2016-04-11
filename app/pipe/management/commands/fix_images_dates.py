from django.core.management.base import BaseCommand, CommandError
from datetime import datetime

from images.models import Image
from images.utils import parsetime

class Command(BaseCommand):
    help = 'Change all image dates to DateTimeField'

    def handle(self, *args, **options):
        images = Image.objects.all()
        self.stdout.write("Converting %s images" % images.count())
        for im in images:
            im.dateobs = parsetime(im.whentaken)
            im.save()
        self.stdout.write("Finished")
