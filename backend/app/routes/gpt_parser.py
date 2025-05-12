from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
import logging
import time
import sys
import json
from typing import Dict, Any

# Importer les fonctions du script parse_fdp_gpt.py
# Assurez-vous que ce script est dans votre PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from parse_fdp_gpt import extract_text_from_pdf, analyze_with_gpt

router = APIRouter(
    prefix="/api",
    tags=["gpt-parser"],
    responses={404: {"description": "Not found"}},
)

@router.post("/parse-with-gpt")
async def parse_with_gpt(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Endpoint pour parser une fiche de poste avec GPT.
    Accepte un fichier PDF, DOC, DOCX ou TXT et retourne les informations structurées.
    """
    start_time = time.time()
    logging.info(f"Traitement du fichier: {file.filename}")
    
    # Vérifier l'extension du fichier
    allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Format de fichier non supporté. Formats acceptés: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Enregistrer temporairement le fichier
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        # Extraire le texte du fichier
        logging.info(f"Extraction du texte du fichier {temp_file_path}")
        text = extract_text_from_pdf(temp_file_path)
        
        # Traiter le texte avec GPT
        logging.info("Analyse du texte avec GPT")
        result = analyze_with_gpt(text)
        
        # Supprimer le fichier temporaire
        try:
            os.unlink(temp_file_path)
        except Exception as e:
            logging.warning(f"Erreur lors de la suppression du fichier temporaire: {e}")
        
        # Vérifier si l'analyse a réussi
        if not result:
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de l'analyse du document par GPT"
            )
        
        # Ajouter des informations de temps
        processing_time = time.time() - start_time
        logging.info(f"Traitement terminé en {processing_time:.2f} secondes")
        
        # Retourner le résultat
        return {
            "success": True,
            "data": result,
            "processing_time": f"{processing_time:.2f} secondes"
        }
    
    except Exception as e:
        logging.error(f"Erreur lors du traitement: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du traitement: {str(e)}"
        )
