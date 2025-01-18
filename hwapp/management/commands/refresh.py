from hwapp.email_helper import canvas_hw,schoology_hw
from django.core.management.base import BaseCommand
import sys
sys.path.append("..")
from integrations.helper import notion_pull, gradescope_refresh
class Command(BaseCommand):
    def handle(self, *args, **options):
        canvas_hw()
        schoology_hw()
        notion_pull()
        gradescope_refresh()
