import os
from datetime import date
import datetime
from .models import User, Homework, Class, Preferences, Carrier, EmailTemplate, Recurring, Day
import requests
from time import time
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import sys
import pytz 
import secrets
import json
from dateutil.relativedelta import relativedelta, MO
sys.path.append("..")
from integrations.views import refresh_ics, notion_push
from integrations.models import SchoologyAuth, SchoologyClasses, NotionData
from mywebsite.settings import DEBUG
def overdue_check():
    my_date = datetime.datetime.now()
    day = my_date.strftime("%d")
    month = my_date.strftime("%m")
    year = my_date.strftime("%Y")
    #day-1 as this refresh runs midnight PST/0700 UTC for all hw due previous day
    allhw = Homework.objects.filter(due_date__date__lt=datetime.datetime(int(year), int(month), int(day)-1), completed=False)
    for hw in allhw:
        hw.overdue = True
        hw.save()
def send_email(interval):
    #load data from .env to get API key
    load_dotenv()
    #refresh ICS
    refresh_ics()
    try:
        recipients = Preferences.objects.filter(email_notifications=True)
        for recipient in recipients:
            listed= f'Homework email for {recipient.preferences_user.username}'
            #get all hw for recipient
            hw_list = Homework.objects.filter(hw_user=recipient.preferences_user, completed=False).order_by('due_date', 'hw_class__period', 'priority')
            #iterate over each hw item, adding it to the email in HTML format
            listed = "<ul>"
            for each in hw_list:
                if each.overdue:
                    if each.notes != None and each.notes != "None":
                        listed = listed + f"<li style='color:red'><a style='color:red' href='https://{os.environ.get('website_root')}/homework/{each.id}'>{each.hw_title} for {each.hw_class} is due at {each.due_date.strftime('%d %B, %Y, %I:%M %p')}</a></li><ul><li style='color:red'>Notes: {each.notes}</li></ul>"
                    else:
                        listed = listed + f"<li style='color:red'><a style='color:red' href='https://{os.environ.get('website_root')}/homework/{each.id}'>{each.hw_title} for {each.hw_class} is due at {each.due_date.strftime('%d %B, %Y, %I:%M %p')}</a></li>"
                else:
                    if each.notes != None and each.notes != "None":
                        listed = listed + f"<li><a href='https://{os.environ.get('website_root')}/homework/{each.id}'>{each.hw_title} for {each.hw_class} is due at {each.due_date.strftime('%d %B, %Y, %I:%M %p')}</a></li><ul><li>Notes: {each.notes}</li></ul>"
                    else:
                        listed = listed + f"<li><a href='https://{os.environ.get('website_root')}/homework/{each.id}'>{each.hw_title} for {each.hw_class} is due at {each.due_date.strftime('%d %B, %Y, %I:%M %p')}</a></li>"
            #add closing tag
            listed = f"{listed}</ul>"
            html_content = str(EmailTemplate.objects.get(id=2).template_body)
            html_content = html_content.replace('$$homework', listed)
            todays = date.today()
            send = requests.post(
                f"{os.environ.get('API_BASE_URL')}/messages",
                auth=("api", f"{os.environ.get('mailgun_api_key')}"),
                data={
                    "from": "Homework App <noreply@matthewtsai.me>",
                    "to": [recipient.preferences_user.email],
                    "subject": f"{recipient.preferences_user.username}'s Homework Email for {todays}",
                    "html": html_content 
                }
            )
    except:
        #pass if no recipients matching preference query
        pass

def text_refresh():
    text_recipients = Preferences.objects.filter(text_notifications=True, phone_number__isnull=False)
    try:
        text_recipients = Preferences.objects.filter(text_notifications=True, phone_number__isnull=False)
        for text_recipient in text_recipients:
            email_base = text_recipient.carrier.email
            phone_number=int(text_recipient.phone_number)
            listed= f'Homework email for {text_recipient.preferences_user.username}'
            #get all hw for recipient
            hw_list = Homework.objects.filter(hw_user=text_recipient.preferences_user, completed=False).order_by('due_date', 'hw_class__period', 'priority')

            #iterate over each hw item, adding it to the email in HTML format
            listed = "<ul>"
            for each in hw_list:
                if each.notes != None and each.notes != "None":
                    listed = listed + f"<li><a href='https://{os.environ.get('website_root')}/homework/{each.id}'>{each.hw_title} for {each.hw_class} is due at {each.due_date}</a></li><ul><li>Notes: {each.notes}</li></ul>"
                else:
                    listed = listed + f"<li><a href='https://{os.environ.get('website_root')}/homework/{each.id}'>{each.hw_title} for {each.hw_class} is due at {each.due_date}</a></li>"
            #add closing tag
            listed = f"{listed}</ul>"
            todays = date.today()
            send = requests.post(
                f"{os.environ.get('API_BASE_URL')}/messages",
                auth=HTTPBasicAuth("api", f"{os.environ.get('mailgun_api_key')}"),
                data={
                    "from": "Homework App <noreply@matthewtsai.me>",
                    "to": [f"{phone_number}{email_base}"],
                    "subject": f"{text_recipient.preferences_user.username}'s Homework Email for {todays}",
                    "html": listed 
                }
            )
    except:
        #pass if no recipients matching preference query
        pass

def pw_reset_email(user, hash_val, expires, email):
    pw_email_template = str(EmailTemplate.objects.get(id=1).template_body)
    listed = pw_email_template.replace('$$exp_time', expires.strftime('%d %B, %Y, %I:%M %p'))
    listed = listed.replace('$$pw_reset_link', f'https://{os.environ.get("website_root")}/reset_password?hash={hash_val}')
    listed = listed.replace('$$website_root', os.environ.get("website_root"))
    #listed = f"<h1>Password Reset Email for {user.username}:</h1><br>Please navigate to the below link to reset your password. Please note that this link expires at {expires}: <br><a href='{os.environ.get('website_root')}/reset_password?hash={hash_val}'>{os.environ.get('website_root')}/reset_password?hash={hash_val}</a>"
    send = requests.post(
        f"{os.environ.get('API_BASE_URL')}/messages",
            auth=HTTPBasicAuth("api", f"{os.environ.get('mailgun_api_key')}"),
            data={
                "from": "Homework App <noreply@matthewtsai.me>",
                "to": [email],
                "subject": f"{user}'s Password Reset Email",
                "html": listed 
            }      
    )
def email_user(emails, content, subject):
    #listed = content.replace('$$website_root', os.environ.get("website_root"))
    listed = content
    send = requests.post(
    "https://api.mailgun.net/v3/matthewtsai.me/messages",
    auth=("api", f"{os.environ.get('mailgun_api_key')}"),
    data={
        "from": "Homework App <noreply@matthewtsai.me>",
        "to": emails,
        "subject": f"{subject}",
        "html": listed 
    }
)

def timezone_helper(u_timezone, u_datetime):
    local_time = pytz.timezone(str(u_timezone))    
    local_datetime = local_time.localize(u_datetime, is_dst=None)
    utc_datetime = local_datetime.astimezone(pytz.utc)
    return utc_datetime
def email_admin(f_name, l_name, email, message):
    content = f"First Name: {f_name}\nLast Name: {l_name}\nEmail: {email}\nMessage: {message}"
    send = requests.post(
    "https://api.mailgun.net/v3/matthewtsai.me/messages",
    auth=("api", f"{os.environ.get('mailgun_api_key')}"),
    data={
        "from": "Homework App <noreply@matthewtsai.me>",
        "to": ['support@matthewtsai.me'],
        "subject": f"[matthewtsai.me] New Help Form Submitted",
        "text": content 
    }
)

def schoology_class():
    users = SchoologyAuth.objects.filter(src='Schoology')
    for s in users:
        url = f'https://api.schoology.com/v1/users/{s.user_id}/sections'
        headers = {
            "Authorization": f'OAuth realm="Schoology API",oauth_consumer_key="{s.s_consumer_key}",oauth_token="",oauth_nonce="{secrets.token_urlsafe()}",oauth_timestamp="{int(time())}",oauth_signature_method="PLAINTEXT",oauth_version="1.0",oauth_signature="{s.s_secret_key}%26"'
        }
        response = requests.get(url, headers=headers)
        response = json.loads(response.text)
        s_class = SchoologyClasses.objects.filter(schoology_user=s.h_user)
        classes = []
        for i in s_class:
            classes.append(i.class_id)
        for i in response['section']:
            if f"{i['id']}" not in str(classes):
                c = Class.objects.create(class_user=s.h_user, class_name=i['course_title'], external_src="Schoology", external_id=i['id'])
                SchoologyClasses.objects.create(schoology_user=s.h_user, class_id=i['id'], s_class_name=i['course_title'],s_grading_period=i['grading_periods'][0], linked_class=c)

def schoology_hw():
    users = SchoologyAuth.objects.filter(src='Schoology')
    for s in users:
        c = SchoologyClasses.objects.filter(schoology_user=s.h_user, src='Schoology').exclude(update=False)
        try:
            existing_hws = Homework.objects.filter(hw_user=s.h_user, external_src="Schoology")
            z = []

            for existing_hw in existing_hws:
                z.append(str(existing_hw.external_id))
            for class1 in c:
                url = f"https://api.schoology.com/v1/sections/{class1.class_id}/assignments?start=0&limit=1000"
                headers = {
                    "Authorization": f'OAuth realm="Schoology API",oauth_consumer_key="{s.s_consumer_key}",oauth_token="",oauth_nonce="{secrets.token_urlsafe()}",oauth_timestamp="{int(time())}",oauth_signature_method="PLAINTEXT",oauth_version="1.0",oauth_signature="{s.s_secret_key}%26"'
                }   
                response = requests.get(url, headers=headers)
                data = json.loads(response.text)
                for hw in data['assignment']:                  
                    if str(hw['id']) not in z:
                        print(str(hw['id']))
                        print('stupid bitch')
                        try:
                            l = datetime.datetime.strptime(hw['due'], "%Y-%m-%d %H:%M:%S")
                        except:
                            l = datetime.datetime.now()
                        h = Homework.objects.create(hw_user=s.h_user,hw_class=class1.linked_class,hw_title=hw['title'], external_id=hw['id'], external_src="Schoology", due_date=l,notes=f"{hw['description']}, {hw['web_url']}",completed=False, overdue=False)
                        notion_push(hw=h,user=s.h_user)
                    pass
        except:
            pass
def canvas_class():
    all = SchoologyAuth.objects.filter(src='Canvas')
    for s in all:
        url = f'https://canvas.instructure.com/api/v1/courses?access_token={s.s_secret_key}'
        headers = {
            "Authorization": f'Bearer {s.s_secret_key}'
        }
        response = requests.get(url, headers=headers)
        #print(response.text)
        response = json.loads(response.text)
        s_class = SchoologyClasses.objects.filter(schoology_user=all.h_user, src='Canvas')
        classes = []
        for i in s_class:
            classes.append(str(i.class_id))
        for i in response:
            try:
                assert i['access_restricted_by_date'] == True
            except KeyError:
                if str(i['id']) not in classes:
                    c = Class.objects.create(class_user=all.h_user, class_name=i['name'], external_src="Canvas", external_id=i['id'])
                    SchoologyClasses.objects.create(schoology_user=all.h_user, class_id=i['id'], s_class_name=i['name'],s_grading_period=i['enrollment_term_id'], linked_class=c, src='Canvas', auth_data=s)

def canvas_hw():
    c = SchoologyClasses.objects.filter(src='Canvas').exclude(update=False)
    for class1 in c:
        existing_hws = Homework.objects.filter(hw_user=class1.schoology_user, external_src="Canvas")
        z = []
        for existing_hw in existing_hws:
            z.append(str(existing_hw.external_id))

        url = f"https://canvas.instructure.com/api/v1/courses/{class1.class_id}/assignments?access_token={class1.auth_data.s_secret_key}"
        headers = {
            "Authorization": f'Bearer {class1.auth_data.s_secret_key}'
        }   
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        for hw in data:
            if str(hw['id']) not in z:
                try:
                    l = datetime.datetime.strptime(hw['due_at'], "%Y-%m-%dT%H:%M:%S%z")
                except:
                    l = datetime.datetime.now()
                h = Homework.objects.create(hw_user=class1.schoology_user,hw_class=class1.linked_class,hw_title=hw['name'], external_id=hw['id'], external_src="Canvas", due_date=l,notes=f"{hw['description']}",completed=False, overdue=False)
                notion_push(hw=h,user=class1.schoology_user)
            pass
def recurring_events():
    #run every sunday
    r = Recurring.objects.all()
    dt = datetime.datetime.now() 
    sunday = dt + relativedelta(weekday=MO(0)) + datetime.timedelta(days=-1)
    for each in r:
        user = each.user
        hw = each
        for day in each.days.all():
            dt = sunday + datetime.timedelta(days=day.id - 1)
            token = NotionData.objects.get(notion_user=user).access_token
            page_id = NotionData.objects.get(notion_user=user).db_id
            url = 'https://api.notion.com/v1/pages'
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
                            "start": f"{dt}",
                            "end": None,
                            "time_zone": "US/Pacific"
                        }
                    }
                    
                }
            }
            requests.post(url, data=json.dumps(body), headers={'Authorization': f'Bearer {token}', 'Notion-Version': '2022-02-22', "Content-Type": "application/json"})
