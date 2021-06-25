from django.forms import ModelForm
from .models import Homework, Preferences, Class, Day
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
        fields = ['email_notifications', 'email_recurrence', 'text_notifications', 'phone_number', 'carrier', 'calendar_output', 'user_timezone']

class AddClassForm(ModelForm):
    class Meta:
        model = Class
        fields = ['class_name', 'period', 'days', 'time']
    days = forms.ModelMultipleChoiceField(
        queryset = Day.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    time = forms.TimeInput()