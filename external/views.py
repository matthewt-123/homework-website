from django.shortcuts import render
from .forms import HelpForm1
from .models import HelpForm
from django.http.response import JsonResponse
import json
# Create your views here.
def contact(request):
    if request.method == 'POST':
        form = json.loads(request.body)
        try:
            first_name = form['first_name']
            last_name = form['last_name']
            email = form['email']
            message = form['message']
            h1 = HelpForm(first_name=first_name, last_name=last_name, email=email, message=message)
            h1.save()
            return JsonResponse({'message': 'Succcess! Your message has been sent, and our team will respond to your request within 7 business days', 'status': 201}, status=201)
        except:
            return JsonResponse({'message': 'Invalid Form', 'status': 400}, status=400)