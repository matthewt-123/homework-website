from . import views
from django.urls import path, include



urlpatterns = [
    path("homework", views.homework)
]

