import streamlit as st
import requests
import re

st.set_page_config(page_title="Fast YT Downloader", page_icon="⬇️", layout="centered")

st.title("⬇️ YouTube Downloader")
st.caption("YT1s Engine Powered | No Cookies Required | 100% Cloud Working")

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

def fetch_yt1s_data(yt_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://yt1s.com.co/'
    }
    
    # 1. Fetch available formats
    search_url = "https://yt1s.com.co/api/ajaxSearch/index"
    payload = {'q': yt_url, 'vt': 'home'}
    
    res = requests.post(search_url, data=payload, headers=headers, timeout=15)
    return res.json()

def get_direct_download_link(vid_id, k_key):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://yt1s.com.co/'
    }
    convert_url = "https://yt1s.com.co/api/ajaxConvert/convert"
    payload = {'vid': vid_id, 'k': k_key}
    
    res = requests.post(convert_url, data=payload, headers=headers, timeout=20)
    return res.json()

url = st.text_input("YouTube Video URL നൽകുക:", placeholder="https://www.youtube.com/watch?v=kzpS-A3QJqE")

if url:
    vid_id = extract_video_id(url)
    if not vid_id:
        st.error("❌ സാധുവായ YouTube URL അല്ല. ദയവായി പരിശോധിക്കുക.")
    else:
        full_yt_url = f"https://www.youtube.com/watch?v={vid_id}"
        
        with st.spinner("വീഡിയോ വിവരങ്ങൾ ശേഖരിക്കുന്നു..."):
            try:
                data = fetch_yt1s_data(full_yt_url)
                
                if data.get('status') == 'ok':
                    title = data.get('title', 'YouTube Video')
                    author = data.get('a', 'YouTube Channel')
                    
                    st.markdown("---")
                    c1, c2 = st.columns([1, 2])
                    with c1:
                        st.image(f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg", use_container_width=True)
                    with c2:
                        st.subheader(title)
                        st.caption(f"📺 {author}")
                    st.markdown("---")
                    
                    # ഫോർമാറ്റുകൾ വേർതിരിക്കുക (MP3 & MP4)
                    links = data.get('links', {})
                    mp4_formats = links.get('mp4', {})
                    mp3_formats = links.get('mp3', {})
                    
                    fmt_choice = st.radio("Format തിരഞ്ഞെടുക്കുക:", ["🎬 MP4 (Video)", "🎵 MP3 (Audio)"], horizontal=True)
                    
                    selected_k = None
                    selected_label = ""
                    
                    if "MP4" in fmt_choice:
                        options = {}
                        for key, val in mp4_formats.items():
                            label = f"{val.get('q', 'Video')} ({val.get('size', 'N/A')})"
                            options[label] = val.get('k')
                        
                        if options:
                            chosen_opt = st.selectbox("Video Quality:", list(options.keys()))
                            selected_k = options[chosen_opt]
                            selected_label = chosen_opt
                    else:
                        options = {}
                        for key, val in mp3_formats.items():
                            label = f"MP3 - {val.get('q', 'Audio')} ({val.get('size', 'N/A')})"
                            options[label] = val.get('k')
                            
                        if options:
                            chosen_opt = st.selectbox("Audio Quality:", list(options.keys()))
                            selected_k = options[chosen_opt]
                            selected_label = chosen_opt
                    
                    if selected_k and st.button("🚀 ഡൗൺലോഡ് ലിങ്ക് തയ്യാറാക്കുക", use_container_width=True):
                        with st.spinner("ഡൗൺലോഡ് ലിങ്ക് ജനറേറ്റ് ചെയ്യുന്നു..."):
                            conv_res = get_direct_download_link(vid_id, selected_k)
                            
                            if conv_res.get('status') == 'ok' and 'dlink' in conv_res:
                                dlink = conv_res['dlink']
                                st.success("✅ ഡൗൺലോഡ് ലിങ്ക് തയ്യാർ!")
                                st.markdown(
                                    f'<a href="{dlink}" target="_blank" style="display:block; text-align:center; background:#22c55e; color:white; padding:12px; border-radius:8px; text-decoration:none; font-weight:bold; font-size:16px;">⬇️ Click Here to Download ({selected_label})</a>',
                                    unsafe_allow_html=True
                                )
                            else:
                                st.error("ഡൗൺലോഡ് ലിങ്ക് എടുക്കാൻ കഴിഞ്ഞില്ല. വീണ്ടും ശ്രമിക്കുക.")
                else:
                    st.error("വീഡിയോ ലഭ്യമാക്കാൻ സാധിച്ചില്ല. URL ശരിയാണോ എന്ന് പരിശോധിക്കുക.")
            except Exception as e:
                st.error(f"Error: {e}")
