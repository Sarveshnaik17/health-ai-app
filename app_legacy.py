import streamlit as st
import pandas as pd
import pickle
from pymongo import MongoClient
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="MediVision AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# LOAD MODEL
# =====================================================
@st.cache_resource
def load_model():
    return pickle.load(open("model.pkl", "rb"))

model = load_model()

# =====================================================
# MONGODB
# =====================================================
MONGO_URI = "mongodb+srv://sarvesh:srushti10@cluster0.eehrxev.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["healthdb"]
users = db["users"]
preds = db["predictions"]

# =====================================================
# CSS - PREMIUM UI
# =====================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp{
    background:
    radial-gradient(circle at top right,#1d4ed8 0%, transparent 25%),
    radial-gradient(circle at bottom left,#06b6d4 0%, transparent 25%),
    linear-gradient(135deg,#020617,#0f172a,#111827);
    color:white;
}

/* Sidebar */
section[data-testid="stSidebar"]{
    background:rgba(15,23,42,0.95);
    border-right:1px solid rgba(255,255,255,0.07);
}

section[data-testid="stSidebar"] *{
    color:white !important;
}

/* Header */
.main-title{
    font-size:52px;
    font-weight:700;
    background: linear-gradient(90deg,#38bdf8,#22c55e,#60a5fa);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    margin-bottom:0px;
}

.sub-title{
    font-size:18px;
    color:#cbd5e1;
    margin-top:-10px;
}

/* Cards */
.glass{
    background: rgba(255,255,255,0.06);
    border:1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(14px);
    border-radius:22px;
    padding:28px;
    box-shadow:0 10px 30px rgba(0,0,0,0.35);
    transition:0.4s;
}

.glass:hover{
    transform:translateY(-6px);
    box-shadow:0 20px 40px rgba(0,0,0,0.45);
}

/* Inputs */
.stTextInput input,
.stNumberInput input{
    border-radius:14px !important;
}

/* Buttons */
.stButton>button{
    width:100%;
    height:52px;
    border:none;
    border-radius:14px;
    background:linear-gradient(90deg,#06b6d4,#2563eb);
    color:white;
    font-size:17px;
    font-weight:600;
    transition:0.3s;
}

.stButton>button:hover{
    transform:scale(1.02);
    box-shadow:0 10px 25px rgba(37,99,235,0.4);
}

/* Metrics */
.metric{
    background:rgba(255,255,255,0.05);
    padding:20px;
    border-radius:18px;
    text-align:center;
}

/* Remove padding top */
.block-container{
    padding-top:1.2rem;
}

/* Fade animation */
.fade{
    animation: fadeIn 1.1s ease-in-out;
}

@keyframes fadeIn{
    from{opacity:0; transform:translateY(20px);}
    to{opacity:1; transform:translateY(0);}
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SESSION
# =====================================================
if "user" not in st.session_state:
    st.session_state["user"] = None

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.markdown("## 🏥 MediVision AI")
st.sidebar.caption("Future of Smart Healthcare")

menu = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Home",
        "📝 Register",
        "🔐 Login",
        "🩺 Predict",
        "📈 Dashboard"
    ]
)

if st.session_state["user"]:
    st.sidebar.success(f"👤 {st.session_state['user']}")

# =====================================================
# HOME
# =====================================================
if menu == "🏠 Home":

    st.markdown('<div class="fade">', unsafe_allow_html=True)

    st.markdown('<div class="main-title">MediVision AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Professional Cloud-Based Disease Risk Prediction Platform</div>', unsafe_allow_html=True)

    st.write("")
    st.write("")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="glass">
        <h2>🤖 AI Engine</h2>
        <p>Advanced machine learning predicts disease risks instantly using real health metrics.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="glass">
        <h2>☁️ Cloud Storage</h2>
        <p>All records safely stored on MongoDB Atlas with 24x7 accessibility.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="glass">
        <h2>📊 Analytics</h2>
        <p>Beautiful dashboards, trends, reports and real-time patient monitoring.</p>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.write("")

    st.markdown("""
    <div class="glass">
    <h2>🚀 Why Choose MediVision?</h2>
    <p>
    ✔ Fast Prediction <br>
    ✔ Secure Records <br>
    ✔ Smart Reports <br>
    ✔ Beautiful Interface <br>
    ✔ Cloud Powered <br>
    </p>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# REGISTER
# =====================================================
elif menu == "📝 Register":

    st.markdown("## 📝 Create Account")

    c1, c2, c3 = st.columns([1,2,1])

    with c2:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Create Account"):

            if users.find_one({"username":u}):
                st.error("Username already exists")
            else:
                users.insert_one({
                    "username":u,
                    "password":p,
                    "created":datetime.now()
                })
                st.success("Registration Successful")

# =====================================================
# LOGIN
# =====================================================
elif menu == "🔐 Login":

    st.markdown("## 🔐 Secure Login")

    c1, c2, c3 = st.columns([1,2,1])

    with c2:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):

            user = users.find_one({"username":u,"password":p})

            if user:
                st.session_state["user"] = u
                st.success("Login Successful")
                st.balloons()
            else:
                st.error("Invalid Username / Password")

# =====================================================
# PREDICT
# =====================================================
elif menu == "🩺 Predict":

    if not st.session_state["user"]:
        st.warning("Please Login First")
        st.stop()

    st.markdown("## 🩺 Health Risk Prediction")

    c1, c2 = st.columns(2)

    with c1:
        pregnancies = st.slider("Pregnancies",0,15,0)
        glucose = st.slider("Glucose",50,250,110)
        bp = st.slider("Blood Pressure",40,180,80)
        skin = st.slider("Skin Thickness",0,100,20)

    with c2:
        insulin = st.slider("Insulin",0,400,80)
        bmi = st.slider("BMI",10.0,50.0,25.0)
        dpf = st.slider("Diabetes Pedigree Function",0.0,3.0,0.5)
        age = st.slider("Age",1,100,25)

    if st.button("Analyze Health"):

        with st.spinner("Running AI Analysis..."):
            time.sleep(2)

        data = [[pregnancies, glucose, bp, skin, insulin, bmi, dpf, age]]

        pred = model.predict(data)[0]
        prob = model.predict_proba(data)[0][1] * 100

        result = "High Risk" if pred == 1 else "Low Risk"

        preds.insert_one({
            "user":st.session_state["user"],
            "risk":result,
            "probability":float(prob),
            "age":age,
            "time":datetime.now()
        })

        st.success("Prediction Completed")

        x1, x2 = st.columns(2)

        with x1:
            st.metric("Prediction", result)

        with x2:
            st.metric("Risk Score", f"{prob:.2f}%")

        st.progress(int(prob))

# =====================================================
# DASHBOARD
# =====================================================
elif menu == "📈 Dashboard":

    if not st.session_state["user"]:
        st.warning("Please Login First")
        st.stop()

    st.markdown("## 📈 Analytics Dashboard")

    data = list(preds.find({"user":st.session_state["user"]}))

    if len(data) == 0:
        st.info("No Prediction Records Yet")
        st.stop()

    df = pd.DataFrame(data)

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Total Tests", len(df))

    with c2:
        st.metric("High Risk Cases", len(df[df["risk"]=="High Risk"]))

    with c3:
        st.metric("Average Risk", f"{df['probability'].mean():.1f}%")

    st.write("")

    fig1 = px.line(
        df,
        x="time",
        y="probability",
        markers=True,
        title="Risk Trend"
    )
    fig1.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.pie(
        df,
        names="risk",
        title="Risk Distribution",
        hole=0.55
    )

    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="white"
    )

    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        df[["risk","probability","age","time"]],
        use_container_width=True
    )