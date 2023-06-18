from django.shortcuts import render
from .models import HelpForm
from django.http.response import JsonResponse
import json
import sys
import html
sys.path.append("..")
from hwapp.email_helper import email_admin
# Create your views here.
def contact(request):
    if request.method == 'POST':
        form = json.loads(request.body)
        try:
            first_name = html.escape(form['first_name'])
            last_name = html.escape(form['last_name'])
            email = form['email']
            message = html.escape(form['message'])
            h1 = HelpForm(first_name=first_name, last_name=last_name, email=email, message=message)
            h1.save()
            email_admin(f_name=first_name, l_name=last_name, email=email, message=message)
            return JsonResponse({'message': 'Succcess! Your message has been sent, and our team will respond to your request within 7 business days', 'status': 201}, status=201)
        except:
            return JsonResponse({'message': 'Invalid Form', 'status': 400}, status=400)