
from django.contrib import admin
from .models import CalendarEvent,IcsHashVal, NotionData, GoogleData,GoogleCalendar,SchoologyAuth,SchoologyClasses,IntegrationLog

@admin.action(description='Disable Class Import')
def disable(modeladmin, request, queryset):
    queryset.update(update=False)
@admin.action(description='Enable Class Import')
def enable(modeladmin, request, queryset):
    queryset.update(update=True)
@admin.action(description='Set src=Schoology')
def schoology(modeladmin, request, queryset):
    queryset.update(src='Schoology')
@admin.action(description='Set auth=Schoology')
def auth_update(modeladmin, request, queryset):
    queryset.update(auth_data=1)

class SchoologyClassesAdmin(admin.ModelAdmin):
    list_display = ("schoology_user", "s_class_name", "class_id", "s_grading_period","update")
    actions=[disable, enable, schoology, auth_update]
class SchoologyAuthAdmin(admin.ModelAdmin):
    actions=[schoology]
# Register your models here.
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "src", "dest", "user", "date", "error")
admin.site.register(CalendarEvent)
admin.site.register(IcsHashVal)
admin.site.register(IntegrationLog, IntegrationLogAdmin)

admin.site.register(NotionData)
admin.site.register(GoogleData)
admin.site.register(GoogleCalendar)
admin.site.register(SchoologyAuth, SchoologyAuthAdmin)
admin.site.register(SchoologyClasses, SchoologyClassesAdmin)


