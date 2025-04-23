"""
API pour l'intégration du chat GPT avec le système de parsing.
Permet d'utiliser l'API ChatGPT pour analyser et discuter des documents parsés.
"""

from fastapi import APIRouter, Body, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json

from app.nlp.chat_gpt import ChatGPTSession, get_chat_response
from app.nlp.enhanced_parsing_system import parse_document
from app.nlp.gpt_parser import parse_document_with_gpt

router = APIRouter()

# Modèles de données pour l'API
class ChatMessage(BaseModel):
    role: str
    content: str

class ParsingChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = None
    document_data: Optional[Dict[str, Any]] = None
    doc_type: Optional[str] = None
    model: Optional[str] = None

class ParsingChatResponse(BaseModel):
    response: str
    history: List[ChatMessage]
    enhanced_data: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ParsingChatResponse)
def chat_about_parsed_document(request: ParsingChatRequest = Body(...)):
    """
    Permet de discuter avec ChatGPT à propos d'un document parsé.
    """
    # Convertir l'historique si présent
    history = None
    if request.history:
        history = [{"role": msg.role, "content": msg.content} for msg in request.history]
    
    # Si nous avons des données de document et qu'il s'agit du premier message (pas d'historique)
    if request.document_data and (not history or len(history) <= 1):
        # Créer un prompt système qui inclut les données du document
        doc_data_str = json.dumps(request.document_data, ensure_ascii=False, indent=2)
        doc_type = request.doc_type or "document"
        
        system_prompt = f"""Tu es un assistant spécialisé dans l'analyse de documents.
Tu réponds aux questions concernant le {doc_type} dont voici les données extraites:

{doc_data_str}

Utilise ces informations pour répondre aux questions de l'utilisateur.
Ne mentionne pas que tu as reçu ces données structurées, agis comme si tu avais analysé directement le document."""

        # Créer une session avec ce prompt spécial
        session = ChatGPTSession(system_prompt=system_prompt, model=request.model)
        response = session.send_message(request.message)
        
        # Convertir l'historique pour la réponse
        history_response = [ChatMessage(role=msg["role"], content=msg["content"]) 
                           for msg in session.get_history()]
        
        return ParsingChatResponse(
            response=response,
            history=history_response,
            enhanced_data=request.document_data
        )
    
    # Sinon, utiliser l'API standard
    result = get_chat_response(request.message, history, request.model)
    
    # Convertir l'historique pour la réponse
    history_response = [ChatMessage(role=msg["role"], content=msg["content"]) 
                       for msg in result["history"]]
    
    return ParsingChatResponse(
        response=result["response"],
        history=history_response,
        enhanced_data=request.document_data
    )

@router.post("/upload")
async def upload_and_parse_for_chat(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form(None)
):
    """
    Télécharge et parse un document pour une utilisation dans le chat.
    """
    try:
        # Lire le contenu du fichier
        file_content = await file.read()
        file_name = file.filename
        
        # Créer un fichier temporaire pour le contenu
        import io
        file_io = io.BytesIO(file_content)
        
        # Parser le document
        parsing_result = parse_document(
            file_content=file_io,
            file_name=file_name,
            doc_type=doc_type,
            use_gpt=True  # Utiliser GPT pour une meilleure extraction
        )
        
        return {
            "success": True,
            "document_data": parsing_result.get("extracted_data", {}),
            "confidence_scores": parsing_result.get("confidence_scores", {}),
            "doc_type": parsing_result.get("doc_type", doc_type or "unknown")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du parsing: {str(e)}")
