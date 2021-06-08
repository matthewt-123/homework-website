from django.contrib.auth.models import AbstractUser
from django.db import models
from phone_field import PhoneField

# Create your models here.
class User(AbstractUser):
    pass
class Recurrence(models.Model):
    basis = models.CharField(max_length=128)
    hour_definition = models.IntegerField()
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
    days = models.ManyToManyField(Day, null=True, blank=True,)
    time = models.TimeField()
    def __str__(self):
        return f"{self.class_name}"
class Homework(models.Model):
    hw_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hw_user')
    hw_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='hw_class1')
    hw_title = models.CharField(max_length=256)
    due_date = models.DateField()
    priority = models.IntegerField()
    notes = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.hw_title}"
class Carrier(models.Model):
    carrier = models.CharField(max_length = 64)
    email = models.CharField(max_length = 128)
    def __str__(self):
        return f"{self.carrier}"
class Preferences(models.Model):
    preferences_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferences_user')
    email_notifications = models.BooleanField(default=False)
    email_recurrence = models.ForeignKey(Recurrence, null=True, blank=True, on_delete=models.CASCADE, related_name="recurrence")
    text_notifications = models.BooleanField(default=False)
    phone_number = PhoneField(blank=True, null=True )
    carrier = models.ForeignKey(Carrier, on_delete=models.CASCADE, null=True, blank=True)
    calendar_output = models.BooleanField(default=False)
