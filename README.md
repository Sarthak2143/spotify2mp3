# Spotify to MP3 Downloader

A Python script that downloads songs from Spotify playlists, albums, or your liked songs as MP3 files (or other audio formats). The tool searches for each track on YouTube and downloads the audio in your preferred format and quality.

## Features

- Download entire Spotify playlists, albums, or your liked songs
- Concurrent downloads for faster processing
- Configurable audio format (MP3, M4A, WAV)
- Adjustable audio quality (128kbps to 320kbps)
- Progress bar with download status
- Graceful handling of interruptions
- Automatic retry mechanism for failed downloads
- Multithreaded YouTube URL fetching

## Prerequisites

- Python 3.6+
- FFmpeg installed on your system
- Spotify Developer Account credentials
- Required Python packages (install via pip):

  ```bash
  pip install yt-dlp spotipy youtube-search-python tqdm
  ```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/sarthak2143/spotify2mp3.git
   cd spotify2mp3
   ```

2. Create a Spotify Developer account and get your credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new application
   - Get your Client ID and Client Secret
   - Add `http://localhost:8888/callback` to your Redirect URIs in the app settings

3. Create a `config.json` file in the project directory:

   ```json
   {
       "CLIENT_ID": "your_client_id_here",
       "CLIENT_SECRET": "your_client_secret_here",
       "REDIRECT_URI": "http://localhost:8888/callback"
   }
   ```

## Usage

The script can be used in several ways:

### Basic Usage

```bash
# Download a playlist
python main.py "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Download an album
python main.py "https://open.spotify.com/album/1DFixLWuPkv3KT3TnV35m3"

# Download your liked songs
python main.py "liked"
```

### Advanced Options

```bash
# Limit the number of songs to download (e.g., first 10 songs)
python main.py "playlist_url" -l 10

# Specify audio format (mp3, m4a, or wav)
python main.py "playlist_url" -f m4a

# Set audio quality (128, 192, 256, or 320 kbps)
python main.py "playlist_url" -q 320

# Combine multiple options
python main.py "playlist_url" -l 5 -f mp3 -q 320
```

### Command Line Arguments

- `url`: Spotify playlist/album URL or 'liked' for your liked songs
- `-l, --limit`: Limit the number of songs to download
- `-f, --format`: Audio format (mp3, m4a, wav)
- `-q, --quality`: Audio quality in kbps (128, 192, 256, 320)


## Legal Notice

This tool is for personal use only. Please respect copyright laws and terms of service of both Spotify and YouTube. Make sure you have the right to download and store the music.


## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloading functionality
- [spotipy](https://spotipy.readthedocs.io/) for Spotify API integration
- [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) for YouTube search functionality
