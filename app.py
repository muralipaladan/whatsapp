import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# --- കോൺഫിഗറേഷൻ ---
CSV_FILE = "contacts.csv"

# Green API Credentials (Streamlit Secrets വഴിയോ നേരിട്ടോ നൽകാം)
ID_INSTANCE = st.secrets.get("GREEN_API_ID", "YOUR_INSTANCE_ID")
API_TOKEN_INSTANCE = st.secrets.get("GREEN_API_TOKEN", "YOUR_API_TOKEN")

# --- WhatsApp അയക്കുന്ന ഫംഗ്ഷൻ ---
def send_whatsapp_message(phone_number, message):
    url = f"https://api.green-api.com/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN_INSTANCE}"
    payload = {
        "chatId": f"{phone_number}@c.us",
        "message": message
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

# --- ഷെഡ്യൂൾ ചെക്ക് ചെയ്യുന്ന ബാക്ക്ഗ്രൗണ്ട് ടാസ്ക് ---
def check_and_send_scheduled_wishes():
    if not os.path.exists(CSV_FILE):
        return
    
    today = datetime.now().strftime("%m-%d")
    df = pd.read_csv(CSV_FILE)
    
    for _, row in df.iterrows():
        # Date ഫോർമാറ്റ് MM-DD ആയിരിക്കണം
        if str(row.get("date")).strip() == today:
            name = row.get("name")
            phone = str(row.get("phone")).replace("+", "").strip()
            custom_msg = row.get("message")
            
            full_message = f"Hello {name},\n\n{custom_msg}"
            send_whatsapp_message(phone, full_message)
            print(f"[Scheduler] Sent wish to {name} ({phone})")

# --- ബാക്ക്ഗ്രൗണ്ട് ഷെഡ്യൂളർ സ്റ്റാർട്ട് ചെയ്യൽ (Single Instance) ---
@st.cache_resource
def start_background_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    # എല്ലാ ദിവസവും രാവിലെ 8:00 മണിക്ക് റൺ ചെയ്യുന്നു
    scheduler.add_job(check_and_send_scheduled_wishes, 'cron', hour=8, minute=0)
    scheduler.start()
    return scheduler

# ഷെഡ്യൂളർ സജീവമാക്കുന്നു
scheduler = start_background_scheduler()

# --- UI (Streamlit Frontend) ---
st.set_page_config(page_title="WhatsApp Schedule Bot", page_icon="📅", layout="wide")
st.title("📅 WhatsApp Schedule & Wishes Manager")

# CSV ഫയൽ ലോഡ് ചെയ്യുക
if os.path.exists(CSV_FILE):
    df_contacts = pd.read_csv(CSV_FILE, dtype={"phone": str, "date": str})
else:
    df_contacts = pd.DataFrame(columns=["name", "phone", "date", "message"])
    df_contacts.to_csv(CSV_FILE, index=False)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("➕ പുതിയ ഷെഡ്യൂൾ ചേർക്കുക")
    with st.form("add_contact_form", clear_on_submit=True):
        name = st.text_input("പേര് (Name)")
        phone = st.text_input("WhatsApp നമ്പർ (Country Code സഹിതം, e.g. 919876543210)")
        selected_date = st.date_input("തീയതി (Date)")
        message = st.text_area("ആശംസ / സന്ദേശം", placeholder="Happy Birthday! Have a great year ahead.")
        
        submitted = st.form_submit_button("സേവ് ചെയ്യുക")
        if submitted:
            if name and phone and message:
                date_str = selected_date.strftime("%m-%d")
                new_data = pd.DataFrame([[name, phone, date_str, message]], columns=["name", "phone", "date", "message"])
                df_contacts = pd.concat([df_contacts, new_data], ignore_index=True)
                df_contacts.to_csv(CSV_FILE, index=False)
                st.success(f"{name}-ന്റെ ഷെഡ്യൂൾ വിജയകരമായി ചേർത്തു!")
                st.rerun()
            else:
                st.error("എല്ലാ കോളങ്ങളും പൂരിപ്പിക്കുക!")

with col2:
    st.subheader("📋 നിലവിലുള്ള ഷെഡ്യൂളുകൾ")
    st.dataframe(df_contacts, use_container_width=True)
    
    # മാന്വൽ ടെസ്റ്റിംഗ് ഓപ്ഷൻ
    st.divider()
    st.write("🧪 **ടെസ്റ്റ് ചെയ്യാൻ (Manual Trigger):**")
    if st.button("ഇന്നത്തെ ഷെഡ്യൂളുകൾ ഇപ്പോൾ തന്നെ അയക്കുക"):
        check_and_send_scheduled_wishes()
        st.info("ഇന്നത്തെ തീയതിയിലുള്ള മെസ്സേജുകൾ അയച്ചു കഴിഞ്ഞു (ലോഗ് പരിശോധിക്കുക).")
