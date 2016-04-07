from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from datetime import datetime

from images.views import recent_frames
from pipeline.views import parse_frames_list

class Command(BaseCommand):
    help = 'Find frames to colour and save coloured images'

    def handle(self, *args, **options):
        self.stdout.write("==== Fetching Recent Observations %s ====" % (datetime.now().strftime('%Y-%m-%d %H:%M')))
        proposals = Proposal.objects.filter(active=True)
        for proposal in proposals:
            frames = recent_frames(proposal_id=proposal.code, datestamp=proposal.last_update.strftime("%Y-%m-%d")
