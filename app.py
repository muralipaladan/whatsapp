import streamlit as st
import yt_dlp
import os
import re
import tempfile

st.set_page_config(page_title="🎵 Song Downloader", page_icon="🎵", layout="centered")

st.markdown("""
<style>
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none;
    border-radius: 8px; font-weight: 600;
}
.thumb-row { display: flex; align-items: center; gap: 12px; padding: 8px 0; border-bottom: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

st.title("🎵 Song Downloader")
st.caption("YouTube-ൽ search ചെയ്ത് MP3 / MP4 download ചെയ്യൂ")

# --- Shared yt-dlp opts (bypass 403) ---
BASE_OPTS = {
    "quiet": True,
    "no_check_certificate": True,
    "extractor_args": {
        "youtube": {
            "player_client": ["android_music", "android", "web"],
        }
    },
    "http_headers": {
        "User-Agent": (
            "com.google.android.apps.youtube.music/"
            "5.34.51 (Linux; U; Android 11) gzip"
        ),
    },
}

# ── Search ──────────────────────────────────────────────
def search_youtube(query, n=8):
    opts = {**BASE_OPTS, "extract_flat": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        res = ydl.extract_info(f"ytsearch{n}:{query}", download=False)
        return res.get("entries", []) or []

# ── Download ────────────────────────────────────────────
def download_track(video_id, fmt, quality="192"):
    url = f"https://www.youtube.com/watch?v={video_id}"
    tmp = tempfile.mkdtemp()

    if fmt == "mp3":
        opts = {
            **BASE_OPTS,
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }],
            "outtmpl": os.path.join(tmp, "%(title)s.%(ext)s"),
        }
        ext, mime = "mp3", "audio/mpeg"
    else:
        opts = {
            **BASE_OPTS,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(tmp, "%(title)s.%(ext)s"),
        }
        ext, mime = "mp4", "video/mp4"

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = re.sub(r'[\\/*?:"<>|]', "", info.get("title", "song"))

    for f in os.listdir(tmp):
        if f.endswith(ext):
            with open(os.path.join(tmp, f), "rb") as fh:
                return fh.read(), f"{title}.{ext}", mime

    raise FileNotFoundError("File not found after download")

# ── Helpers ─────────────────────────────────────────────
def fmt_dur(s):
    if not s: return "?"
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"

def fmt_views(n):
    if not n: return ""
    return f"{n/1e6:.1f}M" if n >= 1e6 else (f"{n/1e3:.0f}K" if n >= 1e3 else str(n))

# ── UI ──────────────────────────────────────────────────
if "results" not in st.session_state: st.session_state.results = []
if "selected" not in st.session_state: st.session_state.selected = None

col1, col2 = st.columns([4, 1])
with col1:
    query = st.text_input("", placeholder="Song / Artist / Movie...", label_visibility="collapsed")
with col2:
    do_search = st.button("🔍 Search")

fmt = st.radio("Format", ["🎵 MP3", "🎬 MP4"], horizontal=True)
mp3_q = None
if "MP3" in fmt:
    mp3_q = st.select_slider("Quality (kbps)", ["128", "192", "320"], value="192")

if do_search and query:
    with st.spinner("Searching..."):
        try:
            st.session_state.results = search_youtube(query)
            st.session_state.selected = None
        except Exception as e:
            st.error(f"Search error: {e}")

# Results
if st.session_state.results:
    st.markdown("---")
    st.markdown("**Results — select ചെയ്യൂ:**")
    for i, e in enumerate(st.session_state.results):
        if not e: continue
        c1, c2, c3 = st.columns([1, 4, 1.5])
        with c1:
            thumb = e.get("thumbnail") or f"https://i.ytimg.com/vi/{e.get('id','')}/mqdefault.jpg"
            st.image(thumb, width=80)
        with c2:
            st.markdown(f"**{e.get('title','?')}**")
            st.caption(f"⏱ {fmt_dur(e.get('duration'))}  •  {e.get('uploader','')}  •  {fmt_views(e.get('view_count'))} views")
        with c3:
            if st.button("✅ Select", key=f"s{i}"):
                st.session_state.selected = {"id": e.get("id"), "title": e.get("title","song")}

# Download
if st.session_state.selected:
    sel = st.session_state.selected
    st.markdown("---")
    st.success(f"🎵 Selected: **{sel['title']}**")
    fmt_type = "mp3" if "MP3" in fmt else "mp4"

    if st.button(f"⬇️ Download {fmt_type.upper()}"):
        with st.spinner(f"Downloading {fmt_type.upper()}... ⏳ (30–60 sec)"):
            try:
                data, filename, mime = download_track(sel["id"], fmt_type, mp3_q or "192")
                st.download_button(
                    label=f"💾 Save — {filename}",
                    data=data,
                    file_name=filename,
                    mime=mime,
                )
                st.balloons()
            except Exception as e:
                st.error(f"Download failed: {e}")
                st.info("💡 മറ്റൊരു song try ചെയ്യൂ, അല്ലെങ്കിൽ കുറച്ചു നേരം കഴിഞ്ഞ് retry ചെയ്യൂ.")
