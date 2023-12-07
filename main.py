import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import os

playlist_uri = "spotify:playlist:63koTFG6JV4XdUTOW9adzZ"
spotipy = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

results = spotipy.playlist_items(playlist_uri, market=None)

for song in results['items']:
    track = f'{song["track"]["name"]} by {song["track"]["artists"][0]["name"]}'
    videosSearch = VideosSearch(track, limit = 2)
    url = videosSearch.result()['result'][1]["link"]
    os.system(f"./ytmp3-dl.py \"{url}\"")