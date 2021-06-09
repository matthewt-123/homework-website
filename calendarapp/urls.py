from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.index, name="calendar_index"),
]
