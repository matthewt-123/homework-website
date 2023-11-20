from django.http.request import RAISE_ERROR
from django.shortcuts import render
from django.http import HttpResponse
import dateparser
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from .models import CalendarEvent, IcsHashVal, NotionData, SchoologyClasses, SchoologyAuth, IntegrationLog, Log
from dotenv import load_dotenv
import datetime
import json
import pytz
import requests
from ics import Calendar, Event
from .helper import full_notion_refresh, notion_push, canvas_notion_push
import sentry_sdk
import secrets
from time import time
import csv
from .helper import notion_expired

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
    try:
        integrations = SchoologyAuth.objects.filter(h_user = request.user)
    except:
        integrations = False
    try:
        n_data = NotionData.objects.filter(notion_user=request.user)
    except:
        n_data = False
    return render(request, 'hwapp/integrations.html', {
        'integrations': integrations,
        'n_datas': n_data
    })

# @login_required(login_url='/login')
# def other_init(request):
#     if request.method == 'POST':
#         try:
#             #make link an https link
#             link = request.POST.get('schoology_ics_link')
#             link = link.replace('webcal', 'https')
#             c = Calendar(requests.get(link).text)
#         except:
#             return render(request, 'hwapp/error.html', {
#                 'error': 'Please copy the full ICS link from the external integration with the instructions below and include the "webcal" portion of the link'
#             })
#         #SETUP: create new Class instance if not already existing(since Canvas does not provide class names with HW assignments)
#         dt_str = '23:59'
#         dt_obj = datetime.datetime.strptime(dt_str, '%H:%M')
#         class_name = request.POST.get('integration_name')
#         try:
#             class2 = Class.objects.get(class_user=request.user, class_name=class_name, time=dt_obj, period=999999, ics_link=link)
#         except:
#             class2 = Class(class_user = request.user, class_name=class_name, time=dt_obj, period=999999, ics_link=link)
#             class2.save()
#         #pull prior integrated events:
#         uids = IcsId.objects.filter(icsID_user=request.user)
#         uid_list = []
#         for uid in uids:
#             uid_list.append(uid.icsID)
#         #pull timezone, default to Pacific if necessary:
#         try:
#             timezone = Preferences.objects.get(preferences_user=request.user).user_timezone
#             if timezone==None:
#                 return render(request, 'hwapp/error.html', {
#                     'error': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
#                 })
#         except:
#             return render(request, 'hwapp/error.html', {
#                 'error': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
#             })  

#         #append new hw to database and calendar
#         #convert ics to Timeline instance
#         for event in c.timeline:
#             #pull summary(name)
#             #pull end date, start date if no end date, or default time(midnight)
#             if event.end:
#                 time=(event.end).to(str(timezone))
#                 time.format('YYYY-MM-DD')
#                 time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
#             elif event.begin:
#                 time=(event.begin).to(str(timezone))
#                 time.format('YYYY-MM-DD')
#                 time = datetime.datetime.strptime(str(time)[0:10], '%Y-%m-%d')
#             else:
#                 time=dt_obj
#             hw_name = str(event.name)
#             try:
#                 notes = str(event.description)
#             except:
#                 notes=None
#             try:
#                 ics_uid = event.uid
#             except:
#                 ics_uid = None
#                         #check if uid exists. If so, do not create the event
#             if ics_uid in uid_list:
#                 pass
#             else:
#                 l = Homework.objects.create(hw_user=request.user, hw_class=class2, due_date=time, hw_title=hw_name, notes=str(notes), completed=False)
#                 notion_push(hw=l, user=request.user)  
#                 IcsId.objects.create(icsID_user=request.user, icsID = ics_uid)
#         return render(request, 'hwapp/success.html', {
#             'message': "Feed integrated successfully. Please <a href='/'>return home</a>"
#         })        
#     else:
#         return render(request, 'hwapp/other.html')

def export(request, user_id, hash_value):
    #check if user is authorized
    if request.method == 'GET':
        #setup hashing functions:
        #sys_val = abs(hash(str(user_id)))
        try:
            sys_val = IcsHashVal.objects.get(hash_user=request.user, hash_type='default')
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'User not found'
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
        response = HttpResponse(c, content_type="text/calendar")
        return response

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
        n = NotionData.objects.get(notion_user=request.user, tag="homework")
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
            "prod": f"https://{os.environ.get('website_root')}/integrations/notion_callback",
        }
        redirect_uri = uri['dev' if DEBUG else 'prod']

        body = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri
        }
        b64 = notion_bearer_token
        response = requests.post(url, data=body, headers={"Authorization": f"Basic {b64}"})
        data1 = json.loads(response.text)
        if str(response) != "<Response [200]>":
            notion_expired(request.user, n_data)
        try:
            n_data = NotionData.objects.get(notion_user=request.user, tag="homework")
            n_data.notion_user = request.user
            n_data.access_token = data1['access_token']
            n_data.bot_id = data1['bot_id']
            n_data.workspace_name = data1['workspace_name']
            n_data.workspace_id = data1['workspace_id']
            n_data.tag = "homework"
            n_data.error = False
            n_data.save()
        except:
            n_data = NotionData.objects.create(notion_user = request.user, access_token = data1['access_token'], bot_id = data1['bot_id'],workspace_name = data1['workspace_name'], workspace_id = data1['workspace_id'], error=False)
        #update notion personal if it exists:
        try:
            n_personal = NotionData.objects.get(notion_user=request.user, tag="personal")
            n_personal.access_token = data1['access_token']
            n_data.bot_id = data1['bot_id']
            n_personal.save()
        except:
            pass

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
            hw.due_date = datetime.datetime.strftime(hw.due_date, '%Y-%m-%dT%H:%M')
            body = {
                "parent": {
                    "database_id": f"{page_id}"
                },
                "properties": {
                    "Name": {
                        "title": [{
                                "text": {
                                    "content":f"{hw.hw_title}"
                                }}]
                        
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
            response = requests.post(url, data=json.dumps(body), headers={'Authorization': f'Bearer {token}', 'Notion-Version': '2022-06-28', "Content-Type": "application/json"})
            hw.notion_migrated = True
            hw.notion_id = json.loads(response.text)['id']
            hw.save()
        return render(request, 'hwapp/success.html', {
            'message': 'Notion feed integrated successfully'
        })
    else:
        return JsonResponse({"error": "invalid request"}, status=400)
 
def notion_toics(request, user_id, hash_value, tag):
    try:
        user = User.objects.get(id=user_id)
        IcsHashVal.objects.get(hash_user=user, hash_val=hash_value)
    except:
        return JsonResponse({"Error": "Not Authorized"}, status=403)
    c = Calendar()
    if tag == "personal":
        notion_obj = NotionData.objects.get(notion_user=user, tag="personal")
        url = f'https://api.notion.com/v1/databases/{notion_obj.db_id}/query'
        response = requests.post(url, headers={'Authorization': f'Bearer {notion_obj.access_token}', 'Notion-Version': '2022-02-22', "Content-Type": "application/json"})
        if '200' not in str(response):
            IntegrationLog.objects.create(user=user, src="notion", dest="hwapp", url = url, date = datetime.datetime.now(), message=response.text, error=True, hw_name="None (ICS Export: Personal)")
            notion_obj.error = True
            notion_obj.save()
            return HttpResponseRedirect(reverse('notion_auth'))
        i = json.loads(response.text)
        for event in i['results']:
            e = Event()
            try:
                e.name = event['properties']['Name']['title'][0]['plain_text']
                e.begin = dateparser.parse(event['properties']['Date']['date']['start']) - datetime.timedelta(hours=7) + datetime.timedelta(days=1)
                print(event['properties']['Date'])
                if event['properties']['Date']['date']['end']:
                    e.end = dateparser.parse(event['properties']['Date']['date']['start']) - datetime.timedelta(hours=7) + datetime.timedelta(days=1)
                e.created = datetime.datetime.now()
                c.events.add(e)
            except:
                pass
    else:
        notion_obj = NotionData.objects.get(notion_user=user, tag="homework")
        url = f'https://api.notion.com/v1/databases/{notion_obj.db_id}/query'
        response = requests.post(url, headers={'Authorization': f'Bearer {notion_obj.access_token}', 'Notion-Version': '2022-02-22', "Content-Type": "application/json"})
        if '200' not in str(response):
            IntegrationLog.objects.create(user=request.user, src="notion", dest="hwapp", url = url, date = datetime.datetime.now(), message=response.text, error=True, hw_name="None (ICS Export: HW)")
            return HttpResponseRedirect(reverse('notion_auth'))
        i = json.loads(response.text)
        for event in i['results']:
            e = Event()
            try:
                e.name = event['properties']['Name']['title'][0]['plain_text']
                e.begin = dateparser.parse(event['properties']['Due']['date']['start']).astimezone(pytz.utc)
                e.created = datetime.datetime.now()
                e.description = f"Class: {event['properties']['Class']['select']['name']}; Status: {event['properties']['Status']['status']['name']}"
                c.events.add(e)
            except Exception as e:
                IntegrationLog.objects.create(user=request.user, src="notion", dest="hwapp- ICS", url = url, date = datetime.datetime.now(), message=e, error=True, hw_name="None (ICS Export: HW)")
    response = HttpResponse(c, content_type="text/html")
    return response

@login_required(login_url='/login')
def schoology_class(request):
    try:
        s = SchoologyAuth.objects.get(h_user= request.user, src='Schoology')
    except:
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
    Log.objects.create(user=request.user, date=datetime.datetime.now(), message="Refreshed Schoology Classes", error=False, log_type="Schoology Refresh", ip_address = request.META.get("REMOTE_ADDR"))

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
        if str(response) != "<Response [200]>":
            error = True
        else:
            error = False
        for hw in data['assignment']:
            if str(hw['id']) not in z:
                try:
                    l = datetime.datetime.strptime(hw['due'], "%Y-%m-%d %H:%M:%S")
                except:
                    l = datetime.datetime.now()
                h = Homework.objects.create(hw_user=request.user,hw_class=class1.linked_class,hw_title=hw['title'], external_id=hw['id'], external_src="Schoology", due_date=l,notes=f"{hw['description']}, {hw['web_url']}",completed=False, overdue=False)
                IntegrationLog.objects.create(user=class1.schoology_user, src="schoology", dest="hwapp", url = url, date = datetime.datetime.now(), message=response.text, error=error, hw_name=h.hw_title)
                try:
                    notion_push(hw=h,user=request.user)
                except:
                    pass
            pass
    Log.objects.create(user=request.user, date=datetime.datetime.now(), message="Refreshed Schoology Homework", error=False, log_type="Schoology Refresh", ip_address = request.META.get("REMOTE_ADDR"))

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
                    c = Class.objects.create(class_user=request.user, class_name=i['name'], external_src="Canvas", external_id=i['id'])
                    SchoologyClasses.objects.create(schoology_user=request.user, class_id=i['id'], s_class_name=i['name'],s_grading_period=i['enrollment_term_id'], linked_class=c, src='Canvas', auth_data=s)
    Log.objects.create(user=request.user, date=datetime.datetime.now(), message="Refreshed Canvas Classes", error=False, log_type="Canvas Refresh", ip_address = request.META.get("REMOTE_ADDR"))

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
        url = f"https://canvas.instructure.com/api/v1/courses/{class1.class_id}/assignments?access_token={class1.auth_data.s_secret_key}&per_page=1000"
        headers = {
            "Authorization": f'Bearer {class1.auth_data.s_secret_key}'
        }   
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        if str(response) != "<Response [200]>":
            error = True
        else:
            error = False
        t = Preferences.objects.get(preferences_user=request.user)
        for hw in data:
            try:
                str(hw['id'])
            except TypeError:
                class1.update = False
                class1.save()
                break
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
                IntegrationLog.objects.create(user=class1.schoology_user, src="canvas", dest="hwapp", url = url, date = datetime.datetime.now(), message=response.text, error=error, hw_name=h.hw_title)
                
                try:
                    notion_push(hw=h,user=request.user)
                except:
                    pass
            pass
    Log.objects.create(user=request.user, date=datetime.datetime.now(), message="Refreshed Canvas Homework", error=False, log_type="Canvas Refresh", ip_address = request.META.get("REMOTE_ADDR"))
    
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
        s_obj = SchoologyAuth(src = "Canvas", h_user = request.user) 
        s_obj.s_secret_key = request.POST.get('secret_key')
        s_obj.url = request.POST.get('base_url')
        s_obj.save()
        return render(request, 'hwapp/success.html', {
            "message": "Success! Your Canvas key has been updated"
        })   
    else:
        return render(request, 'hwapp/canvas_api.html', {
            'service': 'Canvas',
            'location': 'Profile -> Settings -> Add New Access Token',
            'prefix': 'New'
        })
@login_required(login_url='/login')
def schoology_api(request):
    if request.method == 'POST':
        try:
            s_obj = SchoologyAuth.objects.get(h_user=request.user, src="Schoology")
        except:
            s_obj = SchoologyAuth(src = "Schoology", h_user = request.user)
        
        s_obj.s_consumer_key = request.POST.get('consumer_key')
        s_obj.s_secret_key = request.POST.get('secret_key')
        s_obj.user_id = request.POST.get('user_id')
        s_obj.url = request.POST.get('base_url')

        s_obj.save()
        return render(request, 'hwapp/success.html', {
            "message": "Success! Your Schoology key has been updated"
        })
    else:
        return render(request, 'hwapp/schoology_api.html', {
            'service': 'Schoology',
        })

@user_passes_test(matthew_check)
def edit_api(request, integration_id):
    if request.method == 'GET':
        try:
            integration = SchoologyAuth.objects.get(id=integration_id, h_user=request.user)
        except:
            return render(request, 'hwapp/error.html', {
                'error': "You are not authorized to access this page. Click <a href='/'>here</a> to return home."
            })
        try:
            linked_classes = SchoologyClasses.objects.filter(auth_data=integration, schoology_user=request.user).exclude(update=False)
        except:
            linked_classes = False
        if integration.src == "Schoology":
            return render(request, 'hwapp/schoology_api.html', {
                'integration': integration,
                'service': integration.src,
                'linked_classes': linked_classes
            })
        else:
            return render(request, 'hwapp/canvas_api.html', {
                'integration': integration,
                'service': integration.src,
                'linked_classes': linked_classes
            })
    elif request.method == 'POST':
        try:
            s_obj = SchoologyAuth.objects.get(id=integration_id, h_user=request.user)
        except:
            return render(request, 'hwapp/error.html', {
                'error': "You are not authorized to access this page. Click <a href='/'>here</a> to return home."
            })
        if s_obj.src == "Canvas":
            s_obj.s_secret_key = request.POST.get('secret_key')
            s_obj.url = request.POST.get('base_url')
        elif s_obj.src == "Schoology":
            s_obj.s_consumer_key = request.POST.get('consumer_key')
            s_obj.s_secret_key = request.POST.get('secret_key')
            s_obj.user_id = request.POST.get('user_id')
            s_obj.url = request.POST.get('base_url')

        s_obj.save()
        return render(request, 'hwapp/success.html', {
            "message": f"{s_obj.url} updated successfully"
        })
@user_passes_test(matthew_check)
def integration_log(request):
    #not authorized for non-admins
    if not request.user.is_superuser:
        return render(request, '404.html')
    if request.GET.get("error") == 'true':
        logs = IntegrationLog.objects.filter(error=True).order_by("-id")
    else:
        logs = IntegrationLog.objects.all().order_by("-id")
    Log.objects.create(user=request.user, date=datetime.datetime.now(), message="Viewed Integration Log", error=False, log_type="Integration Log Access", ip_address = request.META.get("REMOTE_ADDR"))
    return render(request, 'hwapp/integrationlog.html', {
        "logs": logs,
    })
@user_passes_test(matthew_check)
def integration_log_view(request, log_id):
    #not authorized for non-admins
    if not request.user.is_superuser:
        return render(request, '404.html')
    try:
        log = IntegrationLog.objects.get(id=log_id)
    except:
        return render(request, 'hwapp/error.html', {
            'error': f"Log ID {log_id} Not Found"
        })
    return render(request, 'hwapp/integrationlog_view.html', {
        "log": log,
    })
@login_required(login_url='/home')
def admin_log(request):
    #not authorized for non-admins
    if not request.user.is_superuser:
        return render(request, '404.html')
    if request.GET.get("error") == 'true':
        logs = Log.objects.filter(error=True).order_by("-id")
    else:
        logs = Log.objects.all().order_by("-id")
    return render(request, 'hwapp/admin_log.html', {
        "logs": logs,
    })

@login_required(login_url='/home')
def csv_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="homework.csv"'
    hws = Homework.objects.filter(hw_user=request.user)
    class_id = request.GET.get("class_id")
    if request.GET.get("class_id"):
        try:
            hw_class = Class.objects.get(id=request.GET.get("class_id"), class_user=request.user)
            hws = hws.filter(hw_class=hw_class)
        except:
            return render(request, 'hwapp/error.html', {
                "error": "Access Denied",
            })
    #default: no completed filter
    if str(request.GET.get("completed")) == 'true':
        hws = hws.filter(completed = True)
    elif str(request.GET.get("completed")) == 'false':
        hws = hws.filter(completed = False)

    
    writer = csv.writer(response)
    writer.writerow(['hw_class', 'hw_title', 'due_date', 'completed'])

    hws = hws.values_list('hw_class__class_name', 'hw_title', 'due_date', 'completed')
    for hw in hws:
        writer.writerow(hw)

    return response


@login_required(login_url='/login')
def gcal_tonotion(request):
    if request.method == 'GET':
        db_id = '8bc20dc50f57446fbeecbae976a2a5d1'
        notion_data = NotionData.objects.get(notion_user=request.user, tag='homework')


        try:
            #make link an https link
            link = 'https://calendar.google.com/calendar/ical/matthew.tsai23%40gmail.com/private-57e7103bb7d3ad3042ff79ad166c762a/basic.ics'
            #link = request.POST.get('schoology_ics_link')
            link = link.replace('webcal', 'https')
            c = Calendar(requests.get(link).text)
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'Please copy the full ICS link from the external integration with the instructions below and include the "webcal" portion of the link'
            })
        #SETUP: create new Class instance if not already existing(since Canvas does not provide class names with HW assignments)
        dt_str = '23:59'
        dt_obj = datetime.datetime.strptime(dt_str, '%H:%M')
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
        print(True)
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
                l = Homework()
                notion_push(hw=l, user=request.user)  
                IcsId.objects.create(icsID_user=request.user, icsID = ics_uid)
        return render(request, 'hwapp/success.html', {
            'message': "Feed integrated successfully. Please <a href='/'>return home</a>"
        })        
    else:
        return render(request, 'hwapp/other.html')