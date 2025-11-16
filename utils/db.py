from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]

def insert_document(document):
    """
    Insère un document dans la collection MongoDB.
    """
    collection.insert_one(document)

def fetch_all_documents():
    """
    Récupère tous les documents stockés dans la collection MongoDB.
    """
    return list(collection.find({}, {"_id": 0}))  # Exclure le champ "_id"
