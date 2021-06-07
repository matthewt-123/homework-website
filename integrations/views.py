from django.shortcuts import render
from django.http.response import JsonResponse
from django.shortcuts import render
from django.db import IntegrityError, connection
from django.forms import ModelForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import os
from .models import IntegrationOption, IntegrationPreference, CalendarEvent
from dotenv import load_dotenv
import json
import requests
import random
import string
from ics import Calendar, Event

#import hwapp models
import sys
sys.path.append("..")
from hwapp.models import Homework, Class

load_dotenv()
# Create your views here.
@login_required(login_url='/login')
def index(request):
    pass

@login_required(login_url='/login')
def schoology_init(request):
    if request.method == "POST":
        #make link an https link
        link = request.POST.get('schoology_ics_link')
        link = link.replace('webcal', 'https')
        c = Calendar(requests.get(link).text)
        #append new hw to database and calendar
        for event in c:
            if "VEVENT" in event:
                print(event)

        
    else:
        return render(request, 'hwapp/schoology_ics.html')

@login_required(login_url='/login')
def canvas_init(request):
    pass

@login_required(login_url='/login')
def export(request):
    pass