from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np
from utils.db import fetch_all_documents

# Création de l'application FastAPI
app = FastAPI()

# Charger le modèle SentenceTransformer
model = SentenceTransformer("paraphrase-MiniLM-L6-v2")


# Classe pour les requêtes utilisateur
class Query(BaseModel):
    query: str


# Classe pour représenter un document pertinent
class RelevantDocument(BaseModel):
    id: str
    text: str
    similarity: float


# Calcul de similarité cosinus
def cosine_similarity(vec1, vec2):
    """
    Calcule la similarité cosinus entre deux vecteurs.
    """
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


@app.post("/search_documents", response_model=List[RelevantDocument])
def search_documents(query: Query):
    """
    Recherche les documents les plus pertinents pour une requête donnée.
    """
    try:
        # Étape 1 : Encoder la requête utilisateur
        query_embedding = model.encode(query.query)

        # Étape 2 : Récupérer tous les documents de la base de données
        all_documents = fetch_all_documents()
        if not all_documents:
            raise HTTPException(status_code=404, detail="Aucun document trouvé dans la base de données.")

        # Étape 3 : Calculer la similarité cosinus entre la requête et chaque document
        similarities = []
        for doc in all_documents:
            doc_embedding = np.array(doc["embedding"])
            similarity = cosine_similarity(query_embedding, doc_embedding)
            similarities.append({
                "id": doc["id"],
                "text": doc["text"],
                "similarity": similarity
            })

        # Étape 4 : Trier les documents par similarité décroissante
        sorted_documents = sorted(similarities, key=lambda x: x["similarity"], reverse=True)

        # Étape 5 : Retourner les 2 documents les plus pertinents
        top_documents = sorted_documents[:2]
        return [
            RelevantDocument(
                id=doc["id"],
                text=doc["text"],
                similarity=doc["similarity"]
            ) for doc in top_documents
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la recherche : {str(e)}")
