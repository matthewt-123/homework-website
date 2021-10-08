from io import StringIO
from django.contrib.auth import login
from django.http.request import RAISE_ERROR
from django.shortcuts import render
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.forms import ModelForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import os
from .models import CalendarEvent, IcsHashVal
from dotenv import load_dotenv
import datetime
import json
import requests
from ics import Calendar, Event



#import hwapp models
import sys
sys.path.append("..")
from hwapp.models import Homework, Class, Day, Preferences, User

load_dotenv()
# Create your views here.
@login_required(login_url='/login')
def index(request):
    return render(request, 'hwapp/integrations.html')

@login_required(login_url='/login')
def schoology_init(request):
    if request.method == "POST":
        try:
            #make link an https link
            link = request.POST.get('schoology_ics_link')
            link = link.replace('webcal', 'https')
            c = Calendar(requests.get(link).text)
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'Please copy the full link from Schoology with the instructions below and include the "webcal" portion of the link'
            })
        #SETUP: create Schoology Class instance if not already existing(since Schoology does not provide class names with HW assignments)
        dt_str = '00:00'
        dt_obj = datetime.datetime.strptime(dt_str, '%H:%M')
        day = Day.objects.get(days='Sunday')
        try:
            class1 = Class.objects.get(class_user=request.user, class_name='Schoology Integration', time=dt_obj, period=999999, ics_link=link)
        except:
            class1 = Class(class_user = request.user, class_name='Schoology Integration', time=dt_obj, period=999999, ics_link=link)
            class1.save()
            class1.days.add(day)
            class1.save()
        #pull prior integrated events:
        uids = Homework.objects.filter(hw_class=class1, hw_user=request.user)
        uid_list = []
        for uid in uids:
            uid_list.append(uid.ics_uid)
        #pull timezone, default to Pacific if necessary:
        try:
            timezone = Preferences.objects.get(preferences_user=request.user).user_timezone
            if timezone==None:
                return render(request, 'hwapp/error.html', {
                    'error': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
                })
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
            })  

        #append new hw to database and calendar
        #convert ics to Timeline instance
        for event in c.timeline:
            #pull summary(name)
            #pull end date, start date if no end date, or default time(midnight)
            if event.end:
                time=(event.end).to(str(timezone))
                time.format('YYYY-MM-DD')
                time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
            elif event.begin:
                time=(event.begin).to(str(timezone))
                time.format('YYYY-MM-DD')
                time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
            else:
                time=dt_obj
            hw_name = str(event.name)
            try:
                notes = str(event.description)
            except:
                notes=None
            try:
                ics_uid = event.uid
            except:
                ics_uid = None
            #check if uid exists. If so, do not create the event
            if ics_uid in uid_list:
                pass
            else:
                Homework.objects.create(hw_user=request.user, hw_class=class1, due_date=time, hw_title=hw_name, notes=str(notes), completed=False, ics_uid=ics_uid)        
        return render(request, 'hwapp/success.html', {
            'message': "Schoology feed integrated successfully. Please <a href='/'>return home</a>"
        })    
    else:
        return render(request, 'hwapp/schoology_ics.html')

@login_required(login_url='/login')
def canvas_init(request):
    if request.method == 'POST':
        try:
            #make link an https link
            link = request.POST.get('schoology_ics_link')
            link = link.replace('webcal', 'https')
            c = Calendar(requests.get(link).text)
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'Please copy the full link from Canvas with the instructions below and include the "webcal" portion of the link'
            })
        #SETUP: create Canvas Class instance if not already existing(since Canvas does not provide class names with HW assignments)
        dt_str = '00:00'
        dt_obj = datetime.datetime.strptime(dt_str, '%H:%M')
        day = Day.objects.get(days='Sunday')
        try:
            class2 = Class.objects.get(class_user=request.user, class_name='Canvas Integration', time=dt_obj, period=999999, ics_link=link)
        except:
            class2 = Class(class_user = request.user, class_name='Canvas Integration', time=dt_obj, period=999999, ics_link=link)
            class2.save()
            class2.days.add(day)
            class2.save()
        #pull prior integrated events:
        uids = Homework.objects.filter(hw_class=class2, hw_user=request.user)
        uid_list = []
        for uid in uids:
            uid_list.append(uid.ics_uid)
        #pull timezone, default to Pacific if necessary:
        try:
            timezone = Preferences.objects.get(preferences_user=request.user).user_timezone
            if timezone==None:
                return render(request, 'hwapp/error.html', {
                    'error': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
                })
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
            })  

        #append new hw to database and calendar
        #convert ics to Timeline instance
        for event in c.timeline:
            #pull summary(name)
            #pull end date, start date if no end date, or default time(midnight)
            if event.end:
                time=(event.end).to(str(timezone))
                time.format('YYYY-MM-DD')
                time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
            elif event.begin:
                time=(event.begin).to(str(timezone))
                time.format('YYYY-MM-DD')
                time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
            else:
                time=dt_obj
            hw_name = str(event.name)
            try:
                notes = str(event.description)
            except:
                notes=None
            try:
                ics_uid = event.uid
            except:
                ics_uid = None
            #check if uid exists. If so, do not create the event
            if ics_uid in uid_list:
                pass
            else:
                Homework.objects.create(hw_user=request.user, hw_class=class2, due_date=time, hw_title=hw_name, notes=str(notes), completed=False, ics_uid=ics_uid)
        return render(request, 'hwapp/success.html', {
            'message': "Canvas feed integrated successfully. Please <a href='/'>return home</a>"
        })        
    else:
        return render(request, 'hwapp/canvas_ics.html')
@login_required(login_url='/login')
def other_init(request):
    if request.method == 'POST':
        try:
            #make link an https link
            link = request.POST.get('schoology_ics_link')
            link = link.replace('webcal', 'https')
            c = Calendar(requests.get(link).text)
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'Please copy the full ICS link from the external integration with the instructions below and include the "webcal" portion of the link'
            })
        #SETUP: create new Class instance if not already existing(since Canvas does not provide class names with HW assignments)
        dt_str = '00:00'
        dt_obj = datetime.datetime.strptime(dt_str, '%H:%M')
        day = Day.objects.get(days='Sunday')
        class_name = request.POST.get('integration_name')
        try:
            class2 = Class.objects.get(class_user=request.user, class_name=class_name, time=dt_obj, period=999999, ics_link=link)
        except:
            class2 = Class(class_user = request.user, class_name=class_name, time=dt_obj, period=999999, ics_link=link)
            class2.save()
            class2.days.add(day)
            class2.save()
        #pull prior integrated events:
        uids = Homework.objects.filter(hw_class=class2, hw_user=request.user)
        uid_list = []
        for uid in uids:
            uid_list.append(uid.ics_uid)
        #pull timezone, default to Pacific if necessary:
        try:
            timezone = Preferences.objects.get(preferences_user=request.user).user_timezone
            if timezone==None:
                return render(request, 'hwapp/error.html', {
                    'error': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
                })
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
            })  

        #append new hw to database and calendar
        #convert ics to Timeline instance
        for event in c.timeline:
            #pull summary(name)
            #pull end date, start date if no end date, or default time(midnight)
            if event.end:
                time=(event.end).to(str(timezone))
                time.format('YYYY-MM-DD')
                time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
            elif event.begin:
                time=(event.begin).to(str(timezone))
                time.format('YYYY-MM-DD')
                time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
            else:
                time=dt_obj
            hw_name = str(event.name)
            try:
                notes = str(event.description)
            except:
                notes=None
            try:
                ics_uid = event.uid
            except:
                ics_uid = None
                        #check if uid exists. If so, do not create the event
            if ics_uid in uid_list:
                pass
            else:
                Homework.objects.create(hw_user=request.user, hw_class=class2, due_date=time, hw_title=hw_name, notes=str(notes), completed=False, ics_uid=ics_uid)
        return render(request, 'hwapp/success.html', {
            'message': "Feed integrated successfully. Please <a href='/'>return home</a>"
        })        
    else:
        return render(request, 'hwapp/other.html')

def export(request, user_id, hash_value):
    #check if user is authorized
    if request.method == 'GET':
        #setup hashing functions:
        #sys_val = abs(hash(str(user_id)))
        try:
            sys_val = IcsHashVal.objects.get(hash_user=request.user)

        except:
            return render(request, 'hwapp/error.html', {
                'error': 'User not Found'
            })
        prov_val = abs(hash_value)
        if prov_val == sys_val:
            pass
        else:
            return render(request, 'hwapp/error.html', {
                'error': 'Access Denied'
            })
        allhw =  CalendarEvent.objects.filter(calendar_user=User.objects.get(id=user_id))
        c=Calendar()
        for hw in allhw:
            c.events.add(hw.ics)
        return render(request, 'hwapp/export.html', {
            'ics': c
        })

    else:
        return JsonResponse({'error': 'method not supported'}, status=405)

def refresh_ics():
    classes = Class.objects.exclude(ics_link__isnull=True)
    for class1 in classes:
        link = class1.ics_link
        try:
            #make link an https link
            c = Calendar(requests.get(link).text)
        except:
            pass
        #SETUP: create new Class instance if not already existing(since Canvas does not provide class names with HW assignments)
        dt_str = '00:00'
        dt_obj = datetime.datetime.strptime(dt_str, '%H:%M')
        #pull prior integrated events:
        uids = Homework.objects.filter(hw_class=class1)
        uid_list = []
        for uid in uids:
            uid_list.append(uid.ics_uid)
        timezone = Preferences.objects.get(preferences_user = class1.class_user).user_timezone
        #append new hw to database and calendar
        #convert ics to Timeline instance
        for event in c.timeline:
            #pull summary(name)
            #pull end date, start date if no end date, or default time(midnight)
            if event.end:
                time=(event.end).to(str(timezone))
                time.format('YYYY-MM-DD')
                time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
            elif event.begin:
                time=(event.begin).to(str(timezone))
                time.format('YYYY-MM-DD')
                time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
            else:
                time=dt_obj
            hw_name = str(event.name)
            try:
                notes = str(event.description)
            except:
                notes=None
            try:
                ics_uid = event.uid
            except:
                ics_uid = None
                        #check if uid exists. If so, do not create the event
            if ics_uid in uid_list:
                pass
            else:
                Homework.objects.create(hw_user=class1.class_user, hw_class=class1, due_date=time, hw_title=hw_name, notes=str(notes), completed=False, ics_uid=ics_uid)
