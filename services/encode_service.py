from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sentence_transformers import SentenceTransformer
from utils.db import insert_document
import os
from typing import List

app = FastAPI()

# Charger le modèle
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# Classe pour surveiller les fichiers
class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".txt"):
            print(f"New file detected: {event.src_path}")
            process_documents(event.src_path)

def process_documents(file_path):
    """
    Encode les documents d'un fichier et les insère dans MongoDB.
    """
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        documents = f.readlines()

    for i, text in enumerate(documents):
        text = text.strip()
        if text:  # Ignorer les lignes vides
            embedding = model.encode(text).tolist()
            doc = {
                "id": f"{os.path.basename(file_path)}_{i}",
                "text": text,
                "embedding": embedding,
            }
            insert_document(doc)
    print(f"Processed and stored documents from {file_path}.")

# Classe pour encodage manuel
class Document(BaseModel):
    documents: List[str]

# Route pour encoder les documents manuellement
@app.post("/encode_documents")
def encode_documents(doc: Document):
    """
    Encode les documents reçus et les insère dans MongoDB.
    """
    for i, text in enumerate(doc.documents):
        embedding = model.encode(text).tolist()
        doc = {
            "id": f"manual_{i}",
            "text": text,
            "embedding": embedding,
        }
        insert_document(doc)
    return {"status": "success", "message": "Documents encoded and stored successfully"}
