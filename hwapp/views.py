from django.http.response import JsonResponse
from django.shortcuts import render
from django.forms import ModelForm
from django.contrib.auth import login
from .models import EmailTemplate, User, Class, Homework, Preferences, PWReset, AllAuth,Recurring, Day
from django.http import HttpResponseRedirect
import requests
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from ics import Event
from .forms import PreferencesForm, AddClassForm
from dotenv import load_dotenv
import json
import string
import random
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.core.paginator import Paginator
from .email_helper import pw_reset_email, send_email, overdue_check, timezone_helper, text_refresh, email_user,recurring_events
import arrow
from . import helpers

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode

#allow python to access Calendar data model
import sys
sys.path.append("..")
from integrations.models import CalendarEvent, IcsHashVal, NotionData
from integrations.views import notion_auth, refresh_ics, schoology_class, schoology_hw, canvas_class, canvas_hw
from integrations.helper import notion_push, notion_status_push
from external.forms import HelpForm1

load_dotenv()

def matthew_check(user):
    return user.is_superuser
oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)
def sso_login(request):
    return oauth.auth0.authorize_redirect(
        request, request.build_absolute_uri(reverse("callback"))
    )
def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    request.user = token
    e_info = token.get("userinfo")
    a_id = e_info.get('sub')
    try:
        user1 = AllAuth.objects.get(uid=a_id).allauth_user
    except:
        try:
            user1 = User.objects.create_user(e_info.get('nickname'), e_info.get('email'), ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.punctuation) for _ in range(256)))
            user1.save()
        except:
            s=False
            c=1
            while s==False:
                try:
                    user1 = User.objects.create_user(f"{e_info.get('nickname')}{c}", e_info.get('email'), ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.punctuation) for _ in range(256)))
                    user1.save()
                    s = True
                except:
                    c+=1
        a_auth = AllAuth.objects.create(uid=a_id, extra_data = e_info, allauth_user=user1)
        a_auth.save()
    login(request, user1)
    return redirect(request.build_absolute_uri(reverse("index")))
def login_view(request):
    return HttpResponseRedirect('/accounts/auth0/login/')
def home(request):
    return render(request, 'hwapp/homepage.html', {
        'form': HelpForm1()
    })
def sso_logout(request):
    request.session.clear()
    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )

@login_required(login_url='/home')
def index(request):
    #index feature
    page_size = request.GET.get('page_size')
    if not page_size:
        page_size = 10
    if not request.GET.get('class'):
        hwlist = Homework.objects.filter(hw_user = request.user, completed=False, archive=False).order_by('due_date', 'hw_class__period', 'priority')
        class1 = False
        if request.GET.get('start') or request.GET.get('end'):
            hwlist = Homework.objects.filter(hw_user = request.user, completed=False, archive=False, due_date__range = [request.GET.get('start'), request.GET.get('end')]).order_by('due_date', 'hw_class__period', 'priority')
    else:
        try:
            class1 = Class.objects.get(class_user=request.user, id=request.GET.get('class'), archived = False)
        except:
            return JsonResponse({
                "message": "Access Denied"
            }, status=403)
        hwlist = Homework.objects.filter(hw_user = request.user, completed=False, hw_class=class1).order_by('due_date', 'hw_class__period', 'priority')
        if request.GET.get('start') or request.GET.get('end'):
            hwlist = Homework.objects.filter(hw_user = request.user, completed=False, hw_class=class1).order_by('due_date', 'hw_class__period', 'priority')
        else:
            hwlist = Homework.objects.filter(hw_user = request.user, completed=False, hw_class=class1).order_by('due_date', 'hw_class__period', 'priority')
    # else:
    #     pass
    # if not request.GET.get('end'):
    #     pass
    # else:
    #     pass
    h = Paginator(hwlist, page_size)
    page_number = request.GET.get('page')
    if not page_number:
        page_number=1
    page_obj = h.get_page(page_number)
    class_list = Class.objects.filter(class_user = request.user, archived = False).order_by('period')
    load_dotenv()
    return render(request, 'hwapp/index.html', {
        'hwlist': page_obj,
        'class_list': class_list,
        'page_obj': page_obj,
        'length': list(h.page_range),
        'website_root': os.environ.get('website_root'),
        'class1': class1
    })


@login_required(login_url='/login')
def classes(request):
    classes = Class.objects.filter(class_user=request.user, archived = False).order_by('period')
    return render(request, 'hwapp/classes.html', {
        'classes': classes
    })

@login_required(login_url='/login')
def addhw(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            data['priority'] = int(data['priority'])
        except:
            data['priority'] = None
        #actual code
        try:
            try:
                hw_class = Class.objects.get(id=data['hw_class'], class_user =request.user, archived=False)
            except:
                return JsonResponse({
                    "message": "error: not authorized",
                    "status": 400
                }, 403)
            data['due_date'] = datetime.strptime(data['due_date'], "%Y-%m-%dT%H:%M")
            try:
                if data['notes'] != None:
                    notes=data['notes']
            except:
                notes=""
            new_hw = Homework(hw_user=request.user, hw_class=hw_class, hw_title=data['hw_title'], due_date=data['due_date'], priority=data['priority'], completed=False, notes=notes)
            new_hw.save()
            date_ics = data['due_date']
            date = date_ics.strftime("%b. %d, %Y, %H:%M")
            #create ICS entry if calendar_output is true:
            try:
                var = Preferences.objects.get(preferences_user=request.user).calendar_output
            except:
                var=False
            if var == True:
                try:
                    utc_val = timezone_helper(u_timezone=Preferences.objects.get(preferences_user=request.user).user_timezone.timezone, u_datetime=data['due_date'])
                except:
                    return JsonResponse({
                        'status': '400',
                        'message': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
                    }, status=400)
                e = Event()
                e.name = data['hw_title']
                e.begin = arrow.get(utc_val)
                e.description = f"Class: {hw_class.class_name}; Notes: {notes}"
                #enter new event into database:
                new_calevent = CalendarEvent(calendar_user = request.user, homework_event=new_hw, ics=e)
                new_calevent.save()
            try:
                notion_push(hw=new_hw, user=request.user)
            except NotionData.DoesNotExist:
                pass
            
            return JsonResponse({
                "message": "Homework added successfully!",
                "status": 201,
                'hw_id': new_hw.id,
                'class_name': new_hw.hw_class.class_name,
                'formatted_date': date
            }, status=201)
        except:
            print(NotionData.objects.get(notion_user=request.user).exists())
            return JsonResponse({
                "message": "An unknown error has occured. Please try again",
                "status": 400,
            }, status=400)
    else:
        try:
            classes = Class.objects.filter(class_user=request.user)
        except:
            return HttpResponseRedirect(reverse('classes'))
        return render(request, 'hwapp/addhw.html', {
            'classes':classes,
            'website_root': os.environ.get('website_root')
        })

@login_required(login_url='/login')
def preferences(request):
    if request.method == 'POST':
        form = PreferencesForm(request.POST) 
        if form.is_valid():
            calendar_output = form.cleaned_data['calendar_output']
            user_timezone = form.cleaned_data['user_timezone']
            try:
                preferences = Preferences.objects.get(preferences_user=request.user)
                preferences.calendar_output = calendar_output      
                preferences.user_timezone = user_timezone    
                preferences.save()
            except:
                new_pref = Preferences(preferences_user=request.user)
                new_pref.save()
            return render(request, 'hwapp/preferences.html', {
                'form': form,
                'message': "Success! Your preferences have been saved."
            })
        else:
            return render(request, 'hwapp/preferences.html', {'form': form})

    else:
        try: 
            preferences = Preferences.objects.get(preferences_user=request.user)
            initial = {
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
    if request.method == 'POST':
        form = json.loads(request.body)
        if form:
            #pulling form data
            try:
                hw_class = Class.objects.get(id=form['hw_class'])
            except:
                return render(request, "hwapp/error.html", {
                    "error": "Access Denied"
                })
            hw_title = form['hw_title']
            due_date = form['due_date']
            priority = form['priority']
            completed = form['completed']
            overdue = form['overdue']
            if form['notes'] != None:
                notes = form['notes']
            else:
                #to prevent django from making this field "None"
                notes = ""
            try:
                #updating model
                updated = Homework.objects.get(hw_user=request.user, id=hw_id)
                updated.hw_class = hw_class
                updated.hw_title = hw_title
                updated.due_date = due_date
                updated.completed = completed
                updated.overdue = overdue
                if priority:
                    updated.priority = priority
                if notes:
                    updated.notes = notes
                updated.save()
            except:
                return render(request, 'hwapp/error.html', {
                    'error': "Access Denied"
                })

            #update ICS:
            if Preferences.objects.get(preferences_user=request.user).calendar_output == True:
                try:
                    utc_val = timezone_helper(u_timezone=Preferences.objects.get(preferences_user=request.user).user_timezone.timezone, u_datetime=datetime.strptime(form['due_date'], "%Y-%m-%dT%H:%M"))
                except:
                    return JsonResponse({
                        'status': '400',
                        'message': 'Please set your timezone <a href="/preferences">here</a> to use this feature'
                    }, status=400)
                e = Event()
                e.name = hw_title
                e.begin = utc_val
                e.description = f"Class: {hw_class.class_name}"
                if notes:
                    e.description += f"; {notes}"

                #pull ICS:
                try:
                    edit_event = CalendarEvent.objects.get(calendar_user = request.user, homework_event=updated)
                except:
                    edit_event = CalendarEvent()
                    edit_event.calendar_user = request.user
                    edit_event.homework_event = updated
                edit_event.ics = e
                edit_event.save()
            return JsonResponse({
                'status': 201
            }, status=201)
        else:
            #reload json form and return it to the user with error message
            try:
                hw = Homework.objects.get(hw_user=request.user, id=hw_id)
            except:
                return JsonResponse({'message': 'Access Denied', 'status': '403'}, status=403)
            return JsonResponse({
                'message': 'An error has occured. Please check all your fields and try again.',
                'status': '400'
            }, status=400)
    else:
        #render json/ajax form
        try:
            hw = Homework.objects.get(hw_user=request.user, id=hw_id)
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'Access Denied'
            })

        return render(request, 'hwapp/edit_hw.html', {
            'hw_id': hw_id,
            'classes': Class.objects.filter(class_user=request.user, archived=False),
            'hw': hw,
            'website_root': os.environ.get("website_root"),
            'due_date': hw.due_date.strftime("%Y-%m-%dT%H:%M")
        }) 

@login_required(login_url='/login')
def addclass(request):
    if request.method == 'POST':
        form = AddClassForm(request.POST)
        if form.is_valid():
            user = request.user
            class_name = form.cleaned_data['class_name']
            period = form.cleaned_data['period']
            time = form.cleaned_data['time']
            class1 = Class(class_user=user, class_name=class_name, period=period, time=time)
            class1.save()
            newclass = Class.objects.get(id=class1.id)
      
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
    if request.method == "POST":
        form = AddClassForm(request.POST)
        if form.is_valid():
            class_name = form.cleaned_data['class_name']
            period = form.cleaned_data['period']
            time = form.cleaned_data['time']
            dlist=[]
            try:
                class1 = Class.objects.get(class_user=request.user, id=class_id)
                class1.class_name=class_name
                class1.period=period
                class1.time=time
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
        }
        form = AddClassForm(initial=initial)
        return render(request, 'hwapp/editclass.html', {
            'form': form,
            'class_id': class_id
        })

@login_required(login_url='/login')
def allhw(request):
    page_size = request.GET.get('page_size')
    if not page_size:
        page_size = 10
    if not request.GET.get('class'):
        hwlist = Homework.objects.filter(hw_user = request.user).order_by('due_date', 'hw_class__period', 'priority')
        class1 = False
        if request.GET.get('start') or request.GET.get('end'):
            hwlist = Homework.objects.filter(hw_user = request.user, due_date__range = [request.GET.get('start'), request.GET.get('end')]).order_by('due_date', 'hw_class__period', 'priority')
    else:
        try:
            class1 = Class.objects.get(class_user=request.user, id=request.GET.get('class'))
        except:
            return JsonResponse({
                "message": "Access Denied"
            }, status=403)
        hwlist = Homework.objects.filter(hw_user = request.user, hw_class=class1).order_by('due_date', 'hw_class__period', 'priority')
        if request.GET.get('start') or request.GET.get('end'):
            hwlist = Homework.objects.filter(hw_user = request.user, hw_class=class1).order_by('due_date', 'hw_class__period', 'priority')
        else:
            hwlist = Homework.objects.filter(hw_user = request.user, hw_class=class1).order_by('due_date', 'hw_class__period', 'priority')
    # else:
    #     pass
    # if not request.GET.get('end'):
    #     pass
    # else:
    #     pass
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
        'length': list(h.page_range),
        'website_root': os.environ.get('website_root'),
        'class1': class1,
        'completed': True
    })

def about(request):
    template = EmailTemplate.objects.get(id=4)
    return render(request, 'hwapp/aboutme.html', {
        'template': template.template_body
    })
@login_required(login_url='/login')
def profile(request):

    if request.method == 'POST':
        request.user.first_name = request.POST['first_name']
        request.user.last_name = request.POST['last_name']
        request.user.email = request.POST['email']
        request.user.save()
        return render(request, 'hwapp/profile.html', {
            'message': "Success!",
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
    else:
        initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        }
        return render(request, 'hwapp/profile.html', {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
        })
@login_required(login_url='/login')
def calendar(request):
    if request.method == "GET":
        #pull hash val if it exists or create a new one
        try:
            hash_val = IcsHashVal.objects.get(hash_user=request.user, hash_type='default')
        except:
            hash_val = IcsHashVal(hash_val = abs(hash(str(request.user.id))), hash_user=request.user, hash_type='default')
            hash_val.save()
        ics_link = f"{os.environ.get('website_root')}/integrations/export/{request.user.id}/{hash_val.hash_val}"
        try:
            n = NotionData.objects.get(notion_user=request.user)
            n_ics_link = f"{os.environ.get('website_root')}/integrations/notionexport/{request.user.id}/{hash_val.hash_val}"
        except:
            n_ics_link = False
        return render(request, 'hwapp/calendar.html', {
            'ics_link': ics_link,
            'n_ics_link': n_ics_link
        })
    else:
        return JsonResponse({'error': 'method not supported'}, status=405)


@login_required(login_url='/login')
def completion(request, hw_id):
    if request.method == "POST":
        data = json.loads(request.body)
        hw_id=data['hw_id']
        hw_instance = Homework.objects.get(hw_user=request.user, id=hw_id)
        if str(data['completion']) == str(True):
            try:
                notion_status_push(hw=hw_instance, user=request.user, status='Not Started')
            except NotionData.DoesNotExist:
                pass
            update = False
        else:
            try:
                notion_status_push(hw=hw_instance, user=request.user, status='Completed')
            except NotionData.DoesNotExist:
                pass
            update = True
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

@login_required(login_url='/login')
def getclasstime(request, class_id):
    if request.method == "GET":
        try:
            class_instance = Class.objects.get(id=class_id, class_user=request.user)
        except:
            return JsonResponse({
                'message': 'Access Denied',
                'status': 403,
            }, message=403)
        date_def = datetime.now()
        if class_instance.time is None:
            return JsonResponse({
                'message': 'This class does not have a class time',
                'status': 404
            }, status=404)
        dt = datetime.combine(date_def, class_instance.time)
        dt = dt.strftime('%Y-%m-%dT%H:%M')
        return JsonResponse({
            'class_time': dt,
            'status': 200,
        }, status=200)
    else:
        return JsonResponse({
            'message': 'method not allowed',
            'status': 405,
        }, status=405)

def reset_password(request):
    load_dotenv()
    if request.method == "GET":
        hash_val = request.GET.get('hash')
        if hash_val == None:
            return render(request, 'hwapp/reset_password.html')
        else:
            #check hash against database
            try:
                hash_val_db = PWReset.objects.get(hash_val=hash_val, active=True)
            except:
                return render(request, 'hwapp/error.html', {
                    'error': 'Invalid link. Please request a new one <a href="/reset_password">here</a>'
                })
            if hash_val_db.expires < timezone.now():
                return render(request, 'hwapp/error.html', {
                    'error': 'This link has expired. Please request a new one <a href="/reset_password">here</a>'
                })
            else:
                return render(request, 'hwapp/newpw.html', {
                    'hash_val': hash_val
                })
            
    if request.method == "POST":
            try:
                request.POST['form_email']
                try:
                    user = User.objects.get(email = request.POST['form_email'])
                    hash_val = hash(f"{user.username}{user.id}{datetime.now()}")
                    now_plus_10 = timezone.now() + timedelta(minutes = 45)
                    PWReset.objects.create(reset_user=user, hash_val=hash_val, expires=now_plus_10)
                    pw_reset_email(user=user, hash_val=hash_val, expires=now_plus_10, email=user.email)
                    website_root = os.environ.get('website_root')
                    return render(request, 'hwapp/reset_password.html', {
                        'success': f'If your email is recognized in our system, you will receive an email to reset your password. Please be sure to check your spam folder, and the link will expire in 45 minutes. If you do not receive an email within 10 minutes, there is no account associated with that email, but you may create an account at <a href="https://{website_root}/register">this link</a>. Please visit our <a href="https://itsm.{website_root}">help center</a> with any questions. Thanks!'
                    })
                except:
                    website_root = os.environ.get('website_root')
                    print(False)
                    return render(request, 'hwapp/reset_password.html', {
                        'success': f'If your email is recognized in our system, you will receive an email to reset your password. Please be sure to check your spam folder, and the link will expire in 45 minutes. If you do not receive an email within 10 minutes, there is no account associated with that email, but you may create an account at <a href="https://{website_root}/register">this link</a>. Please visit our <a href="https://itsm.{website_root}">help center</a> with any questions. Thanks!'
                    })
            except:
                try:
                    pw = request.POST['pw']
                    confirm = request.POST['pw_confirmation']
                    hash_val=request.POST['hash_val']
                    #check PW confirmation
                    if pw != confirm:
                        return render(request, 'hwapp/newpw.html', {
                            'message': 'Please make sure that your passwords match',
                            'hash_val': request.POST['hash_val']
                        })
                    else:
                        #check hash again
                        try:
                            hash_val_db = PWReset.objects.get(hash_val=hash_val)
                        except:
                            return render(request, 'hwapp/error.html', {
                                'error': 'Invalid link. Please request a new one <a href="/reset_password">here</a>'
                            })
                        if hash_val_db.expires < timezone.now():
                            return render(request, 'hwapp/error.html', {
                                'error': 'This link has expired. Please request a new one <a href="/reset_password">here</a>'
                            })
                        #check PW strength:
                        if helpers.check_pw(pw) != True:
                            return render(request, 'hwapp/newpw.html', {
                                'message': helpers.check_pw(pw),
                                'hash_val': request.POST['hash_val']
                            })                            
                        
                        else:
                            u = hash_val_db.reset_user
                            u.set_password(pw)
                            u.save()
                            #invalidate link
                            hash_val_db.expires=timezone.now()
                            hash_val_db.active = False
                            return render(request, 'hwapp/newpw.html', {
                                'success': 'Success! Your password has been updated. Please click <a href="/login">here</a> to login.',
                                'hash_val': request.POST['hash_val']
                        })

                except:
                    return HttpResponseRedirect(reverse('index'))

@user_passes_test(matthew_check, login_url='/login')
def admin_console(request):
    if request.method == "POST":
        json_val = json.loads(request.body)
        if json_val['function'] == "refresh":
            send_email("Daily")
            return JsonResponse({"status": 200}, status=200)
        elif json_val['function'] == "overdue":
            overdue_check()
            return JsonResponse({"status": 200}, status=200)
        elif json_val['function'] == 'ics_refresh':
            refresh_ics()
            return JsonResponse({"status": 200}, status=200)
        elif json_val['function'] == 'send_text':
            text_refresh()
            return JsonResponse({"status": 200}, status=200)
        elif json_val['function'] == 'schoology_class':
            schoology_class(request) 
            return JsonResponse({"status": 200}, status=200)
        elif json_val['function'] == 'schoology_hw':
            schoology_hw(request) 
            return JsonResponse({"status": 200}, status=200)    
        elif json_val['function'] == 'canvas_class':
            canvas_class(request) 
            return JsonResponse({"status": 200}, status=200)     
        elif json_val['function'] == 'canvas_hw':
            canvas_hw(request) 
            return JsonResponse({"status": 200}, status=200)     
        elif json_val['function'] == 'recurring_events':
            recurring_events()                
            return JsonResponse({"status": 200}, status=200) 
    elif request.method == "GET":
        return render(request, "hwapp/admin_console.html")
    else:
        return JsonResponse({"error": "method not allowed"}, status=405)

@login_required(login_url='/login')
def new_user_view(request):
    template = EmailTemplate.objects.get(id=5)
    return render(request, 'hwapp/newuser.html', {
        'template': template.template_body
    })
@login_required(login_url='/login')
def homework_entry(request, hw_id):
    try:
        hw = Homework.objects.get(hw_user=request.user, id=hw_id)
        return render(request, 'hwapp/hw_entry.html', {
            'hw': hw
        })
    except:
        return render(request, 'hwapp/error.html', {
            'error': 'Homework matching query does not exist. Please check you link and try again'
        })

@user_passes_test(matthew_check, login_url='/login')
def fivehundrederror(request):
    pass
@user_passes_test(matthew_check, login_url='/login')
def email_template_editor(request):
    if request.method == 'GET':
        template_id = request.GET.get('template_id')
        type1 = request.GET.get('type')
        if template_id == None:
            if type1 is not None:
                return render(request, 'hwapp/template_selector.html', {
                    'templates': EmailTemplate.objects.filter(type=type1)
                })
            else:
                return render(request, 'hwapp/template_selector.html', {
                    'templates': EmailTemplate.objects.all()
                })               
        return render(request, 'hwapp/email_templates.html', {
            'email_template': EmailTemplate.objects.get(id=template_id),
            'website_root': os.environ.get('website_root')
        })
    if request.method == 'POST':
        template_id = request.GET.get('template_id')
        if template_id == None:
            return render(request, 'hwapp/error.html', {
                'error': 'No template selected'
            })
        else:
            to_edit = EmailTemplate.objects.get(id=template_id)
            form_val = request.POST['template_body']
            to_edit.template_body = form_val
            to_edit.version_id = request.POST['version_id']
            to_edit.type = request.POST['type']
            to_edit.save()
            return render(request, 'hwapp/email_templates.html', {
                'message': 'Template Successfully Saved',
                'email_template': EmailTemplate.objects.get(id=template_id),
                'website_root': os.environ.get('website_root')
            })

@user_passes_test(matthew_check, login_url='/login')
def experience(request):
    return render(request, 'hwapp/experience_manager.html')

@user_passes_test(matthew_check, login_url='/login')
def email_all(request):
    if request.method == 'POST':
        content = request.POST['template_body']
        subject = request.POST['subject']
        email_list = []
        for user in User.objects.all():
            email_list.append(user.email)
        email_user(emails = email_list, subject=subject, content=content)
        return render(request, 'hwapp/success.html', {
            'message': 'email sent successfully'
        })
    else:
        return render(request, 'hwapp/email_all.html')
def privacy(request):
    return render(request, 'hwapp/privacy.html')
def terms(request):
    return render(request, 'hwapp/terms.html')
@login_required(redirect_field_name='/login')
def version_manager(request, version_id):
    try:
        template = EmailTemplate.objects.get(version_id=version_id, type='version')
    except:
        return render(request, 'hwapp/error.html', {
            'error': 'invalid version id'
        }) 
    return render(request, 'hwapp/template_render.html', {
        'template': template.template_body,
        'id': version_id,
        'header': f'HW App: Version {version_id}'
    })
@user_passes_test(matthew_check)
def add_template(request):
    if request.method =='GET':
        return render(request, 'hwapp/email_templates.html')
    elif request.method == 'POST':
        to_edit = EmailTemplate.objects.create(template_body=request.POST['template_body'], template_name=request.POST['template_name'], version_id=request.POST['version_id'], type=request.POST['type'])
        to_edit.save()
        return render(request, 'hwapp/email_templates.html', {
            'message': 'Template Successfully Saved',
            'email_template': to_edit,
            'website_root': os.environ.get('website_root')
        })
@login_required(login_url='/login')
def recurring(request):
    try:
        recurrings = Recurring.objects.filter(user=request.user)
        print(recurrings)
        return render(request, 'hwapp/recurring.html', {
            'recurrings': recurrings,
            })
    except:
        return render(request, 'hwapp/recurring.html')

@login_required(login_url='/login')
def recurring_add_edit(request):
    if request.method == 'POST':
        try:
            #find existing record
            r = Recurring.objects.get(user=request.user, id=request.GET.get('recurring_id'))
        except:
            #Create a new one if not found
            r = Recurring(user=request.user)
        r.hw_title = request.POST['hw_title']
        try:
            c = Class.objects.get(id=request.POST['hw_class'], class_user=request.user)
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'Unauthorized'
            })
        r.hw_class = c
        r.hw_title = request.POST['hw_title']   
        r.time = request.POST['due_date']
        r.notes = request.POST['notes']
        r.save()
        days = request.POST.getlist('days')
        print(days)
        r.days.clear()
        for day in days:
            r.days.add(day) 
        r.save()
        return render(request, 'hwapp/success.html', {
            'message':'Assignment updated successfully. Click <a href="/recurring">here</a> to return to the recurring assignments'
        })
    else:
        if request.GET.get('recurring_id'):
            try:
                recurring = Recurring.objects.get(user=request.user, id=request.GET.get('recurring_id'))
            except:
                return render(request, 'hwapp/error.html', {
                    'error': 'Unauthorized'
                })
            return render(request, 'hwapp/recurringedit.html',{
                'recurring': recurring,
                'classes':Class.objects.filter(class_user=request.user, archived=False),
                'days': Day.objects.all(),
                'time1': recurring.time.strftime("%H:%M:%S")
            })
        else:
            return render(request, 'hwapp/recurringedit.html', {
                'classes':Class.objects.filter(class_user=request.user, archived=False),
                'days': Day.objects.all()
            })
def archiveclass(request, id):
    try:
        c = Class.objects.get(class_user=request.user, id=id)
        c.archived = True
        c.save()
        h = Homework.objects.filter(hw_class = c, hw_user=request.user)
        for hw in h:
            hw.archive = True
            hw.save()
    except:
        return JsonResponse({'error': 'Access Denied', 'status': 400}, status=400)