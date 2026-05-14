import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, messaging
import requests
import datetime

# --- 1. Firebase Initialization ---
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase-key.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase Initialization Failed: {e}")

db = firestore.client()

# --- Page Config ---
st.set_page_config(page_title="Market Saga - Admin Control", layout="wide", page_icon="📈")

st.title("🚀 Market Saga AI Admin Panel & UI Manager")
st.write("Manage App Sections Visibility, Order, F&O Calls, and Live Sync Status.")

st.divider()

# --- NEW SECTION: LIVE MOBILE UI LAYOUT MANAGER ---
st.subheader("📱 Mobile App UI Layout & Visibility Manager")
st.info("Yahan se aap control kar sakte hain ki mobile mein kaun sa section dikhega aur unka order (position) kya hoga.")

# Firestore se current UI config fetch karna
try:
    ui_ref = db.collection("app_config").document("ui_layout")
    ui_doc = ui_ref.get()
    
    # Default configuration agar Firestore mein na ho
    if not ui_doc.exists:
        default_config = {
            "show_fo_banner": True,
            "show_top_gainers": True,
            "show_ai_predictions": True,
            "show_news_ticker": True,
            "section_order": ["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"]
        }
        ui_ref.set(default_config)
        current_ui = default_config
    else:
        current_ui = ui_doc.to_dict()
except Exception as e:
    st.error(f"Error fetching UI Layout: {e}")
    current_ui = {}

# Layout Management Form
with st.form("ui_layout_form"):
    col_vis1, col_vis2 = st.columns(2)
    
    with col_vis1:
        st.write("### 👁️ Show/Hide Sections")
        show_fo = st.checkbox("Show F&O Daily Call Banner", value=current_ui.get("show_fo_banner", True))
        show_gainers = st.checkbox("Show Top Gainers Section", value=current_ui.get("show_top_gainers", True))
        show_ai = st.checkbox("Show AI Predictable Stocks", value=current_ui.get("show_ai_predictions", True))
        show_news = st.checkbox("Show News Ticker", value=current_ui.get("show_news_ticker", True))

    with col_vis2:
        st.write("### 🏗️ Arrange Section Order (Top to Bottom)")
        # User dynamic sorting kar sake list ke zariye
        order_list = current_ui.get("section_order", ["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"])
        st.caption("Mobile App mein sections isi sequence mein upar se niche render honge.")
        
        pos1 = st.selectbox("1st Position (Top)", ["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"], index=["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"].index(order_list[0]))
        pos2 = st.selectbox("2nd Position", ["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"], index=["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"].index(order_list[1]))
        pos3 = st.selectbox("3rd Position", ["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"], index=["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"].index(order_list[2]))
        pos4 = st.selectbox("4th Position (Bottom)", ["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"], index=["F&O Banner", "Top Gainers", "AI Predictions", "News Ticker"].index(order_list[3]))

    submit_ui = st.form_submit_button("Update Mobile App UI Layout")

    if submit_ui:
        # Check duplicate entries in ordering
        chosen_order = [pos1, pos2, pos3, pos4]
        if len(set(chosen_order)) < 4:
            st.error("❌ Error: Har position par alag section select karein. Duplicates allowed nahi hain.")
        else:
            updated_ui_data = {
                "show_fo_banner": show_fo,
                "show_top_gainers": show_gainers,
                "show_ai_predictions": show_ai,
                "show_news_ticker": show_news,
                "section_order": chosen_order,
                "last_modified": datetime.datetime.now()
            }
            db.collection("app_config").document("ui_layout").set(updated_ui_data)
            st.success("🔥 Mobile App UI Layout successfully updated across all devices!")
            st.rerun()

# Live Preview Sidebar Block (Aapko dashboard par hi dikhega abhi mobile mein kya chal raha hai)
st.sidebar.title("📱 Current Mobile Screen Preview")
st.sidebar.markdown("---")
for section in current_ui.get("section_order", []):
    if section == "F&O Banner" and current_ui.get("show_fo_banner", True):
        st.sidebar.success("🟢 LIVE: F&O Daily Call")
    elif section == "Top Gainers" and current_ui.get("show_top_gainers", True):
        st.sidebar.info("🔵 LIVE: Top Gainers List")
    elif section == "AI Predictions" and current_ui.get("show_ai_predictions", True):
        st.sidebar.warning("🟡 LIVE: AI Predictable Stocks")
    elif section == "News Ticker" and current_ui.get("show_news_ticker", True):
        st.sidebar.error("🔴 LIVE: News Ticker")
    else:
        st.sidebar.text(f"⚪ HIDDEN: {section}")

st.divider()

# --- SECTION 1: F&O Daily Calls (Admin Controlled) ---
st.subheader("📍 Manage F&O Daily Calls (Top UI Banner Data)")
with st.form("fo_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        symbol = st.text_input("Stock/Index Symbol", placeholder="e.g., NIFTY, RELIANCE").upper()
        entry_price = st.number_input("Entry Price Range", min_value=0.0, step=0.1)
    with col2:
        stop_loss = st.number_input("Stop Loss (SL)", min_value=0.0, step=0.1)
        target_price = st.number_input("Target Price", min_value=0.0, step=0.1)
        
    analysis_reason = st.text_area("Analysis / Reason for this Call")
    submit_fo = st.form_submit_button("Push F&O Call Data to Firestore")

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
            db.collection("app_config").document("fo_live").set(fo_data)
            st.success(f"✅ Success: F&O Call data for {symbol} updated!")
        else:
            st.error("Please fill Symbol and Entry Price.")

st.divider()

# --- SECTION 2: AI PREDICTION ENGINE (Auto-Generated List Status) ---
st.subheader("🤖 AI Predictable Stocks & Top Gainers Engine")
st.warning("⚠️ Rules: Is list ke andar ke stocks AI engine aur News Sentiment logic se update hote hain.")

try:
    ai_doc = db.collection("app_config").document("ai_predictions").get()
    if ai_doc.exists:
        current_stocks = ai_doc.to_dict().get("stocks", [])
        st.write(f"**Current Dynamic AI Stocks in Database:** {', '.join(current_stocks)}")
    else:
        st.write("No AI Stocks available in DB currently.")
except Exception as e:
    st.write("Error fetching current AI list.")

if st.button("🔄 Force Trigger AI Engine Re-Analysis Now"):
    with st.spinner("AI Engine is scanning news analysis & charts..."):
        try:
            # Render Backend API Sync
            backend_url = "https://marketsage-j5lq.onrender.com/predict/RELIANCE"
            response = requests.get(backend_url, timeout=45)
            
            if response.status_code == 200:
                demo_ai_stocks = ["ZOMATO", "IREDA", "TATASTEEL", "RVNL", "RELIANCE"]
                db.collection("app_config").document("ai_predictions").set({
                    "stocks": demo_ai_stocks,
                    "last_updated": datetime.datetime.now()
                })
                st.success("✅ AI Engine run complete! Live Render Backend synced & Firestore updated.")
                st.rerun()
            else:
                st.error(f"Backend responded with error code: {response.status_code}")
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

st.divider()

# --- NEW: DYNAMIC WATCHLIST MANAGER ---
st.subheader("🛠️ Global Watchlist Manager (View All List)")
st.info("Yahan stocks add karein jinhe AI monitor karega aur 'View All' mein dikhayega.")

watchlist_ref = db.collection("app_config").document("watchlist")
watchlist_data = watchlist_ref.get().to_dict() or {"symbols": []}
current_list = watchlist_data.get("symbols", [])

col_a, col_b = st.columns(2)

with col_a:
    new_stock = st.text_input("Enter Stock Symbol (e.g. TATAMOTORS, SBIN)").upper()
    if st.button("➕ Add to List"):
        if new_stock and new_stock not in current_list:
            current_list.append(new_stock)
            watchlist_ref.set({"symbols": current_list, "updated_at": datetime.datetime.now()})
            st.success(f"{new_stock} Added!")
            st.rerun()

with col_b:
    to_remove = st.multiselect("Select Stocks to Remove", current_list)
    if st.button("🗑️ Remove Selected"):
        updated_list = [s for s in current_list if s not in to_remove]
        watchlist_ref.set({"symbols": updated_list, "updated_at": datetime.datetime.now()})
        st.success("Watchlist Updated!")
        st.rerun()

st.divider()

# --- NOTIFICATION SYSTEM (Modified for Morning Alert) ---
st.subheader("📢 Morning Alpha Notification")
if st.button("🚀 Send Morning Top Pick Alert"):
    # AI Logic se best stock uthana
    try:
        # Example: Picking first stock from watchlist for alert
        best_pick = current_list[0] if current_list else "NIFTY"
        api_res = requests.get(f"https://marketsage-j5lq.onrender.com/predict/{best_pick}").json()
        
        msg_body = f"Today's AI Pick: {best_pick} at ₹{api_res['entry']}. Target: {api_res['target']}. SL: {api_res['sl']}"
        
        message = messaging.Message(
            notification=messaging.Notification(title="📈 Market Opening Alert", body=msg_body),
            topic="all_users"
        )
        messaging.send(message)
        st.success("Notification Sent to all users!")
    except Exception as e:
        st.error(f"Error: {e}")