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

# Global variable to track if we're exiting
exiting = False

def signal_handler(signum, frame):
    global exiting
    exiting = True
    print("\nReceived interrupt signal. Finishing current downloads and exiting...")

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Load Spotify credentials
with open("config.json") as file:
    data = json.load(file)
    client_id = data['CLIENT_ID']
    client_secret = data['CLIENT_SECRET']
    redirect_uri = data['REDIRECT_URI']

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id, client_secret=client_secret, 
    redirect_uri=redirect_uri, scope="user-library-read"))

def get_youtube_url(song_name, artist_name, retries=3):
    for attempt in range(retries):
        try:
            time.sleep(attempt * 1)  # Exponential backoff
            videosSearch = VideosSearch(f"{song_name} {artist_name}", limit=1).result()
            if videosSearch["result"]:
                return videosSearch["result"][0]["link"]
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
    id = url.split("/")[-1]
    playlist = sp.playlist(id)
    total_tracks = playlist['tracks']['total']
    tracks = []
    
    for offset in range(0, total_tracks, 100):
        results = sp.playlist_tracks(id, offset=offset, limit=100)
        tracks.extend(results['items'])
        if limit and len(tracks) >= limit:
            tracks = tracks[:limit]
            break
    
    return process_tracks(tracks, playlist['name'], total_tracks)

def download_album(url):
    id = url.split("/")[-1]
    album = sp.album(id)
    tracks = album['tracks']['items']
    return process_tracks(tracks, album['name'], len(tracks))

def download_user_library(limit=None):
    tracks = []
    offset = 0
    while True:
        results = sp.current_user_saved_tracks(limit=50, offset=offset)
        tracks.extend(results['items'])
        if len(results['items']) < 50 or (limit and len(tracks) >= limit):
            break
        offset += 50
    
    if limit:
        tracks = tracks[:limit]
    
    return process_tracks(tracks, "My Liked Songs", len(tracks))

def process_tracks(tracks, name, total_tracks):
    print(f"Processing {len(tracks)} out of {total_tracks} tracks")
    
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

    for attempt in range(3):  # Try up to 3 times
        if exiting:
            return False
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            if attempt == 2:  # Last attempt
                print(f"Error downloading {url}: {str(e)}")
                return False
            time.sleep(attempt * 2)  # Exponential backoff

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