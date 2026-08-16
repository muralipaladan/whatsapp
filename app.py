import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler

# --- കോൺഫിഗറേഷൻ ---
CSV_FILE = "contacts.csv"

# Green API Credentials
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
        print(f"Error sending to {phone_number}: {e}")
        return False

# --- ഷെഡ്യൂൾ ചെക്ക് ചെയ്യുന്ന ബാക്ക്ഗ്രൗണ്ട് ടാസ്ക് (ഓരോ മിനിറ്റിലും റൺ ചെയ്യും) ---
def check_and_send_scheduled_wishes():
    if not os.path.exists(CSV_FILE):
        return
    
    now = datetime.now()
    today_date = now.strftime("%m-%d")    # ഉദാ: 08-16
    current_time = now.strftime("%H:%M")  # ഉദാ: 08:30, 14:00 (24-hour)
    current_year_date = now.strftime("%Y-%m-%d")

    df = pd.read_csv(CSV_FILE, dtype=str).fillna("")
    updated = False

    for idx, row in df.iterrows():
        row_date = str(row.get("date", "")).strip()
        row_time = str(row.get("time", "")).strip()
        last_sent = str(row.get("last_sent", "")).strip()

        # തീയതിയും സമയവും ഒത്തുവരികയും, ഇന്ന് ഇതിനകം അയച്ചിട്ടില്ലെങ്കിൽ മാത്രം അയക്കുക
        if row_date == today_date and row_time == current_time:
            if last_sent != current_year_date:
                name = row.get("name")
                phone = str(row.get("phone")).replace("+", "").strip()
                custom_msg = row.get("message")

                full_message = f"Hello {name},\n\n{custom_msg}"
                success = send_whatsapp_message(phone, full_message)
                
                if success:
                    print(f"[Scheduler] Sent wish to {name} ({phone}) at {current_time}")
                    df.at[idx, "last_sent"] = current_year_date
                    updated = True

    if updated:
        df.to_csv(CSV_FILE, index=False)

# --- ബാക്ക്ഗ്രൗണ്ട് ഷെഡ്യൂളർ സ്റ്റാർട്ട് ചെയ്യൽ ---
@st.cache_resource
def start_background_scheduler():
    scheduler = BackgroundScheduler(timezone="Asia/Kolkata")
    # ഓരോ മിനിറ്റിലും സമയം ഒത്തുനോക്കാൻ ചെക്ക് ചെയ്യുന്നു
    scheduler.add_job(check_and_send_scheduled_wishes, 'interval', minutes=1)
    scheduler.start()
    return scheduler

# ഷെഡ്യൂളർ സജീവമാക്കുന്നു
scheduler = start_background_scheduler()

# --- UI (Streamlit Frontend) ---
st.set_page_config(page_title="WhatsApp Schedule Bot", page_icon="📅", layout="wide")
st.title("📅 WhatsApp Schedule & Wishes Manager")

# CSV ഫയൽ പരിശോധിക്കുകയും ലോഡ് ചെയ്യുകയും ചെയ്യുന്നു
columns = ["name", "phone", "date", "time", "message", "last_sent"]
if os.path.exists(CSV_FILE):
    df_contacts = pd.read_csv(CSV_FILE, dtype=str).fillna("")
    # പഴയ CSV ഫയലിൽ പുതിയ കോളങ്ങൾ ഇല്ലെങ്കിൽ ചേർക്കുന്നു
    for col in columns:
        if col not in df_contacts.columns:
            df_contacts[col] = ""
else:
    df_contacts = pd.DataFrame(columns=columns)
    df_contacts.to_csv(CSV_FILE, index=False)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("➕ പുതിയ ഷെഡ്യൂൾ ചേർക്കുക")
    with st.form("add_contact_form", clear_on_submit=True):
        name = st.text_input("പേര് (Name)")
        phone = st.text_input("WhatsApp നമ്പർ (Country code സഹിതം, e.g. 919876543210)")
        
        # തീയതിയും സമയവും
        c_date, c_time = st.columns(2)
        with c_date:
            selected_date = st.date_input("തീയതി (Date)")
        with c_time:
            selected_time = st.time_input("സമയം (Time)", value=time(8, 0)) # Default 08:00 AM
            
        message = st.text_area("ആശംസ / സന്ദേശം", placeholder="Happy Birthday! Have a great year ahead.")
        
        submitted = st.form_submit_button("സേവ് ചെയ്യുക")
        if submitted:
            if name and phone and message:
                date_str = selected_date.strftime("%m-%d")
                time_str = selected_time.strftime("%H:%M")
                
                new_data = pd.DataFrame([[name, phone, date_str, time_str, message, ""]], columns=columns)
                df_contacts = pd.concat([df_contacts, new_data], ignore_index=True)
                df_contacts.to_csv(CSV_FILE, index=False)
                st.success(f"{name}-ന്റെ ഷെഡ്യൂൾ ({date_str} - {time_str}) ചേർത്തു!")
                st.rerun()
            else:
                st.error("എല്ലാ കോളങ്ങളും പൂരിപ്പിക്കുക!")

with col2:
    st.subheader("📋 നിലവിലുള്ള ഷെഡ്യൂളുകൾ")
    st.dataframe(df_contacts, use_container_width=True)
    
    # ലിസ്റ്റിൽ നിന്ന് കോൺടാക്റ്റ് ഡിലീറ്റ് ചെയ്യാനുള്ള സൗകര്യം
    if not df_contacts.empty:
        st.divider()
        st.write("🗑️ **ഷെഡ്യൂൾ ഒഴിവാക്കാൻ (Delete):**")
        del_idx = st.selectbox(
            "ഒഴിവാക്കേണ്ട ആളെ തിരഞ്ഞെടുക്കുക:", 
            options=df_contacts.index, 
            format_func=lambda x: f"{df_contacts.loc[x, 'name']} ({df_contacts.loc[x, 'date']} {df_contacts.loc[x, 'time']})"
        )
        if st.button("Delete Selected Entry"):
            df_contacts = df_contacts.drop(del_idx).reset_index(drop=True)
            df_contacts.to_csv(CSV_FILE, index=False)
            st.success("ഷെഡ്യൂൾ നീക്കം ചെയ്തു!")
            st.rerun()

    # മാന്വൽ ടെസ്റ്റിംഗ്
    st.divider()
    st.write("🧪 **ടെസ്റ്റ് ചെയ്യാൻ:**")
    if st.button("ഇന്നത്തെ തീയതിയിലുള്ള എല്ലാ മെസ്സേജുകളും ഇപ്പോൾ അയക്കുക"):
        today_date = datetime.now().strftime("%m-%d")
        for _, r in df_contacts.iterrows():
            if str(r.get("date", "")).strip() == today_date:
                send_whatsapp_message(str(r["phone"]).replace("+", "").strip(), f"Hello {r['name']},\n\n{r['message']}")
        st.info("ഇന്നത്തെ തീയതിയിലുള്ള മെസ്സേജുകൾ അയച്ചു കഴിഞ്ഞു.")
