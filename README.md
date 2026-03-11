# 🧠 PulseAI: Multi-Modal Personal Health Tracker
### *Next-Gen Heart Disease Risk Prediction System*

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.0+-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![Flask](https://img.shields.io/badge/Flask-Web_Framework-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)


## 📌 Project Overview
PulseAI is an end-to-end medical intelligence application designed to assess heart disease risk by combining multiple types of patient data into one unified prediction system. Instead of relying on a single data source, this project integrates three distinct modalities to simulate a real-world clinical decision support system.

### **Integrated Modalities:**
1.  **Clinical & Demographic Data** (Tabular)
2.  **ECG Time-Series Signals** (Temporal)
3.  **Chest X-ray Images** (Spatial)

---

## 🚀 New & Updated Features (v2.0)
* **🔒 Secure User Authentication:** Integrated **Flask-Login** for session management, ensuring private access to health profiles.
* **📂 Persistent Data Storage:** Implemented **SQLite** to store User Credentials, Health Profiles, and historical Risk Predictions.
* **🤖 Integrated AI Chatbot:** A custom-built assistant that interprets results and provides actionable health recommendations in natural language.
* **🐋 Deployment Ready:** Optimized for containerized environments using **Docker** for seamless cloud hosting.

---

## 🧠 Model Architecture Overview
The system utilizes a **Late Fusion** approach where specialized models extract features from each modality before concatenation.

| Modality | Architecture | Purpose | Performance |
| :--- | :--- | :--- | :--- |
| **ANN** | Dense (128) → ReLU → Embedding (32-D) | Analyze structured data (Age, BMI, BP). | ~90% Acc |
| **CNN** | **MobileNetV2** (Transfer Learning) | Extract visual patterns from Chest X-rays. | ~83% Acc |
| **LSTM** | Bidirectional LSTM (64 units) | Detect abnormal heart rhythms in ECG signals. | High-Fidelity |

**Fusion Mechanism:** The embeddings (32-D ANN + 1280-D CNN + 64-D LSTM) are concatenated and passed through a final Dense layer (256 units) to produce the final probability score.

---

## 📊 Risk Interpretation
Predictions are mapped to actionable health tiers:

| Prediction Probability | Risk Level | Recommendation |
| :--- | :--- | :--- |
| **≥ 0.75** | 🔴 **High Risk** | Immediate cardiologist consultation recommended. |
| **0.45 – 0.74** | 🟡 **Moderate Risk** | Lifestyle improvement and regular monitoring. |
| **< 0.45** | 🟢 **Low Risk** | Maintain a healthy routine. |

---

## 🛠️ Tech Stack
* **Language:** Python
* **Deep Learning:** TensorFlow / Keras
* **Data Science:** Scikit-learn, NumPy, Pandas, OpenCV
* **Backend:** Flask, Flask-Login, SQLite (SQLAlchemy)
* **Frontend:** HTML & CSS (Custom Responsive UI)
* **DevOps:** Docker

---

## 📦 Deployment
The system is architected for scalability and can be hosted via:
* **Render / Hugging Face Spaces**
* **Docker-based cloud services** (AWS, Azure, GCP)

---

## ⚠️ Disclaimer
This project is for **educational and research purposes only**. It is not a certified medical diagnostic system and should not be used as a replacement for professional medical advice.

---

## 👩‍💻 Author
**Musfira Mubeen** *Aspiring AI Engineer & Data Scientist* ⭐ **If you find this project interesting, feel free to star the repository!**
