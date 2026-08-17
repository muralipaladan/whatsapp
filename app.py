import streamlit as st
import yt_dlp
import os
import tempfile
import glob

st.set_page_config(page_title="Cloud YT Downloader", page_icon="⬇️", layout="centered")

st.title("⬇️ YouTube Downloader")
st.caption("Streamlit Cloud Powered | 403 Bypass Engine")

url = st.text_input("YouTube Video URL നൽകുക:", placeholder="https://www.youtube.com/watch?v=...")

col1, col2 = st.columns(2)
with col1:
    format_type = st.selectbox("Format തിരഞ്ഞെടുക്കുക:", ["MP3 (Audio)", "MP4 (Video)"])

with col2:
    if format_type == "MP3 (Audio)":
        quality = st.selectbox("Audio Quality:", ["128 kbps", "192 kbps", "320 kbps"], index=1)
    else:
        quality = st.selectbox("Video Quality:", ["720p", "480p", "360p"], index=0)

# Cloud bypass extractor configuration (iOS + mweb combo)
base_extractor_args = {
    'youtube': {
        'player_client': ['ios', 'mweb'],
        'player_skip': ['webpage', 'configs'],
    }
}

if url:
    try:
        meta_opts = {
            'quiet': True,
            'nocheckcertificate': True,
            'extractor_args': base_extractor_args,
        }
        
        # Check for cookies.txt
        if os.path.exists('cookies.txt'):
            meta_opts['cookiefile'] = 'cookies.txt'

        with yt_dlp.YoutubeDL(meta_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'YouTube_Media')
            thumb = info.get('thumbnail', '')
            uploader = info.get('uploader', 'Unknown')
            duration = info.get('duration', 0)

        st.markdown("---")
        c1, c2 = st.columns([1, 2])
        with c1:
            if thumb:
                st.image(thumb, use_container_width=True)
        with c2:
            st.subheader(title)
            st.caption(f"📺 Channel: {uploader} | ⏱️ Duration: {duration // 60}m {duration % 60}s")
        st.markdown("---")

        if st.button("🚀 ഡൗൺലോഡ് ഫയൽ തയ്യാറാക്കുക", use_container_width=True):
            with st.spinner("സെർവറിൽ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കൂ..."):
                with tempfile.TemporaryDirectory() as temp_dir:
                    out_template = os.path.join(temp_dir, "%(title).50s.%(ext)s")

                    ydl_opts = {
                        'outtmpl': out_template,
                        'quiet': True,
                        'nocheckcertificate': True,
                        'extractor_args': base_extractor_args,
                        'http_headers': {
                            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
                        }
                    }

                    if os.path.exists('cookies.txt'):
                        ydl_opts['cookiefile'] = 'cookies.txt'

                    if format_type == "MP3 (Audio)":
                        bitrate = quality.split()[0]
                        ydl_opts.update({
                            'format': 'bestaudio/best',
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': bitrate,
                            }]
                        })
                    else:
                        height = quality.split("p")[0]
                        ydl_opts.update({
                            'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
                            'merge_output_format': 'mp4'
                        })

                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])

                    downloaded_files = glob.glob(os.path.join(temp_dir, "*"))
                    
                    if downloaded_files:
                        file_path = downloaded_files[0]
                        file_name = os.path.basename(file_path)
                        mime_type = "audio/mp3" if format_type == "MP3 (Audio)" else "video/mp4"

                        with open(file_path, "rb") as f:
                            file_bytes = f.read()

                        st.success("✅ ഫയൽ തയ്യാറായിക്കഴിഞ്ഞു!")
                        st.download_button(
                            label=f"💾 Save {file_name}",
                            data=file_bytes,
                            file_name=file_name,
                            mime=mime_type,
                            use_container_width=True
                        )
                    else:
                        st.error("ഫയൽ പ്രോസസ്സ് ചെയ്യാൻ സാധിച്ചില്ല.")

    except Exception as e:
        st.error(f"Error: {e}")
        st.info("💡 നിർദ്ദേശം: YouTube സെർവർ IP ബ്ലോക്ക് തുടരുകയാണെങ്കിൽ, ഒരു `cookies.txt` ഫയൽ GitHub-ൽ ആഡ് ചെയ്യുക.")
