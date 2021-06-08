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
import datetime
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
        i=0
        open(f"{request.user.username}_schoology_temp.ics", 'wb').
        for event in c:
            if "BEGIN:VEVENT" in event:
                for x in range(20):
                    if "END:VEVENT" in c[i+x]:
                        break
                    elif "SUMMARY" in c[i+x]:
                        hw_title = c[i+x]
                    elif "DESCRIPTION" in c[i+x]:
                        notes = c[i+x]
                try:
                    class1=Class.objects.get(class_user=request.user, class_name="Schoology")
                except:
                    class1=Class(class_user=request.user, class_name="Schoology", period=100, time=datetime.datetime.now().time() )
                    class1.save()
                if not notes:
                    notes=None
                new_hw = Homework(hw_user=request.user, hw_title=hw_title, notes=notes, hw_class=class1)
                new_hw.save
            i+=1

        
    else:
        return render(request, 'hwapp/schoology_ics.html')

@login_required(login_url='/login')
def canvas_init(request):
    pass

@login_required(login_url='/login')
def export(request):
    pass