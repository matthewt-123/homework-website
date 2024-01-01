from django.contrib import admin
from .models import User, Class, Homework, Preferences, Timezone, EmailTemplate, AllAuth, FileBin, PasteBin
from django.contrib.admin.models import LogEntry
from django.contrib.auth.admin import UserAdmin

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

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        if not is_superuser:
            disabled_fields = {
                'username',
                'is_superuser',
                'date_joined',
                'last_login'
            }
            for f in disabled_fields:
                if f in form.base_fields:
                    form.base_fields[f].disabled = True
        form.base_fields['bookmarks'] = True
        return form

admin.site.register(Class, ClassAdmin)
admin.site.register(Homework, HomeworkAdmin)
admin.site.register(Preferences, PreferencesAdmin)
admin.site.register(Timezone)
admin.site.register(EmailTemplate)
admin.site.register(AllAuth)
admin.site.register(LogEntry)
admin.site.register(PasteBin)
admin.site.register(FileBin)
