from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass

class Day(models.Model):
    days = models.CharField(max_length=128)
    abbreviation = models.CharField(max_length=128)
    def __str__(self):
        return f"{self.days}"
class Class(models.Model):
    class_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_owner')
    class_name = models.CharField(max_length=128)
    period = models.IntegerField(null=True, blank=True,)
    time = models.TimeField(null=True, blank=True)
    ics_link = models.CharField(blank=True, null=True, max_length=512)
    archived = models.BooleanField(blank=False, default=False, null=False)
    external_id = models.CharField(null=True, blank=True,max_length=128)
    external_src = models.CharField(null=True, blank=True,max_length=128)
    def __str__(self):
        return f"{self.class_name}"
class Recurring(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    days = models.ManyToManyField(Day)
    time = models.TimeField(blank=True,null=True)
    hw_class = models.ForeignKey(Class, on_delete=models.CASCADE, blank=True, null=True)
    hw_title = models.CharField(blank=True, max_length=256, null=True)
    notes = models.TextField(blank=True, null=True)
class Homework(models.Model):
    hw_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hw_user')
    hw_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='hw_class1', blank=True, null=True)
    hw_title = models.CharField(blank=True, max_length=256, null=True)
    due_date = models.DateTimeField(blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(blank=True, default=True, null=True)
    overdue = models.BooleanField(blank=True, default=False, null=True)
    notion_migrated = models.BooleanField(blank=True, default=False, null=True)
    notion_id = models.CharField(blank=True, default=False, null=True, max_length=256)
    ics_id = models.CharField(blank=True, default=False, null=True, max_length=256)
    external_id = models.CharField(blank=True, default=False, null=True, max_length=128)
    external_src = models.CharField(null=True, blank=True,max_length=128)
    recurring = models.ForeignKey(Recurring, on_delete=models.CASCADE,null=True, blank=True)
    archive = models.BooleanField(blank=False, default=False, null=False)
    def __str__(self):
        return f"{self.hw_title}"
class Carrier(models.Model):
    carrier = models.CharField(max_length = 64)
    email = models.CharField(max_length = 128)
    def __str__(self):
        return f"{self.carrier}"
class Timezone(models.Model):
    timezone = models.CharField(max_length=256)
    def __str__(self):
        return f"{self.timezone}"
class Preferences(models.Model):
    preferences_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferences_user')
    calendar_output = models.BooleanField(default=True)
    user_timezone = models.ForeignKey(Timezone, null=True, blank=True, on_delete=models.CASCADE)
class PWReset(models.Model):
    reset_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pw_reset_user')
    hash_val = models.CharField(max_length=256)
    expires = models.DateTimeField()
    active = models.BooleanField(default=True)
class IcsLink(models.Model):
    link_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='links')
    link_application = models.CharField(max_length=128)
    link = models.TextField()
class EmailTemplate(models.Model):
    template_name = models.CharField(max_length=64)
    template_body = models.TextField()
    type = models.CharField(max_length=64, default=False, blank=False, null=True)
    version_id = models.IntegerField(default=False, blank=False, null=True)
    def __str__(self):
        return f"{self.template_name}"
class IcsId(models.Model):
    icsID_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='icsID_user')
    icsID = models.CharField(max_length=512)
class AllAuth(models.Model):
    allauth_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='allauth_user')
    uid = models.CharField(max_length=512)
    extra_data = models.TextField()
