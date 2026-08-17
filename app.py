import streamlit as st
import re

st.set_page_config(page_title="Direct YT Downloader", page_icon="⬇️", layout="centered")

st.title("⬇️ YouTube Downloader")
st.caption("Client-Side Engine | No Server IP Blocking | High Speed")

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

url = st.text_input("YouTube Video URL നൽകുക:", placeholder="https://www.youtube.com/watch?v=kzpS-A3QJqE")

if url:
    vid_id = extract_video_id(url)
    if not vid_id:
        st.error("❌ സാധുവായ YouTube URL അല്ല.")
    else:
        st.markdown("---")
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(f"https://i.ytimg.com/vi/{vid_id}/mqdefault.jpg", use_container_width=True)
        with c2:
            st.subheader("Video Ready for Download")
            st.caption(f"ID: {vid_id}")
        st.markdown("---")

        # Client-Side Direct Download Component (Runs in User's Browser)
        downloader_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <style>
            body {{ font-family: sans-serif; background: transparent; color: #fff; margin: 0; padding: 0; }}
            .btn-grid {{ display: flex; flex-direction: column; gap: 12px; max-width: 480px; margin: 0 auto; }}
            .dl-btn {{
              display: flex;
              align-items: center;
              justify-content: center;
              gap: 10px;
              padding: 14px;
              border-radius: 8px;
              font-weight: 600;
              font-size: 15px;
              text-decoration: none;
              color: #ffffff;
              cursor: pointer;
              transition: transform 0.1s, opacity 0.2s;
              border: none;
            }}
            .dl-btn:hover {{ opacity: 0.9; transform: translateY(-1px); }}
            .btn-mp3 {{ background: linear-gradient(135deg, #7c6af7, #9333ea); }}
            .btn-mp4 {{ background: linear-gradient(135deg, #22c55e, #16a34a); }}
            .btn-alt {{ background: #1e293b; border: 1px solid #334155; color: #cbd5e1; }}
            .spin {{
              display: inline-block;
              width: 14px; height: 14px;
              border: 2px solid #fff;
              border-top-color: transparent;
              border-radius: 50%;
              animation: spin 0.6s linear infinite;
            }}
            @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
            #status-msg {{ margin-top: 12px; font-size: 13px; color: #94a3b8; text-align: center; }}
          </style>
        </head>
        <body>
          <div class="btn-grid">
            <button class="dl-btn btn-mp3" id="mp3-btn" onclick="fetchDownload('mp3')">
              🎵 Download MP3 (Audio)
            </button>
            <button class="dl-btn btn-mp4" id="mp4-btn" onclick="fetchDownload('mp4')">
              🎬 Download MP4 (Video - 720p)
            </button>
            
            <a class="dl-btn btn-alt" href="https://yt1s.com.co/en227/?url=https://www.youtube.com/watch?v={vid_id}" target="_blank">
              ⚡ Open in Alternative Server (Fast)
            </a>
          </div>

          <div id="status-msg"></div>

          <script>
            async function fetchDownload(fmt) {{
              const btn = document.getElementById(fmt + '-btn');
              const status = document.getElementById('status-msg');
              const originalText = btn.innerHTML;
              
              btn.innerHTML = '<span class="spin"></span> പ്രോസസ്സ് ചെയ്യുന്നു...';
              btn.style.pointerEvents = 'none';
              status.innerText = 'ഡൗൺലോഡ് സ്ട്രീം കണക്റ്റ് ചെയ്യുന്നു...';

              const payload = {{
                url: 'https://www.youtube.com/watch?v={vid_id}',
                downloadMode: fmt === 'mp3' ? 'audio' : 'auto',
                audioFormat: fmt === 'mp3' ? 'mp3' : undefined,
                videoQuality: fmt === 'mp4' ? '720' : undefined
              }};

              // List of active Client-Accessible Instances
              const apis = [
                'https://api.cobalt.tools',
                'https://cobalt-api.kwiatekm.tokyo',
                'https://co.wuk.sh',
                'https://cobalt.synzr.space'
              ];

              let success = false;

              for (const api of apis) {{
                try {{
                  const res = await fetch(api, {{
                    method: 'POST',
                    headers: {{ 'Accept': 'application/json', 'Content-Type': 'application/json' }},
                    body: JSON.stringify(payload)
                  }});

                  if (res.ok) {{
                    const data = await res.json();
                    if (data.url) {{
                      status.innerHTML = '✅ <span style="color:#22c55e;">ഡൗൺലോഡ് ആരംഭിച്ചു!</span>';
                      window.open(data.url, '_blank');
                      success = true;
                      break;
                    }}
                  }}
                }} catch (e) {{
                  continue;
                }}
              }}

              if (!success) {{
                status.innerHTML = '⚠️ ഡയറക്ട് കണക്ഷൻ കിട്ടിയില്ല, ദയവായി താഴെയുള്ള "Alternative Server" ഉപയോഗിക്കുക.';
              }}

              btn.innerHTML = originalText;
              btn.style.pointerEvents = 'auto';
            }}
          </script>
        </body>
        </html>
        """

        st.components.v1.html(downloader_html, height=220)
