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
