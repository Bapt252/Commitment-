"""
Module d'intégration directe avec l'API Chat GPT.
Permet d'avoir des conversations directes avec les modèles GPT.
"""

import os
import logging
from typing import List, Dict, Any, Optional
import openai
from dotenv import load_dotenv

# Configuration du logging
logger = logging.getLogger(__name__)

# Configuration de l'API OpenAI - priorité aux secrets GitHub
if "OPENAI" in os.environ:
    openai.api_key = os.environ["OPENAI"]
    logger.info("Utilisation de la clé API OpenAI depuis les secrets GitHub")
else:
    # Fallback vers le fichier .env pour les environnements de développement
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    logger.info("Utilisation de la clé API OpenAI depuis le fichier .env")

# Modèle par défaut - utiliser gpt-4o-mini
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4o-mini")


class ChatGPTSession:
    """
    Classe pour gérer une session de conversation avec l'API Chat GPT.
    Conserve l'historique des échanges pour maintenir le contexte de la conversation.
    """
    
    def __init__(self, system_prompt: str = None, model: str = None):
        """
        Initialise une nouvelle session de chat.
        
        Args:
            system_prompt: Instruction système initiale (optionnel)
            model: Modèle GPT à utiliser (par défaut: celui défini dans l'environnement)
        """
        self.model = model or GPT_MODEL
        self.messages = []
        
        # Ajouter le message système si fourni
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})
        else:
            # Message système par défaut
            self.messages.append({
                "role": "system", 
                "content": "Tu es un assistant intelligent et utile pour Commitment, une plateforme de matching entre candidats et offres d'emploi."
            })
    
    def send_message(self, message: str) -> str:
        """
        Envoie un message à l'API Chat GPT et obtient une réponse.
        
        Args:
            message: Message utilisateur à envoyer
            
        Returns:
            str: Réponse de l'API Chat GPT
        """
        # Ajouter le message de l'utilisateur à l'historique
        self.messages.append({"role": "user", "content": message})
        
        try:
            # Appeler l'API
            response = openai.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.7,
                max_tokens=1000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            # Extraire la réponse
            assistant_message = response.choices[0].message.content.strip()
            
            # Ajouter la réponse à l'historique
            self.messages.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API Chat GPT: {e}")
            return f"Désolé, une erreur s'est produite lors de la communication avec l'API : {str(e)}"
    
    def clear_history(self) -> None:
        """
        Efface l'historique de la conversation tout en conservant le message système initial.
        """
        system_message = None
        for message in self.messages:
            if message["role"] == "system":
                system_message = message
                break
        
        self.messages = []
        if system_message:
            self.messages.append(system_message)
    
    def get_history(self) -> List[Dict[str, str]]:
        """
        Récupère l'historique complet de la conversation.
        
        Returns:
            List: Liste des messages échangés
        """
        return self.messages


# Fonction d'interface simple pour utilisation dans d'autres modules
def get_chat_response(message: str, history: List[Dict[str, str]] = None, model: str = None) -> Dict[str, Any]:
    """
    Obtient une réponse de l'API Chat GPT pour un message.
    
    Args:
        message: Message à envoyer
        history: Historique des messages précédents (optionnel)
        model: Modèle GPT à utiliser (optionnel)
        
    Returns:
        Dict: Contient la réponse et l'historique mis à jour
    """
    model = model or GPT_MODEL
    
    # Préparer les messages
    messages = history.copy() if history else []
    
    # Ajouter un message système par défaut si aucun n'est présent
    has_system_message = any(msg.get("role") == "system" for msg in messages)
    if not has_system_message:
        messages.insert(0, {
            "role": "system", 
            "content": "Tu es un assistant intelligent et utile pour Commitment, une plateforme de matching entre candidats et offres d'emploi."
        })
    
    # Ajouter le message utilisateur
    messages.append({"role": "user", "content": message})
    
    try:
        # Appeler l'API
        response = openai.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        # Extraire la réponse
        assistant_message = response.choices[0].message.content.strip()
        
        # Ajouter la réponse à l'historique
        messages.append({"role": "assistant", "content": assistant_message})
        
        return {
            "response": assistant_message,
            "history": messages
        }
            
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à l'API Chat GPT: {e}")
        messages.append({"role": "assistant", "content": f"Désolé, une erreur s'est produite: {str(e)}"})
        return {
            "response": f"Désolé, une erreur s'est produite lors de la communication avec l'API : {str(e)}",
            "history": messages
        }
