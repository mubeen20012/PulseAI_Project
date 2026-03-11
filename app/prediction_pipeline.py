# prediction_pipeline.py
import os
import json
import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array

# -----------------------------
# BASE DIRECTORY OF THE PROJECT
# -----------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE, "model")
DATA_DIR  = os.path.join(BASE, "data")

# Tabular files
FEATURES_JSON = os.path.join(BASE, "feature_names.json")
TABULAR_CSV   = os.path.join(DATA_DIR, "Feature_engineering.csv")
SCALER_FILE   = os.path.join(BASE, "tabular_scaler.pkl")

# Model files
ANN_MODEL_PATH  = os.path.join(MODEL_DIR, "ann_embedding_model.h5")
CNN_MODEL_PATH  = os.path.join(MODEL_DIR, "cnn_embedding_model.h5")
LSTM_MODEL_PATH = os.path.join(MODEL_DIR, "fusion_ready_lstm_embedding_model.h5")
FUSION_MODEL_PATH = os.path.join(MODEL_DIR, "heart_disease_fusion_model.h5")

# -----------------------------
# LOAD MODELS AND SCALER
# -----------------------------
feature_names = json.load(open(FEATURES_JSON))
ann_embed_model  = load_model(ANN_MODEL_PATH, compile=False)
cnn_embed_model  = load_model(CNN_MODEL_PATH, compile=False)
lstm_embed_model = load_model(LSTM_MODEL_PATH, compile=False)
fusion_model     = load_model(FUSION_MODEL_PATH, compile=False)
scaler = joblib.load(SCALER_FILE)

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def fix_tabular_input(input_data, feature_names, fill_value=0):
    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    elif isinstance(input_data, pd.DataFrame):
        df = input_data.copy()
    else:
        raise ValueError("Input must be dict or DataFrame")
    
    full_df = pd.DataFrame(columns=feature_names, index=df.index)
    for col in feature_names:
        full_df[col] = df[col] if col in df.columns else fill_value
    return full_df[feature_names]

def prepare_ecg(ecg_array, expected_timesteps=187):
    arr = np.array(ecg_array)
    if arr.ndim == 1:
        arr = arr[None, :]
    if arr.shape[1] < expected_timesteps:
        arr = np.pad(arr, ((0,0),(0,expected_timesteps-arr.shape[1])), mode='constant')
    elif arr.shape[1] > expected_timesteps:
        arr = arr[:, :expected_timesteps]
    arr = arr.astype(np.float32)
    arr = arr / (np.max(arr) if np.max(arr)!=0 else 1.0)
    return arr[..., None]

def prepare_xray(img_path, target_size=(224,224)):
    img = load_img(img_path, target_size=target_size)
    arr = img_to_array(img)/255.0
    return np.expand_dims(arr, axis=0)

# -----------------------------
# PREDICTION FUNCTION
# -----------------------------
def predict_patient(tabular_input, ecg_input, xray_path, explain_shap=False):
    # --- Tabular ANN embedding
    tab_fixed = fix_tabular_input(tabular_input, feature_names)
    tab_scaled = scaler.transform(tab_fixed)
    ann_emb = ann_embed_model.predict(tab_scaled, verbose=0)
    
    # --- ECG LSTM embedding
    ecg_arr = prepare_ecg(ecg_input)
    lstm_emb = lstm_embed_model.predict(ecg_arr, verbose=0)
    
    # --- X-ray CNN embedding
    if xray_path and os.path.exists(xray_path):
        x_arr = prepare_xray(xray_path)
        cnn_emb = cnn_embed_model.predict(x_arr, verbose=0)
    else:
        cnn_emb = np.zeros((1, 1280))  # fallback if no X-ray provided

    # --- Fusion prediction
    prob = fusion_model.predict([ann_emb, cnn_emb, lstm_emb], verbose=0)[0][0]

    # --- Risk thresholds
    if prob >= 0.75:
        risk = "High Risk"
        rec = "High risk — see a cardiologist soon; diagnostic tests recommended."
        badge_color = "red"
    elif prob >= 0.45:
        risk = "Moderate Risk"
        rec = "Moderate risk — lifestyle changes and regular follow-up recommended."
        badge_color = "yellow"
    else:
        risk = "Low Risk"
        rec = "Low risk — maintain healthy lifestyle and routine check-ups."
        badge_color = "green"

    results_df = pd.DataFrame({
        "probability": [float(prob)],
        "risk_level": [risk],
        "recommendation": [rec],
        "badge_color": [badge_color]
    })

    shap_values = None
    if explain_shap:
        df_train = pd.read_csv(TABULAR_CSV).drop("HeartDiseaseorAttack", axis=1)
        bg = df_train.sample(min(len(df_train), 100), random_state=42)
        bg_scaled = scaler.transform(bg)
        import shap
        explainer = shap.KernelExplainer(ann_embed_model.predict, bg_scaled)
        shap_values = explainer.shap_values(tab_scaled, nsamples=100)

    return results_df, shap_values
