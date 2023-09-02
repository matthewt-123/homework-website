from django.contrib import admin

# Register your models here.

from .models import SpotifyAuth, SpotifyPlaylist

admin.site.register(SpotifyAuth)
admin.site.register(SpotifyPlaylist)


