from fastapi import APIRouter, UploadFile, File, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR
import tempfile
import os
import logging
import json
import time
import requests
from typing import Optional

from app.services.cv_parser import cv_parser_service

router = APIRouter()
logger = logging.getLogger(__name__)

# URL du service de parsing CV
CV_PARSER_URL = os.environ.get("CV_PARSER_SERVICE_URL", "http://cv-parser:5000")

@router.post("/parse-cv/", summary="Parse un CV à partir d'un fichier PDF ou DOCX")
async def parse_cv(
    file: UploadFile = File(...),
    force_refresh: Optional[bool] = Form(False),
    detailed_mode: Optional[bool] = Form(True)
):
    """
    Parse un CV à partir d'un fichier PDF ou DOCX et extrait les informations pertinentes.
    
    Cet endpoint prend en entrée un fichier CV et renvoie une structure de données
    contenant les informations extraites, notamment :
    - Informations personnelles (nom, email, téléphone)
    - Poste actuel ou recherché
    - Compétences techniques
    - Logiciels maîtrisés
    - Expériences professionnelles
    - Formation
    """
    try:
        # Vérifier l'extension du fichier
        if not file.filename or not (file.filename.endswith('.pdf') or 
                                     file.filename.endswith('.docx') or 
                                     file.filename.endswith('.doc')):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Le fichier doit être au format PDF ou DOCX"
            )
        
        try:
            # Essayer d'utiliser le service de parsing amélioré local
            parsed_cv = await cv_parser_service.parse_cv(file)
            normalized_data = normalize_parser_result(parsed_cv)
            
            # Ajouter les métadonnées de traitement
            normalized_data["processing_time"] = 0.5  # Valeur estimée
            
            return normalized_data
            
        except Exception as local_err:
            logger.warning(f"Échec du parsing local, essai avec le service distant: {str(local_err)}")
            
            # Réinitialiser la position du fichier
            await file.seek(0)
            
            # Créer un fichier temporaire pour stocker le contenu du fichier
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                try:
                    # Écrire le contenu du fichier téléchargé dans le fichier temporaire
                    content = await file.read()
                    temp_file.write(content)
                    temp_file.flush()
                    
                    # Préparer les données du formulaire multipart pour l'API de parsing
                    files = {'file': (file.filename, open(temp_file.name, 'rb'), file.content_type)}
                    data = {
                        'force_refresh': 'true' if force_refresh else 'false',
                        'detailed_mode': 'true' if detailed_mode else 'false'
                    }
                    
                    # Appeler le service de parsing CV externe
                    logger.info(f"Envoi du fichier {file.filename} au service de parsing CV externe")
                    start_time = time.time()
                    
                    response = requests.post(
                        f"{CV_PARSER_URL}/api/parse-cv/",
                        files=files,
                        data=data
                    )
                    
                    processing_time = time.time() - start_time
                    logger.info(f"Parsing terminé en {processing_time:.2f} secondes")
                    
                    if response.status_code == 200:
                        # Normaliser la réponse pour assurer la compatibilité avec le frontend
                        parsed_data = response.json()
                        
                        # S'assurer que les champs requis existent dans la réponse
                        normalized_data = normalize_parser_result(parsed_data)
                        
                        # Ajouter les métadonnées de traitement
                        normalized_data["processing_time"] = processing_time
                        
                        return normalized_data
                    else:
                        logger.error(f"Erreur lors du parsing du CV: {response.text}")
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=f"Erreur du service de parsing: {response.text}"
                        )
                finally:
                    # Nettoyer le fichier temporaire
                    if os.path.exists(temp_file.name):
                        os.unlink(temp_file.name)
                
    except HTTPException:
        # Re-lancer les exceptions HTTP déjà formatées
        raise
    except Exception as e:
        logger.exception(f"Erreur lors du parsing du CV: {str(e)}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du parsing du CV: {str(e)}"
        )

def normalize_parser_result(data):
    """
    Normaliser les données du parsing pour assurer une structure cohérente
    """
    # Si les données sont un objet Pydantic, le convertir en dict
    if not isinstance(data, dict):
        try:
            data = data.dict()
        except:
            # Si ce n'est pas un objet Pydantic avec méthode dict()
            pass
    
    # Si les données sont imbriquées dans un sous-objet 'data'
    parsed_data = data.get('data', data)
    
    # Structure de base normalisée
    normalized = {
        "personal_info": {
            "name": "",
            "email": "",
            "phone": "",
            "address": ""
        },
        "position": "",
        "skills": [],
        "experiences": [],
        "education": [],
        "languages": [],
        "softwares": []
    }
    
    # Récupérer les informations personnelles
    if 'personal_info' in parsed_data:
        personal_info = parsed_data['personal_info']
        if isinstance(personal_info, dict):
            normalized["personal_info"]["name"] = personal_info.get("name", "")
            normalized["personal_info"]["email"] = personal_info.get("email", "")
            normalized["personal_info"]["phone"] = personal_info.get("phone", "")
            normalized["personal_info"]["address"] = personal_info.get("address", "")
            
            # Enlever le préfixe "undefined" des noms si présent
            if normalized["personal_info"]["name"] and normalized["personal_info"]["name"].startswith("undefined "):
                normalized["personal_info"]["name"] = normalized["personal_info"]["name"].replace("undefined ", "")
    
    # Récupérer le poste
    normalized["position"] = parsed_data.get("position", "")
    
    # Normaliser les compétences
    if 'skills' in parsed_data and isinstance(parsed_data['skills'], list):
        for skill in parsed_data['skills']:
            if isinstance(skill, dict) and 'name' in skill:
                normalized["skills"].append(skill)
            else:
                normalized["skills"].append({"name": str(skill)})
    
    # Normaliser les expériences professionnelles
    experiences_key = 'experiences' if 'experiences' in parsed_data else 'experience'
    if experiences_key in parsed_data and isinstance(parsed_data[experiences_key], list):
        for exp in parsed_data[experiences_key]:
            if isinstance(exp, dict):
                normalized["experiences"].append({
                    "title": exp.get("title", ""),
                    "company": exp.get("company", ""),
                    "start_date": exp.get("start_date", ""),
                    "end_date": exp.get("end_date", ""),
                    "description": exp.get("description", "")
                })
    
    # Normaliser l'éducation
    if 'education' in parsed_data and isinstance(parsed_data['education'], list):
        for edu in parsed_data['education']:
            if isinstance(edu, dict):
                normalized["education"].append({
                    "degree": edu.get("degree", ""),
                    "institution": edu.get("institution", ""),
                    "start_date": edu.get("start_date", ""),
                    "end_date": edu.get("end_date", "")
                })
    
    # Normaliser les langues
    if 'languages' in parsed_data and isinstance(parsed_data['languages'], list):
        for lang in parsed_data['languages']:
            if isinstance(lang, dict):
                normalized["languages"].append({
                    "language": lang.get("language", ""),
                    "level": lang.get("level", "")
                })
    
    # Normaliser les logiciels
    if 'softwares' in parsed_data and isinstance(parsed_data['softwares'], list):
        normalized["softwares"] = parsed_data['softwares']
    
    return normalized