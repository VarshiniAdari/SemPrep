from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from pymongo import MongoClient
from bson.objectid import ObjectId
from models.prepgenie import generate_notes_from_topic
from database.db_models import (
    insert_user, find_user_by_email,
    insert_note, create_folder,
    get_folders_by_user, get_notes_by_folder, get_or_create_my_notes_folder, get_note_by_id
)
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["semprep"]
users_collection = db["users"]

# ---------- Routes ----------

@app.route('/')
def home():
    return render_template('about.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if find_user_by_email(email):
            return "User already exists."
        insert_user({"email": email, "password": password})
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = find_user_by_email(email)
        if user and user['password'] == password:
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials."
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/generate_notes', methods=['POST'])
def generate_notes():
    if 'email' not in session:
        return redirect(url_for('login'))

    email = session['email']
    user = find_user_by_email(email)
    if not user:
        return "User not found"

    subject = request.form['subject']
    syllabus = request.form['syllabus']

    # ✅ Get or create the 'My Notes' folder
    my_notes_folder = get_or_create_my_notes_folder(user['_id'])

    topics = syllabus.strip().split("\n")

    for topic in topics:
        if not topic.strip():
            continue

        detailed_note = generate_notes_from_topic(topic.strip())

        note_data = {
            "user_id": user['_id'],
            "folder_id": my_notes_folder['_id'],
            "subject": f"{subject} – {topic.strip()}",
            "content": detailed_note
        }
        insert_note(note_data)

    return redirect(url_for('dashboard'))


@app.route('/add_folder', methods=['POST'])
def add_folder():
    if 'email' not in session:
        return redirect(url_for('login'))

    folder_name = request.form['folder_name']
    email = session['email']
    user = find_user_by_email(email)

    create_folder(folder_name, user['_id'])
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))

    email = session['email']
    user = find_user_by_email(email)
    user_id = user['_id']

    folders = list(get_folders_by_user(user_id))

    # Always show "My Notes" first
    folders.sort(key=lambda x: (not x.get('is_default', False), x['name'].lower()))

    folder_id = request.args.get('folder_id')
    if not folder_id:
        # Default to My Notes folder
        default_folder = next((f for f in folders if f.get('is_default')), None)
        if default_folder:
            folder_id = str(default_folder['_id'])

    notes_by_folder = {}
    for folder in folders:
        notes = list(get_notes_by_folder(folder['_id']))
        notes_by_folder[str(folder['_id'])] = notes

    return render_template(
        'dashboard.html',
        email=email,
        folders=folders,
        notes_by_folder=notes_by_folder,
        active_folder_id=folder_id
    )
@app.route('/note/<note_id>', methods=['GET'])
def note_reading(note_id):
    # Fetch the note using the note_id
    note = get_note_by_id(note_id)  # Replace with your method to fetch the note from the database
    
    if not note:
        return "Note not found", 404
    
    return render_template('note_reading.html', note=note)

if __name__ == '__main__':
    app.run(debug=True)
