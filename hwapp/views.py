from django.http.response import JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, connection
from django.forms import ModelForm
from .models import User, Recurrence, Day, Class, Homework, Preferences
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
import time, sched
from django.contrib.auth.decorators import login_required
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from . import basics
from ics import Calendar, Event
from .forms import HomeworkForm, PreferencesForm, AddClassForm
from dotenv import load_dotenv
import json
from datetime import datetime
from django.core.paginator import Paginator



#allow python to access Calendar data model
import sys
sys.path.append("..")
from integrations.models import CalendarEvent, IntegrationPreference

load_dotenv()




@login_required(login_url='/login')
def index(request):
    page_size = request.GET.get('page_size')
    if not page_size:
        page_size = 10
    if not request.GET.get('class'):
        hwlist = Homework.objects.filter(hw_user = request.user, completed=False).order_by('due_date', 'hw_class__period', 'priority')
    else:
        try:
            class1 = Class.objects.get(class_user=request.user, id=request.GET.get('class'))
        except:
            return JsonResponse({
                "message": "Access Denied"
            }, status=403)
        hwlist = Homework.objects.filter(hw_user = request.user, completed=False, hw_class=class1).order_by('due_date', 'hw_class__period', 'priority')
    h = Paginator(hwlist, page_size)
    page_number = request.GET.get('page')
    if not page_number:
        page_number=1
    page_obj = h.get_page(page_number)
    class_list = Class.objects.filter(class_user = request.user).order_by('period')
    load_dotenv()
    return render(request, 'hwapp/index.html', {
        'hwlist': page_obj,
        'class_list': class_list,
        'page_obj': page_obj,
        'length': list(h.page_range)
    })



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"), status=302)
        else:
            return render(request, "hwapp/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "hwapp/login.html", {
            'CLIENT_ID': os.environ.get('oauth_client_id_google'),
            'ENDPOINT': os.environ.get('oauth_endpoint_google')
        })


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "hwapp/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "hwapp/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        #create integration profile
        integration_profile = IntegrationPreference(integrations_user=request.user)
        calendar = CalendarEvent(calendar_user=request.user)
        calendar.save()
        integration_profile.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "hwapp/register.html")
# Create your views here.

def hourly_refresh(request):
    user = request.user
    hw =  Homework.objects.filter(hw_user=user, completed=False)
    listed= f'Homework email for {user.username}.'
    for each in hw:
        listed = listed + f"<li>{each.hw_title}({each.hw_class}) is due at {each.due_date}</li>"
    message = Mail(
        from_email = basics.from_email,
        to_emails= basics.to_emails,
        subject = f"{user.username} Homework Email",
        html_content=listed
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e.details)
    pass

def weekly_refresh(request):
    user = request.user
    hw =  Homework.objects.filter(hw_user=user, completed=False)
    listed= f'Homework email for {user.username}.'
    for each in hw:
        listed = listed + f"<li>{each.hw_title}({each.hw_class}) is due at {each.due_date}</li>"
    message = Mail(
        from_email = basics.from_email,
        to_emails= basics.to_emails,
        subject = f"{user.username} Homework Email",
        html_content=listed
    )
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
    except Exception as e:
        print(e.details)
    pass

@login_required(login_url='/login')
def classes(request):
    classes = Class.objects.filter(class_user=request.user).order_by('period')
    return render(request, 'hwapp/classes.html', {
        'classes': classes
    })

@login_required(login_url='/login')
def addhw(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        data['priority'] = int(data['priority'])
        try:
            try:
                hw_class = Class.objects.get(id=data['hw_class'], class_user =request.user)
            except:
                return JsonResponse({
                    "message": "error: not authorized",
                    "status": 400
                }, 403)
            new_hw = Homework(hw_user=request.user, hw_class=hw_class, hw_title=data['hw_title'], due_date=data['due_date'], priority=data['priority'], completed=False)   
            new_hw.save()
            date_ics = datetime.strptime(data['due_date'], "%Y-%m-%d").date()
            date = date_ics.strftime("%b. %d, %Y")
            
            #create full time entry:
            ics_date = datetime.combine(date_ics, hw_class.time)

            #create ICS entry:
            try:
                var = Preferences.objects.get(preferences_user=request.user).calendar_output
            except:
                var=False
            if var == True:
                e = Event()
                e.name = data['hw_title']
                e.begin = ics_date
                e.description = f"Class: {hw_class.class_name}"
                #enter new event into database:
                new_calevent = CalendarEvent(calendar_user = request.user, homework_event=new_hw, ics=e)
                new_calevent.save()
            return JsonResponse({
                "message": "Homework added successfully!",
                "status": 201,
                'hw_id': new_hw.id,
                'class_name': new_hw.hw_class.class_name,
                'formatted_date': date
            }, status=201)
        except:
            return JsonResponse({
                "message": "An unknown error has occured. Please try again",
                "status": 400,
            }, status=400)
    else:
        return JsonResponse({
            "message": "method GET not allowed"
        })

@login_required(login_url='/login')
def preferences(request):
    if request.method == 'POST':
        form = PreferencesForm(request.POST)  
        if form.is_valid():
            email_recurrence=form.cleaned_data['email_recurrence']
            email_notifications=form.cleaned_data['email_notifications']
            phone_number=form.cleaned_data['phone_number']
            carrier=form.cleaned_data['carrier']
            text_notifications = form.cleaned_data['text_notifications']
            calendar_output = form.cleaned_data['calendar_output']
            user_timezone = form.cleaned_data['user_timezone']
            if phone_number and not carrier:
                return render(request, 'hwapp/preferences.html', {
                    'form': form,
                    'error': "The carrier field is required."
                })
            try:
                preferences = Preferences.objects.get(preferences_user=request.user)
                preferences.email_notifications = email_notifications
                preferences.email_recurrence = email_recurrence
                preferences.phone_number = phone_number
                preferences.carrier = carrier    
                preferences.text_notifications = text_notifications  
                preferences.calendar_output = calendar_output      
                preferences.user_timezone = user_timezone    
                preferences.save()
            except:
                new_pref = Preferences(preferences_user=request.user, email_recurrence=email_recurrence, email_notifications=email_notifications, carrier=carrier, phone_number=phone_number, text_notifications=text_notifications)
                new_pref.save()
            return render(request, 'hwapp/preferences.html', {
                'form': form,
                'message': "Success! Your preferences have been saved."
            })
    else:
        try: 
            preferences = Preferences.objects.get(preferences_user=request.user)
            email_notifications = preferences.email_notifications
            email_recurrence = preferences.email_recurrence
            initial = {
                'email_notifications': email_notifications,
                'email_recurrence': email_recurrence,
                'carrier': preferences.carrier,
                'phone_number': preferences.phone_number,
                'text_notifications': preferences.text_notifications,
                'calendar_output': preferences.calendar_output,
                'user_timezone': preferences.user_timezone
            }
            form = PreferencesForm(initial=initial)
            return render(request, 'hwapp/preferences.html', {
                'form': form
        })
        except:
            form = PreferencesForm()
            return render(request, 'hwapp/preferences.html', {
                'form': form
            })
@login_required(login_url='/login')
def edit_hw(request, hw_id):
    class EditHwForm(ModelForm):
        class Meta:
            model = Homework
            fields = ['hw_class', 'hw_title', 'due_date', 'priority', 'notes']
        def __init__(self, *args, **kwargs):
            super(EditHwForm, self).__init__(*args, **kwargs)
            self.fields['hw_class'].queryset = Class.objects.filter(class_user=request.user)
    if request.method == 'POST':
        form = EditHwForm(request.POST)
        if form.is_valid():
            #pulling form data
            hw_class = form.cleaned_data['hw_class']
            hw_title = form.cleaned_data['hw_title']
            due_date = form.cleaned_data['due_date']
            priority = form.cleaned_data['priority']
            notes = form.cleaned_data['notes']
            try:
                #updating model
                updated = Homework.objects.get(hw_user=request.user, id=hw_id)
                updated.hw_class = hw_class
                updated.hw_title = hw_title
                updated.due_date = due_date
                updated.priority = priority
                updated.notes = notes
                updated.save()
            except:
                return render(request, 'hwapp/error.html', {
                    'error': "Access Denied"
                })
            #format date:
            formatted_date = datetime.combine(due_date, hw_class.time)

            #update ICS:
            if Preferences.objects.get(preferences_user=request.user).calendar_output == True:
                e = Event()
                e.name = hw_title
                e.begin = formatted_date
                e.description = f"Class: {hw_class.class_name}"
                if notes:
                    e.description += f"; {notes}"

                #pull ICS:
                edit_event = CalendarEvent.objects.get(calendar_user = request.user, homework_event=updated)
                edit_event.ics = e
                edit_event.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'hwapp/edit_hw.html', {
                'form': form
            })
    else:
        try:
            hw = Homework.objects.get(hw_user=request.user, id=hw_id)
            values = {
                'hw_class': hw.hw_class,
                'hw_title': hw.hw_title,
                'notes': hw.notes,
                'priority': hw.priority,
                'due_date': hw.due_date
            }   
            form = EditHwForm(initial=values)
            return render(request, 'hwapp/edit_hw.html', {
                'form': form,
                'hw_id': hw_id
            })  
        except:
            return HttpResponseRedirect(reverse('index'))  

@login_required(login_url='/login')
def addclass(request):
    if request.method == 'POST':
        form = AddClassForm(request.POST)
        if form.is_valid():
            user = request.user
            class_name = form.cleaned_data['class_name']
            period = form.cleaned_data['period']
            days = form.cleaned_data['days']
            time = form.cleaned_data['time']
            dlist=[]
            for day in days.iterator():
                dlist.append(day)
            class1 = Class(class_user=user, class_name=class_name, period=period, time=time)
            class1.save()
            newclass = Class.objects.get(id=class1.id)
            
            for item in dlist:
                newclass.days.add(item)
      
            newclass.save()
        else:
            return render(request, 'hwapp/addclass.html', {
                'form': form
            })
        return HttpResponseRedirect(reverse('classes'))
    else:
        form = AddClassForm()
        return render(request, 'hwapp/addclass.html', {
            'form': form
        })
@login_required(login_url='/login')
def editclass(request, class_id):
    try:
        do_not_edit = Class.objects.get(class_user=request.user, class_name='Schoology Integration', period=999999)
    except:
        do_not_edit=None
    try:
        do_not_edit = Class.objects.get(class_user=request.user, class_name='Canvas Integration', period=999999)
    except:
        do_not_edit=None
    if request.method == "POST":
        form = AddClassForm(request.POST)
        if form.is_valid():
            class_name = form.cleaned_data['class_name']
            period = form.cleaned_data['period']
            days = form.cleaned_data['days']
            time = form.cleaned_data['time']
            dlist=[]
            print(do_not_edit)
            if class_id==do_not_edit.id:
                if int(period) == int(999999):
                    return render(request, 'hwapp/error.html', {
                        'error': "Access Denied: Please do not edit this class"
                    })
            for day in days.iterator():
                dlist.append(day)
            try:
                class1 = Class.objects.get(class_user=request.user, id=class_id)
                class1.class_name=class_name
                class1.period=period
                class1.time=time
                class1.save()
                for day in days:
                    class1.days.add(day)
                class1.save()
            except:
                return render(request, 'hwapp/error.html', {
                    'error': "There was an error saving your changes"
                })
            return HttpResponseRedirect(reverse('classes'))

    else:
        try:
            if class_id==do_not_edit.id:
                return render(request, 'hwapp/error.html', {
                    'error': "Access Denied: Please do not edit this class"
                })
        except:
            pass
        try:
            editclass = Class.objects.get(class_user=request.user, id=class_id)
        except:
            return render(request, 'hwapp/error.html', {
                'error': "Access Denied"
            })
        initial = {
            'class_name': editclass.class_name,
            'period': editclass.period,
            'time': editclass.time,
            'days': editclass.days.all()
        }
        form = AddClassForm(initial=initial)
        return render(request, 'hwapp/editclass.html', {
            'form': form,
            'class_id': class_id
        })

@login_required(login_url='/login')
def allhw(request):
    user = request.user
    hwall = Homework.objects.filter(hw_user = user).order_by('due_date', 'hw_class__period', 'priority')
    class_list = Class.objects.filter(class_user = request.user).order_by('period')
    hwlist = []
    completed = []
    for hw in hwall:
        if hw.completed == True:
            completed.append(hw)
        else:
            hwlist.append(hw)
    return render(request, 'hwapp/index.html', {
        'hwlist': hwlist,
        'completed': completed,
        'class_list': class_list,
    })
def about(request):
    return render(request, 'hwapp/aboutme.html')
@login_required(login_url='/login')
def profile(request):
    class UserForm(ModelForm):
        class Meta:
            model = User
            fields = ['first_name', 'last_name', 'email']
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return render(request, 'hwapp/profile.html', {
                'form': form,
                'message': "Success!"
            })
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        form = UserForm(initial = initial)
        return render(request, 'hwapp/profile.html', {
            'form': form
        })
@login_required(login_url='/login')
def calendar(request):
    if request.method == "GET":
        hash_val = abs(hash(str(request.user.id)))
        ics_link = f"matthewshomeworkapp.herokuapp.com/integrations/export/{request.user.id}/{hash_val}"
        return render(request, 'hwapp/calendar.html', {
            'ics_link': ics_link
        })
    else:
        return JsonResponse({'error': 'method not supported'}, status=405)


@login_required(login_url='/login')
def completion(request, hw_id):
    if request.method == "POST":
        data = json.loads(request.body)
        hw_id=data['hw_id']
        if str(data['completion']) == str(True):
            update = False
        else:
            update = True

        hw_instance = Homework.objects.get(hw_user=request.user, id=hw_id)
        hw_instance.completed=update
        hw_instance.save()
        return JsonResponse({
            "message": "Item updated successfully",
            "status": 201,
        }, status=201)
    else:
        return JsonResponse({
            "message": "method GET not supported"
        })
@login_required(login_url='/login')
def deleteclass(request, id):
    if request.method == 'DELETE':
        try:
            class_req = Class.objects.get(class_user=request.user, id=id)
            class_req.delete()
            print(True)
            return JsonResponse({
                "message": "Class removed successfully",
                "status": 200,
            }, status=200)
        except:
            return JsonResponse({
                'message': "Error: Access Denied",
                'status': 403,
            }, status=403)
    else:
        return JsonResponse({
            'message': 'method not allowed'
        }, status=405)