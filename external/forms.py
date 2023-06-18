from django.forms import ModelForm
from .models import HelpForm
from django.contrib.admin import widgets


class HelpForm1(ModelForm):
    class Meta:
        model = HelpForm
        fields = ['first_name', 'last_name', 'email', 'message']
