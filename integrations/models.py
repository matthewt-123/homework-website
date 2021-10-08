from django.db import models
import sys
sys.path.append("..")
from hwapp.models import User
# Create your models here.
class IntegrationOption(models.Model):
    integration = models.CharField(max_length=128)
    def __str__(self):
        return self.integration


class AdminOnly(models.Model):
    admin_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    application = models.CharField(max_length=128, default=None, blank=True, null=True)
    admin_cookie = models.TextField(default=None)
    
    
class CalendarEvent(models.Model):
    calendar_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    homework_event = models.ForeignKey('hwapp.Homework', on_delete=models.CASCADE, blank=True, null=True)
    integration_event = models.ForeignKey(IntegrationOption, on_delete=models.CASCADE, blank=True, null=True)
    ics = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.calendar_user}"
class IcsHashVal(models.Model):
    hash_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hash_user')
    hash_val = models.CharField(max_length=128)