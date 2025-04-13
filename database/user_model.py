from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from pymongo import MongoClient
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Replace with a secure random key in production

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["semprep"]
users_collection = db["users"]

# Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if users_collection.find_one({"email": email}):
            return "User already exists."
        users_collection.insert_one({"email": email, "password": password, "notes": []})
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email, "password": password})
        if user:
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials."
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        email = session['email']
        user = users_collection.find_one({"email": email})
        notes = user.get("notes", [])
        return render_template('dashboard.html', notes=notes, email=email)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
