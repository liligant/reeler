# Import the required modules
import torch
from PIL import Image as PILImage
import torchvision.transforms as transforms
import torchvision.models as models
from flask import Flask, render_template_string, request, redirect, url_for, session
import os
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError
import re
import sqlite3
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import uuid
import kagglehub
import subprocess
import time
import requests
from pyngrok import ngrok
ngrok.set_auth_token("2n9XEXXU68CofplPN1lLvUiXqef_ihJ8EF4vhfScC9LWLcsy")

def start_ngrok():
    from subprocess import Popen, PIPE
    ngrok_path = "ngrok"  # Ensure 'ngrok' is in PATH or provide full path
    port = 5000
    try:
        process = Popen([ngrok_path, "http", str(port)], stdout=PIPE, stderr=PIPE)
        time.sleep(2)  # Allow ngrok time to start
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        public_url = response.json()["tunnels"][0]["public_url"]
        print(f"ngrok public URL: {public_url}")
        return public_url
    except Exception as e:
        print(f"Error starting ngrok: {e}")
        return None

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Set upload folder inside the static directory
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load RoBERTa model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("cybersectony/phishing-email-detection-distilbert_v2.4.1")
model = AutoModelForSequenceClassification.from_pretrained("cybersectony/phishing-email-detection-distilbert_v2.4.1")

# Database initialization function
def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# Call the database initialization function
init_db()

# HTML templates
register_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
</head>
<body>
    <h1>Register</h1>
    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}
    <form method="post">
        <label for="email">Email:</label>
        <input type="text" name="email" id="email" required><br>
        <label for="password">Password:</label>
        <input type="password" name="password" id="password" required><br>
        <button type="submit">Register</button>
    </form>
</body>
</html>
'''

login_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        .register-link {
            display: inline-block;
            margin-top: 10px;
            padding: 10px 15px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-size: 14px;
        }
        .register-link:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <h1>Login</h1>
    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}
    <form method="post">
        <label for="email">Email:</label>
        <input type="text" name="email" id="email" required><br>
        <label for="password">Password:</label>
        <input type="password" name="password" id="password" required><br>
        <button type="submit">Login</button>
    </form>
    <a href="/register" class="register-link">Register</a>
</body>
</html>
'''

upload_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phishing Email Detector</title>
    <style>
        .logout {
            position: absolute;
            top: 10px;
            right: 10px;
            text-decoration: none;
            padding: 8px 15px;
            background-color: #f44336;
            color: white;
            border-radius: 5px;
            font-size: 14px;
        }
        .logout:hover {
            background-color: #d32f2f;
        }
        textarea {
            width: 100%;
            height: 150px;
            overflow-y: scroll;
        }
    </style>
</head>
<body>
    <a href="/logout" class="logout">Logout</a>
    <h1>Phishing Email Detector</h1>
    <form method="post" enctype="multipart/form-data">
        <textarea name="email_text" placeholder="Paste email content here..." rows="10" cols="50"></textarea><br>
        <button type="submit">Check Email</button>
    </form>
    {% if prediction %}
        <h2>Prediction: {{ prediction }}</h2>
        <p>{{ explanation }}</p>
    {% endif %}
</body>
</html>
'''

# Password validation function
def validate_password(password):
    if (len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"[0-9]", password) and
        re.search(r"[\W_]", password)):
        return True
    return False

# Define the phishing detection function
def detect_phishing(email_text):
    # Tokenize and prepare the input
    inputs = tokenizer(email_text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    # Get model predictions
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=1)

    # Get predicted label (0: Not Phishing, 1: Phishing)
    predicted_label = torch.argmax(probabilities).item()
    confidence = probabilities[0][predicted_label].item()

    if predicted_label == 0:
        return "Not Phishing", f"Confidence: {confidence:.2f}"
    else:
        return "Phishing", f"Confidence: {confidence:.2f}"

# Route for registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            valid = validate_email(email)
            email = valid.email
        except EmailNotValidError as e:
            return render_template_string(register_template, error=str(e))

        if not validate_password(password):
            return render_template_string(register_template, error='Password must be at least 8 characters long and contain an uppercase letter, a lowercase letter, a digit, and a special character.')

        hashed_password = generate_password_hash(password)

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (email, passhash) VALUES (?, ?)", (email, hashed_password))
                conn.commit()
            except sqlite3.IntegrityError:
                return render_template_string(register_template, error='Email is already registered.')

        return redirect(url_for('login'))

    return render_template_string(register_template)

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT passhash FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()

        if row and check_password_hash(row[0], password):
            session['email'] = email
            return redirect(url_for('home'))
        else:
            return render_template_string(login_template, error='Invalid email or password.')

    return render_template_string(login_template)

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def home():
    if 'email' not in session:
        return redirect(url_for('login'))

    prediction = None
    explanation = None

    if request.method == 'POST':
        email_text = request.form['email_text']
        prediction, explanation = detect_phishing(email_text)

    return render_template_string(upload_template, prediction=prediction, explanation=explanation)

# Route for logout
@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

# Main entry point
if __name__ == '__main__':
    # Start ngrok and store the public URL
    public_url = start_ngrok()
    # Print the public URL to access the web application
    print(f" * Access the web app at: {public_url}")
    # Run the Flask app on port 5000
    app.run(port=5000)