import openai
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupérer la clé API depuis les variables d'environnement
openai.api_key = os.getenv("OPENAI_API_KEY")

def reformulate_with_chatgpt(documents, user_query):
    """
    Combine les deux meilleurs documents et reformule la réponse avec ChatGPT (GPT-3.5-turbo).
    """
    if len(documents) < 2:
        raise ValueError("Deux documents pertinents sont nécessaires pour reformuler la réponse.")

    # Préparer le prompt pour ChatGPT
    prompt = f"""
    L'utilisateur a posé la question suivante : "{user_query}"
    Voici deux documents pertinents :
    1. {documents[0]["text"]}
    2. {documents[1]["text"]}
    Reformule une réponse complète et claire en utilisant ces documents comme base.
    """

    try:
        # Appeler l'API OpenAI avec le modèle GPT-3.5-turbo via v1/chat/completions
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Utilisation du modèle GPT-3.5-turbo
            messages=[
                {"role": "system", "content": "Vous êtes un assistant utile et précis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,         # Limiter la réponse à 150 tokens
            temperature=0.7         # Paramètre pour varier la créativité de la réponse
        )
        
        # Retourner la réponse reformulée
        return response['choices'][0]['message']['content'].strip()

    except openai.OpenAIError as e:
        print(f"Erreur avec l'API OpenAI : {e}")
        return "Une erreur s'est produite lors de la génération de la réponse."
