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
    class Meta:
        verbose_name = ('Class')
        verbose_name_plural = ('Classes')
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
    external_id = models.CharField(blank=True, default=False, null=True, max_length=128)
    external_src = models.CharField(null=True, blank=True,max_length=128)
    archive = models.BooleanField(blank=False, default=False, null=False)
    def __str__(self):
        return f"{self.hw_title}"
class Timezone(models.Model):
    timezone = models.CharField(max_length=256)
    def __str__(self):
        return f"{self.timezone}"
class Preferences(models.Model):
    preferences_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferences_user')
    user_timezone = models.ForeignKey(Timezone, null=True, blank=True, on_delete=models.CASCADE)
    class Meta:
        verbose_name = ('Preferences')
        verbose_name_plural = ('Preferences')
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
    class Meta:
        verbose_name = ('Auth0 SSO')
        verbose_name_plural = ('Auth0 SSO')

class PasteBin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(default="", blank="") 
def user_directory_path(instance, filename): 
  
    # file will be uploaded to MEDIA_ROOT / user_<id>/<filename> 
    return 'uploads/user_{0}/{1}'.format(instance.user.id, filename) 
class FileBin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=user_directory_path) 