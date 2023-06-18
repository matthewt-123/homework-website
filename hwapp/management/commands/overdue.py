from hwapp.email_helper import overdue_check
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        overdue_check()
