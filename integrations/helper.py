import requests
import json
import sys
from .models import NotionData, IntegrationLog
sys.path.append("..")
from hwapp.models import Homework
import pytz
from datetime import datetime

def notion_push(hw, user):
    n_data = NotionData.objects.get(notion_user=user, tag="homework")
    token = n_data.access_token
    page_id = n_data.db_id
    url = 'https://api.notion.com/v1/pages'
    print(type(hw.due_date))
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
        error = True
    else:
        error = False
    i = IntegrationLog.objects.create(user=user, src="hwapp", dest="notion", url = url, date = datetime.now(), message=response.text, error=error, hw_name=hw.hw_title)
    i.save()
    return 0
def canvas_notion_push(hw, user, timezone):
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
                    "start": f"{hw.due_date.astimezone(pytz.timezone(f'{timezone}')).replace(tzinfo=None)}",
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

    return 0
def full_notion_refresh(user):
    token = 'secret_MhEfmsvCF6ru7RybJVUj7johlJ4buNYDCHc4YSXRf08'
    page_id = 'f6b38a903c284453a6c49d00de237064'
    url = 'https://api.notion.com/v1/pages'
    to_post = Homework.objects.filter(hw_user=user, completed=False, notion_migrated=False)
    m = []
    for hw in to_post:
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
        m.append(hw.hw_title)
    migrated = Homework.objects.filter(hw_user=user, completed=True, notion_migrated=True)
    for m1 in migrated:
        url = f'https://api.notion.com/v1/pages/{m1.notion_id}'
        data = {
        "properties": {
            "Status": {
                "status": {
                    "name":"Completed"
                }
            },    
        }}
        response = requests.patch(url, data=json.dumps(data), headers={'Authorization': f'Bearer {token}', 'Notion-Version': '2022-02-22', "Content-Type": "application/json"})
    return m
def notion_status_push(hw, user, status):
    token = NotionData.objects.get(notion_user=user, tag="homework").access_token
    page_id = hw.notion_id
    url = f'https://api.notion.com/v1/pages/{page_id}'
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
                    "name":status
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
    response = requests.patch(url, data=json.dumps(body), headers={'Authorization': f'Bearer {token}', 'Notion-Version': '2022-02-22', "Content-Type": "application/json"})
    print(response) 
    IntegrationLog.objects.create(user=user, src="hwapp", dest="notion", url = url, date = datetime.now(), message=response.text, error=False, hw_name=hw.hw_title)

    return(response)

def notion_pull():
    tokens = NotionData.objects.filter(tag="homework")
    for notion_obj in tokens:
        url = ""
        url = f'https://api.notion.com/v1/databases/{notion_obj.db_id}/query'
        data = {"filter": {"property": "Status", "status": {"equals": "Completed"}}}
        response = requests.post(url, headers={'Authorization': f'Bearer {notion_obj.access_token}', 'Notion-Version': '2022-06-28', "Content-Type": "application/json"}, data=json.dumps(data))
        if '200' not in str(response):
            IntegrationLog.objects.create(user=notion_obj.notion_user, src="notion", dest="hwapp", url = url, date = datetime.now(), message=response.text, error=True)
            break
        i = json.loads(response.text)
        completed_list = []
        for event in i['results']:
            completed_list.append(event['id'])
        hw_list = Homework.objects.filter(completed=False, hw_user=notion_obj.notion_user, notion_migrated=True)
        for hw in hw_list:
            if hw.notion_id in completed_list:
                print(hw.hw_title)
                hw.completed = True
                hw.save()
                IntegrationLog.objects.create(user=notion_obj.notion_user, src="notion", dest="hwapp", url = url, date = datetime.now(), message=response.text, error=False, hw_name=hw.hw_title)