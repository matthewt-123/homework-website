from . import views
from django.urls import path, include



urlpatterns = [
    path("", views.index, name="integrations_index"),
    path("export/<int:user_id>/<int:hash_value>", views.export, name="export"),
    path("notion_auth", views.notion_auth, name='notion_auth'),
    path("notion_callback", views.notion_callback),
    path('notionexport/<int:user_id>/<int:hash_value>/<str:tag>', views.notion_toics, name='notionicsfeed'),
    path('schoology_api', views.schoology_api, name='schoology_api'),
    path('canvas_api', views.canvas_api, name='canvas_api'),
    path('api/<int:integration_id>', views.edit_api, name='edit_api'),
    path('integration_log', views.integration_log, name='integration_log'),
    path('integration_log/<int:log_id>', views.integration_log_view, name='integration_log_view'),
    # path('admin_log', views.admin_log, name='admin_log'),
    path('csv_export', views.csv_export, name='csv_export'),
    # path('admin_log_ajax', views.admin_log_ajax, name='admin_log_ajax')
]
