from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from datetime import date
import datetime
from .models import Recurrence, User, Homework, Class, Preferences, Carrier
import requests
from dotenv import load_dotenv

def send_email(interval):
    #load data from .env to get API key
    load_dotenv()
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
                if datetime.datetime.now() > each.due_date:
                    color = 'red'
                else:
                    color = 'black' 
                if each.notes != None and each.notes != "None":

                    listed = listed + f"<li style='color:{color}'>{each.hw_title} for {each.hw_class} is due at {each.due_date}</li><ul><li>Notes: {each.notes}</li></ul>"
                else:
                    listed = listed + f"<li style='color:{color}'>{each.hw_title} for {each.hw_class} is due at {each.due_date}</li>"
            #add closing tag
            listed = f"{listed}</ul>"
            todays = date.today()
            send = requests.post(
                f"{os.environ.get('API_BASE_URL')}/messages",
                auth=("api", f"{os.environ.get('mailgun_api_key')}"),
                data={
                    "from": "Homework App <noreply@mail.matthewtsai.games>",
                    "to": [recipient.preferences_user.email],
                    "subject": f"{recipient.preferences_user.username}'s Homework Email for {todays}",
                    "html": listed 
                }
            )
    except:
        #pass if no recipients matching preference query
        pass
    try:
        text_recipients = Preferences.objects.get(text_notifications=True, phone_number__isnull=False)
        for text_recipient in text_recipients:
            email_base = text_recipient.carrier.email
            phone_number=int(text_recipient.phone_number)
            listed= f'Homework email for {recipient.preferences_user.username}'
            #get all hw for recipient
            hw_list = Homework.objects.filter(hw_user=recipient.preferences_user, completed=False).order_by('due_date', 'hw_class__period', 'priority')

            #iterate over each hw item, adding it to the email in HTML format
            listed = "<ul>"
            for each in hw_list:
                if each.notes != None and each.notes != "None":
                    listed = listed + f"<li>{each.hw_title} for {each.hw_class} is due at {each.due_date}</li><ul><li>Notes: {each.notes}</li></ul>"
                else:
                    listed = listed + f"<li>{each.hw_title} for {each.hw_class} is due at {each.due_date}</li>"
            #add closing tag
            listed = f"{listed}</ul>"
            todays = date.today()
            send = requests.post(
                f"{os.environ.get('API_BASE_URL')}/messages",
                auth=("api", f"{os.environ.get('mailgun_api_key')}"),
                data={
                    "from": "Homework App <noreply@mail.matthewtsai.games>",
                    "to": [f"{phone_number}{email_base}"],
                    "subject": f"{recipient.preferences_user.username}'s Homework Email for {todays}",
                    "html": listed 
                }
            )
    except:
        #pass if no recipients matching preference query
        pass

def pw_reset_email(user, hash_val, expires, email):
    listed = f"<h1>Password Reset Email for {user.username}:</h1><br>Please navigate to the below link to reset your password. Please note that this link expires at {expires}: <br><a href='{os.environ.get('website_root')}/reset_password?hash={hash_val}'>{os.environ.get('website_root')}/reset_password?hash={hash_val}</a>"
    send = requests.post(
        f"{os.environ.get('API_BASE_URL')}/messages",
            auth=("api", f"{os.environ.get('mailgun_api_key')}"),
            data={
                "from": "Homework App <noreply@mail.matthewtsai.games>",
                "to": [email],
                "subject": f"{user}'s Password Reset Email",
                "html": listed 
            }      
    )
