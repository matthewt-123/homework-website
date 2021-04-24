from . import views
from django.urls import path


urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("hourly_refresh", views.hourly_refresh, name="hr_refresh"),
    path("classes", views.classes, name="classes"),
    path("preferences", views.preferences, name="preferences"),
    path("addhw", views.addhw, name="addhw"),
    path("edit_hw/<int:hw_id>", views.edit_hw, name="edit_hw"),
    path("addclass", views.addclass, name="addclass"),
    path("editclass/<int:class_id>", views.editclass, name="editclass"),
    path("classhw/<int:class_id>", views.classhw, name="classhw"),
    path("allhw", views.allhw, name="allhw"),

]
