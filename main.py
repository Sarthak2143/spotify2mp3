import yt_dlp
import os
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from youtubesearchpython import VideosSearch
import json
import time
from tqdm import tqdm
import argparse
import signal

# Constants for configuration
SPOTIFY_SCOPE = "user-library-read"  # Scope for Spotify API access
YOUTUBE_SEARCH_LIMIT = 1  # Limit for YouTube search results
SPOTIFY_TRACK_LIMIT = 50  # Limit for Spotify track retrieval
YOUTUBE_RETRIES = 3  # Number of retries for YouTube search
DOWNLOAD_RETRIES = 3  # Number of retries for downloading audio
DOWNLOAD_BACKOFF = 2  # Backoff time for retries in seconds

# Global variable to track if we're exiting
exiting = False

def signal_handler():
    """
    Signal handler for graceful shutdown on interrupt signal.
    Sets the global 'exiting' flag to True.
    """
    global exiting
    exiting = True
    print("\nReceived interrupt signal. Finishing current downloads and exiting...")

# Register the signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)

# Loading Spotify credentials from config.json
with open("config.json") as file:
    data = json.load(file)
    client_id = data['CLIENT_ID']
    client_secret = data['CLIENT_SECRET']
    redirect_uri = data['REDIRECT_URI']

# Initialize Spotify client with OAuth credentials
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id, client_secret=client_secret, 
    redirect_uri=redirect_uri, scope=SPOTIFY_SCOPE))

def get_youtube_url(song_name, artist_name, retries=YOUTUBE_RETRIES):
    for attempt in range(retries):
        try:
            time.sleep(attempt)  # Exponential backoff
            # we are searching for "{song_name} {artist_name}" to reduce any confusions
            videos_search = VideosSearch(f"{song_name} {artist_name}", limit=YOUTUBE_SEARCH_LIMIT).result()
            if videos_search["result"]:
                return videos_search["result"][0]["link"] # getting the link of the video
            else:
                print(f"No YouTube results for: \"{song_name} {artist_name}\"")
                return None
        except Exception as e:
            if attempt == retries - 1:
                print(f"Error searching for \"{song_name} {artist_name}\": {str(e)}")
                return None

def get_songs_url(url, limit=None):
    if "album" in url:
        return download_album(url)
    elif "playlist" in url:
        return download_playlist(url, limit)
    elif "spotify.com/user" in url:
        return download_user_library(limit)
    else:
        raise ValueError("Unknown URL format. Please use a Spotify album, playlist, or user library URL.")

def download_playlist(url, limit=None):
    return download_spotify_tracks(sp.playlist, sp.playlist_tracks, url, limit)

def download_album(url):
    return download_spotify_tracks(sp.album, lambda id, **kwargs: sp.album(id)['tracks'], url)

def download_user_library(limit=None):
    tracks = []
    offset = 0
    while True:
        results = sp.current_user_saved_tracks(limit=SPOTIFY_TRACK_LIMIT, offset=offset)
        tracks.extend(results['items'])
        if len(results['items']) < SPOTIFY_TRACK_LIMIT or (limit and len(tracks) >= limit):
            break
        offset += SPOTIFY_TRACK_LIMIT
    
    if limit:
        tracks = tracks[:limit]
    
    return process_tracks(tracks, "My Liked Songs", len(tracks))

def download_spotify_tracks(get_func, get_tracks_func, url, limit=None):
    id = url.split("/")[-1]
    item = get_func(id)
    total_tracks = item['tracks']['total']
    tracks = []
    
    for offset in range(0, total_tracks, 100):
        results = get_tracks_func(id, offset=offset, limit=100)
        tracks.extend(results['items'])
        if limit and len(tracks) >= limit:
            tracks = tracks[:limit]
            break
    
    return process_tracks(tracks, item['name'], total_tracks)

def process_tracks(tracks, name, total_tracks):
    print(f"Processing {len(tracks)} out of {total_tracks} tracks")
    
    url_list = []
    not_found = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(get_youtube_url, song["track"]["name"], song['track']['artists'][0]['name']) for song in tracks]
        
        for future in futures:
            result = future.result()
            if result:
                url_list.append(result)
            else:
                not_found.append(future)
    
    print(f"Found YouTube URLs for {len(url_list)} out of {len(tracks)} tracks")
    if not_found:
        print(f"Could not find YouTube URLs for {len(not_found)} tracks")
    
    return url_list, name

def download_youtube_audio(args):
    url, output_dir, audio_format, audio_quality = args
    global exiting
    if exiting:
        return False

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': audio_quality,
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
    }

    for attempt in range(DOWNLOAD_RETRIES):  # Try up to 3 times
        if exiting:
            return False
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            if attempt == DOWNLOAD_RETRIES - 1:  # Last attempt
                print(f"Error downloading {url}: {str(e)}")
                return False
            time.sleep(attempt * DOWNLOAD_BACKOFF)  # Exponential backoff

def download_multiple(urls, output_dir, num_processes=5, audio_format='mp3', audio_quality='192'):
    global exiting
    os.makedirs(output_dir, exist_ok=True)
    
    with multiprocessing.Pool(processes=num_processes) as pool:
        args_list = [(url, output_dir, audio_format, audio_quality) for url in urls]
        results = []
        pbar = tqdm(total=len(urls), desc="Downloading")
        for result in pool.imap(download_youtube_audio, args_list):
            results.append(result)
            pbar.update(1)
            if exiting:
                pool.terminate()
                break
        pbar.close()
    
    success_count = sum(results)
    print(f"\nSuccessfully downloaded {success_count} out of {len(urls)} songs.")
    if exiting:
        print("Download process was interrupted. Some songs may not have been downloaded.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Spotify playlist/album as MP3")
    parser.add_argument("url", help="Spotify playlist/album URL or 'liked' for user's liked songs")
    parser.add_argument("-l", "--limit", type=int, help="Limit number of songs to download")
    parser.add_argument("-f", "--format", default="mp3", choices=["mp3", "m4a", "wav"], help="Audio format")
    parser.add_argument("-q", "--quality", default="192", choices=["128", "192", "256", "320"], help="Audio quality (bitrate)")
    args = parser.parse_args()

    try:
        if args.url.lower() == 'liked':
            urls, output_dir = download_user_library(args.limit)
        else:
            urls, output_dir = get_songs_url(args.url, args.limit)

        num_processes = min(multiprocessing.cpu_count(), 5)
        
        print(f"Attempting to download {len(urls)} songs to '{output_dir}'...")
        download_multiple(urls, output_dir, num_processes, args.format, args.quality)
        
        if not exiting:
            print("All downloads completed.")
            print(f"Successfully downloaded {len([f for f in os.listdir(output_dir) if f.endswith('.' + args.format)])} songs.")
    except KeyboardInterrupt:
        print("\nScript interrupted by user. Exiting...")
    finally:
        if exiting:
            print("Download process finished. Some songs may not have been downloaded due to interruption.")