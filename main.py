from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import requests
import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from sentence_transformers import SentenceTransformer
from services.chatgpt_service import reformulate_with_chatgpt
from utils.db import insert_document
from fastapi.middleware.cors import CORSMiddleware




# Création de l'application FastAPI
app = FastAPI()

# Ajouter le middleware CORS à votre application FastAPI
origins = [
    "http://localhost:8000",  # Frontend
    "http://127.0.0.1:8000",  # Frontend en cas de différences d'adresses
    "http://127.0.0.1:8005",  # Backend
    "http://localhost:8005",  # Backend
    "http://127.0.0.1:8001",  # Autres services backend si nécessaire
    "http://localhost:8001",  # Autres services backend si nécessaire
    "http://127.0.0.1:8002",  # Autres services backend si nécessaire
    "http://localhost:8002",  # Autres services backend si nécessaire
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Liste des domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permet tous les en-têtes
)
# Configuration des templates et des fichiers statiques
templates_dir = "templates"
static_dir = "static"

# Mount des fichiers statiques
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Démarrer les services secondaires en parallèle
subprocess.Popen(["uvicorn", "services.encode_service:app", "--host", "0.0.0.0", "--port", "8001", "--reload"])
subprocess.Popen(["uvicorn", "services.search_service:app", "--host", "0.0.0.0", "--port", "8002", "--reload"])

# Configuration des templates
templates = Jinja2Templates(directory=templates_dir)

# Charger le modèle pour le Watchdog
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")

# Classe pour surveiller les fichiers
class FileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith(".txt"):
            print(f"New file detected: {event.src_path}")
            time.sleep(2)  # Attendre 2 secondes avant de traiter
            process_documents(event.src_path)


def process_documents(file_path):
    """
    Encode les documents d'un fichier et les insère dans MongoDB.
    """
    # Réessayer plusieurs fois si le fichier est verrouillé
    retries = 5
    while retries > 0:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                documents = f.readlines()
            break  # Sortir de la boucle si l'ouverture réussit
        except PermissionError:
            print(f"Permission denied for file {file_path}. Retrying...")
            retries -= 1
            time.sleep(1)  # Attendre 1 seconde avant de réessayer
    else:
        print(f"Failed to open file {file_path} after multiple attempts.")
        return

    # Traiter les documents
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

# Route principale pour l'interface utilisateur
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "results": None})

# Route de recherche

from fastapi.responses import JSONResponse

@app.post("/search_and_reformulate")
async def search_and_reformulate(request: Request, query: str = Form(...)):
    """
    Recherche les documents et reformule une réponse avec ChatGPT.
    """
    print(f"Received query: {query}")  # Log de la requête reçue

    # Étape 1 : Rechercher les 2 meilleurs documents
    try:
        search_response = requests.post(
            "http://127.0.0.1:8002/search_documents",
            json={"query": query}
        )
        print(f"Search service status: {search_response.status_code}")  # Log du status du service de recherche
    except Exception as e:
        print(f"Error with search service: {e}")  # Log si l'appel échoue

    if search_response.status_code != 200:
        print("Error: Could not fetch relevant documents.")  # Log si erreur dans la récupération des documents
        return JSONResponse(
            content={"response": "Erreur : Impossible de récupérer les documents pertinents."},
            status_code=500
        )

    # Récupérer les documents
    relevant_documents = search_response.json()
    if len(relevant_documents) < 2:
        print("Not enough documents found.")  # Log si pas assez de documents
        return JSONResponse(
            content={"response": "Pas assez de documents pertinents pour reformuler une réponse."},
            status_code=400
        )

    # Étape 2 : Reformuler avec ChatGPT
    reformulated_response = reformulate_with_chatgpt(relevant_documents, query)

    print(f"Reformulated response: {reformulated_response}")  # Log de la réponse reformulée

    # Retourner la réponse reformulée
    return JSONResponse(content={"response": reformulated_response})


# Lancer l'application sur le port 8005
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)
