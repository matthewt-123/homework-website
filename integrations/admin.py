
from django.contrib import admin
from .models import CalendarEvent,IcsHashVal, NotionData, GoogleData,GoogleCalendar,SchoologyAuth,SchoologyClasses

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
def schoology(modeladmin, request, queryset):
    queryset.update(auth_data=1)

class SchoologyClassesAdmin(admin.ModelAdmin):
    list_display = ("schoology_user", "s_class_name", "class_id", "s_grading_period","update")
    actions=[disable, enable, schoology]
class SchoologyAuthAdmin(admin.ModelAdmin):
    actions=[schoology]
# Register your models here.

admin.site.register(CalendarEvent)
admin.site.register(IcsHashVal)

admin.site.register(NotionData)
admin.site.register(GoogleData)
admin.site.register(GoogleCalendar)
admin.site.register(SchoologyAuth, SchoologyAuthAdmin)
admin.site.register(SchoologyClasses, SchoologyClassesAdmin)


