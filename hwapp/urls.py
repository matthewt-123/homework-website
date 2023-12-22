from . import views
from django.urls import path, include



urlpatterns = [
    path("", views.index, name="index"),
    path("", views.index, name="homework"),
    path("classes", views.classes, name="classes"),
    path("addhw", views.addhw, name="addhw"),
    path("edit_hw/<int:hw_id>", views.edit_hw, name="edit_hw"),
    path("addclass", views.addclass, name="addclass"),
    path("editclass/<int:class_id>", views.editclass, name="editclass"),
    path("about", views.about, name="about"),
    path("profile", views.profile, name="profile"),
    path("calendar/", views.calendar, name="calendar"),
    path("deleteclass/<int:id>", views.deleteclass, name='delete_a_class'),
    path("getclasstime/<int:class_id>", views.getclasstime, name='getclasstime'),
    path('admin_view', views.admin_console, name='admin_view'),
    path('welcome', views.new_user_view, name='new_user_view'),
    path('homework/<int:hw_id>', views.homework_entry, name='homework_entry'),
    path('config/email_templates', views.email_template_editor, name='email_template_editor'),
    path('config/add_template', views.add_template, name='email_add_template'),
    path('templates', views.email_template_editor, name='experience_manager'),
    path('communications', views.email_all, name='communications'),
    path('privacy', views.privacy, name='privacy'),
    path('termsandconditions', views.terms, name='terms'),
    path('home', views.home, name='home'),
    path('callback', views.callback, name='callback'),
    path('login', views.sso_login, name='login'),
    path('logout', views.sso_logout, name='logout'),
    path('version/<int:version_id>', views.version_manager, name='version_manager'),
    path('archive/<int:id>', views.archiveclass),
    path('change_password', views.change_password),
    path('helpformview/<int:id>', views.helpformview, name="helpformview"),
    path('helpformlist', views.helpformlist, name="helpformlist"),
    path('csv_export', views.csv_export_template, name="csv_export_template"),
    path('pastebin', views.pastebin, name="pastebin"),
    path('pastebin_html', views.pastebin_html, name="pastebin_html"),
    path('filebin', views.filebin, name="filebin"),
    path('email', views.custom_email, name="email"),
    path('page/<int:page_id>', views.page_manager, name='page_manager'),
    path('pages', views.all_pages, name='all_pages'),
    path('filebin_html', views.filebin_html, name="filebin_html"),

    #path('login_as', views.login_as)
]

