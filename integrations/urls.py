from . import views
from django.urls import path, include



urlpatterns = [
    path("", views.index, name="integrations_index"),
    path("schoology_init", views.schoology_init, name="schoology_init")
]
