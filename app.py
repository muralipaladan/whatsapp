import streamlit as st
import requests
import re
import urllib.parse

st.set_page_config(page_title="Universal YT Downloader", page_icon="⬇️", layout="centered")

st.title("⬇️ YouTube Downloader")
st.caption("Multi-Server Fast Engine | No Cookies Required")

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

def fetch_oembed_info(vid_id):
    try:
        r = requests.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid_id}&format=json", timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

# Method 1: Public Cobalt instances
def try_cobalt(yt_url, is_audio=False):
    cobalt_servers = [
        "https://cobalt-api.kwiatekm.tokyo",
        "https://api.cobalt.tools",
        "https://cobalt.synzr.space"
    ]
    payload = {
        "url": yt_url,
        "downloadMode": "audio" if is_audio else "auto",
        "audioFormat": "mp3" if is_audio else None,
        "videoQuality": "720" if not is_audio else None
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    for srv in cobalt_servers:
        try:
            res = requests.post(srv, json=payload, headers=headers, timeout=8)
            if res.status_code == 200:
                data = res.json()
                if "url" in data:
                    return data["url"]
        except Exception:
            continue
    return None

url = st.text_input("YouTube Video URL നൽകുക:", placeholder="https://www.youtube.com/watch?v=kzpS-A3QJqE")

if url:
    vid_id = extract_video_id(url)
    if not vid_id:
        st.error("❌ സാധുവായ YouTube URL നൽകുക.")
    else:
        full_yt_url = f"https://www.youtube.com/watch?v={vid_id}"
        meta = fetch_oembed_info(vid_id)
        title = meta.get("title", "YouTube Video")
        author = meta.get("author_name", "YouTube Channel")

        st.markdown("---")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg", use_container_width=True)
        with c2:
            st.subheader(title)
            st.caption(f"📺 {author}")
        st.markdown("---")

        fmt_choice = st.radio("Format തിരഞ്ഞെടുക്കുക:", ["🎵 MP3 (Audio)", "🎬 MP4 (Video)"], horizontal=True)
        is_audio = "MP3" in fmt_choice

        if st.button("🚀 ഡൗൺലോഡ് ലിങ്ക് എടുക്കുക", use_container_width=True):
            with st.spinner("സെർവറിൽ നിന്ന് ഡൗൺലോഡ് ലിങ്ക് എടുക്കുന്നു..."):
                dl_link = try_cobalt(full_yt_url, is_audio=is_audio)

                if dl_link:
                    st.success("✅ ഡൗൺലോഡ് ലിങ്ക് തയ്യാർ!")
                    st.markdown(
                        f'<a href="{dl_link}" target="_blank" style="display:block; text-align:center; background:#22c55e; color:white; padding:12px; border-radius:8px; text-decoration:none; font-weight:bold; font-size:16px;">⬇️ Click Here to Download ({fmt_choice.split()[1]})</a>',
                        unsafe_allow_html=True
                    )
                else:
                    st.warning("⚠️ ഡയറക്ട് സെർവർ ബിസിയാണ്. താഴെയുള്ള ഫാസ്റ്റ് ഡൗൺലോഡ് ബട്ടണുകൾ ഉപയോഗിക്കുക:")
                    
                    encoded_url = urllib.parse.quote(full_yt_url, safe='')
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown(
                            f'<a href="https://yt1s.com.co/en227/?url={encoded_url}" target="_blank" style="display:block; text-align:center; background:#7c6af7; color:white; padding:10px; border-radius:6px; text-decoration:none; font-weight:600;">🌐 Open in YT1s</a>',
                            unsafe_allow_html=True
                        )
                    with col_b:
                        st.markdown(
                            f'<a href="https://y2mate.nu/en/?url={encoded_url}" target="_blank" style="display:block; text-align:center; background:#0284c7; color:white; padding:10px; border-radius:6px; text-decoration:none; font-weight:600;">⚡ Open in Y2Mate</a>',
                            unsafe_allow_html=True
                        )
