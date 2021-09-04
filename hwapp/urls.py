from . import views
from django.urls import path, include



urlpatterns = [
    path("", views.index, name="index"),
    path("", views.index, name="homework"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("classes", views.classes, name="classes"),
    path("preferences", views.preferences, name="preferences"),
    path("addhw", views.addhw, name="addhw"),
    path("edit_hw/<int:hw_id>", views.edit_hw, name="edit_hw"),
    path("addclass", views.addclass, name="addclass"),
    path("editclass/<int:class_id>", views.editclass, name="editclass"),
    path("allhw", views.allhw, name="allhw"),
    path("about", views.about, name="about"),
    path("profile", views.profile, name="profile"),
    path("calendar/", views.calendar, name="calendar"),
    path("completion/<int:hw_id>", views.completion, name="completion"),
    path("deleteclass/<int:id>", views.deleteclass, name='delete_a_class'),
    path("refresh/<str:occurence>/<str:hash_value>", views.refresh, name='refresh'),
    path("getclasstime/<int:class_id>", views.getclasstime, name='getclasstime'),
    path("reset_password", views.reset_password, name='reset_password'),
    path('matthew/schoology_grades', views.matthew_schoology_grades, name='matthew_schoology_grades'),
    path('admin_view', views.admin_console, name='admin_view'),


]
