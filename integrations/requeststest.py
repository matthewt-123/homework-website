import requests
import os
from dotenv import load_dotenv
from ics import Calendar, Event

url = "https://fuhsd.schoology.com/calendar/feed/ical/1608575122/708193ddc3bb8629dba62c854cf86d6e/ical.ics"

c = Calendar(requests.get(url).text)

for each in c.events:
    print(each.name)
    if each.name == "VEVENT":
        print(each.get('summary'))


