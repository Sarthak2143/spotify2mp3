# imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import os

playlist_uri = "spotify:playlist:63koTFG6JV4XdUTOW9adzZ" # playlist to be specified
spotipy = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials()) # creating the spotipy handler

results = spotipy.playlist_items(playlist_uri, market=None) # getting the playlist

for song in results['items']: # getting each song name and its artist
    track = f'{song["track"]["name"]} by {song["track"]["artists"][0]["name"]}'
    videosSearch = VideosSearch(track, limit = 2) # searching for songs name
    url = videosSearch.result()['result'][1]["link"] # getting url of first video
    os.system(f"./ytmp3-dl.py \"{url}\"") # downloading music by url