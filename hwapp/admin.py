from django.contrib import admin
from .models import User, Recurrence, Day, Class, Homework, Preferences, Carrier, Timezone, PWReset, IcsLink, EmailTemplate, IcsId, AllAuth

# Register your models here.
@admin.action(description='Unpush Notion')
def unpush_notion(modeladmin, request, queryset):
    queryset.update(notion_migrated=False)
@admin.action(description='Archive Class')
def archive_class(modeladmin, request, queryset):
    queryset.update(archived=True)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "class_user", "class_name", "period", "time")
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("id", "hw_class", "hw_user", "hw_title", "priority", "notes", "completed")
    actions=[unpush_notion]
class PreferencesAdmin(admin.ModelAdmin):
    list_display = ("id", "preferences_user")
admin.site.register(User)
admin.site.register(Recurrence)
admin.site.register(Day)
admin.site.register(Class, ClassAdmin)
admin.site.register(Homework, HomeworkAdmin)
admin.site.register(Preferences, PreferencesAdmin)
admin.site.register(Carrier)
admin.site.register(PWReset)
admin.site.register(IcsLink)
admin.site.register(Timezone)
admin.site.register(EmailTemplate)
admin.site.register(IcsId)
admin.site.register(AllAuth)
