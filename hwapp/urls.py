from . import views
from django.urls import path, include
from django.views.generic import TemplateView


urlpatterns = [
    #public views
    path('home', views.home, name='home'),
    path('login', views.sso_login, name='login'),
    path('logout', views.sso_logout, name='logout'),
    path('callback', views.callback, name='callback'),
    path('privacy', views.privacy, name='privacy'),
    path('termsandconditions', views.terms, name='terms'),
    path('404', views.not_found, name="403"),

    #log in required views
    path("", views.index, name="index"), #hw listing
    path("classes", views.classes, name="classes"), #class listing
    path("addhw", views.addhw, name="addhw"), #add homework
    path("edit_hw/<int:hw_id>", views.edit_hw, name="edit_hw"), #edit hw
    path("addclass", views.addclass, name="addclass"), #add class
    path("editclass/<int:class_id>", views.editclass, name="editclass"), #edit class
    path("about", views.about, name="about"), #about the site
    path("settings", views.profile, name="settings"), #settings
    path("calendar/", views.calendar, name="calendar"), #calendar export
    path("deleteclass/<int:id>", views.deleteclass, name='delete_a_class'), 
    path("getclasstime/<int:class_id>", views.getclasstime, name='getclasstime'),
    path('welcome', views.new_user_view, name='new_user_view'),
    path('homework/<int:hw_id>', views.homework_entry, name='homework_entry'),
    path('version/<int:version_id>', views.version_manager, name='version_manager'),
    path('version', views.latest_version, name='latest_version'),
    path('archive/<int:id>', views.archiveclass),
    path('change_password', views.change_password),

    #Help Desk Admins
    path('helpformview/<int:id>', views.helpformview, name="helpformview"),
    path('helpformlist', views.helpformlist, name="helpformlist"),
    path('email', views.custom_email, name="email"),
    path('admin_dashboard/users', views.user_management, name="user_management"),
    path('admin_dashboard/users/<int:user_id>', views.user_management_individual, name="user_management_individual"),

    #Custom Page Users
    path('page/<int:page_id>', views.page_manager, name='page_manager'),
    path('pages', views.all_pages, name='all_pages'),
    path('bookmark', views.bookmark, name='bookmark'),

    #pastebin users
    path('pastebin', views.pastebin, name="pastebin"),
    path('pastebin_html', views.pastebin_html, name="pastebin_html"),
    path('filebin', views.filebin, name="filebin"),
    path('filebin_html', views.filebin_html, name="filebin_html"),

    #permission admins
    path('groups', views.group_management, name="group_management"),

    #is_superuser required
    path('admin_dashboard', views.admin_console, name='admin_dashboard'),
    path('config/email_templates', views.email_template_editor, name='email_template_editor'),
    path('config/add_template', views.add_template, name='email_add_template'),
    path('templates', views.email_template_editor, name='experience_manager'),
    path('communications', views.email_all, name='communications'),

]

