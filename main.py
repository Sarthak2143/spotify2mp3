# imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
import os
import time

spotipy = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials()) # creating the spotipy handler

def download_playlist(playlist_url):
    playlist_uri = f"spotify:playlist:{playlist_url.split('/')[-1]}"
    results = spotipy.playlist_items(playlist_uri, market=None) # getting the playlist
    playlist_name = spotipy.user_playlist(user=None, playlist_id=playlist_uri.split(":")[-1], fields="name")["name"]
    print(f"Downloading '{playlist_name}'...")
    time.sleep(1)

    for song in results['items']: # getting each song name and its artist
        track = f'{song["track"]["name"]} by {song["track"]["artists"][0]["name"]}'
        videosSearch = VideosSearch(track, limit = 2) # searching for songs name
        url = videosSearch.result()['result'][0]["link"] # getting url of first video
        os.system(f"./ytmp3-dl.py \"{url}\"") # downloading music by url

def download_song(song_url):
    song_uri = f"spotify:track:{song_url.split('/')[-1]}"
    track = spotipy.track(song_uri, market=None)
    name = track['name']
    videosSearch = VideosSearch(name, limit = 2) # searching for song name
    url = videosSearch.result()['result'][0]['link']
    os.system(f"./ytmp3-dl.py '{url}'")

if __name__ == "__main__":
    try:
        url = input("Enter the url of your playlist/song: ")
    except Exception as e:
        print(e)
    if url.split("/")[-2] == "playlist":
        download_playlist(url)
    elif url.split("/")[-2] == "track":
        download_song(url)
    else:
        print("Error")
    