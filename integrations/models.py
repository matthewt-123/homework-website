from django.db import models
import sys
sys.path.append("..")
from hwapp.models import User
# Create your models here.
    
class CalendarEvent(models.Model):
    calendar_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    homework_event = models.ForeignKey('hwapp.Homework', on_delete=models.CASCADE, blank=True, null=True)
    ics = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.calendar_user}"
class IcsHashVal(models.Model):
    hash_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hash_user')
    hash_val = models.CharField(max_length=128)
    hash_type = models.CharField(max_length=128, default=None, blank=True, null=True)
class NotionData(models.Model):
    notion_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    access_token = models.CharField(max_length=512, default=None, blank=True, null=True)
    bot_id = models.CharField(max_length=512, default=None, blank=True, null=True)
    workspace_name = models.CharField(max_length=512, default=None, blank=True, null=True)
    workspace_id =  models.CharField(max_length=512, default=None, blank=True, null=True)
    db_id = models.TextField(default=None, blank=True, null=True)
    def __str__(self):
        return f"{self.notion_user}"
class GoogleData(models.Model):
    google_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    code = models.CharField(max_length=512, default=None, blank=True, null=True)
    refresh_token = models.CharField(max_length=512, default=None, blank=True, null=True)
    access_token = models.CharField(max_length=512, default=None, blank=True, null=True)
    id_token = models.CharField(max_length=512, default=None, blank=True, null=True)
    sync_token = models.CharField(max_length=512, default=None, blank=True, null=True)
    def __str__(self):
        return f"{self.google_user}"
class GoogleCalendar(models.Model):
    google_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    calendar_name = models.CharField(max_length=512, default=None, blank=True, null=True)
    calendar_id = models.CharField(max_length=256, default=None, blank=True, null=True)
    sync_token = models.CharField(max_length=512, default=None, blank=True, null=True)
    def __str__(self):
        return f"{self.calendar_name}"
