import yt_dlp
import os
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython import VideosSearch
import json
import time

# Load Spotify credentials
with open("config.json") as file:
    data = json.load(file)
    client_id = data['CLIENT_ID']
    client_secret = data['CLIENT_SECRET']
    redirect_uri = data['REDIRECT_URI']

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id, client_secret=client_secret, 
    redirect_uri=redirect_uri, scope="user-library-read"))

def get_youtube_url(song_name, artist_name):
    try:
        videosSearch = VideosSearch(f"{song_name} {artist_name}", limit=1).result()
        if videosSearch["result"]:
            return videosSearch["result"][0]["link"]
        else:
            print(f"No YouTube results for: \"{song_name} {artist_name}\"")
            return None
    except Exception as e:
        print(f"Error searching for \"{song_name} {artist_name}\": {str(e)}")
        return None

def get_songs_url(url):
    if "album" in url:
        return download_album(url)
    elif "playlist" in url:
        return download_playlist(url)
    else:
        raise ValueError("Unknown URL format. Please use a Spotify album or playlist URL.")

def download_playlist(url):
    id = url.split("/")[-1]
    playlist = sp.playlist(id)
    total_tracks = playlist['tracks']['total']
    tracks = []
    
    # Fetch all tracks with pagination
    for offset in range(0, total_tracks, 100):
        results = sp.playlist_tracks(id, offset=offset, limit=100)
        tracks.extend(results['items'])
    
    print(f"Total tracks in playlist: {total_tracks}")
    
    url_list = []
    not_found = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for song in tracks:
            try:
                song_name = song["track"]["name"]
                artist_name = song['track']['artists'][0]['name']
                futures.append(executor.submit(get_youtube_url, song_name, artist_name))
            except TypeError:
                print(f"Problem with song: {song}")
        
        for future in futures:
            result = future.result()
            if result:
                url_list.append(result)
            else:
                not_found.append(future)
    
    print(f"Found YouTube URLs for {len(url_list)} out of {total_tracks} tracks")
    if not_found:
        print(f"Could not find YouTube URLs for {len(not_found)} tracks")
    
    return url_list, playlist['name']

def download_album(url):
    id = url.split("/")[-1]
    album = sp.album(id)
    artist_name = album['artists'][0]['name']
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_youtube_url, song["name"], artist_name) for song in album["tracks"]["items"]]
        url_list = [future.result() for future in futures if future.result() is not None]
    
    return url_list, album['name']

def download_youtube_audio(url, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Download complete: {url}")
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")

def download_multiple(urls, output_dir, num_processes=5):
    os.makedirs(output_dir, exist_ok=True)
    with multiprocessing.Pool(processes=num_processes) as pool:
        pool.starmap(download_youtube_audio, [(url, output_dir) for url in urls])

if __name__ == "__main__":
    spotify_url = input("Enter URL of Spotify album or playlist: ")
    urls, output_dir = get_songs_url(spotify_url)
    num_processes = min(multiprocessing.cpu_count(), 5)
    
    print(f"Attempting to download {len(urls)} songs to '{output_dir}'...")
    download_multiple(urls, output_dir, num_processes)
    print("All downloads completed.")
    print(f"Successfully downloaded {len([f for f in os.listdir(output_dir) if f.endswith('.mp3')])} songs.")