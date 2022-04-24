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
from .models import CalendarEvent, GoogleData, IcsHashVal, NotionData, GoogleCalendar
from dotenv import load_dotenv
import datetime
import json
import requests
from ics import Calendar, Event
from dateutil import tz
from pathlib import Path
import base64
from .helper import full_notion_refresh, notion_push
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import google.oauth2.credentials
import google_auth_oauthlib.flow
from notion.client import NotionClient
from notion.collection import CalendarView
from notion.block import BasicBlock
from notion.user import User as notion_user

notion_bearer_token = 'NTkyMDM3YmYtNjE2Ni00YTliLWJmNjctNjlkODc5NTA3NjNkOnNlY3JldF9IWXA0RFdCemNLckUxTGNlMkRIdjhpTG5LczJyZkVsMTBOcXg3SWV6eGc1'

#import hwapp models
import sys
sys.path.append("..")
from hwapp.models import Homework, Class, Day, IcsId, Preferences, User
from mywebsite.settings import DEBUG
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
                        "select": {
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
def google_info(request): 
    return render(request, 'hwapp/google_auth.html')
@login_required(login_url='/login')
def google_view(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/calendar.readonly', 'openid', 'email'])
    if DEBUG:
        flow.redirect_uri = 'http://localhost:8000/integrations/google_callback'
    else:
        flow.redirect_uri = 'https://matthewtsai.me/integrations/google_callback'
    authorization_url, state = flow.authorization_url(
    access_type='offline',
    include_granted_scopes='true')
    return HttpResponseRedirect(authorization_url)
@login_required(login_url='/login')
def google_callback(request):
    if request.method == 'GET':
        code = request.GET.get('code')
        scopes = request.GET.get('scope')
        if 'https://www.googleapis.com/auth/calendar.readonly' not in str(scopes):
            return render(request, 'hwapp/error.html', {
                'error': 'Please grant this app access to your Calendar'
            })
        print(scopes)
        try:
            g_obj = GoogleData.objects.get(google_user=request.user)
            g_obj.code = code
            g_obj.save()
        except:
            g_obj = GoogleData.objects.create(google_user=request.user, code=code)
            g_obj.save()
        url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': '117121647082-9rt8p5sdt9smad8ln6onl7tk828ks2b8.apps.googleusercontent.com',
            'client_secret': os.environ.get('google_client_secret'),
            'grant_type': 'authorization_code',
            'redirect_uri': 'http://localhost:8000/integrations/google_callback' 

        }
        response = requests.post(url, params=data, data=data)

        i = json.loads(response.text)
        g_obj.refresh_token = i['refresh_token']
        g_obj.access_token = i['access_token']
        g_obj.id_token = i['id_token']
        g_obj.save()
        print(response, response.text)
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
        dt_str = '00:00'
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
        IcsHashVal.objects.get(hash_user=User.objects.get(id=user_id), hash_val=hash_value)
    except:
        return JsonResponse({"Error": "Not Authorized"}, status=403)
    notion_obj = NotionData.objects.get(notion_user=request.user)
    url = f'https://api.notion.com/v1/databases/{notion_obj.db_id}/query'
    response = requests.post(url, headers={'Authorization': f'Bearer {notion_obj.access_token}', 'Notion-Version': '2022-02-22', "Content-Type": "application/json"})
    if '200' not in str(response):
        return HttpResponseRedirect(reverse('notion_auth'))
    i = json.loads(response.text)
    print(response)
    c = Calendar()
    for event in i['results']:
        e = Event()
        try:
            e.name = event['properties']['Name']['title'][0]['plain_text']
            e.begin = event['properties']['Due']['date']['start']
            e.description = f"Class: {event['properties']['Class']['select']['name']}; Status: {event['properties']['Status']['select']['name']}"
            c.events.add(e)
        except:
            pass
    return render(request, 'hwapp/export.html', {
        'ics': c
    })
