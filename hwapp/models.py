from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class User(AbstractUser):
    pass
class Recurrence(models.Model):
    basis = models.CharField(max_length=128)
    def __str__(self):
        return f"{self.basis}"
class Day(models.Model):
    days = models.CharField(max_length=128)
    def __str__(self):
        return f"{self.days}"
class Class(models.Model):
    class_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='class_owner')
    class_name = models.CharField(max_length=128)
    period = models.IntegerField(null=True, blank=True,)
    time = models.TimeField()
    ics_link = models.CharField(blank=True, null=True, max_length=512)
    def __str__(self):
        return f"{self.class_name}"
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
    email_notifications = models.BooleanField(default=False)
    email_recurrence = models.ForeignKey(Recurrence, null=True, blank=True, on_delete=models.CASCADE, related_name="recurrence")
    text_notifications = models.BooleanField(default=False)
    phone_number = models.BigIntegerField(blank=True, null=True )
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, null=True, blank=True)
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
    def __str__(self):
        return f"{self.template_name}"
class IcsId(models.Model):
    icsID_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='icsID_user')
    icsID = models.CharField(max_length=512)
class AllAuth(models.Model):
    allauth_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='allauth_user')
    uid = models.CharField(max_length=512)
    extra_data = models.TextField()