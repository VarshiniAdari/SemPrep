# database/db_models.py
import markdown
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['semprep']

users_collection = db['users']
notes_collection = db['notes']
folders_collection = db['folders']

# ----------------- User Operations -----------------
def find_user_by_email(email):
    return users_collection.find_one({"email": email})

def insert_user(user_data):
    result = users_collection.insert_one(user_data)
    user_id = result.inserted_id

    # Automatically create 'My Notes' folder for the user
    folders_collection.insert_one({
        "user_id": user_id,
        "name": "My Notes",
        "is_default": True
    })

    return result


# ----------------- Folder Operations -----------------
def create_folder(folder_name, user_id):
    existing = folders_collection.find_one({"name": folder_name, "user_id": ObjectId(user_id)})
    if existing:
        return existing['_id']
    folder_data = {
        "name": folder_name,
        "user_id": ObjectId(user_id)
    }
    return folders_collection.insert_one(folder_data).inserted_id

def create_my_notes_folder(user_id):
    return create_folder("My Notes", user_id)

def get_folders_by_user(user_id):
    return folders_collection.find({"user_id": ObjectId(user_id)})

def get_folder_by_name(user_id, name):
    return folders_collection.find_one({"name": name, "user_id": ObjectId(user_id)})

# ----------------- Note Operations -----------------
# Convert markdown to HTML
def convert_markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text)

# ----------------- Note Operations -----------------
def insert_note(note_data):
    # Convert markdown to HTML before inserting
    note_data['content'] = convert_markdown_to_html(note_data['content'])
    return notes_collection.insert_one(note_data)

def get_notes_by_folder(folder_id):
    return notes_collection.find({"folder_id": ObjectId(folder_id)})

# database/db_models.py

def get_or_create_my_notes_folder(user_id):
    folder = folders_collection.find_one({
        "user_id": user_id,
        "name": "My Notes"
    })

    if folder:
        return folder

    # If not exists, create it
    folder_id = folders_collection.insert_one({
        "user_id": user_id,
        "name": "My Notes",
        "is_default": True  # Optional flag for clarity
    }).inserted_id

    return folders_collection.find_one({"_id": folder_id})
def get_note_by_id(note_id):
    return notes_collection.find_one({"_id": ObjectId(note_id)})

