from hwapp.email_helper import send_email, canvas_hw,schoology_hw
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        canvas_hw()
        schoology_hw()
