import streamlit as st
import yt_dlp
import os
import tempfile
import re

st.set_page_config(
    page_title="🎵 Song Downloader",
    page_icon="🎵",
    layout="centered"
)

st.markdown("""
<style>
.main { max-width: 700px; margin: auto; }
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.6em 1em;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
}
.stButton > button:hover { opacity: 0.9; }
.result-card {
    background: #1e1e2e;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: 0.5rem 0;
    border: 1px solid #333;
    cursor: pointer;
}
.result-title { font-weight: 600; font-size: 1rem; color: #e0e0e0; }
.result-meta { font-size: 0.8rem; color: #888; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

st.title("🎵 Song Downloader")
st.caption("Song name search ചെയ്ത് MP3 / MP4 download ചെയ്യൂ")

# --- Search ---
col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("", placeholder="Song name / Artist / Movie...", label_visibility="collapsed")
with col2:
    search_btn = st.button("🔍 Search")

fmt = st.radio("Format", ["🎵 MP3 (Audio)", "🎬 MP4 (Video)"], horizontal=True)
quality_mp3 = st.select_slider("MP3 Quality", options=["128", "192", "320"], value="192") if "MP3" in fmt else None


def search_youtube(query, max_results=8):
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "default_search": "ytsearch",
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        return results.get("entries", [])


def format_duration(seconds):
    if not seconds:
        return "?"
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def format_views(n):
    if not n:
        return ""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M views"
    if n >= 1_000:
        return f"{n/1_000:.0f}K views"
    return f"{n} views"


def download_track(url, fmt_type, mp3_quality="192"):
    tmp_dir = tempfile.mkdtemp()

    if fmt_type == "mp3":
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": mp3_quality,
            }],
            "outtmpl": os.path.join(tmp_dir, "%(title)s.%(ext)s"),
            "quiet": True,
        }
        ext = "mp3"
        mime = "audio/mpeg"
    else:
        ydl_opts = {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "outtmpl": os.path.join(tmp_dir, "%(title)s.%(ext)s"),
            "quiet": True,
            "merge_output_format": "mp4",
        }
        ext = "mp4"
        mime = "video/mp4"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = re.sub(r'[\\/*?:"<>|]', "", info.get("title", "song"))

    # Find downloaded file
    for f in os.listdir(tmp_dir):
        if f.endswith(ext):
            filepath = os.path.join(tmp_dir, f)
            with open(filepath, "rb") as fh:
                data = fh.read()
            return data, f"{title}.{ext}", mime

    raise FileNotFoundError("Downloaded file not found")


# --- Session state ---
if "results" not in st.session_state:
    st.session_state.results = []
if "selected" not in st.session_state:
    st.session_state.selected = None

# --- Search action ---
if search_btn and query:
    with st.spinner("🔍 Searching..."):
        try:
            st.session_state.results = search_youtube(query)
            st.session_state.selected = None
        except Exception as e:
            st.error(f"Search failed: {e}")

# --- Show results ---
if st.session_state.results:
    st.markdown("---")
    st.markdown("**Results — ഒരു song select ചെയ്യൂ:**")

    for i, entry in enumerate(st.session_state.results):
        if not entry:
            continue
        title = entry.get("title", "Unknown")
        duration = format_duration(entry.get("duration"))
        views = format_views(entry.get("view_count"))
        uploader = entry.get("uploader", "")
        thumb = entry.get("thumbnail", "")
        url = entry.get("url") or f"https://www.youtube.com/watch?v={entry.get('id', '')}"

        col_img, col_info, col_btn = st.columns([1, 4, 1.5])
        with col_img:
            if thumb:
                st.image(thumb, width=80)
        with col_info:
            st.markdown(f"**{title}**")
            st.caption(f"⏱ {duration}  •  {uploader}  •  {views}")
        with col_btn:
            if st.button("Select", key=f"sel_{i}"):
                st.session_state.selected = {"url": url, "title": title}

# --- Download section ---
if st.session_state.selected:
    sel = st.session_state.selected
    st.markdown("---")
    st.success(f"✅ Selected: **{sel['title']}**")

    fmt_type = "mp3" if "MP3" in fmt else "mp4"
    label = f"⬇️ Download {fmt_type.upper()}"

    if st.button(label):
        with st.spinner(f"Downloading {fmt_type.upper()}... ⏳"):
            try:
                data, filename, mime = download_track(
                    sel["url"], fmt_type,
                    mp3_quality=quality_mp3 or "192"
                )
                st.download_button(
                    label=f"💾 Save {filename}",
                    data=data,
                    file_name=filename,
                    mime=mime,
                )
                st.balloons()
            except Exception as e:
                st.error(f"Download failed: {e}")
                st.info("YouTube restrictions മൂലം ചില songs download ആകാറില്ല.")
