
from django.contrib import admin
from .models import IntegrationOption, Cookie, CalendarEvent

# Register your models here.

admin.site.register(Cookie)
admin.site.register(IntegrationOption)
admin.site.register(CalendarEvent)

