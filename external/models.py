from django.db import models
from model_utils.fields import StatusField
from model_utils import Choices
from datetime import datetime
import django
# Create your models here.
class HelpForm(models.Model):
    STATUS = Choices('Incomplete', 'In Progress', 'Completed')
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    received = models.DateField(default = django.utils.timezone.now)
    subject = models.CharField(default="", null=True, blank=True, max_length=256)
    message = models.TextField()
    status = StatusField()
    parent_form= models.ForeignKey('HelpForm',null=True,blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.received}: {self.subject}"