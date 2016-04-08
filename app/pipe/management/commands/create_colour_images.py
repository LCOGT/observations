from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime

from images.views import recent_frames
from pipeline.imager import parse_frames_list, run_colour_imager

class Command(BaseCommand):
    help = 'Find frames to colour and save coloured images'

    def add_arguments(self, parser):
        parser.add_argument("-c", "--credit", help="apply a standard LCOGT credit watermark", action="store_true")
        parser.add_argument("-p", "--preview", help="show a PIL generated JPEG preview", action="store_true")
        parser.add_argument("-f", "--feedback", help="Console feedback on file downloads", action="store_true")

    def handle(self, *args, **options):
        self.stdout.write("==== Fetching Recent Observations %s ====" % (datetime.now().strftime('%Y-%m-%d %H:%M')))
        proposals = Proposal.objects.filter(active=True)
        for proposal in proposals:
            frames = recent_frames(proposal_id=proposal.code, datestamp=proposal.last_update.strftime("%Y-%m-%d"))
            resp = parse_frames_list(frames, args)
            for block in resp:
                new_image = run_colour_imager(block, args)
                if new_image:
                    image = Image(
                                imageid = models.IntegerField(primary_key=True)
                                whentaken = models.CharField(max_length=42, blank=True,null=True)
                                schoolid = models.IntegerField(blank=True,null=True)
                                objectname = models.CharField(max_length=100,blank=True,null=True)
                                ra = models.FloatField(blank=True,null=True)
                                dec = models.FloatField(blank=True,null=True)
                                filter = models.CharField(max_length=30, blank=True,null=True)
                                exposure = models.FloatField(blank=True,null=True)
                                requestids = models.CharField(max_length=50, blank=True,null=True)
                                telescope = models.ForeignKey(Telescope)
                                filename = models.CharField(max_length=150, blank=True,null=True)
                                rti_username = models.CharField(max_length=150, blank=True,null=True)
                                observer = models.CharField(max_length=150, blank=True,null=True)
                                processingtype = models.CharField(max_length=20, blank=True, null=True)
                                instrumentname = models.CharField(max_length=60, blank=True, null=True)
                                archive_link = models.CharField(max_length=200,blank=True,null=True)
                    )
