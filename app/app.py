import os
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.utils import secure_filename
from prediction_pipeline import predict_patient
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from chatbot import get_chat_response

# --- INITIALIZE APP ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev_key_musfira_2026'

# --- DATABASE CONFIGURATION ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, '..', 'database', 'health_tracker.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"connect_args": {"timeout": 20}}

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# --- DATABASE MODELS ---
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    records = db.relationship('HealthRecord', backref='patient', lazy=True)

class HealthRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Float)
    bmi = db.Column(db.Float)
    risk_score = db.Column(db.Float)
    risk_level = db.Column(db.String(50)) # Correctly stores "Low", "Moderate", or "High"
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/predict', methods=['GET','POST'])
@login_required 
def index():
    if request.method == 'POST':
        try:
            tabular_input = {
                "Age": float(request.form['Age']),
                "BMI": float(request.form['BMI']),
                "Sex_Male": 1 if request.form['Gender'] == 'Male' else 0,
                "RestingBP": float(request.form['RestingBP']),
                "Cholesterol": float(request.form['Cholesterol'])
            }
            # Placeholder for image handling logic
            ecg_input = np.zeros(187) 
            results_df, _ = predict_patient(tabular_input, ecg_input, None)
            
            # This result_dict now contains the 'risk_level' from your 3-class logic
            result_dict = results_df.iloc[0].to_dict()
            
            new_record = HealthRecord(
                age=tabular_input['Age'],
                bmi=tabular_input['BMI'],
                risk_score=float(result_dict['probability']),
                risk_level=result_dict['risk_level'], # Saves "Moderate Risk" correctly
                user_id=current_user.id 
            )
            db.session.add(new_record)
            db.session.commit()
            return render_template('result.html', result=result_dict)
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}"
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('Username or Email already exists!', 'danger')
            return redirect(url_for('signup'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! You can now login.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Failed. Please check credentials.', 'danger')
    return render_template('login.html')

# --- FIX: FORGOT PASSWORD ROUTE ---
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            # Logic for reset would go here (e.g., sending a tokenized link)
            flash(f'Reset link sent to {email}. (Note: Email server not configured yet)', 'info')
            return redirect(url_for('login'))
        else:
            flash('Email address not found.', 'danger')
    return render_template('forgot_password.html')

@app.route('/history')
@login_required
def history():
    user_records = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.timestamp.desc()).all()
    return render_template('history.html', records=user_records)

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    user_message = request.json.get("message")
    last_record = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.timestamp.desc()).first()
    ai_data = None
    if last_record:
        ai_data = {'probability': last_record.risk_score, 'risk_level': last_record.risk_level}
    response = get_chat_response(user_message, ai_data)
    return jsonify({"response": response})

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)