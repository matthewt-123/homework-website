
from hwapp.email_helper import recurring_events
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        recurring_events()
