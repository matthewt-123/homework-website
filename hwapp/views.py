from django.http.response import JsonResponse, HttpResponse, Http404
from django.shortcuts import redirect, render, redirect
from django.contrib.auth import login
from .models import EmailTemplate, User, Class, Homework, Preferences, AllAuth, Timezone, PasteBin, FileBin
from django.http import HttpResponseRedirect
import requests
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
import os
from .forms import AddClassForm
from dotenv import load_dotenv
import json
import string
import random
from datetime import datetime
from django.core.paginator import Paginator
from .email_helper import send_email, email_user
from django.views.decorators.csrf import csrf_exempt

from authlib.integrations.django_client import OAuth
from django.conf import settings
from urllib.parse import quote_plus, urlencode

#allow python to access Calendar data model
import sys
sys.path.append("..")
from integrations.models import IcsHashVal, NotionData, Log
from integrations.views import schoology_class, schoology_hw, canvas_class, canvas_hw
from integrations.helper import notion_push, notion_pull
from external.forms import HelpForm1
from external.models import HelpForm
from mywebsite.settings import DEBUG
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
    if request.GET.get('error'):
        #getting access token
        url = "https://dev-q8234yaa.us.auth0.com/oauth/token"
        data = "{\"client_id\":\"OMlu360UoElELWmLxf4heWZOSJWmL8yv\",\"client_secret\":\"XQvngJGK_3SUjuaEuzzJ3jX1WGrMxgcwJfcT6nPj6Sx5-bOzOORkfQtGWAnyEEmw\",\"audience\":\"https://dev-q8234yaa.us.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"
        headers = { 'content-type': "application/json" }
        response = requests.post(url, data=data, headers=headers)
        uid = request.GET.get('error_description')
        url = f"https://dev-q8234yaa.us.auth0.com/api/v2/jobs/verification-email"
        data = {
            "user_id": uid,
        }
        headers = { 'content-type': "application/json", "Authorization": f"Bearer {json.loads(response.text)['access_token']}" }
        response = requests.post(url, data = json.dumps(data), headers=headers)
        extra_msg = "One more step to create your profile! Please check your email for a verification link"
        request.session.clear()

        return render(request, 'hwapp/success.html', {
            "message": extra_msg
        })
    else:
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
    extra_message = False
    if not page_size:
        page_size = 10 #default page size
    #date range filter
    if request.GET.get('start') or request.GET.get('end'):
        if not request.GET.get('start'): #if there is no start dt(only end dt), filter by it
            hwlist = Homework.objects.filter(hw_user = request.user, due_date__lte = request.GET.get('end')).order_by('due_date', 'hw_class__period', 'priority')
        elif not request.GET.get('end'): #if no end date, filter by start dt
            hwlist = Homework.objects.filter(hw_user = request.user, due_date__gte = request.GET.get('start')).order_by('due_date', 'hw_class__period', 'priority')
        else: #filter by specific range
            hwlist = Homework.objects.filter(hw_user = request.user, due_date__range = [request.GET.get('start'), request.GET.get('end')]).order_by('due_date', 'hw_class__period', 'priority')
    else:
        hwlist = Homework.objects.filter(hw_user = request.user).order_by('due_date', 'hw_class__period', 'priority')
    #class filter
    if request.GET.get('class'):
        try:
            class1 = Class.objects.get(class_user=request.user, id=request.GET.get('class'))
            hwlist = hwlist.filter(hw_class = class1, hw_class__archived = False)
        except:
            return JsonResponse({
                "message": "Access Denied"
            }, status=403)
        if class1.archived == True:
            return render(request, 'hwapp/error.html', {
                "error": "Please unarchive your class to view homework"
            })
    else:
        class1 = False
    
    #active filter
    if request.GET.get('inactive') == 'true':
        hwlist = hwlist.filter(completed=True, archive=False, hw_class__archived=False)
    else:
        hwlist = hwlist.filter(completed=False, archive=False, hw_class__archived=False)
    #assignment filter
    if request.GET.get('assignment'):
        tmp = []
        q = str(request.GET.get('assignment')).lower()
        for hw in hwlist:
            if q in hw.hw_title.lower():
                tmp.append(hw)
        hwlist = tmp

    h = Paginator(hwlist, page_size)
    page_number = request.GET.get('page')
    if not page_number:
        page_number=1
    page_obj = h.get_page(page_number)
    class_list = Class.objects.filter(class_user = request.user, archived = False).order_by('period')
    try:
        n_status = NotionData.objects.get(notion_user=request.user, tag="homework").error
    except:
        n_status = False
    load_dotenv()
    return render(request, 'hwapp/index.html', {
        'hwlist': page_obj,
        'class_list': class_list,
        'page_obj': page_obj,
        'length': list(h.page_range),
        'website_root': os.environ.get('website_root'),
        'class1': class1,
        'extra_message': extra_message,
        'n_status': n_status,
        'debug': DEBUG
    })


@login_required(login_url='/login')
def classes(request):
    if str(request.GET.get("archived")) == "true":
        classes = Class.objects.filter(class_user=request.user, archived = True).order_by('period')
        archive=True
    else:
        classes = Class.objects.filter(class_user=request.user, archived = False).order_by('period')
        archive=False
    return render(request, 'hwapp/classes.html', {
        'classes': classes,
        'archived': archive
    })

@login_required(login_url='/login')
def addhw(request):
    if request.method == 'POST':
        data = json.loads(request.body)
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
            new_hw = Homework(hw_user=request.user, hw_class=hw_class, hw_title=data['hw_title'], due_date=data['due_date'], completed=False, notes=notes)
            new_hw.save()
            date_ics = data['due_date']
            date = date_ics.strftime("%b. %d, %Y, %H:%M")
            #notion push

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
            return JsonResponse({
                "message": "An unknown error has occured. Please try again",
                "status": 400,
            }, status=400)
    else:
        try:
            classes = Class.objects.filter(class_user=request.user, archived=False)
        except:
            return HttpResponseRedirect(reverse('classes'))
        return render(request, 'hwapp/addhw.html', {
            'classes':classes,
            'website_root': os.environ.get('website_root')
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
            overdue = form['overdue']
            completed = form['completed']
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
                updated.overdue = overdue
                updated.completed = completed
                if notes:
                    updated.notes = notes
                updated.save()
            except:
                return render(request, 'hwapp/error.html', {
                    'error': "Access Denied"
                })

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
def about(request):
    template = EmailTemplate.objects.get(id=4)
    return render(request, 'hwapp/template_render.html', {
        'template': template,
        'header': "About Me"
    })
@login_required(login_url='/login')
def profile(request):
    if request.method == 'POST':
        request.user.first_name = request.POST['first_name']
        request.user.last_name = request.POST['last_name']
        extra_msg = ""
        #update email
        if request.user.email != request.POST['email']:
            #getting access token
            url = "https://dev-q8234yaa.us.auth0.com/oauth/token"
            data = "{\"client_id\":\"OMlu360UoElELWmLxf4heWZOSJWmL8yv\",\"client_secret\":\"XQvngJGK_3SUjuaEuzzJ3jX1WGrMxgcwJfcT6nPj6Sx5-bOzOORkfQtGWAnyEEmw\",\"audience\":\"https://dev-q8234yaa.us.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"
            headers = { 'content-type': "application/json" }
            response = requests.post(url, data=data, headers=headers)
            #checking duplicate
            url = f"https://dev-q8234yaa.us.auth0.com/api/v2/users-by-email?email={request.POST['email']}"
            headers = { 'content-type': "application/json", "Authorization": f"Bearer {json.loads(response.text)['access_token']}" }
            data = {
                "email": request.POST['email']
            }
            response = requests.get(url, headers=headers)
            if not json.loads(response.text):
                uid = AllAuth.objects.get(allauth_user=request.user).uid
                #updating user
                url = f"https://dev-q8234yaa.us.auth0.com/api/v2/users/{uid}"
                data = {
                    "connection": "Username-Password-Authentication",
                    "email": request.POST['email']
                }
                response = requests.patch(url, data=json.dumps(data), headers=headers)
                url = f"https://dev-q8234yaa.us.auth0.com/api/v2/jobs/verification-email"
                data = {
                    "user_id": uid,
                }
                response = requests.post(url, data = json.dumps(data), headers=headers)
                extra_msg = "Please check your email for a verification link"
            else:
                return render(request, 'hwapp/profile.html', {
                    'error': "Invalid email",
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email,
                })   
        request.user.email = request.POST['email']
        request.user.save()

        #updating timezone:
        tz_id = request.POST['timezone']
        try:
            new_tz = Timezone.objects.get(id=tz_id)
        except:
            return render(request, 'hwapp/error.html', {
                'error': "Invalid Timezone. Please try again"
            })
        preference = Preferences.objects.get(preferences_user=request.user)
        preference.user_timezone = new_tz
        preference.save()
        return render(request, 'hwapp/profile.html', {
            'message': f"Success! {extra_msg}",
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'timezones': Timezone.objects.all(),
            'selected': new_tz.id
        })
    else:
        url = "https://dev-q8234yaa.us.auth0.com/oauth/token"
        data = "{\"client_id\":\"OMlu360UoElELWmLxf4heWZOSJWmL8yv\",\"client_secret\":\"XQvngJGK_3SUjuaEuzzJ3jX1WGrMxgcwJfcT6nPj6Sx5-bOzOORkfQtGWAnyEEmw\",\"audience\":\"https://dev-q8234yaa.us.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"
        headers = { 'content-type': "application/json" }
        response = requests.post(url, data=data, headers=headers)
        try: 
            selected = Preferences.objects.get(preferences_user=request.user).user_timezone
        except:
            selected = -1
        return render(request, 'hwapp/profile.html', {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'selected': selected,
                'timezones': Timezone.objects.all()
            })
@login_required(login_url='/login')  
def change_password(request):
    if request.method == "PATCH":
        headers = { 'content-type': "application/json" }
        url = "https://dev-q8234yaa.us.auth0.com/dbconnections/change_password"
        data = {
            "email": request.user.email,
            "connection": "Username-Password-Authentication"
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        if str(response) == "<Response [200]>":
            return JsonResponse({"message": "password link sent to your email", "status": 200}, status=200)
        else:
            return JsonResponse({"message": "an error has occurred", "status": 500}, status=500)
    else:
        return JsonResponse({"error": "not authorized"}, status=400)
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
        s = NotionData.objects.filter(notion_user=request.user)
        z = [each.tag for each in s]
        if "homework" in z:
            n_ics_link = f"{os.environ.get('website_root')}/integrations/notionexport/{request.user.id}/{hash_val.hash_val}/homework"
        else:
            n_ics_link = False
        if "personal" in z:
            p_ics_link = f"{os.environ.get('website_root')}/integrations/notionexport/{request.user.id}/{hash_val.hash_val}/personal"
            return render(request, 'hwapp/calendar.html', {
                'ics_link': ics_link,
                'n_ics_link': n_ics_link,
                'p_ics_link': p_ics_link
            })
        return render(request, 'hwapp/calendar.html', {
            'ics_link': ics_link,
            'n_ics_link': n_ics_link
        })
    else:
        return JsonResponse({'error': 'method not supported'}, status=405)


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

@user_passes_test(matthew_check, login_url='/login')
def admin_console(request):
    if request.method == "POST":
        json_val = json.loads(request.body)
        if json_val['function'] == "refresh":
            response = send_email()
            if response:
                message = send_email()
                if str(message['status']) == "Succeeded":
                    error = False
                else:
                    error = True
            else: #no emails sent
                error = False
                message = None
            Log.objects.create(user=request.user, date=datetime.now(), message=message, error=error, log_type="Refresh", ip_address = request.META.get("REMOTE_ADDR"))
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
        elif json_val['function'] == 'notion_pull':
            notion_pull() 
            return JsonResponse({"status": 200}, status=200) 
        else:
            return JsonResponse({"status": 404}, status=404)
    elif request.method == "GET":
        return render(request, "hwapp/admin_console.html")
    else:
        return JsonResponse({"error": "method not allowed"}, status=405)

@login_required(login_url='/login')
def new_user_view(request):
    template = EmailTemplate.objects.get(id=5)
    return render(request, 'hwapp/template_render.html', {
        'template': template,
        'header': 'Welcome to the Homework App!'
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
def email_template_editor(request):
    if request.method == 'GET':
        template_id = request.GET.get('template_id')
        type1 = request.GET.get('type')
        if template_id == None:
            #not editing specific template
            if type1 is not None:
                #and a type is specified, return filtered selector
                return render(request, 'hwapp/template_selector.html', {
                    'templates': EmailTemplate.objects.filter(type=type1),
                    'type': type1,
                })
            else:
                #and type not specified, return all templates
                return render(request, 'hwapp/template_selector.html', {
                    'templates': EmailTemplate.objects.all(),
                    'type': ""
                })         
        #if editing specific template      
        try:
            template = EmailTemplate.objects.get(id=template_id)
        except:
            return render(request, 'hwapp/error.html', {
                'error': "Not a valid email template"
            })
        return render(request, 'hwapp/email_templates.html', {
            'email_template': template,
            'website_root': os.environ.get('website_root'),
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
        'template': template,
        'header': f'HW App: Version {version_id}'
    })
@user_passes_test(matthew_check)
def add_template(request):
    if request.method =='GET':
        type1 = request.GET.get('type')
        if type1:
            version_id =  EmailTemplate.objects.filter(type=type1).order_by('id').last().version_id + 1
        else:
            version_id = 0

        print(type1)
        return render(request, 'hwapp/email_templates.html', {
            'type': type1,
            'version_id': version_id
        })
    elif request.method == 'POST':
        to_edit = EmailTemplate.objects.create(template_body=request.POST['template_body'], template_name=request.POST['template_name'], version_id=request.POST['version_id'], type=request.POST['type'])
        to_edit.save()
        return render(request, 'hwapp/email_templates.html', {
            'message': 'Template Successfully Saved',
            'email_template': to_edit,
            'website_root': os.environ.get('website_root')
        })
@login_required()
def archiveclass(request, id):
    try:
        c = Class.objects.get(class_user=request.user, id=id)
        if c.archived == False:
            c.archived = True
            c.save()
            h = Homework.objects.filter(hw_class = c, hw_user=request.user)
            for hw in h:
                hw.archive = True
                hw.save()
        else:
            c.archived = False
            c.save()
            h = Homework.objects.filter(hw_class = c, hw_user=request.user)
            for hw in h:
                hw.archive = False
                hw.save()            
        return JsonResponse({'message': 'completed', 'status': 200}, status=204)
    except:
        return JsonResponse({'error': 'Access Denied', 'status': 400}, status=400)
@user_passes_test(matthew_check)
def helpformlist(request):
    if str(request.GET.get('status')).lower() == 'all':
        return render(request, 'hwapp/helpformlist.html', {
            'helpforms': HelpForm.objects.all().order_by('-id')
        })
    else:
        return render(request, 'hwapp/helpformlist.html', {
            'helpforms': HelpForm.objects.filter(parent_form = None).exclude(status="Completed").order_by('-id')
        })        
@user_passes_test(matthew_check)
def helpformview(request, id):
    try:
        helpform = HelpForm.objects.get(id=id, parent_form = None)
        email_history = HelpForm.objects.filter(parent_form=HelpForm.objects.get(id=id))
    except Exception as e:
        print(e)
        return render(request, 'hwapp/error.html', {
            'error': f'no help form matching id {id} found'
        })
    if request.method == 'GET':
        return render(request, 'hwapp/helpformview.html', {
            'helpform': helpform,
            'email_history': email_history
        })
    else:
        try:
            helpform = HelpForm.objects.get(id=id, parent_form=None)
            tracking_id = round(46789234*(int(helpform.id) + 34952)/234567)
            tracking_info = f"----------------------------------------------------------------------------------------------------------------------------------------------<div style='display:none;color:white;font-size:0%'>@@@@tracking_id={tracking_id}@@@@</div>"
            email_user(email=helpform.email, content=f"{request.POST['message']}{tracking_info}", subject=f"[matthewtsai.tech] Help Form: {request.POST['subject']}", recipient_name=helpform.first_name)
            helpform.status = "Completed"
            helpform.save()
            new_response = HelpForm(parent_form=helpform, first_name=request.user.first_name, last_name = request.user.last_name, email = "support@email.matthewtsai.tech", received=datetime.now(), subject=f"[matthewtsai.tech] Help Form: {request.POST['subject']}", message=request.POST['message'], status="Completed")
            new_response.save()
            return render(request, 'hwapp/success.html', {
                'message': f"Message sent successfully. Click <a href='/helpformlist'>here</a> to return to the help form listing or <a href='/helpformview/{helpform.id}'>here</a> to return to your previous page"
            })
        except Exception as e:
            print(e)
            return JsonResponse({"error": "form not found"}, status=404)
@login_required(login_url="/login")
def csv_export_template(request):
    if DEBUG:
        return render(request, "hwapp/csv_export.html", {
            "class_list": Class.objects.filter(class_user=request.user),
            'export_link': f"http://{os.environ.get('WEBSITE_ROOT')}/integrations/csv_export"
        })
    else:
        return render(request, "hwapp/csv_export.html", {
            "class_list": Class.objects.filter(class_user=request.user),
            'export_link': f"https://{os.environ.get('WEBSITE_ROOT')}/integrations/csv_export"
        })
@login_required(login_url="/login")
def pastebin(request):
    if request.method == "POST":
        try:
            p = PasteBin.objects.get(user=request.user)
        except:
            p = PasteBin.objects.create(user=request.user)
        p.content = request.POST['content']
        p.save()
        return render(request, 'hwapp/pastebin.html', {
            'p': p
        })
    else:
        try:
            p = PasteBin.objects.get(user=request.user)
        except:
            p = PasteBin.objects.create(user=request.user)
        return render(request, 'hwapp/pastebin.html', {
            'p': p
        })
def pastebin_html(request):
    try:
        assert(request.headers['login'] == "7jo4RcqewFnb2hu61QgF")
        p = PasteBin.objects.get(user=User.objects.get(username="admin"))
        try:
            d = request.headers['link']
            p.content = d
            p.save()
        except:
            pass
        return HttpResponse(p.content)
    except:
        raise Http404()

@login_required(login_url="/login")
def filebin(request):
    if request.method == "POST":
        try:
            p = FileBin.objects.get(user=request.user)
        except:
            p = FileBin.objects.create(user=request.user)
            
        p.hash_val = hash(f"{datetime.now()}:{p.user}")
        if os.path.exists(p.file.path):
            os.remove(p.file.path)
        p.file = request.FILES['content']
        p.save()
        name = p.file.name.rsplit('/', 1)[-1]
        return render(request, 'hwapp/filebin.html', {
            'p': p,
            'name': name
        })
    else:
        try:
            p = FileBin.objects.get(user=request.user)
        except:
            p = FileBin.objects.create(user=request.user)
        name = p.file.name.rsplit('/', 1)[-1]
        return render(request, 'hwapp/filebin.html', {
            'p': p,
            'name': name
        })
@csrf_exempt
def filebin_html(request):
    try:
        assert(request.headers['login'] == "7jo4RcqewFnb2hu61QgF")
        p = FileBin.objects.get(user=User.objects.get(username="admin"))
        if os.path.exists(p.file.path):
            os.remove(p.file.path)
        try:
            d = request.FILES['file']
            p.file = d
            p.file.name = request.FILES['file'].name
            p.save()
        except:
            pass
        return HttpResponse(p.file.url)
    except:
        raise Http404()

@user_passes_test(matthew_check)
def custom_email(request):
    if request.method == "GET":
        return render(request, 'hwapp/email_user.html')
    else:
        email_user(email=request.POST['recipient'], content=request.POST['message'], subject=f"{request.POST['subject']}", recipient_name=request.POST['name'])
        return render(request, 'hwapp/success.html', {
            "message": "Email sent successfully. Click <a href='/email'>here</a> to return to the previous page"
        })
@login_required(login_url="/login")
def page_manager(request, page_id):
    try:
        template = EmailTemplate.objects.get(version_id=page_id, type='custom')
    except:
        return render(request, 'hwapp/error.html', {
            'error': 'Invalid page id'
        }) 
    return render(request, 'hwapp/template_render.html', {
        'template': template,
        'header': f'{template.template_name}'
    })
@login_required(login_url="/login")
def all_pages(request):
    pages =  EmailTemplate.objects.filter(type='custom')
    return render(request, 'hwapp/pages.html', {
        'pages': pages
    })