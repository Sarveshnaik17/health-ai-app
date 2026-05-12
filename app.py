import streamlit as st
import pandas as pd
import pickle
from pymongo import MongoClient, errors
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time
import random
import os

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="MediVision AI Pro",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# LOAD MODEL
# =====================================================
@st.cache_resource
def load_model():
    try:
        return pickle.load(open("model.pkl", "rb"))
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

model = load_model()

# =====================================================
# MONGODB CONNECTION
# =====================================================
MONGO_URI = "mongodb+srv://sarvesh:srushti10@cluster0.eehrxev.mongodb.net/?appName=Cluster0" 

@st.cache_resource

def get_db():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.server_info() # trigger connection
        return client["healthdb"]
    except errors.ServerSelectionTimeoutError:
        st.error("🚨 Database Connection Timeout. Please check your internet or MongoDB URI.")
        return None
    except Exception as e:
        st.error(f"🚨 MongoDB Error: {e}")
        return None

db = get_db()
if db is not None:
    users = db["users"]
    preds = db["predictions"]
else:
    st.stop()

# =====================================================
# CSS - PREMIUM MEDICAL UI (Inspired by User)
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

:root {
    --bg-gradient: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    --accent-blue: #0072ff;
    --accent-cyan: #00c6ff;
    --glass: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.1);
}

* { font-family: 'Poppins', sans-serif; }

.stApp {
    background: var(--bg-gradient);
    color: #ffffff;
    overflow-x: hidden;
}

/* --- ANIMATED ELEMENTS --- */
.bubble {
    position: fixed;
    bottom: -100px;
    width: 40px;
    height: 40px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 50%;
    animation: rise 10s infinite ease-in;
    z-index: 0;
}

@keyframes rise {
    0% { transform: translateY(0) scale(1); opacity: 0; }
    50% { opacity: 0.5; }
    100% { transform: translateY(-110vh) scale(1.5); opacity: 0; }
}

.doctor-anim {
    position: fixed;
    width: 100px;
    bottom: 20px;
    left: -150px;
    animation: doctorMove 25s linear infinite;
    z-index: 1;
    opacity: 0.7;
}

@keyframes doctorMove {
    0% { left: -150px; }
    100% { left: 110%; }
}

/* --- GLASS CARDS --- */
.glass-container {
    background: var(--glass);
    backdrop-filter: blur(15px);
    border: 1px solid var(--glass-border);
    border-radius: 25px;
    padding: 35px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
    margin-bottom: 25px;
    animation: fadeIn 1s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

/* --- HEADINGS --- */
.main-title {
    font-size: 3.5rem;
    font-weight: 700;
    text-align: center;
    background: linear-gradient(to right, #00c6ff, #0072ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}

.sub-title {
    text-align: center;
    color: #94a3b8;
    font-size: 1.2rem;
    margin-bottom: 3rem;
}

/* --- BUTTONS --- */
.stButton > button {
    background: linear-gradient(90deg, #00c6ff, #0072ff) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    transition: 0.4s !important;
    width: 100%;
    text-transform: uppercase;
}

.stButton > button:hover {
    transform: scale(1.03);
    box-shadow: 0 10px 30px rgba(0, 114, 255, 0.4);
}

/* --- SIDEBAR --- */
section[data-testid="stSidebar"] {
    background: rgba(15, 32, 39, 0.95) !important;
    border-right: 1px solid var(--glass-border);
}

/* Metrics */
[data-testid="stMetricValue"] {
    color: #00c6ff !important;
    font-weight: 700 !important;
}

header, footer { visibility: hidden; }
</style>

<!-- Animated Background Elements -->
<div class="bubble" style="left:10%; animation-delay:0s; width:60px; height:60px;"></div>
<div class="bubble" style="left:30%; animation-delay:2s"></div>
<div class="bubble" style="left:55%; animation-delay:4s; width:80px; height:80px;"></div>
<div class="bubble" style="left:80%; animation-delay:1s"></div>
<div class="bubble" style="left:92%; animation-delay:3s; width:50px; height:50px;"></div>

<!-- Moving Doctor -->
<img src="https://cdn-icons-png.flaticon.com/512/387/387569.png" class="doctor-anim">
""", unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================
if "user" not in st.session_state:
    st.session_state["user"] = None
if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "Login"

# =====================================================
# AUTHENTICATION SCREEN
# =====================================================
if st.session_state["user"] is None:
    st.markdown('<h1 class="main-title">MediVision Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Secure AI-Driven Clinical Risk Analysis</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        auth_choice = st.radio("Access Portal", ["🔐 Secure Login", "📝 New Account"], horizontal=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)

        if "Secure Login" in auth_choice:
            with st.form("login_form"):
                u = st.text_input("Username", placeholder="e.g. sarvesh")
                p = st.text_input("Password", type="password", placeholder="••••••••")
                login_btn = st.form_submit_button("Authenticate")
                
                if login_btn:
                    if not u or not p:
                        st.warning("Please provide credentials")
                    else:
                        user_rec = users.find_one({"username": u, "password": p})
                        if user_rec:
                            st.session_state["user"] = u
                            st.success("Access Granted. Loading workspace...")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Authentication Failed: Invalid user or password")
        else:
            with st.form("register_form"):
                new_u = st.text_input("Choose Username", placeholder="minimum 3 characters")
                new_p = st.text_input("Create Password", type="password", placeholder="minimum 6 characters")
                confirm_p = st.text_input("Verify Password", type="password")
                reg_btn = st.form_submit_button("Create My Account")
                
                if reg_btn:
                    if len(new_u) < 3:
                        st.error("Username too short")
                    elif len(new_p) < 6:
                        st.error("Password too short")
                    elif new_p != confirm_p:
                        st.error("Passwords do not match")
                    elif users.find_one({"username": new_u}):
                        st.error("This username is already registered")
                    else:
                        users.insert_one({
                            "username": new_u,
                            "password": new_p,
                            "joined": datetime.now(),
                            "role": "patient"
                        })
                        st.success("Account Ready! Please switch to Login.")
        st.markdown('</div>', unsafe_allow_html=True)

else:
    # =====================================================
    # MAIN WORKSPACE
    # =====================================================
    with st.sidebar:
        st.markdown(f"### 👨‍⚕️ Welcome, {st.session_state['user']}")
        st.caption("MediVision AI Professional v2.0")
        st.markdown("---")
        
        selection = st.radio(
            "WORKSPACE NAVIGATION",
            ["🩺 Prediction Engine", "📊 Clinical Insights", "📜 Health Reports", "⚙️ Account Console"]
        )
        
        st.markdown("<br>"*10, unsafe_allow_html=True)
        if st.button("🚪 TERMINATE SESSION"):
            st.session_state["user"] = None
            st.rerun()

    # --- Prediction Engine ---
    if selection == "🩺 Prediction Engine":
        st.markdown('<h2 style="font-weight:700;">Diagnostic Risk Assessment</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.info("Input patient biometrics below. Our AI analyzes 8 distinct clinical markers to calculate risk probability.")
        
        col1, col2 = st.columns(2)
        with col1:
            preg = st.number_input("Pregnancies", 0, 20, 0)
            glu = st.slider("Glucose (Plasma)", 0, 300, 120)
            bp = st.slider("Blood Pressure (Diastolic)", 0, 150, 80)
            skin = st.slider("Skin Thickness (Triceps)", 0, 100, 20)
        with col2:
            ins = st.slider("Insulin (2-Hour)", 0, 900, 80)
            bmi = st.number_input("BMI (Body Mass Index)", 0.0, 70.0, 25.0)
            dpf = st.slider("Diabetes Pedigree Function", 0.0, 3.0, 0.5, 0.01)
            age = st.number_input("Patient Age", 1, 120, 30)

        if st.button("🚀 EXECUTE AI ANALYSIS"):
            if model is None:
                st.error("Predictor model not loaded on server.")
            else:
                with st.spinner("Processing neural network weights..."):
                    time.sleep(2)
                    features = [[preg, glu, bp, skin, ins, bmi, dpf, age]]
                    risk_pred = model.predict(features)[0]
                    risk_prob = model.predict_proba(features)[0][1] * 100
                    
                    status = "HIGH RISK" if risk_pred == 1 else "OPTIMAL"
                    color = "#ff4b4b" if risk_pred == 1 else "#00c6ff"
                    
                    preds.insert_one({
                        "user": st.session_state["user"],
                        "risk": status,
                        "probability": float(risk_prob),
                        "timestamp": datetime.now(),
                        "biometrics": features[0]
                    })
                    
                    st.markdown("---")
                    res1, res2, res3 = st.columns(3)
                    with res1:
                        st.metric("Clinical Status", status)
                    with res2:
                        st.metric("Risk Probability", f"{risk_prob:.1f}%")
                    with res3:
                        health_score = 100 - risk_prob
                        st.metric("Health Score", f"{health_score:.1f}/100")
                    
                    st.markdown(f"""
                    <div style="background: rgba(255,255,255,0.05); border-radius: 15px; height: 12px; margin-top: 10px;">
                        <div style="background: {color}; width: {risk_prob}%; height: 100%; border-radius: 15px; transition: width 1s;"></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if risk_pred == 1:
                        st.warning("⚠️ Critical: Patient metrics indicate high risk. Immediate medical consultation is advised.")
                    else:
                        st.success("✅ Positive: Metrics are within safe thresholds. Maintain regular monitoring.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Clinical Insights ---
    elif selection == "📊 Clinical Insights":
        st.markdown('<h2 style="font-weight:700;">Personal Health Trends</h2>', unsafe_allow_html=True)
        
        user_data = list(preds.find({"user": st.session_state["user"]}).sort("timestamp", 1))
        
        if not user_data:
            st.warning("No clinical data available for analysis. Please run a Prediction first.")
        else:
            df = pd.DataFrame(user_data)
            
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Lifetime Tests", len(df))
            c2.metric("Peak Risk", f"{df['probability'].max():.1f}%")
            c3.metric("Current Avg", f"{df['probability'].mean():.1f}%")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="glass-container">', unsafe_allow_html=True)
            fig = px.area(df, x="timestamp", y="probability", title="Disease Risk Trajectory", template="plotly_dark")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.write("Recent Activity Log")
            st.dataframe(df[["timestamp", "risk", "probability"]].sort_values("timestamp", ascending=False), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Health Reports (New Feature) ---
    elif selection == "📜 Health Reports":
        st.markdown('<h2 style="font-weight:700;">Generated Medical Reports</h2>', unsafe_allow_html=True)
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.info("Download your comprehensive health summaries in PDF format (Coming Soon). For now, view your raw record data.")
        
        user_data = list(preds.find({"user": st.session_state["user"]}))
        if user_data:
            df = pd.DataFrame(user_data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export My Records (CSV)", csv, "health_report.csv", "text/csv")
            st.json(user_data)
        else:
            st.write("No records to export.")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- Account Console ---
    elif selection == "⚙️ Account Console":
        st.markdown('<h2 style="font-weight:700;">System Settings</h2>', unsafe_allow_html=True)
        st.markdown('<div class="glass-container">', unsafe_allow_html=True)
        st.write(f"Account: **{st.session_state['user']}**")
        st.write("Database: **CONNECTED (MongoDB Atlas)**")
        st.write("Security: **SHA-256 Mocked (In-Transit Encryption Active)**")
        
        if st.button("⚠️ WIPE DATA & RESET ACCOUNT"):
            preds.delete_many({"user": st.session_state["user"]})
            st.success("All personal records purged from the cloud database.")
            time.sleep(1)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

