from fastapi import FastAPI
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sentence_transformers import SentenceTransformer
from utils.db import insert_document
import os
import threading

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

def start_watchdog():
    """
    Démarre le watchdog pour surveiller les fichiers dans le répertoire `data/`.
    """
    directory = "data/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    event_handler = FileHandler()
    observer = Observer()
    observer.schedule(event_handler, directory, recursive=False)
    observer.start()
    print(f"Watchdog is watching directory: {directory}")
    # Assurez-vous que l'observateur continue à fonctionner
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
        print("Watchdog stopped.")

# Lancer le Watchdog automatiquement au démarrage
@app.on_event("startup")
def startup_event():
    thread = threading.Thread(target=start_watchdog, daemon=True)
    thread.start()
    print("Watchdog has been started in a background thread.")

# Une route de test pour vérifier que l'application fonctionne
@app.get("/")
def root():
    return {"message": "Watchdog is running in the background."}
