from django.shortcuts import render

# Create your views here.
from django.db import models, connections
from django.contrib.auth.decorators import login_required, user_passes_test
import sys
from hwapp.models import Homework, Class, Day, IcsId, Preferences, User
from django.db.models.functions import ExtractWeek
from collections import Counter
sys.path.append("..")
from integrations.models import CalendarEvent, IcsHashVal, NotionData
# Create your models here.
from django.db.models import Sum
from slick_reporting.views import ReportView, Chart
from slick_reporting.fields import SlickReportField



@login_required(login_url="/home")
def homework(request):
    
    print(request.user.id)
    hws = Homework.objects.filter(hw_user=request.user).values("due_date").annotate(week_no=ExtractWeek("due_date")).order_by("week_no")
    hws = hws.annotate(count = models.Count("week_no"))
    #hws = Homework.objects.raw("SELECT strftime('%%W', due_date) as Week_Number, COUNT(*) AS Weekly_Count FROM hwapp_homework WHERE hw_user_id = %s GROUP BY Week_Number LIMIT 1000", (request.user.id,))
    weeks = []
    for hw in hws:
        weeks.append(hw['week_no'])
    weeks = Counter(weeks)
    Keys = list(weeks.keys())
    Keys.sort()
    weeks_sorted = {key: weeks[key] for key in Keys}
    print(weeks_sorted)

    return render(request, 'hwapp/success.html', {
        "message": hws
    })