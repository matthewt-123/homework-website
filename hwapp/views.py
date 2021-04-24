from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, connection
from django.forms import ModelForm
from .models import User, Recurrence, Day, Class, Homework, Preferences
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
import time, sched
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from . import basics
from django.contrib.admin import widgets
s= sched.scheduler(time.time, time.sleep)
class AddClassForm(ModelForm):
    class Meta:
        model = Class
        fields = ['class_name', 'period', 'days', 'time']
    days = forms.ModelMultipleChoiceField(
        queryset = Day.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    time = forms.TimeInput()
    def __init__(self, *args, **kwargs):
        super(AddClassForm, self).__init__(*args, **kwargs)
        self.fields['time'].widget = widgets.AdminTimeWidget()
class PreferencesForm(ModelForm):
    class Meta:
        model = Preferences
        fields = ['email_notifications', 'email_recurrence']

def user_check(user):
    return user.username=="Power_Automate"

@login_required(login_url='/login')
def index(request):
    hwlist = Homework.objects.filter(hw_user = request.user, completed=False).order_by('due_date', 'hw_class__period', 'priority')
    if request.is_ajax():
        hw_id=request.POST.get('hw_id')
        try: 
            update = request.POST['hw_completion']
            update = True
        except:
            update = False
        hw_instance = Homework.objects.get(hw_user=request.user, id=hw_id)
        hw_instance.completed=update
        hw_instance.save()
    return render(request, 'hwapp/index.html', {
        'hwlist': hwlist
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
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "hwapp/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "hwapp/login.html")


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
@user_passes_test(user_check)
def daily_refresh(request):
    user = User.objects.get(id=request.session['id'])
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
@user_passes_test(user_check)
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
@user_passes_test(user_check)
def monthly_refresh(request):
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
    classes = Class.objects.filter(class_user=request.user)
    return render(request, 'hwapp/classes.html', {
        'classes': classes
    })

@login_required(login_url='/login')
def addhw(request):
    class AddHwForm(ModelForm):
        class Meta:
            model = Homework
            fields = ['hw_class', 'hw_title', 'due_date', 'priority', 'notes']
        def __init__(self, *args, **kwargs):
            super(AddHwForm, self).__init__(*args, **kwargs)
            self.fields['hw_class'].queryset = Class.objects.filter(class_user=request.user)
    if request.method == 'POST':
        form = AddHwForm(request.POST)
        if form.is_valid():
            hw_class = form.cleaned_data['hw_class']
            hw_title = form.cleaned_data['hw_title']
            due_date = form.cleaned_data['due_date']
            priority = form.cleaned_data['priority']
            notes = form.cleaned_data['notes']
            addhw = Homework(hw_user=request.user, hw_class=hw_class, hw_title=hw_title, priority=priority, notes=notes, due_date=due_date, completed=False)
            addhw.save()
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'hwapp/addhw.html', {
                'form': form
            })
    else:

        form = AddHwForm()
        return render(request, 'hwapp/addhw.html', {
            'form': form
        })
@login_required(login_url='/login')
def preferences(request):
    if request.method == 'POST':
        form = PreferencesForm(request.POST)  
        if form.is_valid():
            email_recurrence=form.cleaned_data['email_recurrence']
            email_notifications=form.cleaned_data['email_notifications']
            try:
                preferences = Preferences.objects.get(preferences_user=request.user)
                preferences.email_notifications = email_notifications
                preferences.email_recurrence = email_recurrence
                preferences.save()
            except:
                new_pref = Preferences(preference_user=request.user, email_recurrence=email_recurrence, email_notifications=email_notifications)
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
                'email_recurrence': email_recurrence
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
    if request.method == 'POST':
        form = AddHwForm(request.POST)
        if form.is_valid():
            #pulling form data
            hw_class = form.cleaned_data['hw_class']
            hw_title = form.cleaned_data['hw_title']
            due_date = form.cleaned_data['due_date']
            priority = form.cleaned_data['priority']
            notes = form.cleaned_data['notes']

            #updating model
            updated = Homework.objects.get(hw_user=request.user, id=hw_id)
            updated.hw_class = hw_class
            updated.hw_title = hw_title
            updated.due_date = due_date
            updated.priority = priority
            updated.notes = notes
            updated.save()
            try:
                x=1
            except:
                return render(request, 'hwapp/error.html', {
                    'error': "Unknown error"
                })
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'hwapp/edit_hw.html', {
                'form': form
            })
    else:
        class EditHwForm(ModelForm):
            class Meta:
                model = Homework
                fields = ['hw_class', 'hw_title', 'due_date', 'priority', 'notes']
            def __init__(self, *args, **kwargs):
                super(EditHwForm, self).__init__(*args, **kwargs)
                self.fields['hw_class'].queryset = Class.objects.filter(class_user=request.user)
      
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
            wasteofspace = Class.objects.get(id=class1.id)
            
            for item in dlist:
                wasteofspace.days.add(item)
            wasteofspace.save()
        else:
            return render(request, 'hwapp/addclass.html', {
                'form': form
            })
        return HttpResponseRedirect(reverse('index'))
    else:
        form = AddClassForm()
        return render(request, 'hwapp/addclass.html', {
            'form': form
        })
@login_required(login_url='/login')
def editclass(request, class_id):
    if request.method == "POST":
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
def classhw(request, class_id):
    if class_id == None:
        return HttpResponseRedirect(reverse('index'))
    class1=Class.objects.get(id=class_id, class_user=request.user)
    hwlist = Homework.objects.filter(hw_class=class1, hw_user=request.user)
    if hwlist is None:
        hwlist = f"No Homework for {class1.class_name}"
    return render(request, 'hwapp/classhw.html', {
        'hwlist': hwlist,
        'class1': class1
    })
@login_required(login_url='/login')
def allhw(request):
    user = request.user
    hwlist = Homework.objects.filter(hw_user = user)
    return render(request, 'hwapp/index.html', {
        'hwlist': hwlist
    })