from django.db import models

# Create your models here.
class IntegrationOption(models.Model):
    integration = models.CharField(max_length=128)
    def __str__(self):
        return self.integration
class IntegrationPreference(models.Model):
    integrations_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    integration_choices = models.ManyToManyField(IntegrationOption, blank=True, null=True)
    schoology_ics_link = models.CharField(max_length=512, blank=True, null=True)
    schoology_ics = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.integrations_user}"
    
class CalendarEvent(models.Model):
    calendar_user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    homework_event = models.ForeignKey('hwapp.Homework', on_delete=models.CASCADE, blank=True, null=True)
    integration_event = models.ForeignKey(IntegrationOption, on_delete=models.CASCADE, blank=True, null=True)
    ics = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.calendar_user}"
