from django.contrib import admin
from .models import User, Day, Class, Homework, Preferences, Timezone, IcsLink, EmailTemplate, IcsId, AllAuth
from django.contrib.admin.models import LogEntry

# Register your models here.
@admin.action(description='Unpush Notion')
def unpush_notion(modeladmin, request, queryset):
    queryset.update(notion_migrated=False)

@admin.action(description='Archive Class')
def archive_class(modeladmin, request, queryset):
    queryset.update(archived=True)
@admin.action(description='Archive Homework')
def archive_hw(modeladmin, request, queryset):
    queryset.update(archive=True)
@admin.action(description='Complete Homework')
def archive_hw(modeladmin, request, queryset):
    queryset.update(completed=True)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "class_user", "class_name", "archived")
    actions = [archive_class]
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("id", "hw_class", "hw_user", "hw_title", "priority", "notes", "completed")
    actions=[unpush_notion, archive_hw]
class PreferencesAdmin(admin.ModelAdmin):
    list_display = ("id", "preferences_user")
admin.site.register(User)
admin.site.register(Day)
admin.site.register(Class, ClassAdmin)
admin.site.register(Homework, HomeworkAdmin)
admin.site.register(Preferences, PreferencesAdmin)
admin.site.register(IcsLink)
admin.site.register(Timezone)
admin.site.register(EmailTemplate)
admin.site.register(IcsId)
admin.site.register(AllAuth)
admin.site.register(LogEntry)
