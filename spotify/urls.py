from . import views
from django.urls import path, include

urlpatterns = [
    path("", views.index, name="spotify_index"),
    path("callback", views.callback, name="spotify_callback"),
    path("expired", views.expired, name="spotify_expired"),
    path("recommendations", views.recommendations, name="spotify_recommendations"),
    path("playlists", views.playlists, name="spotify_playlists"),
    path("deleteplaylist", views.deleteplaylist, name="spotify_deleteplaylist"),
    # path("widget/<int:user_id>/<int:hash_value>", views.spotify_widget)
    #path("test", views.test, name="spotify_test"),

]
