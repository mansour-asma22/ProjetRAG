# ProjetRAG

**Système de récupération de documents augmentée avec embeddings et API**

##  Description

Projet académique : 

L’objectif du projet est de créer un système capable de :

1. Encoder des documents textuels sous forme de vecteurs (embeddings) et les stocker dans une base de données.
2. Rechercher les documents les plus pertinents selon une requête utilisateur.
3. Reformuler et contextualiser la réponse via l’API OpenAI.

Le système inclut également une interface utilisateur interactive sous forme de **chatbot** pour faciliter les interactions.

---

##  Architecture

- **Watchdog** : Surveille le dossier `data/` pour détecter automatiquement de nouveaux documents.
- **Service Web API d’encodage** : Encode les documents en embeddings et les stocke dans MongoDB.
- **Service Web API de recherche** : Recherche les documents les plus pertinents via similarité cosinus.
- **Service Web API de reformulation** : Génère une réponse contextuelle à partir des documents trouvés.
- **Interface utilisateur** : Chat interactif basé sur un template open-source.

---

##  Exécution : 


Créer un environnement virtuel Python (recommandé) : python -m venv venv
Installer les dépendances : pip install -r requirements.txt
Créer un fichier .env pour tes clés secrètes : OPENAI_API_KEY=ta_cle_openai
Lancer le projet : python main.py
Déposer des fichiers textuels dans le dossier data/.
Ouvrir l’interface utilisateur dans un navigateur pour poser des questions.
Les réponses seront générées automatiquement en combinant recherche et reformulation.
