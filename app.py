import streamlit as st
import yt_dlp
import os
import tempfile
import glob

st.set_page_config(page_title="Cloud YT Downloader", page_icon="⬇️", layout="centered")

st.title("⬇️ YouTube Downloader")
st.caption("Streamlit Cloud Powered | Auto-Fallback Format Engine")

url = st.text_input("YouTube Video URL നൽകുക:", placeholder="https://www.youtube.com/watch?v=...")

col1, col2 = st.columns(2)
with col1:
    format_type = st.selectbox("Format തിരഞ്ഞെടുക്കുക:", ["MP3 (Audio)", "MP4 (Video)"])

with col2:
    if format_type == "MP3 (Audio)":
        quality = st.selectbox("Audio Quality:", ["128 kbps", "192 kbps", "320 kbps"], index=1)
    else:
        quality = st.selectbox("Video Quality:", ["Best Available", "720p", "480p", "360p"], index=0)

base_extractor_args = {
    'youtube': {
        'player_client': ['android', 'web', 'ios'],
    }
}

if url:
    try:
        meta_opts = {
            'quiet': True,
            'nocheckcertificate': True,
            'extractor_args': base_extractor_args,
        }
        
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

                    # Robust fallback format selectors
                    if format_type == "MP3 (Audio)":
                        bitrate = quality.split()[0]
                        format_str = "ba/b"  # Best audio fallback to best available stream
                        ydl_opts = {
                            'format': format_str,
                            'outtmpl': out_template,
                            'postprocessors': [{
                                'key': 'FFmpegExtractAudio',
                                'preferredcodec': 'mp3',
                                'preferredquality': bitrate,
                            }],
                            'quiet': True,
                            'nocheckcertificate': True,
                            'extractor_args': base_extractor_args,
                        }
                    else:
                        if quality == "Best Available":
                            format_str = "bv*+ba/b"
                        else:
                            height = quality.replace("p", "")
                            # Fallback: specific height -> smaller height -> any best stream
                            format_str = f"bv*[height<={height}]+ba/b[height<={height}]/bv*+ba/b"

                        ydl_opts = {
                            'format': format_str,
                            'outtmpl': out_template,
                            'merge_output_format': 'mp4',
                            'quiet': True,
                            'nocheckcertificate': True,
                            'extractor_args': base_extractor_args,
                        }

                    if os.path.exists('cookies.txt'):
                        ydl_opts['cookiefile'] = 'cookies.txt'

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
