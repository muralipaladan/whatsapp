import streamlit as st
import requests
import re

st.set_page_config(page_title="Direct YT Downloader", page_icon="⬇️", layout="centered")

st.title("⬇️ YouTube Direct Downloader")
st.caption("High-Speed Direct Stream | No External Links")

def extract_video_id(url):
    patterns = [
        r'(?:v=|\/embed\/|\/shorts\/|youtu\.be\/)([A-Za-z0-9_-]{11})',
        r'^([A-Za-z0-9_-]{11})$'
    ]
    for pattern in patterns:
        match = re.search(pattern, url.strip())
        if match:
            return match.group(1)
    return None

# Piped / Invidious reliable public instances
INVIDIOUS_INSTANCES = [
    "https://api.piped.private.coffee",
    "https://pipedapi.kavin.rocks",
    "https://api.piped.projectsegfau.lt",
    "https://inv.tux.pizza/api/v1",
    "https://invidious.nerdvpn.de/api/v1"
]

def fetch_stream_data(vid_id):
    # Try Piped instances first
    for base in [
        "https://api.piped.private.coffee",
        "https://pipedapi.kavin.rocks",
        "https://api.piped.projectsegfau.lt"
    ]:
        try:
            res = requests.get(f"{base}/streams/{vid_id}", timeout=6)
            if res.status_code == 200:
                data = res.json()
                return {
                    "type": "piped",
                    "title": data.get("title", "YouTube Video"),
                    "uploader": data.get("uploader", "Channel"),
                    "audio": data.get("audioStreams", []),
                    "video": data.get("videoStreams", [])
                }
        except Exception:
            continue

    # Fallback to Invidious instances
    for base in [
        "https://inv.tux.pizza/api/v1",
        "https://invidious.nerdvpn.de/api/v1"
    ]:
        try:
            res = requests.get(f"{base}/videos/{vid_id}", timeout=6)
            if res.status_code == 200:
                data = res.json()
                return {
                    "type": "invidious",
                    "title": data.get("title", "YouTube Video"),
                    "uploader": data.get("author", "Channel"),
                    "audio": [f for f in data.get("formatStreams", []) if "audio" in f.get("type", "")],
                    "video": [f for f in data.get("formatStreams", []) if "video" in f.get("type", "")]
                }
        except Exception:
            continue
    return None

url = st.text_input("YouTube Video URL നൽകുക:", placeholder="https://www.youtube.com/watch?v=kzpS-A3QJqE")

if url:
    vid_id = extract_video_id(url)
    if not vid_id:
        st.error("❌ സാധുവായ YouTube URL അല്ല.")
    else:
        with st.spinner("സ്ട്രീം ഡാറ്റ ലഭ്യമാക്കുന്നു..."):
            stream_data = fetch_stream_data(vid_id)

        if stream_data:
            title = stream_data["title"]
            uploader = stream_data["uploader"]

            st.markdown("---")
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg", use_container_width=True)
            with c2:
                st.subheader(title)
                st.caption(f"📺 {uploader}")
            st.markdown("---")

            fmt_type = st.radio("Format തിരഞ്ഞെടുക്കുക:", ["🎵 Audio (MP3 / M4A)", "🎬 Video (MP4)"], horizontal=True)

            if "Audio" in fmt_type:
                audio_list = stream_data["audio"]
                if audio_list:
                    # Select best quality audio stream
                    best_audio = audio_list[0]
                    audio_url = best_audio.get("url")
                    quality_label = best_audio.get("quality", "High Quality Audio")

                    st.markdown(
                        f"""
                        <div style="background:#1e293b; padding:16px; border-radius:10px; text-align:center;">
                            <p style="color:#94a3b8; font-size:14px; margin-bottom:10px;">Audio സ്ട്രീം തയ്യാറാണ് ({quality_label})</p>
                            <a href="{audio_url}" download="{title}.mp3" target="_blank" 
                               style="display:inline-block; background:#22c55e; color:white; padding:12px 24px; border-radius:8px; text-decoration:none; font-weight:bold; font-size:16px;">
                               ⬇️ Download Audio (Direct Stream)
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("ഓഡിയോ സ്ട്രീം ലഭ്യമായില്ല.")

            else:
                video_list = [v for v in stream_data["video"] if v.get("videoOnly") is False or stream_data["type"] == "invidious"]
                if not video_list:
                    video_list = stream_data["video"]

                if video_list:
                    # Map available resolutions
                    quality_options = {}
                    for v in video_list:
                        label = v.get("quality", "Standard") + " (" + v.get("format", "mp4") + ")"
                        quality_options[label] = v.get("url")

                    selected_q = st.selectbox("Video Resolution:", list(quality_options.keys()))
                    direct_video_url = quality_options[selected_q]

                    st.markdown(
                        f"""
                        <div style="background:#1e293b; padding:16px; border-radius:10px; text-align:center; margin-top:10px;">
                            <a href="{direct_video_url}" download="{title}.mp4" target="_blank" 
                               style="display:inline-block; background:#3b82f6; color:white; padding:12px 24px; border-radius:8px; text-decoration:none; font-weight:bold; font-size:16px;">
                               ⬇️ Download Video ({selected_q})
                            </a>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("വീഡിയോ സ്ട്രീം ലഭ്യമായില്ല.")
        else:
            st.error("❌ സ്ട്രീം കണക്റ്റ് ചെയ്യാൻ കഴിഞ്ഞില്ല. വീണ്ടും ശ്രമിക്കുക.")
