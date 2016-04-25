from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime

from images.views import recent_frames
from pipe.imager import parse_frames_list, run_colour_imager
from pipe.models import Proposal

class Command(BaseCommand):
    help = 'Find frames to colour and save coloured images'

    def add_arguments(self, parser):
        parser.add_argument("-c", "--credit", help="apply a standard LCOGT credit watermark", action="store_true")
        parser.add_argument("-p", "--preview", help="show a PIL generated JPEG preview", action="store_true")
        parser.add_argument("-f", "--feedback", help="Console feedback on file downloads", action="store_true")
        parser.add_argument("-s", "--start", help="Start end to look for observations in ISO format")

    def handle(self, *args, **options):
        self.stdout.write("==== Fetching Recent Observations %s ====" % (datetime.now().strftime('%Y-%m-%d %H:%M')))
        proposals = Proposal.objects.filter(active=True)
        for proposal in proposals:
            if args.start:
                start = datetime.strftime(args.start, "%Y-%m-%d")
            else:
                start = proposal.last_update.strftime("%Y-%m-%d")
            frames = recent_frames(proposal_id=proposal.code, datestamp=start)
            resp = parse_frames_list(frames, args)
            for block in resp:
                new_image = run_colour_imager(block, args)
