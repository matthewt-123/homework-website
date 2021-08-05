from hwapp.email_helper import send_email
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        send_email('Daily')
        print(True)