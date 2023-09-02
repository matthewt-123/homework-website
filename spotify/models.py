from django.db import models

# Create your models here.
class SpotifyAuth(models.Model):
    user = models.ForeignKey('hwapp.User', on_delete=models.CASCADE)
    access_token = models.TextField(default=None, blank=True, null=True)
    refresh_token = models.TextField(default=None, blank=True, null=True)
    scope = models.CharField(max_length=512, default=None, blank=True, null=True)
    s_user_id = models.TextField(default=None, blank=True, null=True)
    error = models.BooleanField(default=False, blank=False, null=False)
    def __str__(self):
        return f"{self.user}"

class SpotifyPlaylist(models.Model):
    auth = models.ForeignKey('SpotifyAuth', on_delete=models.CASCADE) 
    playlist_name = models.CharField(max_length=512, default=None, blank=True, null=True)
    url = models.CharField(max_length=512, default=None, blank=True, null=True)
    uri = models.CharField(max_length=512, default=None, blank=True, null=True)
    created = models.DateTimeField(default=None, blank=True, null=True)
    def __str__(self):
        return f"{self.playlist_name}"    