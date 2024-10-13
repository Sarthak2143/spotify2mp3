import spotipy
import json
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython import VideosSearch

with open("config.json") as file: # getting all data from config file.
    data = json.loads(file.read())
    client_id = data['CLIENT_ID']
    client_secret = data['CLIENT_SECRET']
    redirect_uri = data['REDIRECT_URI']

scope = "user-library-read"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id, client_secret=client_secret, 
    redirect_uri=redirect_uri, scope=scope))

def get_songs_url(url):
    if url.split("/")[-2] == "album":
        return download_album(url)
    elif url.split("/")[-2] == "playlist":
        return download_playlist(url)
    else:
        print("Unknown url, pass in the format of *.spotify.com/(album/playlist)/ID")

def download_playlist(url):
    """Download playlist by spotify url."""
    url_list = []
    id = url.split("/")[-1]
    playlist = sp.playlist(id)

    for song in playlist["tracks"]["items"]:
        try:
            song_name = song["track"]["name"]
            artist_name = song['track']['artists'][0]['name']
        except TypeError:
            print(f"problem in song: {song}")
        videosSearch = VideosSearch(f"{song_name} {artist_name}", limit=2).result()
        try:
            url = videosSearch["result"][0]["link"]
        except IndexError:
            print(f"Song not found: \"{song_name} {artist_name}\"")
        url_list.append(url)

    return url_list, playlist['name']

def download_album(url):
    """Download album by spotify url."""
    url_list = []
    id = url.split("/")[-1]
    album = sp.album(id)
    artist_name = album['artists'][0]['name']

    for song in album["tracks"]["items"]:
        song_name = song["name"]
        videosSearch = VideosSearch(f"{song_name} {artist_name}", limit=2).result()
        url = videosSearch["result"][0]["link"]
        url_list.append(url)

    return url_list, album['name']
