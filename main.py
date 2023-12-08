# imports
try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    from youtubesearchpython import VideosSearch
    import os
    import time

except Exception as e:
    print(e)

LIMIT = 5 # change it if you have high computing power

def download_playlist(playlist_url):
    playlist_uri = f"spotify:playlist:{playlist_url.split('/')[-1]}" # making uri out of url
    results = spotipy.playlist_items(playlist_uri, market=None) # getting the playlist
    playlist_name = spotipy.user_playlist(user=None, playlist_id=playlist_uri.split(":")[-1], fields="name")["name"] # getting playlist name
    print(f"Downloading '{playlist_name}'...")
    txt = ""

    for song in results['items']: # getting each song name and its artist
        track = f'{song["track"]["name"]} by {song["track"]["artists"][0]["name"]}' # query string to search
        videosSearch = VideosSearch(track, limit = 2) # searching for songs name
        url = videosSearch.result()['result'][0]["link"] # getting url of first video
        txt += url + " "

    os.system(f"./ytmp3-dl.py --limit {LIMIT} {txt}")

def download_song(song_url):
    song_uri = f"spotify:track:{song_url.split('/')[-1]}" # makin uri out of url
    track = spotipy.track(song_uri, market=None)["name"] # getting the name of the song
    videosSearch = VideosSearch(track, limit = 2) # searching for song name
    url = videosSearch.result()['result'][0]['link'] # getting url

    os.system(f"./ytmp3-dl.py {url}")

def download_album(album_url):
    album_uri = f"spotify:album:{album_url.split('/')[-1]}" # making uri out of url
    result = spotipy.album_tracks(album_id=album_uri.split(":")[-1], limit=None) # getting album
    print(f"Downloading {spotipy.album(album_id=album_uri.split(':')[-1])['name']}...")
    txt = ""

    for song in result['items']:
        track = f"{song['name']} {song['artists'][0]['name']}" # getting name of song
        videosSearch = VideosSearch(track, limit = 2) # searching for song name
        url = videosSearch.result()['result'][0]['link'] # getting url
        txt += url + " "

    os.system(f"./ytmp3-dl.py --limit {LIMIT} {txt}")

if __name__ == "__main__":
    spotipy = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials()) # creating the spotipy handler
    try:
        url = input("Enter the url of your playlist/song: ")
    except Exception as e:
        print(e)
    if url.split("/")[-2] == "playlist":
        download_playlist(url)
    elif url.split("/")[-2] == "track":
        download_song(url)
    elif url.split("/")[-2] == "album":
        download_album(url)
    else:
        print("Error")
