import requests
import json
import os
from .models import NotionData, IntegrationLog
from hwapp.models import Homework
from integrations.models import GradescopeClasses, GradescopeCredentials
from datetime import datetime
from azure.communication.email import EmailClient
from bs4 import BeautifulSoup

#email helper function

domain_name = os.environ.get("DOMAIN_NAME")

g_headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.gradescope.com",
    "Referer": "https://www.gradescope.com/login",
    "DNT": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
}
def email_user(email, content, subject, recipient_name):
    client = EmailClient.from_connection_string(os.environ.get('AZURE_CONNECTION_STRING', ""))
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
        "senderAddress": f"support@email.{domain_name}",
        "replyTo": [
            {
                "address": f"support@{domain_name}",  # Email address. Required.
                "displayName": "Homework App Support"  
            }
        ]
    }
    poller = client.begin_send(message)
    result = poller.result()
def notion_expired(user, notion_data=None):
    """
    if notion credentials expire, notify user
    """
    content = f"Notion login has expired. Please \
        <a href='https://{os.environ.get('website_root')}/integrations/notion_auth'>sign in again</a> to continue using Notion with HW App. Thank you"
    email_user(user.email, content, "[ACTION REQUIRED]: HW App Notion Login Expired", user.username)   
    if notion_data:
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
                "type": "select",
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
    response = requests.post(url, data=json.dumps(body), \
                             headers={'Authorization': f'Bearer {token}', 'Notion-Version': \
                                      '2022-02-22', "Content-Type": "application/json"})
    hw.notion_migrated = True
    hw.notion_id = json.loads(response.text)['id']
    hw.save()
    if str(response) != "<Response [200]>":
        notion_expired(user, n_data)
        error = True
    else:
        error = False
    i = IntegrationLog.objects.create(user=user, src="hwapp", dest="notion", url = url, \
                                      date = datetime.now(), message=response.text, error=error, \
                                        hw_name=hw.hw_title)
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
def gradescope_refresh():
    # helper function
    for creds in GradescopeCredentials.objects.all():
        session = requests.Session()
        # step 1: get authenticity token
        url = "https://www.gradescope.com"
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        token = 0
        for f in soup.find_all('form'):
            if f.get('action') == '/login': # type: ignore
                for val in f.find_all('input'): # type: ignore
                    if val.get('name') == "authenticity_token": # type: ignore
                        token = val.get('value') # type: ignore
        url = 'https://www.gradescope.com/login'
        gs_classes = GradescopeClasses.objects.filter(user=creds.user)
        email = creds.email
        password = creds.password
        body = {
            'utf8': '✓',
            'authenticity_token': token,
            'session[email]': email,
            'session[password]': password,
            'session[remember_me]': 0,
            'commit': 'Log In',
            'session[remember_me_sso]': 0
        }
        # step 2: log in
        res = session.post(url, headers=g_headers, data=body)
        for gclass in gs_classes:
            url = f'https://www.gradescope.com/courses/{gclass.class_id}'
            response = session.get(url, headers=g_headers)
            # return response.text
            assignment_list = [i.external_id for i in Homework.objects.filter(external_src="gradescope", hw_user=gclass.user)]
            if '200' in str(response):
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.find_all('table'):
                    #each assignment in table
                    if "assignments-student-table" in str(a.get('id')): # type: ignore
                        s = BeautifulSoup(str(a), 'html.parser')
                        for row in s.find_all('tr'):
                            print(row)
                            try:
                                id = -1
                                name = "unnamed assignment"
                                for a1 in row.find_all('a'): # type: ignore
                                    name = a1.text
                                    id = a1.get('href').split('/assignments/')[1].split('/submissions')[0] # type: ignore
                                due = row.find('time', class_='submissionTimeChart--dueDate').get('datetime') # type: ignore
                                
                                # If assignment has been graded, the tag changes from --text to --score. check both to accurately 
                                status_tag = row.find('div', class_="submissionStatus--text") # type: ignore
                                submitted = False
                                if status_tag is None:
                                    status_tag = row.find('div', class_="submissionStatus--score") # type: ignore
                                    submitted = True
                                status = status_tag.text # type: ignore
                                due = datetime.strptime(due, '%Y-%m-%d %H:%M:%S %z') # type: ignore
                                #check: is assignment logged? 
                                if str(id) in str(assignment_list):
                                    #yes:
                                    if status.lower() == "submitted" or submitted:
                                        #update status
                                        hw = Homework.objects.get(external_id=id, hw_user=gclass.user)
                                        hw.completed = True
                                        hw.save()
                                    else:
                                        hw = Homework.objects.get(external_id=id, hw_user=gclass.user)
                                        hw.completed = False
                                        hw.save()
                                else:
                                    #create:
                                    complete = False
                                    if status.lower() == "submitted" or submitted:
                                        complete = True
                                    h = Homework.objects.create(
                                        hw_user=gclass.user, 
                                        hw_class=gclass.linked_class, 
                                        hw_title=name, 
                                        due_date=due, 
                                        completed=complete, 
                                        overdue=False, 
                                        notion_migrated=False, 
                                        notion_id="", 
                                        ics_id="", 
                                        external_id=id, 
                                        external_src="gradescope", 
                                        archive=False
                                    )
                                    h.save()
                                #Yes: update if needed
                            except Exception as e:
                                # must not be a row oopsie OR is a header row. Does not matter keep processing
                                pass