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
    tag = models.CharField(max_length = 128, default="homework", blank="homework", null="homework")
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
class SchoologyClasses(models.Model):
    schoology_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    class_id = models.IntegerField(default=None, blank=True, null=True)
    s_class_name =  models.CharField(max_length=512, default=None, blank=True, null=True)
    s_grading_period = models.IntegerField(default=None, blank=True, null=True)
    update = models.BooleanField(null=True, blank=True)
    linked_class = models.ForeignKey('hwapp.Class', on_delete=models.CASCADE,default=None, blank=True, null=True)
    src = models.CharField(max_length=512, default=None, blank=True, null=True) 
    auth_data = models.ForeignKey('SchoologyAuth', on_delete=models.CASCADE,default=None, blank=True, null=True)
    def __str__(self):
        return f"{self.schoology_user}- {self.s_class_name}-{self.update}"
class SchoologyAuth(models.Model):
    h_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    s_consumer_key =  models.CharField(max_length=512, default=None, blank=True, null=True)
    s_secret_key = models.CharField(max_length=512, default=None, blank=True, null=True)
    user_id = models.IntegerField(default=None, blank=True, null=True)
    src = models.CharField(max_length=512, default=None, blank=True, null=True)
    url = models.CharField(max_length=512, default=None, blank=True, null=True)  
    def __str__(self):
        return f"{self.h_user}- {self.url}"
class IntegrationLog(models.Model):
    user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    src = models.CharField(max_length=512, default=None, blank=True, null=True)
    dest = models.CharField(max_length=512, default=None, blank=True, null=True)
    url = models.CharField(max_length=512, default=None, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    message = models.TextField(default=None, blank=True, null=True)
    error = models.BooleanField(default=False, blank=True, null=True)
    hw_name = models.CharField(max_length=512, default=None, blank=True, null=True)
    def __str__(self):
        return f"{self.user}: {self.src}->{self.dest}"
class Log(models.Model):
    user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    url = models.CharField(max_length=512, default=None, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    message = models.TextField(default=None, blank=True, null=True)
    error = models.BooleanField(default=False, blank=True, null=True)
    log_type = models.CharField(max_length=512, default=None, blank=True, null=True) #types: access, manual refresh, cron, hw/class refresh, notion pull
    ip_address = models.CharField(max_length=16, default=0, blank=0, null=0)
    def __str__(self):
        return f"{self.user}: {self.log_type}"