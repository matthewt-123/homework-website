from django.db import models

# Create your models here.
class HelpForm(models.Model):
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=64)
    email = models.EmailField()
    message = models.TextField()