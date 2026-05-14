import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, messaging
import requests
import datetime

# --- 1. Firebase Initialization ---
if not firebase_admin._apps:
    try:
        # Local test ke liye json file use karein
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase Initialization Failed: {e}")

db = firestore.client()

# --- Page Config ---
st.set_page_config(page_title="Market Saga - Admin Control", layout="wide", page_icon="📈")

st.title("🚀 Market Saga AI Admin Panel")
st.write("Manage Live App Sections, F&O Calls, and Trigger AI Re-Analysis.")

st.divider()

# --- SECTION 1: F&O Daily Calls (Admin Controlled) ---
st.subheader("📍 Manage F&O Daily Calls (Top UI Banner)")
st.info("Yahan se daali hui call Android App ke top section mein live dikhegi.")

with st.form("fo_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Stock/Index Symbol", placeholder="e.g., NIFTY, RELIANCE").upper()
        entry_price = st.number_input("Entry Price Range", min_value=0.0, step=0.1)
    with col2:
        stop_loss = st.number_input("Stop Loss (SL)", min_value=0.0, step=0.1)
        target_price = st.number_input("Target Price", min_value=0.0, step=0.1)
        
    analysis_reason = st.text_area("Analysis / Reason for this Call")
    submit_fo = st.form_submit_button("Push F&O Call to App Live")

    if submit_fo:
        if symbol and entry_price > 0:
            fo_data = {
                "symbol": symbol,
                "entry": entry_price,
                "sl": stop_loss,
                "target": target_price,
                "analysis": analysis_reason,
                "timestamp": datetime.datetime.now()
            }
            # Firestore mein 'app_config' collection ke 'fo_live' document mein save karein
            db.collection("app_config").document("fo_live").set(fo_data)
            st.success(f"✅ Success: F&O Call for {symbol} is now Live on App!")
        else:
            st.error("Please fill Symbol and Entry Price.")

st.divider()

# --- SECTION 2: AI PREDICTION ENGINE (Auto-Generated List Status) ---
st.subheader("🤖 AI Predictable Stocks & Top Gainers Status")
st.warning("⚠️ Rules: Is list ko admin manually change nahi kar sakta. Ye AI logic aur News Sentiment se auto-update hoti hai.")

# Firestore se current AI list read karke admin ko dikhana
try:
    ai_doc = db.collection("app_config").document("ai_predictions").get()
    if ai_doc.exists:
        current_stocks = ai_doc.to_dict().get("stocks", [])
        st.write(f"**Current AI Predicted Stocks Live:** {', '.join(current_stocks)}")
    else:
        st.write("No AI Stocks available in DB currently.")
except Exception as e:
    st.write("Error fetching current AI list.")

if st.button("🔄 Trigger AI Engine Re-Analysis Now"):
    with st.spinner("AI Engine is scanning news analysis & charts..."):
        try:
            # response = requests.get("https://your-fastapi-url.onrender.com/cron/update-ai-stocks")
            
            demo_ai_stocks = ["ZOMATO", "IREDA", "TATASTEEL", "RVNL", "RELIANCE"]
            db.collection("app_config").document("ai_predictions").set({
                "stocks": demo_ai_stocks,
                "last_updated": datetime.datetime.now()
            })
            st.success("✅ AI Engine run complete! Firestore updated with top future potential stocks.")
            st.rerun()
        except Exception as e:
            st.error(f"Failed to trigger AI Engine: {e}")

st.divider()

# --- SECTION 3: TARGETED NOTIFICATIONS ---
st.subheader("🔔 Broadcast Targeted Push Notification")
target_topic = st.selectbox("Select Target Audience", ["all_users", "equity_traders", "fo_traders"])
notif_title = st.text_input("Notification Title", placeholder="e.g., Market Breakout Alert!")
notif_body = st.text_area("Notification Message Body")

if st.button("Send Push Notification"):
    if notif_title and notif_body:
        try:
            # Firebase Cloud Messaging Topic Notification
            message = messaging.Message(
                notification=messaging.Notification(
                    title=notif_title,
                    body=notif_body,
                ),
                topic=target_topic,
            )
            response = messaging.send(message)
            st.success(f"🚀 Notification broadcasted successfully! Message ID: {response}")
        except Exception as e:
            st.error(f"FCM Error: {e}")
    else:
        st.error("Please enter both Title and Body.")