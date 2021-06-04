from django.shortcuts import render
from django.db import IntegrityError, connection
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms
import time, sched
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from dotenv import load_dotenv
# Create your views here.

def index(request):
    load_dotenv()
    return render(request, "hwapp/calendar.html", {
        'CLIENT_ID': os.environ.get('oauth_client_id_google'),
        'ENDPOINT': os.environ.get('oauth_endpoint_google')
    })
