from io import StringIO
from django.contrib.auth import login
from django.http.request import RAISE_ERROR
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.forms import ModelForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from django.views.decorators.csrf import csrf_exempt
import re
from .models import CalendarEvent, IcsHashVal
from dotenv import load_dotenv
import datetime
import json
import requests
from ics import Calendar, Event
from pathlib import Path



#import hwapp models
import sys
sys.path.append("..")
from hwapp.models import Homework, Class, Day, IcsId, Preferences, User
def matthew_check(user):
    return user.id == 1

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
        try:
            class1 = Class.objects.get(class_user=request.user, class_name='Schoology Integration', time=dt_obj, period=999999, ics_link=link)
        except:
            class1 = Class(class_user = request.user, class_name='Schoology Integration', time=dt_obj, period=999999, ics_link=link)
            class1.save()
        #pull prior integrated events:
        uids = IcsId.objects.filter(icsID_user=request.user)
        uid_list = []
        for uid in uids:
            uid_list.append(uid.icsID)
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
                Homework.objects.create(hw_user=request.user, hw_class=class1, due_date=time, hw_title=hw_name, notes=str(notes), completed=False)        
                IcsId.objects.create(icsID_user=request.user, icsID = ics_uid)
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
        try:
            class2 = Class.objects.get(class_user=request.user, class_name='Canvas Integration', time=dt_obj, period=999999, ics_link=link)
        except:
            class2 = Class(class_user = request.user, class_name='Canvas Integration', time=dt_obj, period=999999, ics_link=link)
            class2.save()
        #pull prior integrated events:
        uids = IcsId.objects.filter(icsID_user=request.user)
        uid_list = []
        for uid in uids:
            uid_list.append(uid.icsID)
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
                Homework.objects.create(hw_user=request.user, hw_class=class2, due_date=time, hw_title=hw_name, notes=str(notes), completed=False)
                IcsId.objects.create(icsID_user=request.user, icsID = ics_uid)

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
        class_name = request.POST.get('integration_name')
        try:
            class2 = Class.objects.get(class_user=request.user, class_name=class_name, time=dt_obj, period=999999, ics_link=link)
        except:
            class2 = Class(class_user = request.user, class_name=class_name, time=dt_obj, period=999999, ics_link=link)
            class2.save()
        #pull prior integrated events:
        uids = IcsId.objects.filter(icsID_user=request.user)
        uid_list = []
        for uid in uids:
            uid_list.append(uid.icsID)
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
                Homework.objects.create(hw_user=request.user, hw_class=class2, due_date=time, hw_title=hw_name, notes=str(notes), completed=False)
                IcsId.objects.create(icsID_user=request.user, icsID = ics_uid)
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
            sys_val = IcsHashVal.objects.get(hash_user=User.objects.get(id=user_id))
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'User not Found'
            })
        prov_val = abs(hash_value)
        if prov_val == int(sys_val.hash_val):
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
        uids = IcsId.objects.filter(icsID_user=class1.class_user)
        uid_list = []
        for uid in uids:
            uid_list.append(uid.icsID)
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
                IcsId.objects.create(icsID_user=class1.class_user, icsID = ics_uid)
                Homework.objects.create(hw_user=class1.class_user, hw_class=class1, due_date=time, hw_title=hw_name, notes=str(notes), completed=False)
intake_verification = ''
@csrf_exempt
def vmsapi(request):
    global intake_verification
    if request.method == 'POST':
        reg = re.compile('[+]account%3A[+]*')
        res = reg.search(str(request.body))
        span_val = int(res.span()[1])
        code = str(request.body)[span_val:span_val+4]
        intake_verification = code
        return JsonResponse({'message': 'success'}, status=200)

    else:
        if request.headers['Matthewstoken'] != None:
            if request.headers['Matthewstoken'] == 'ZVX)9Zje2v"DEq3f':
                return HttpResponse(intake_verification)
            else:
                return JsonResponse({
                    'error':'access denied'
                }, status=403)
        else:
            return JsonResponse({
                'error':'access denied'
            }, status=403)
intake_verification = ''
@csrf_exempt
def vmsapi(request):
    global intake_verification
    if request.method == 'POST':
        reg = re.compile('[+]account%3A[+]*')
        res = reg.search(str(request.body))
        span_val = int(res.span()[1])
        code = str(request.body)[span_val:span_val+4]
        p = Path(__file__).with_name('tmp.json')
        with p.open('r') as f:
            intakejson = json.loads(f.read())
        intakejson['code'] = code
        print(intakejson)
        intake_verification = code
        return JsonResponse({'message': 'success'}, status=200)

    else:
        if request.headers['Matthewstoken'] != None:
            p = Path(__file__).with_name('tmp.json')
            with p.open('r') as f:
                intakejson = json.loads(f.read())
            if request.headers['Matthewstoken'] == 'ZVX)9Zje2v"DEq3f':
                return HttpResponse(intakejson['code'])
            else:
                return JsonResponse({
                    'error':'access denied'
                }, status=403)
        else:
            return JsonResponse({
                'error':'access denied'
            }, status=403)
@user_passes_test(matthew_check, login_url='/login')
def intake_api_console(request):
    return render(request, 'hwapp/intakecode.html', {
        'code': intake_verification
        })
