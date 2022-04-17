
from django.contrib import admin
from .models import IntegrationOption, AdminOnly, CalendarEvent,IcsHashVal, NotionData

# Register your models here.

admin.site.register(AdminOnly)
admin.site.register(IntegrationOption)
admin.site.register(CalendarEvent)
admin.site.register(IcsHashVal)

admin.site.register(NotionData)