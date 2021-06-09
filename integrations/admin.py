
from django.contrib import admin
from .models import IntegrationOption, IntegrationPreference, CalendarEvent

# Register your models here.

admin.site.register(IntegrationPreference)
admin.site.register(IntegrationOption)
admin.site.register(CalendarEvent)

