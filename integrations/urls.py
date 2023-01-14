from . import views
from django.urls import path, include



urlpatterns = [
    path("", views.index, name="integrations_index"),
    path("schoology_init", views.schoology_init, name="schoology_init"),
    path("canvas_init", views.canvas_init, name="canvas_init"),
    path("export/<int:user_id>/<int:hash_value>", views.export, name="export"),
    path("other_init", views.other_init, name="other_init"),
    path("notion_auth", views.notion_auth, name='notion_auth'),
    path("notion_callback", views.notion_callback),
    path('admin_notion', views.admin_notion, name='matthew_notion'),
    path('google', views.google_view, name='google_view'),
    path('google_callback', views.google_callback, name='google_callback'),
    path('google_info', views.google_info, name='google_info'),
    #path('notion_to_ics', views.notion_toics, name='notion_toics'),
    path('notionexport/<int:user_id>/<int:hash_value>', views.notion_toics, name='notionicsfeed'),
    #path('authentication_manager/<int:user_id>', views.authentication_manager, name='authentication_manager'),

]
