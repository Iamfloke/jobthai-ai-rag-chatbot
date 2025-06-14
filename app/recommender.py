# app/recommender.py

import os
import json
from datetime import date
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv
from langdetect import detect

load_dotenv()
client = OpenAI()

def translate_thai_to_english(text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Translate the following Thai text to English. Reply only with the translation."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Translation failed: {e}")
        return text


def load_embeddings():
    today = date.today().isoformat()
    path = f"data/jobs_{today}_embeddings.json"
    if not os.path.exists(path):
        raise FileNotFoundError(f"No embedding file: {path}")
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def get_embedding(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding failed: {e}")
        return None

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def recommend_jobs(query: str, top_k=5):
    try:
        if detect(query) == "th":
            query = translate_thai_to_english(query)
            print(f"Translated query: {query}")
    except:
        pass
    query_embedding = get_embedding(query)
    if query_embedding is None:
        return [{"error": "Failed to embed query"}]

    data = load_embeddings()
    results = []
    for item in data:
        job = item["job"]
        embedding = item["embedding"]
        score = cosine_similarity(query_embedding, embedding)
        results.append((score, job))

    results.sort(reverse=True, key=lambda x: x[0])

    return [
        {
            "title": job["title"],
            "company": job["company"],
            "location": job["location"],
            "salary": job["salary"],
            "url": job["url"],
            "score": round(score, 3)
        }
        for score, job in results[:top_k]
    ]
