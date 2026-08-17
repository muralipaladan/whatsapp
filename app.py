#!/usr/bin/env python3
"""
Online Song Downloader
YouTube, SoundCloud, Instagram, Facebook - ഏത് URL-ൽ നിന്നും audio download ചെയ്യാം.
yt-dlp ഉപയോഗിക്കുന്നു (pip install yt-dlp)
"""

import os
import sys
import subprocess

# ---- yt-dlp auto-install ----
try:
    import yt_dlp
except ImportError:
    print("yt-dlp install ചെയ്യുന്നു...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp", "-q"])
    import yt_dlp


def download_song(url: str, output_dir: str = "downloads", quality: str = "best"):
    """
    URL-ൽ നിന്ന് audio download ചെയ്യുന്നു.

    Parameters:
        url        : YouTube / SoundCloud / any yt-dlp supported URL
        output_dir : Download folder (default: ./downloads)
        quality    : 'best' | 'worst' | '128' | '192' | '320' (kbps)
    """
    os.makedirs(output_dir, exist_ok=True)

    # Audio quality setting
    audio_quality = "0" if quality == "best" else ("9" if quality == "worst" else quality)

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": audio_quality,
            }
        ],
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "quiet": False,
        "noplaylist": False,   # playlist support ON - single URL ആണെങ്കിൽ single file മാത്രം
        "progress_hooks": [progress_hook],
    }

    print(f"\n📥 Downloading: {url}")
    print(f"📁 Save location: {os.path.abspath(output_dir)}\n")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get("title", "Unknown")
            print(f"\n✅ Done: {title}.mp3")
            return True
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Download error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def progress_hook(d):
    """Download progress display"""
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "?%").strip()
        speed = d.get("_speed_str", "?").strip()
        eta = d.get("_eta_str", "?").strip()
        print(f"\r  ⏬ {percent}  Speed: {speed}  ETA: {eta}   ", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\n  🎵 Audio extract ചെയ്യുന്നു...")


def download_playlist(playlist_url: str, output_dir: str = "downloads"):
    """YouTube Playlist മുഴുവൻ download ചെയ്യുന്നു"""
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "outtmpl": os.path.join(output_dir, "%(playlist_index)s - %(title)s.%(ext)s"),
        "quiet": False,
        "noplaylist": False,
        "progress_hooks": [progress_hook],
        "ignoreerrors": True,   # playlist-ൽ ഒരു video unavailable ആണെങ്കിൽ skip ചെയ്യും
    }

    print(f"\n📋 Playlist download: {playlist_url}")
    print(f"📁 Save location: {os.path.abspath(output_dir)}\n")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])
    print("\n✅ Playlist download complete!")


def batch_download(urls: list, output_dir: str = "downloads"):
    """Multiple URLs ഒരുമിച്ച് download ചെയ്യുന്നു"""
    success = 0
    fail = 0
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Processing...")
        if download_song(url.strip(), output_dir):
            success += 1
        else:
            fail += 1

    print(f"\n📊 Summary: ✅ {success} success | ❌ {fail} failed")


# ========== INTERACTIVE MODE ==========
def main():
    print("=" * 50)
    print("  🎵 Online Song Downloader")
    print("  YouTube, SoundCloud, Instagram, Facebook")
    print("=" * 50)

    print("\nMode select:")
    print("  1. Single song / video download")
    print("  2. Playlist download")
    print("  3. Batch download (multiple URLs)")
    print("  4. URL list from text file")

    choice = input("\nOption (1-4): ").strip()

    output_dir = input("Download folder [downloads]: ").strip() or "downloads"

    if choice == "1":
        url = input("URL paste ചെയ്യൂ: ").strip()
        quality = input("Quality kbps [192] (128/192/320/best): ").strip() or "192"
        download_song(url, output_dir, quality)

    elif choice == "2":
        url = input("Playlist URL: ").strip()
        download_playlist(url, output_dir)

    elif choice == "3":
        print("URLs enter ചെയ്യൂ (blank line കൊടുത്ത് finish ചെയ്യൂ):")
        urls = []
        while True:
            u = input().strip()
            if not u:
                break
            urls.append(u)
        if urls:
            batch_download(urls, output_dir)

    elif choice == "4":
        filepath = input("Text file path (ഓരോ line-ലും ഒരു URL): ").strip()
        try:
            with open(filepath, "r") as f:
                urls = [line.strip() for line in f if line.strip()]
            print(f"  {len(urls)} URLs found.")
            batch_download(urls, output_dir)
        except FileNotFoundError:
            print(f"❌ File not found: {filepath}")

    else:
        print("❌ Invalid option")


# ========== DIRECT USE EXAMPLE ==========
# Script-ൽ നേരിട്ട് URL കൊടുക്കാൻ:
#
#   download_song("https://www.youtube.com/watch?v=XXXXXXX")
#   download_playlist("https://www.youtube.com/playlist?list=XXXXXXX")
#   batch_download(["url1", "url2", "url3"])

if __name__ == "__main__":
    # Interactive mode
    main()

    # --- OR --- comment ചെയ്ത് direct call use ചെയ്യാം:
    # download_song("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "my_songs", "320")
