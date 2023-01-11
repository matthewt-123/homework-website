
from django.contrib import admin
from .models import CalendarEvent,IcsHashVal, NotionData, GoogleData,GoogleCalendar,SchoologyAuth,SchoologyClasses

@admin.action(description='Disable Class Import')
def disable(modeladmin, request, queryset):
    queryset.update(update=False)
@admin.action(description='Enable Class Import')
def enable(modeladmin, request, queryset):
    queryset.update(update=True)

class SchoologyClassesAdmin(admin.ModelAdmin):
    list_display = ("schoology_user", "s_class_name", "class_id", "s_grading_period","update")
    actions=[disable, enable]
# Register your models here.

admin.site.register(CalendarEvent)
admin.site.register(IcsHashVal)

admin.site.register(NotionData)
admin.site.register(GoogleData)
admin.site.register(GoogleCalendar)
admin.site.register(SchoologyAuth)
admin.site.register(SchoologyClasses, SchoologyClassesAdmin)


