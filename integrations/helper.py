import requests
import json
import sys
import os
from .models import NotionData, IntegrationLog
sys.path.append("..")
from hwapp.models import Homework
import pytz
from datetime import datetime
from azure.communication.email import EmailClient
#email helper function
def email_user(email, content, subject, recipient_name):
    client = EmailClient.from_connection_string(os.environ.get('AZURE_CONNECTION_STRING'))
    message = {
        "content": {
            "subject": subject,
            "html": content
        },
        "recipients": {
            "to": [
                {
                    "address": email,
                    "displayName": recipient_name
                }
            ]
        },
        "senderAddress": f"support@email.matthewtsai.tech",
        "replyTo": [
            {
                "address": "support@matthewtsai.tech",  # Email address. Required.
                "displayName": "Homework App Support"  
            }
        ]
    }
    poller = client.begin_send(message)
    result = poller.result()
#if notion credentials expire, notify user
def notion_expired(user, notion_data):
    content = f"Notion login has expired. Please <a href='https://{os.environ.get('website_root')}/integrations/notion_auth'>sign in again</a> to continue using Notion with HW App. Thank you"
    email_user(user.email, content, "[ACTION REQUIRED]: HW App Notion Login Expired", user.username)   
    notion_data.error = True
    notion_data.save() 
#push hwapp to notion
def notion_push(hw, user):
    n_data = NotionData.objects.get(notion_user=user, tag="homework")
    token = n_data.access_token
    page_id = n_data.db_id
    url = 'https://api.notion.com/v1/pages'
    hw.due_date = datetime.strftime(hw.due_date, '%Y-%m-%dT%H:%M')
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
    if str(response) != "<Response [200]>":
        notion_expired(user, n_data)
        error = True
    else:
        error = False
    i = IntegrationLog.objects.create(user=user, src="hwapp", dest="notion", url = url, date = datetime.now(), message=response.text, error=error, hw_name=hw.hw_title)
    i.save()
    return 0

#sync completed notion hw with hwapp
def notion_pull():
    tokens = NotionData.objects.filter(tag="homework")
    for notion_obj in tokens:
        url = ""
        url = f'https://api.notion.com/v1/databases/{notion_obj.db_id}/query'
        data = {"filter": {"property": "Status", "status": {"equals": "Not Started"}}}
        response = requests.post(url, headers={'Authorization': f'Bearer {notion_obj.access_token}', 'Notion-Version': '2022-06-28', "Content-Type": "application/json"}, data=json.dumps(data))
        if '200' not in str(response):
            notion_expired(notion_obj.notion_user, notion_obj)
            IntegrationLog.objects.create(user=notion_obj.notion_user, src="notion", dest="hwapp", url = url, date = datetime.now(), message=response.text, error=True)
            break
        i = json.loads(response.text)
        incomplete_list = []
        for event in i['results']:
            incomplete_list.append(event['id'])
        hw_list = Homework.objects.filter(completed=False, hw_user=notion_obj.notion_user, notion_migrated=True)
        for hw in hw_list:
            if hw.notion_id not in incomplete_list:
                hw.completed = True
                hw.save()
                IntegrationLog.objects.create(user=notion_obj.notion_user, src="notion", dest="hwapp", url = url, date = datetime.now(), message=response.text, error=False, hw_name=hw.hw_title)