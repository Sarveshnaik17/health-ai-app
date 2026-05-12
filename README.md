# 🏥 MediVision AI — Cloud-Based Health Risk Prediction System

## 📌 Overview

MediVision AI is a professional cloud-powered healthcare analytics platform that predicts disease risk using Machine Learning and stores patient records securely using MongoDB Atlas Cloud Database.

The system provides real-time health risk analysis, prediction dashboards, cloud storage, and interactive visualizations through a modern web interface.

---

# 🚀 Features

✅ AI-Based Disease Risk Prediction
✅ Cloud Database Integration (MongoDB Atlas)
✅ Professional Dashboard UI
✅ User Authentication System
✅ Real-Time Analytics & Graphs
✅ Secure Cloud Storage
✅ Prediction History Tracking
✅ Fully Responsive Web Application
✅ Deployable on Render / Streamlit Cloud

---

# 🧠 Technologies Used

| Technology    | Purpose            |
| ------------- | ------------------ |
| Python        | Backend Logic      |
| Streamlit     | Frontend UI        |
| Scikit-learn  | Machine Learning   |
| MongoDB Atlas | Cloud Database     |
| Plotly        | Interactive Charts |
| Render        | Cloud Deployment   |
| GitHub        | Version Control    |

---

# 📂 Project Structure

```bash
health-ai-app/
│
├── app.py
├── dataset.csv
├── model.pkl
├── train_model.py
├── requirements.txt
├── render.yaml
├── .streamlit/
│   └── config.toml
│
├── backend/
├── frontend/
```

---

# 🤖 Machine Learning Model

The application uses a Random Forest Classifier trained on the Pima Indians Diabetes Dataset.

### Input Features:

* Pregnancies
* Glucose
* Blood Pressure
* Skin Thickness
* Insulin
* BMI
* Diabetes Pedigree Function
* Age

### Output:

* High Risk
* Low Risk

---

# 📊 Dashboard Features

✅ Risk Trend Analysis
✅ Prediction Distribution Charts
✅ Total Tests Overview
✅ High Risk Case Statistics
✅ Real-Time Prediction Monitoring

---

# ☁️ MongoDB Atlas Setup

1. Create MongoDB Atlas Account
2. Create Free Cluster
3. Create Database User
4. Whitelist IP Address (`0.0.0.0/0`)
5. Copy MongoDB Connection String
6. Add Connection String as Environment Variable

Example:

```python
MONGO_URI = os.getenv("MONGO_URI")
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/Sarveshnaik17/health-ai-app.git
cd health-ai-app
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Train Model

```bash
python train_model.py
```

---

## Run Application

```bash
python -m streamlit run app.py
```

---

# 🌐 Deployment on Render

## Build Command

```bash
pip install -r requirements.txt
```

## Start Command

```bash
python -m streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

---

# 📈 Dataset

Dataset Used:

* Pima Indians Diabetes Dataset

Source:

* UCI Machine Learning Repository
* Kaggle

---

# 🔒 Security Improvements

Future enhancements:

* Password Hashing
* JWT Authentication
* Secure API Tokens
* Role-Based Access Control

---

# 🔮 Future Enhancements

✅ PDF Medical Reports
✅ AI Chatbot Assistant
✅ Email Alerts
✅ Doctor Appointment Booking
✅ Multi-Disease Prediction
✅ Mobile App Version
✅ Voice-Based Health Assistant

---

# 👨‍💻 Developed By

Sarvesh Naik

Cloud Computing + AI/ML Course Project

---

# 📜 License

This project is developed for educational and academic purposes.
