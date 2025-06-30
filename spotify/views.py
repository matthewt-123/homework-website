from django.shortcuts import render
from .models import SpotifyAuth, SpotifyPlaylist
import secrets
import os
import string
import sys
import requests
import json
from datetime import datetime
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http.response import JsonResponse, HttpResponse, Http404
import re
from django.contrib.auth.decorators import login_required, user_passes_test

from mywebsite.settings import DEBUG
from hwapp.models import User

def matthew_check(user):
    return user.id == 1
def user_in_group(*group_names):
    """Requires user membership in at least one of the groups passed in."""
    def in_groups(u):
        if u.is_authenticated:
            if bool(u.groups.filter(name__in=group_names)) | u.is_superuser:
                return True
        return False
    return user_passes_test(in_groups, login_url='403')

# Create your views here.
@user_in_group("Spotify Users")
def index(request):
    try:
        int_status = SpotifyAuth.objects.get(user=request.user, error=False)
    except:
        int_status = False
    state = ''.join(secrets.choice(string.ascii_uppercase + string.digits)
              for i in range(64))
    request.session['spotify_state'] = state
    if request.user.id == 1:
        url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={os.environ.get('SPOTIFY_CLIENT_ID')}&scope=playlist-modify-public%20playlist-modify-private%20user-read-playback-state%20streaming%20user-read-email%20user-read-currently-playing%20user-read-private&redirect_uri=http{'' if DEBUG else 's'}://{os.environ.get('WEBSITE_ROOT')}/spotify/callback&state={state}"
    else:
        url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={os.environ.get('SPOTIFY_CLIENT_ID')}&scope=playlist-modify-public%20playlist-modify-private&redirect_uri=http{'' if DEBUG else 's'}://{os.environ.get('WEBSITE_ROOT')}/spotify/callback&state={state}"

    return render(request, 'spotify/spotify_index.html', {
        'int_status': int_status,
        'url': url,
        'website_root': os.environ.get("WEBSITE_ROOT")
    })

@user_in_group("Spotify Users")
def callback(request):
    if request.method == "GET":
        if request.session['spotify_state'] and request.GET.get('state') != request.session['spotify_state']:
            return render(request, 'hwapp/error.html', {
                "error": "Invalid request"
            })
        if request.GET.get("error"):
            return render(request, 'hwapp/error.html', {
                "error": request.GET.get("error")
            })           
        url = 'https://accounts.spotify.com/api/token' 
        data = {
            "grant_type": "authorization_code",
            "code": request.GET.get('code'),
            "redirect_uri": f"http{'' if DEBUG else 's'}://{os.environ.get('website_root')}/spotify/callback",
            "client_id": os.environ.get('SPOTIFY_CLIENT_ID'),
            "client_secret": os.environ.get('SPOTIFY_CLIENT_SECRET'),
        }
        response = requests.post(url, data=data)
        data1 = json.loads(response.text)
        try:
            spotify_auth = SpotifyAuth.objects.get(user=request.user)
        except:
            spotify_auth = SpotifyAuth.objects.create(user=request.user)   
        spotify_auth.access_token = data1['access_token']
        spotify_auth.refresh_token = data1['refresh_token']
        spotify_auth.scope = data1['scope']
        spotify_auth.save()

        #get user id
        url = 'https://api.spotify.com/v1/me'
        headers = {"Authorization": f"Bearer {SpotifyAuth.objects.get(user=request.user).access_token}"}
        response = requests.get(url, headers=headers)
        data1 = json.loads(response.text)
        spotify_auth.s_user_id = data1['id']
        spotify_auth.save()

        return HttpResponseRedirect(reverse("spotify_index"))
    else:
        return HttpResponseRedirect(reverse("index"))

@user_in_group("Spotify Users")
def expired(request):
    url = "https://accounts.spotify.com/api/token"
    
    try:
        spotify_auth = SpotifyAuth.objects.get(user=request.user)
    except:
        return JsonResponse({"message": "an error has occurred", "status": 401}, status=401)
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": spotify_auth.refresh_token,
        "client_id": os.environ.get('SPOTIFY_CLIENT_ID'),
        "client_secret": os.environ.get('SPOTIFY_CLIENT_SECRET'),
    }
    print(data)
    response = requests.post(url, data=data)
    print(response.text)
    spotify_auth.access_token = json.loads(response.text)['access_token']
    spotify_auth.save()
    return JsonResponse({"message": "refresh completed successfully", "status": 200}, status=200)
@user_in_group("Spotify Users")
def recommendations(request):
    data = json.loads(request.body)
    seed_tracks = ""
    seed_artists = ""
    count = 0
    spotify_auth = SpotifyAuth.objects.get(user=request.user)

    #part 1: get recommendations
    for uri in data:
        if data[uri] != "" and str(data[uri]).startswith("spotify:"):
            t_type = re.search("(?<=spotify:)(.*)(?=:)", data[uri]).group(0) # type: ignore
            if str(t_type) == "artist":
                seed_artists += f'{re.search(f"(?<=artist:)(.*)", data[uri]).group(0)},' # type: ignore
            elif str(t_type) == "track":
                seed_tracks += f'{re.search(f"(?<=track:)(.*)", data[uri]).group(0)},' # type: ignore
            count += 1
    if count == 0:
        return JsonResponse({"error": "No tracks selected"}, status=400)
    url = "https://api.spotify.com/v1/recommendations"
    body = {
        "limit": 50,
        "market": "US",
        "target_energy": data['target_energy'],
        "target_danceability": data['target_danceability'],
        "target_acousticness": data['target_acousticness'],
        "target_instrumentalness": data['target_instrumentalness'],
        "target_liveness": data['target_liveness'],
        "target_speechiness": data['target_speechiness']
    }
    if seed_artists != "" and seed_tracks != "":
        body["seed_artists"]= seed_artists[:-1]
        body["seed_tracks"] = seed_tracks[:-1]
    elif seed_artists != "":
        body["seed_artists"]= seed_artists[:-1]
    elif seed_tracks != "":
        body["seed_tracks"] = seed_tracks[:-1] 
    headers = {"Authorization": f"Bearer {spotify_auth.access_token}"}
    response = requests.get(url, params=body, headers=headers)
    if str(response) != "<Response[200]>":
        expired(request)
        response = requests.get(url, params=body, headers=headers)
    tracks = json.loads(response.text)
    uri = []
    for track in tracks['tracks']:
        uri.append(track["uri"])
    seed_tracks = seed_tracks[:-1].split(",")
    for seed_track in seed_tracks:
        uri.append(f"spotify:track:{seed_track}")

    #Part 2: Create New Playlist
    url = f"https://api.spotify.com/v1/users/{spotify_auth.s_user_id}/playlists"
    if data['playlist_name'] == "":
        playlist_name = "Study Playlist"
    else:
        playlist_name = data['playlist_name']
    data = {
        "name": playlist_name,
        "public": False,
        "description": f"Created by Homework App on {datetime.now().strftime('%m-%d-%Y')}"
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    data1 = json.loads(response.text)
    s_playlist = SpotifyPlaylist.objects.create(auth=spotify_auth, playlist_name=playlist_name, url = data1['external_urls']['spotify'], uri = data1['id'], created=datetime.now())

    #Part 3: Add to Playlist
    url = f"https://api.spotify.com/v1/playlists/{s_playlist.uri}/tracks"
    data = {
        "uris": uri
    }
    response = requests.post(url, data=json.dumps(data), headers=headers)
    return JsonResponse({"message": "playlist created successfully", "status": 200, "playlist_id": s_playlist.id}, status=200) # type: ignore
@user_in_group("Spotify Users")
def playlists(request):
    spotify_auth = SpotifyAuth.objects.get(user=request.user)
    if request.GET.get("playlist"):
        try:
            playlist = SpotifyPlaylist.objects.get(auth=spotify_auth, id=request.GET.get("playlist"))
            return render(request, 'spotify/playlist_view.html', {
                'playlist': playlist
            })
        except:
            return render(request, 'hwapp/error.html', {
                'error': 'no playlist found'
            })
    else:
        playlists_all = SpotifyPlaylist.objects.filter(auth=spotify_auth)
        return render(request, 'spotify/playlist_listing.html', {
            'playlists': playlists_all
        })
@user_in_group("Spotify Users")
def deleteplaylist(request):
    try:
        playlist = SpotifyPlaylist.objects.get(auth=SpotifyAuth.objects.get(user=request.user), id=request.GET.get('playlist_id'))
        playlist.delete()
        return JsonResponse({"message": "Playlist deleted successfully", "status": 200}, status=200)
    except:
        return JsonResponse({"message": "Playlist not found", "status": 404}, status=404)

@user_in_group("Spotify Users")
def queuedump(request):
    if request.method == "POST":
        spotify_auth = SpotifyAuth.objects.get(user=request.user)
        url = "https://api.spotify.com/v1/me/player/queue"

        #Part 1: Get Queue
        headers = {"Authorization": f"Bearer {spotify_auth.access_token}"}
        response = requests.get(url, headers=headers)
        if str(response) != "<Response[200]>":
            expired(request)
            response = requests.get(url, headers=headers)
        tracks = json.loads(response.text)
        uri = []
        for track in tracks['queue']:
            if track['type'] == "track":
                uri.append(track["uri"])
        
        #Part 2: Create New Playlist
        url = f"https://api.spotify.com/v1/users/{spotify_auth.s_user_id}/playlists"
        name = request.POST.get("playlist_name")
        if name == "":
            playlist_name = f"Queue {datetime.now().strftime('%m-%d-%Y')}"
        else:
            playlist_name = name
        data = {
            "name": playlist_name,
            "public": False,
            "description": f"Created by Homework App on {datetime.now().strftime('%m-%d-%Y')}"
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        data1 = json.loads(response.text)
        s_playlist = SpotifyPlaylist.objects.create(
            auth=spotify_auth,
            playlist_name=playlist_name,
            url = data1['external_urls']['spotify'],
            uri = data1['id'],
            created=datetime.now()
        )

        #Part 3: Add to Playlist
        url = f"https://api.spotify.com/v1/playlists/{s_playlist.uri}/tracks"
        data = {
            "uris": uri
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return JsonResponse({"message": "playlist created successfully", "status": 200, "playlist_id": s_playlist.id}, status=200) # type: ignore
    else:
        return render(request, 'spotify/queue.html')

def queue_html(request):
    try:
        assert(request.headers['login'] == os.environ.get("PASTEBIN_HASH", ""))
        user = User.objects.get(id=1)
        spotify_auth = SpotifyAuth.objects.get(user=user)
        url = "https://api.spotify.com/v1/me/player/queue"

        #Part 1: Get Queue
        headers = {"Authorization": f"Bearer {spotify_auth.access_token}"}
        response = requests.get(url, headers=headers)
        if str(response) != "<Response[200]>":
            from django.contrib.auth import login
            login(request, user)
            expired(request)
            response = requests.get(url, headers=headers)
        tracks = json.loads(response.text)
        uri = []
        for track in tracks['queue']:
            if track['type'] == "track":
                uri.append(track["uri"])
        
        #Part 2: Create New Playlist
        url = f"https://api.spotify.com/v1/users/{spotify_auth.s_user_id}/playlists"
        name = request.GET.get('playlist_name')
        if name == "":
            playlist_name = f"Queue {datetime.now().strftime('%m-%d-%Y')}"
        else:
            playlist_name = name
        data = {
            "name": playlist_name,
            "public": False,
            "description": f"Created by Homework App on {datetime.now().strftime('%m-%d-%Y')}"
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        data1 = json.loads(response.text)
        s_playlist = SpotifyPlaylist.objects.create(auth=spotify_auth, playlist_name=playlist_name, url = data1['external_urls']['spotify'], uri = data1['id'], created=datetime.now())

        #Part 3: Add to Playlist
        url = f"https://api.spotify.com/v1/playlists/{s_playlist.uri}/tracks"
        data = {
            "uris": uri
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return HttpResponse("playlist created successfully")
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}")