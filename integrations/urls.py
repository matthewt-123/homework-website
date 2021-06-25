from . import views
from django.urls import path, include



urlpatterns = [
    path("", views.index, name="integrations_index"),
    path("schoology_init", views.schoology_init, name="schoology_init"),
    path("canvas_init", views.canvas_init, name="canvas_init"),
    path("export/<int:user_id>/<int:hash_value>", views.export, name="export"),
    path("other_init", views.other_init, name="other_init"),
    
]
