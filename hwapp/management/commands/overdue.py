from django.core.management.base import BaseCommand # pylint: disable=0401
from hwapp.email_helper import overdue_check

class Command(BaseCommand):
    def handle(self, *args, **options):
        """ Update overdue assignment flags """
        overdue_check()
