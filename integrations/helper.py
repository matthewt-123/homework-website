import requests
import json
import sys
from .models import NotionData
sys.path.append("..")
from hwapp.models import Homework

def notion_push(hw, user):
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
def full_notion_refresh(user):
    token = 'secret_MhEfmsvCF6ru7RybJVUj7johlJ4buNYDCHc4YSXRf08'
    page_id = 'f6b38a903c284453a6c49d00de237064'
    url = 'https://api.notion.com/v1/pages'
    to_post = Homework.objects.filter(hw_user=user, completed=False, notion_migrated=False)
    m = []
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
        m.append(hw.hw_title)
    migrated = Homework.objects.filter(hw_user=user, completed=True, notion_migrated=True)
    for m1 in migrated:
        url = f'https://api.notion.com/v1/pages/{m1.notion_id}'
        data = {
        "properties": {
            "Status": {
                "select": {
                    "name":"Completed"
                }
            },    
        }}
        response = requests.patch(url, data=json.dumps(data), headers={'Authorization': f'Bearer {token}', 'Notion-Version': '2022-02-22', "Content-Type": "application/json"})
    return m