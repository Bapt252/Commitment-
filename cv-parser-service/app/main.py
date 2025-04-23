import os
import tempfile
import shutil
import logging
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from services.cv_parser import parse_cv, CVParserError
from app.models.cv_model import CVModel

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Commitment CV Parser API",
    description="API pour extraire automatiquement les informations des CV",
    version="1.0.0",
)

# Configuration des CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines exactes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Point d'entrée racine pour vérifier que l'API est en ligne"""
    return {"message": "Commitment CV Parser API v1.0.0"}

@app.get("/health")
async def health_check():
    """Endpoint de health check pour la surveillance de l'application"""
    return {"status": "ok"}

@app.post("/api/parse-cv/", response_model=CVModel)
async def parse_cv_endpoint(
    file: UploadFile = File(...),
    force_refresh: bool = Form(False),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Parse un CV (PDF ou DOCX) et extrait les informations structurées.
    
    - **file**: Fichier CV (PDF ou DOCX)
    - **force_refresh**: Forcer le rafraîchissement du cache (défaut: False)
    
    Retourne un objet structuré contenant les informations du CV.
    """
    # Vérification de l'extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    allowed_extensions = ['.pdf', '.docx', '.doc']
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Format de fichier non supporté. Formats supportés: {', '.join(allowed_extensions)}"
        )
    
    # Sauvegarde temporaire du fichier
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_extension)
    try:
        # Copie du contenu
        with temp_file as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parsing du CV
        try:
            cv_model, from_cache = parse_cv(open(temp_file.name, 'rb'), file.filename, force_refresh)
            logger.info(f"CV parsed successfully, from cache: {from_cache}")
            
            # Nettoyage du fichier en arrière-plan
            background_tasks.add_task(os.unlink, temp_file.name)
            
            return cv_model
        except CVParserError as e:
            logger.error(f"Error parsing CV: {str(e)}")
            raise HTTPException(status_code=422, detail=str(e))
        
    except Exception as e:
        # Nettoyage en cas d'erreur
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Une erreur inattendue s'est produite: {str(e)}")

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Une erreur inattendue s'est produite: {str(exc)}"}
    )

# Point d'entrée pour uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENVIRONMENT", "production").lower() == "development"
    )
