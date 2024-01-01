from hwapp.models import Homework
from django.core.management.base import BaseCommand

from integrations.models import NotionData
from integrations.helper import notion_push, notion_pull

class Command(BaseCommand):
    def handle(self, *args, **options):
        notion_pull()
        users = NotionData.objects.all()
        for user1 in users:
            to_post = Homework.objects.filter(hw_user=user1.notion_user, completed=False, notion_migrated=False)
            for hw in to_post:
                notion_push(hw, user1.notion_user)
                