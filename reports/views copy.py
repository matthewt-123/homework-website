from django.shortcuts import render

# Create your views here.
from django.db import models, connections
from django.contrib.auth.decorators import login_required, user_passes_test
import sys
from hwapp.models import Homework, Class, Day, IcsId, Preferences, User
from django.db.models.functions import ExtractWeek

sys.path.append("..")
from integrations.models import CalendarEvent, IcsHashVal, NotionData
# Create your models here.

@login_required(login_url="/home")
def homework(request):
    
    id = int(request.user.id)
    #hws = Homework.objects.filter(hw_user=request.user).annotate(week_no=ExtractWeek("due_date")).order_by("week_no")
    hws = Homework.objects.raw("SELECT strftime('%%W', due_date) as Week_Number, COUNT(*) AS Weekly_Count FROM hwapp_homework WHERE hw_user_id = %s GROUP BY Week_Number LIMIT 1000", (request.user.id,))
    print(hws)
    return render(request, 'hwapp/success.html', {
        "message": hws
    })