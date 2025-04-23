"""
API de conversation avec l'API Chat GPT.
"""

from fastapi import APIRouter, Body, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.nlp.chat_gpt import ChatGPTSession, get_chat_response

router = APIRouter()

# Modèles de données pour l'API
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None
    model: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    history: List[ChatMessage]

@router.post("/chat", response_model=ChatResponse)
def chat_with_gpt(request: ChatRequest = Body(...)):
    """
    Point d'entrée API pour discuter avec GPT.
    Conserve l'historique de la conversation pour maintenir le contexte.
    """
    # Convertir l'historique si présent
    history = None
    if request.history:
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
    
    # Obtenir une réponse
    result = get_chat_response(request.message, history, request.model)
    
    # Convertir l'historique pour la réponse
    history_response = [ChatMessage(role=msg["role"], content=msg["content"]) 
                      for msg in result["history"]]
    
    return ChatResponse(
        response=result["response"],
        history=history_response
    )

@router.post("/chat/session", response_model=ChatResponse)
def start_chat_session(request: ChatRequest = Body(...)):
    """
    Démarre une nouvelle session de chat avec GPT.
    Utilisez cet endpoint pour le premier message d'une conversation.
    """
    # Créer une nouvelle session
    session = ChatGPTSession(model=request.model)
    
    # Envoyer le message et obtenir une réponse
    response = session.send_message(request.message)
    
    # Convertir l'historique pour la réponse
    history_response = [ChatMessage(role=msg["role"], content=msg["content"]) 
                      for msg in session.get_history()]
    
    return ChatResponse(
        response=response,
        history=history_response
    )
