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
from .models import CalendarEvent, GoogleData, IcsHashVal, NotionData, GoogleCalendar, SchoologyClasses, SchoologyAuth
from dotenv import load_dotenv
import datetime
import json
import pytz
import requests
from ics import Calendar, Event
from dateutil import tz
from pathlib import Path
import base64
from .helper import full_notion_refresh, notion_push, canvas_notion_push
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.oauth2.credentials
import sentry_sdk
import secrets
from time import time

import google_auth_oauthlib.flow


notion_bearer_token = 'NTkyMDM3YmYtNjE2Ni00YTliLWJmNjctNjlkODc5NTA3NjNkOnNlY3JldF9IWXA0RFdCemNLckUxTGNlMkRIdjhpTG5LczJyZkVsMTBOcXg3SWV6eGc1'

#import hwapp models
import sys
sys.path.append("..")
from hwapp.models import Homework, Class, Day, IcsId, Preferences, User
from mywebsite.settings import DEBUG
def matthew_check(user):
    return user.id == 1
def google_check(user):
    return user.groups.filter(name='Authorized Google Users') or user.is_superuser
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
        dt_str = '23:59'
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
                l = Homework.objects.create(hw_user=request.user, hw_class=class1, due_date=time, hw_title=hw_name, notes=str(notes), completed=False)  
                notion_push(hw=l, user=request.user)      
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
        dt_str = '23:59'
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
                l = Homework.objects.create(hw_user=request.user, hw_class=class2, due_date=time, hw_title=hw_name, notes=str(notes), completed=False)
                notion_push(hw=l, user=request.user)  
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
        dt_str = '23:59'
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
                l = Homework.objects.create(hw_user=request.user, hw_class=class2, due_date=time, hw_title=hw_name, notes=str(notes), completed=False)
                notion_push(hw=l, user=request.user)  
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
            sys_val = IcsHashVal.objects.get(hash_user=request.user, hash_type='default')
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
        allhw =  CalendarEvent.objects.filter(calendar_user=request.user)
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
        dt_str = '23:59'
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
                time = datetime.datetime.strptime(str(time)[0:10] + ' 11:59', '%Y-%m-%d %H:%M')
            elif event.begin:
                time=(event.begin).to(str(timezone))
                time.format('YYYY-MM-DD')
                time = datetime.datetime.strptime(str(time)[0:10] + ' 11:59', '%Y-%m-%d %H:%M')
            else:
                time=dt_obj
            time = time
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
                l = Homework.objects.create(hw_user=class1.class_user, hw_class=class1, due_date=time, hw_title=hw_name, notes=str(notes), completed=False)
                notion_push(hw=l, user=class1.class_user)  

@login_required(login_url='/login')
def notion_auth(request):
    try:
        n = NotionData.objects.get(notion_user=request.user)
    except:
        n = False
    return render(request, 'hwapp/notion_import.html', {
            'DEBUG': DEBUG,
            'int_status': n
    })

@login_required(login_url='/login')
def notion_callback(request):
    if request.method == "GET":
        if request.GET.get('code'):
            code = request.GET.get('code')
        elif request.GET.get('error'):
            return render(request, 'hwapp/error.html', {
                'error': request.GET.get('error')
            })
        else:
            return JsonResponse({"status": "400", "error": "no callback code"}, status=400)
        url = 'https://api.notion.com/v1/oauth/token'
        uri = {
            "dev": "http://localhost:8000/integrations/notion_callback",
            "prod": "https://matthewtsai.me/integrations/notion_callback",
        }
        redirect_uri = uri['dev' if DEBUG else 'prod']
        print(redirect_uri)

        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
        b64 = notion_bearer_token
        response = requests.post(url, data=body, headers={"Authorization": f"Basic {b64}"})
        data1 = json.loads(response.text)
        print(data1)
        try:
            n_data = NotionData.objects.get(notion_user=request.user)
            n_data.notion_user = request.user
            n_data.access_token = data1['access_token']
            n_data.bot_id = data1['bot_id']
            n_data.workspace_name = data1['workspace_name']
            n_data.workspace_id = data1['workspace_id']
            n_data.save()
        except:
            n_data = NotionData.objects.create(notion_user = request.user, access_token = data1['access_token'], bot_id = data1['bot_id'],workspace_name = data1['workspace_name'], workspace_id = data1['workspace_id'])

        #get DB id 
        try:
            url = 'https://api.notion.com/v1/databases'
            response = requests.get(url, headers={"Authorization": f"Bearer {n_data.access_token}", "Notion-Version": "2021-08-16"})
            n_data.db_id = json.loads(response.text)['results'][0]['id']
            n_data.save()
        except:
            return render(request, 'hwapp/error.html', {
                'error': "Too many pages selected. Please return to the <a href=/integrations/notion_auth>previous page</a> and select only <b>ONE</b> page"
            })

        #get DB properties:
        url = f'https://api.notion.com/v1/databases/{n_data.db_id}'
        token = n_data.access_token
        page_id = n_data.db_id
        url = 'https://api.notion.com/v1/pages'
        to_post = Homework.objects.filter(hw_user=request.user, completed=False, notion_migrated=False)
        for hw in to_post:
            body = {
                "parent": {
                    "database_id": f"{page_id}"
                },
                "properties": {
                    "Name": {
                        "title": [{"type":"text","text":{"content":f"{hw.hw_title}","link":None},"plain_text":f"{hw.hw_title}","href":None}]
                        
                    },
                    "Status": {
                        "status": {
                            "name":"Not started"
                        }
                    },
                    "Class": {
                        "type": f"select",
                        "select": {
                            "name": f"{hw.hw_class.class_name}"
                        }
                    },
                    "Due": {
                        "type": "date",
                        "date": {
                            "start": f"{hw.due_date}",
                            "end": None,
                            "time_zone": "US/Pacific"
                        }
                    }
                    
                }
            }
            response = requests.post(url, data=json.dumps(body), headers={'Authorization': f'Bearer {token}', 'Notion-Version': '2022-02-22', "Content-Type": "application/json"})
            hw.notion_migrated = True
            hw.notion_id = json.loads(response.text)['id']
            hw.save()
            print(hw)
        return render(request, 'hwapp/success.html', {
            'message': 'Notion feed integrated successfully'
        })
    else:
        return JsonResponse({"error": "invalid request"}, status=400)
 
@user_passes_test(matthew_check)
def admin_notion(request):
    m = full_notion_refresh(request.user)
    return render(request, 'hwapp/success.html', {
        'message': f'migration completed successfully. Added: <br> {m}'
    })
@login_required(login_url='/login')
@user_passes_test(google_check)
def google_info(request): 
    try:
        g_data = GoogleData.objects.get(google_user=request.user)
    except:
        g_data = False
    return render(request, 'hwapp/google_auth.html', {
        'int_status': g_data
    })
@login_required(login_url='/login')
@user_passes_test(google_check)
def google_view(request):
    if DEBUG:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/calendar.readonly', 'openid', 'email'])
        flow.redirect_uri = 'http://localhost:8000/integrations/google_callback'

    else:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        '/home/TestVM/mywebsite-dev/client_secret.json',
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/calendar.readonly', 'openid', 'email'])
        flow.redirect_uri = 'https://matthewtsai.me/integrations/google_callback'
    authorization_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true')
    return HttpResponseRedirect(authorization_url)
@login_required(login_url='/login')
@user_passes_test(google_check)
def google_callback(request):
    if request.method == 'GET':
        if request.user.groups.filter(name='Authorized Google Users'):
            print(True)
        else:
            pass
        code = request.GET.get('code')
        scopes = request.GET.get('scope')
        if 'https://www.googleapis.com/auth/calendar.readonly' not in str(scopes):
            return render(request, 'hwapp/error.html', {
                'error': 'Please grant this app access to your Calendar'
            })
        try:
            g_obj = GoogleData.objects.get(google_user=request.user)
            g_obj.code = code
            g_obj.save()
        except:
            g_obj = GoogleData.objects.create(google_user=request.user, code=code)
            g_obj.save()
        url = 'https://oauth2.googleapis.com/token?prompt=consent&access_type=offline'
        if DEBUG:
            url1 = 'http://localhost:8000/integrations/google_callback' 
        else:
            url1 = 'https://matthewtsai.me/integrations/google_callback' 
        data = {
            'code': code,
            'client_id': '117121647082-9rt8p5sdt9smad8ln6onl7tk828ks2b8.apps.googleusercontent.com',
            'client_secret': os.environ.get('google_client_secret'),
            'grant_type': 'authorization_code',
            'redirect_uri': url1

        }
        response = requests.post(url, params=data, data=data)
        i = json.loads(response.text)
        g_obj.refresh_token = i['refresh_token']
        g_obj.access_token = i['access_token']
        g_obj.id_token = i['id_token']
        g_obj.save()
        url = 'https://www.googleapis.com/calendar/v3/users/me/calendarList/'
        response = requests.get(url, headers={'Authorization': f"Bearer {g_obj.access_token}"})
        i = json.loads(response.text)
        g_obj.sync_token = i['nextSyncToken']
        return render(request, 'hwapp/gcal_list.html', {
            'calendars': i['items']
        })
    elif request.method =='POST':
        json1 = json.loads(request.body)
        i = json1['calIDs']
        j = json1['calname']
        for num in range(len(i)):
            try:
                cal = GoogleCalendar.objects.get(google_user=request.user, calendar_id=i[num])
                cal.save()
            except:
                cal = GoogleCalendar.objects.create(google_user=request.user, calendar_id=i[num], calendar_name=j[num])
                cal.save()
        all_objs = GoogleCalendar.objects.filter(google_user=request.user)
        dt_str = '23:59'
        dt_obj = datetime.datetime.strptime(dt_str, '%H:%M')
        for obj in all_objs:
            try:
                sync1 = obj.sync_token
            except:
                sync1 = None
            r_now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:00")
            if sync1:
                response = requests.get(f"https://www.googleapis.com/calendar/v3/calendars/{obj.calendar_id}/events?&sync_token={sync1}", headers={"Authorization": f"Bearer {GoogleData.objects.get(google_user=request.user).access_token}"})
                if '410' in str(response):
                    response = requests.get(f"https://www.googleapis.com/calendar/v3/calendars/{obj.calendar_id}/events?timeMin={r_now}Z", headers={"Authorization": f"Bearer {GoogleData.objects.get(google_user=request.user).access_token}"})
            else:
                response = requests.get(f"https://www.googleapis.com/calendar/v3/calendars/{obj.calendar_id}/events?timeMin={r_now}Z", headers={"Authorization": f"Bearer {GoogleData.objects.get(google_user=request.user).access_token}"})
            
            i = json.loads(response.text)
            #create new class
            try:
                c = Class.objects.get(class_user=request.user, class_name=obj.calendar_name, period=None, time=dt_obj)
            except:
                c = Class.objects.create(class_user=request.user, class_name=obj.calendar_name, period=None, time=dt_obj)
            c.save()
            obj.sync_token = i['nextSyncToken']
            try:
                for l in i['items']:
                    to_zone = tz.gettz('UTC')
                    d = datetime.datetime.strptime(l['start']['dateTime'], "%Y-%m-%dT%H:%M:%SZ").astimezone(to_zone)
                    try:
                        h = Homework.objects.get(hw_user=request.user, ics_id=l['iCalUID'])
                    except:
                        h = Homework.objects.create(hw_user=request.user, hw_class=c, hw_title = l['summary'], due_date=d, completed=False, ics_id=l['iCalUID'])
                    h.save()
                    try:
                        notion_push(hw=h, user=request.user)
                    except:
                        pass
            except:
                pass
        return JsonResponse({"message": "Homework Imported Successfully", "status": '201'}, status=201)

def notion_toics(request, user_id, hash_value):
    try:
        user = User.objects.get(id=user_id)
        IcsHashVal.objects.get(hash_user=user, hash_val=hash_value)
    except:
        return JsonResponse({"Error": "Not Authorized"}, status=403)
    notion_obj = NotionData.objects.get(notion_user=user)
    url = f'https://api.notion.com/v1/databases/{notion_obj.db_id}/query'
    response = requests.post(url, headers={'Authorization': f'Bearer {notion_obj.access_token}', 'Notion-Version': '2022-02-22', "Content-Type": "application/json"})
    if '200' not in str(response):
        return HttpResponseRedirect(reverse('notion_auth'))
    i = json.loads(response.text)
    sentry_sdk.set_context("character", {
    "response": response,
    "response_text": response.text,
    })
    c = Calendar()
    for event in i['results']:
        e = Event()
        try:
            e.name = event['properties']['Name']['title'][0]['plain_text']
            e.begin = event['properties']['Due']['date']['start']
            e.description = f"Class: {event['properties']['Class']['select']['name']}; Status: {event['properties']['Status']['status']['name']}"
            c.events.add(e)
        except:
            pass
    return render(request, 'hwapp/export.html', {
        'ics': c
    })
@login_required(login_url='/login')
def schoology_class(request):
    try:
        s = SchoologyAuth.objects.get(h_user= request.user, src='Schoology')
    except:
        print(False)
        return render(request, 'hwapp/error.html', {
            'error': 'No Schoology Classes found. Please contact website admin for access'
        })
    url = f'https://api.schoology.com/v1/users/{s.user_id}/sections'
    headers = {
        "Authorization": f'OAuth realm="Schoology API",oauth_consumer_key="{s.s_consumer_key}",oauth_token="",oauth_nonce="{secrets.token_urlsafe()}",oauth_timestamp="{int(time())}",oauth_signature_method="PLAINTEXT",oauth_version="1.0",oauth_signature="{s.s_secret_key}%26"'
    }
    response = requests.get(url, headers=headers)
    response = json.loads(response.text)
    s_class = SchoologyClasses.objects.filter(schoology_user=request.user, src='Schoology')
    classes = []
    for i in s_class:
        classes.append(i.class_id)
    for i in response['section']:
        if i['id'] in classes:
            pass
        else:
            c = Class.objects.create(class_user=request.user, class_name=i['course_title'], external_src="Schoology", external_id=i['id'])
            SchoologyClasses.objects.create(schoology_user=request.user, class_id=i['id'], s_class_name=i['course_title'],s_grading_period=i['grading_periods'][0], linked_class=c, src='Schoology', auth_data=s)
@login_required(login_url='/login')
def schoology_hw(request):
    try:
        c = SchoologyClasses.objects.filter(schoology_user=request.user, src='Schoology').exclude(update=False)
    except:
        return render(request, 'hwapp/error.html', {
            'error': 'No Schoology Classes found. Please contact website admin for access'
        })
    existing_hws = Homework.objects.filter(hw_user=request.user, external_src="Schoology")
    z = []
    for existing_hw in existing_hws:
        z.append(str(existing_hw.external_id))
    for class1 in c:
        s = class1.auth_data
        url = f"https://api.schoology.com/v1/sections/{class1.class_id}/assignments?start=0&limit=1000"
        headers = {
            "Authorization": f'OAuth realm="Schoology API",oauth_consumer_key="{s.s_consumer_key}",oauth_token="",oauth_nonce="{secrets.token_urlsafe()}",oauth_timestamp="{int(time())}",oauth_signature_method="PLAINTEXT",oauth_version="1.0",oauth_signature="{s.s_secret_key}%26"'
        }   
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        for hw in data['assignment']:
            if str(hw['id']) not in z:
                try:
                    l = datetime.datetime.strptime(hw['due'], "%Y-%m-%d %H:%M:%S")
                except:
                    l = datetime.datetime.now()
                h = Homework.objects.create(hw_user=request.user,hw_class=class1.linked_class,hw_title=hw['title'], external_id=hw['id'], external_src="Schoology", due_date=l,notes=f"{hw['description']}, {hw['web_url']}",completed=False, overdue=False)
                notion_push(hw=h,user=request.user)
            pass
@login_required(login_url='/login')
def canvas_class(request):
    try:
        all = SchoologyAuth.objects.filter(h_user= request.user, src='Canvas')
    except:
        return render(request, 'hwapp/error.html', {
            'error': 'No Canvas Classes found. Please contact website admin for access'
        })

    for s in all:
        url = f'https://canvas.instructure.com/api/v1/courses?access_token={s.s_secret_key}'
        headers = {
            "Authorization": f'Bearer {s.s_secret_key}'
        }
        response = requests.get(url, headers=headers)
        #print(response.text)
        response = json.loads(response.text)
        s_class = SchoologyClasses.objects.filter(schoology_user=request.user, src='Canvas')
        classes = []
        for i in s_class:
            classes.append(str(i.class_id))
        for i in response:
            try:
                assert i['access_restricted_by_date'] == True
            except KeyError:
                if str(i['id']) not in classes:
                    print(i['id'])
                    print(False)
                    c = Class.objects.create(class_user=request.user, class_name=i['name'], external_src="Canvas", external_id=i['id'])
                    SchoologyClasses.objects.create(schoology_user=request.user, class_id=i['id'], s_class_name=i['name'],s_grading_period=i['enrollment_term_id'], linked_class=c, src='Canvas', auth_data=s)
@login_required(login_url='/login')
def canvas_hw(request):
    try:
        c = SchoologyClasses.objects.filter(schoology_user=request.user, src='Canvas').exclude(update=False)
    except:
        return render(request, 'hwapp/error.html', {
            'error': 'No Canvas Classes found. Please contact website admin for access'
        })
    existing_hws = Homework.objects.filter(hw_user=request.user, external_src="Canvas")
    z = []

    for existing_hw in existing_hws:
        z.append(str(existing_hw.external_id))
    for class1 in c:
        url = f"https://canvas.instructure.com/api/v1/courses/{class1.class_id}/assignments?access_token={class1.auth_data.s_secret_key}"
        headers = {
            "Authorization": f'Bearer {class1.auth_data.s_secret_key}'
        }   
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        t = Preferences.objects.get(preferences_user=request.user)
        for hw in data:
            if str(hw['id']) not in z:
                try:
                    l = datetime.datetime.strptime(hw['due_at'], "%Y-%m-%dT%H:%M:%S%z")
                except:
                    l = datetime.datetime.now()
                try:
                    l = l.astimezone(pytz.timezone(f'{t.user_timezone}')).replace(tzinfo=None)
                except:
                    return render(request, 'hwapp/error.html', {
                        "error": "Please set timezone <a href='/preferences'>here</a>"
                    })
                h = Homework.objects.create(hw_user=request.user,hw_class=class1.linked_class,hw_title=hw['name'], external_id=hw['id'], external_src="Canvas", due_date=l,notes=f"{hw['description']}",completed=False, overdue=False)
                notion_push(hw=h,user=request.user)
            pass
@user_passes_test(matthew_check, login_url='/login')
def authentication_manager(request, user_id):
    if request.method == 'POST':
        pass
    else:
        c = SchoologyAuth.objects.filter(h_user=user_id)
        user = User.objects.get(id=user_id)
        return render(request, 'hwapp/authentication.html', {
            "users": c,
            "user": user
        })
@login_required(login_url='/login')
def canvas_api(request):
    if request.method == 'POST':
        pass
    else:
        return render(request, 'hwapp/add_edit_api.html', {
            'service': 'Canvas',
            'location': 'Profile -> Settings -> Add New Access Token'
        })
@login_required(login_url='/login')
def schoology_api(request):
    if request.method == 'POST':
        pass
    else:
        return render(request, 'hwapp/add_edit_api.html', {
            'service': 'Schoology',
            'location': '{Schoology URL}/api'
        })