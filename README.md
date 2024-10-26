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

## Features in Detail

### Concurrent Downloads
The script uses Python's multiprocessing to download multiple songs simultaneously, significantly reducing the total download time. The number of concurrent downloads is automatically set based on your CPU cores (maximum 5 processes).

### Error Handling
- Automatic retries for failed YouTube searches and downloads
- Graceful handling of keyboard interrupts
- Progress tracking with tqdm
- Detailed success/failure reporting

### File Organization
Downloads are automatically organized in folders named after the playlist or album. Files are named according to the song title and include the specified format extension.

## Limitations

- The script relies on YouTube search results, so occasionally it might not find the exact version of a song
- Download speed depends on your internet connection and YouTube's limitations
- Some songs might fail to download due to YouTube restrictions or region blocking

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Here's how you can contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Legal Notice

This tool is for personal use only. Please respect copyright laws and terms of service of both Spotify and YouTube. Make sure you have the right to download and store the music.

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024 Sarthak2143

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube downloading functionality
- [spotipy](https://spotipy.readthedocs.io/) for Spotify API integration
- [youtube-search-python](https://github.com/alexmercerind/youtube-search-python) for YouTube search functionality

## Troubleshooting

### Common Issues

1. **Spotify Authentication Failed**
   - Verify your credentials in config.json
   - Ensure your redirect URI matches exactly in both config.json and Spotify Developer Dashboard

2. **Downloads Failing**
   - Check your internet connection
   - Verify FFmpeg is properly installed
   - Try lowering the number of concurrent downloads
   - Check if the songs are available in your region

3. **Script Crashes**
   - Update your Python packages to the latest versions
   - Check system memory usage
   - Verify you have enough disk space

### Getting Help

If you encounter any issues:
1. Check the existing issues on the [GitHub repository](https://github.com/sarthak2143/spotify2mp3/issues)
2. Update all dependencies to their latest versions
3. If the problem persists, create a new issue with:
   - Your system information
   - Complete error message
   - Steps to reproduce the problem