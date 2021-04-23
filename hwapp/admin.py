from django.contrib import admin
from .models import User, Recurrence, Day, Class, Homework, Preferences

# Register your models here.
class ClassAdmin(admin.ModelAdmin):
    list_display = ("id", "class_user", "class_name", "period", "time")
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("id", "hw_class", "hw_user", "hw_title", "priority", "notes", "active")
class PreferencesAdmin(admin.ModelAdmin):
    list_display = ("id", "preferences_user", "email_notifications", "email_recurrence")
admin.site.register(User)
admin.site.register(Recurrence)
admin.site.register(Day)
admin.site.register(Class, ClassAdmin)
admin.site.register(Homework, HomeworkAdmin)
admin.site.register(Preferences, PreferencesAdmin)