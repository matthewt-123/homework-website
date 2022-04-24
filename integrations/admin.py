
from django.contrib import admin
from .models import CalendarEvent,IcsHashVal, NotionData, GoogleData,GoogleCalendar

# Register your models here.

admin.site.register(CalendarEvent)
admin.site.register(IcsHashVal)

admin.site.register(NotionData)
admin.site.register(GoogleData)
admin.site.register(GoogleCalendar)
