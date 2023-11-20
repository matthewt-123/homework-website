from django.shortcuts import render
from .models import HelpForm
from django.http.response import JsonResponse, HttpResponse
import json
import sys
import html
from datetime import datetime
sys.path.append("..")
from hwapp.email_helper import email_admin
# Create your views here.
def contact(request):
    if request.method == 'POST':
        form = json.loads(request.body)
        try:
            first_name = html.escape(form['first_name'])
            last_name = html.escape(form['last_name'])
            subject = html.escape(form['subject'])
            email = form['email']
            message = html.escape(form['message'])
            if not first_name or not last_name or not subject or not email or not message:
                return JsonResponse({'message': 'Invalid Form', 'status': 400}, status=400)
            if "@" not in email:
                return JsonResponse({'message': 'Invalid Form. Email must contain "@" sign.', 'status': 400}, status=400)
            h1 = HelpForm(first_name=first_name, last_name=last_name, email=email, message=message, subject=subject, received=datetime.now())
            h1.save()
            email_admin(f_name=first_name, l_name=last_name, email=email, message=message)
            return JsonResponse({'message': 'Succcess! Your message has been sent, and our team will respond to your request within 7 business days', 'status': 201}, status=201)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Invalid Form', 'status': 400}, status=400)
    else:
        return HttpResponse(status=405)