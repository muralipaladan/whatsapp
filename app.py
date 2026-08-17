import streamlit as st
import yt_dlp
import os, re, tempfile

st.set_page_config(page_title="🎵 Song Downloader", page_icon="🎵", layout="centered")

st.markdown("""
<style>
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white; border: none; border-radius: 8px; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.title("🎵 Song Downloader")
st.caption("YouTube-ൽ search ചെയ്ത് MP3 / MP4 download ചെയ്യൂ")

def search_songs(query, max_results=8):
    """yt-dlp search — android_music + android client chain"""
    opts = {
        "quiet": True,
        "extract_flat": True,
        "no_check_certificate": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android_music", "android", "web"],
            }
        },
        "http_headers": {
            "User-Agent": "com.google.android.apps.youtube.music/5.34.51 (Linux; U; Android 11) gzip",
        },
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        res = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        entries = res.get("entries") or []
        return [
            {
                "id": e.get("id", ""),
                "title": e.get("title", "?"),
                "artist": e.get("uploader", ""),
                "duration": fmt_dur(e.get("duration")),
                "thumbnail": (
                    e.get("thumbnail")
                    or f"https://i.ytimg.com/vi/{e.get('id','')}/mqdefault.jpg"
                ),
            }
            for e in entries if e and e.get("id")
        ]


# ─── Download ───────────────────────────────────────────────────────────────
def download_track(video_id, fmt, quality="192"):
    url = f"https://www.youtube.com/watch?v={video_id}"
    tmp = tempfile.mkdtemp()

    base_opts = {
        "quiet": True,
        "no_check_certificate": True,
        "extractor_args": {"youtube": {"player_client": ["android_music", "android", "web"]}},
        "http_headers": {
            "User-Agent": "com.google.android.apps.youtube.music/5.34.51 (Linux; U; Android 11) gzip",
        },
        "outtmpl": os.path.join(tmp, "%(title)s.%(ext)s"),
    }

    if fmt == "mp3":
        opts = {
            **base_opts,
            "format": "bestaudio/best",
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": quality}],
        }
        ext, mime = "mp3", "audio/mpeg"
    else:
        opts = {
            **base_opts,
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
        }
        ext, mime = "mp4", "video/mp4"

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = re.sub(r'[\\/*?:"<>|]', "", info.get("title", "song"))

    for f in os.listdir(tmp):
        if f.endswith(ext):
            with open(os.path.join(tmp, f), "rb") as fh:
                return fh.read(), f"{title}.{ext}", mime

    raise FileNotFoundError("Downloaded file not found")


def fmt_dur(s):
    if not s: return ""
    try:
        m, sec = divmod(int(s), 60)
        return f"{m}:{sec:02d}"
    except: return str(s)


# ─── UI ─────────────────────────────────────────────────────────────────────
if "results"  not in st.session_state: st.session_state.results  = []
if "selected" not in st.session_state: st.session_state.selected = None

c1, c2 = st.columns([4, 1])
with c1:
    query = st.text_input("", placeholder="Song / Artist / Movie...", label_visibility="collapsed")
with c2:
    do_search = st.button("🔍 Search")

fmt   = st.radio("Format", ["🎵 MP3", "🎬 MP4"], horizontal=True)
mp3_q = st.select_slider("Quality (kbps)", ["128","192","320"], value="192") if "MP3" in fmt else None

if do_search and query:
    with st.spinner("Searching..."):
        try:
            st.session_state.results  = search_songs(query)
            st.session_state.selected = None
            if not st.session_state.results:
                st.warning("Results കിട്ടിയില്ല — വേറൊരു query try ചെയ്യൂ.")
        except Exception as e:
            st.error(f"Search error: {e}")

if st.session_state.results:
    st.markdown("---")
    st.markdown("**Results:**")
    for i, e in enumerate(st.session_state.results):
        col_img, col_info, col_btn = st.columns([1, 4, 1.5])
        with col_img:
            st.image(e["thumbnail"], width=80)
        with col_info:
            st.markdown(f"**{e['title']}**")
            st.caption(f"{e['artist']}  •  {e['duration']}")
        with col_btn:
            if st.button("✅ Select", key=f"sel{i}"):
                st.session_state.selected = e

if st.session_state.selected:
    sel = st.session_state.selected
    st.markdown("---")
    st.success(f"🎵 **{sel['title']}** — {sel['artist']}")
    fmt_type = "mp3" if "MP3" in fmt else "mp4"

    if st.button(f"⬇️ Download {fmt_type.upper()}"):
        with st.spinner("Downloading... ⏳ (30–60 sec)"):
            try:
                data, filename, mime = download_track(sel["id"], fmt_type, mp3_q or "192")
                st.download_button(f"💾 Save — {filename}", data=data,
                                   file_name=filename, mime=mime)
                st.balloons()
            except Exception as e:
                st.error(f"Download failed: {e}")
                st.info("💡 മറ്റൊരു song try ചെയ്യൂ അല്ലെങ്കിൽ കുറച്ചു കഴിഞ്ഞ് retry ചെയ്യൂ.")
