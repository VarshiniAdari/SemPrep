# prepgenie.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY")

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}"}

def generate_notes_from_topic(topic):
    prompt = (
        f"Generate detailed and well-structured study notes (~500 words) for the topic: '{topic}'. "
        "Include headings, bullet points, and examples if necessary. Notes should be informative, "
        "easy to read, and useful for a student preparing for exams."
    )
    
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 700, "temperature": 0.7}
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)
    result = response.json()
    print("Hugging Face response:", result)

    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    else:
        return "Note generation failed. Please try again."
