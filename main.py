import yt_dlp
import os
import multiprocessing
from spotify2mp3 import get_songs_url

def download_youtube_audio(url, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            mp3_filename = f"{os.path.splitext(filename)[0]}.mp3"
            print(f"Download complete: {mp3_filename}")
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")

def download_multiple(urls, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Create a pool of worker processes
    with multiprocessing.Pool() as pool:
        # Start the download processes
        results = [pool.apply_async(download_youtube_audio, (url, output_dir)) for url in urls]

        # Wait for all processes to complete
        for result in results:
            result.get()

if __name__ == "__main__":
    # List of YouTube URLs to download
    urls, output_dir = get_songs_url(input("Enter url of album or playlist: "))

    download_multiple(urls, output_dir)

    print("All downloads completed.")