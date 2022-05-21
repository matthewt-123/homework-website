import os
from datetime import date
import datetime
from .models import Recurrence, User, Homework, Class, Preferences, Carrier, EmailTemplate
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
import sys
import pytz 
sys.path.append("..")
from integrations.views import refresh_ics

def overdue_check():
    my_date = datetime.datetime.now()
    day = my_date.strftime("%d")
    month = my_date.strftime("%m")
    year = my_date.strftime("%Y")
    #day-1 as this refresh runs midnight PST/0700 UTC for all hw due previous day
    allhw = Homework.objects.filter(due_date__date=datetime.datetime(int(year), int(month), int(day)-1), completed=False)
    for hw in allhw:
        hw.overdue = True
        hw.save()
def send_email(interval):
    #load data from .env to get API key
    load_dotenv()
    #refresh ICS
    refresh_ics()
    interval_instance = Recurrence.objects.get(basis=str(interval))
    try:
        recipients = Preferences.objects.filter(email_notifications=True, email_recurrence=interval_instance)
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