from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
import logging
from typing import Dict, Any

# Importez votre script de parsing existant
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from parse_fdp_gpt import parse_job_posting

app = FastAPI()

# Configuration du CORS pour permettre les requêtes depuis votre frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, limitez ceci à vos domaines spécifiques
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/parse-job-posting")
async def parse_job_posting_api(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Endpoint pour analyser une fiche de poste avec GPT et en extraire les informations structurées.
    
    Args:
        file: Le fichier de la fiche de poste à analyser
        
    Returns:
        Un dictionnaire contenant les informations structurées extraites
    """
    try:
        # Vérifier le type de fichier
        allowed_extensions = [".pdf", ".docx", ".txt"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Format de fichier non supporté. Formats acceptés: {', '.join(allowed_extensions)}"
            )
        
        # Sauvegarder le fichier temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        logger.info(f"Fichier temporaire créé: {temp_file_path}")
        
        try:
            # Appeler votre fonction de parsing existante
            parsed_data = parse_job_posting(temp_file_path)
            
            # Vérifier si les données extraites sont valides
            if not parsed_data or not isinstance(parsed_data, dict):
                raise ValueError("La fonction de parsing n'a pas retourné de données valides")
                
            return {
                "success": True,
                "data": parsed_data
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du parsing du fichier: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse du document: {str(e)}")
            
        finally:
            # Supprimer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.info(f"Fichier temporaire supprimé: {temp_file_path}")
    
    except Exception as e:
        logger.error(f"Erreur serveur: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5055)
