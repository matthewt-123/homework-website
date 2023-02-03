from django.forms import ModelForm
from .models import Homework, Preferences, Class, Day, EmailTemplate, Recurring
from django import forms
from django.contrib.admin import widgets


forms.DateInput.input_type="date"
forms.TimeInput.input_type="time"

class HomeworkForm(ModelForm):
    class Meta:
        model = Homework
        fields = ['hw_class', 'hw_title', 'due_date', 'priority', 'notes']


class PreferencesForm(ModelForm):
    class Meta:
        model = Preferences
        fields = ['calendar_output', 'user_timezone']

class AddClassForm(ModelForm):
    class Meta:
        model = Class
        fields = ['class_name', 'period', 'time']
    time = forms.TimeInput()
class AddTemplateForm(ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['template_name', 'template_body']
class AddRecurrenceForm(ModelForm):
    class Meta:
        model = Recurring
        fields = ['hw_title','hw_class','days', 'time','notes']