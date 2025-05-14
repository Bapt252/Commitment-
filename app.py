from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import sys
import json
import logging
from typing import Dict, Any, Optional, Union, List

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

# Configuration CORS plus permissive pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simuler l'extraction de données si le module parse_fdp_gpt n'est pas disponible
def mock_parse_job_posting(file_path: str) -> Dict[str, Union[str, List[str]]]:
    """
    Fonction de simulation pour tester l'API sans le module de parsing réel.
    """
    logger.info(f"Analyse simulée du fichier: {file_path}")
    
    # Extraire juste le nom du fichier pour les tests
    file_name = os.path.basename(file_path)
    
    # Résultats simulés
    mock_data = {
        "titre": f"Développeur Python (Extrait de {file_name})",
        "entreprise": "TechCorp Solutions",
        "localisation": "Paris, France",
        "type_contrat": "CDI",
        "competences": ["Python", "FastAPI", "JavaScript", "HTML/CSS", "Git"],
        "experience": "3-5 ans",
        "formation": "Bac+5 en informatique ou équivalent",
        "salaire": "45-55K€ selon expérience",
        "responsabilites": [
            "Développement de nouvelles fonctionnalités",
            "Maintenance des applications existantes",
            "Participation aux revues de code",
            "Tests et déploiement"
        ]
    }
    
    # Pour le débogage : écrire le contenu extrait dans un fichier
    with open('extracted_data.json', 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=2)
    
    return mock_data

@app.get("/")
async def read_root():
    return {"message": "API d'analyse de fiches de poste active"}

@app.get("/status")
async def check_status():
    """Endpoint pour vérifier que l'API fonctionne."""
    return {"status": "ok", "message": "Le serveur d'analyse de fiches de poste est opérationnel"}

@app.post("/api/parse-job-posting")
async def parse_job_posting_api(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Endpoint pour analyser une fiche de poste et en extraire les informations structurées.
    
    Args:
        file: Le fichier de la fiche de poste à analyser
        
    Returns:
        Un dictionnaire contenant les informations structurées extraites
    """
    try:
        logger.info(f"Réception d'un fichier: {file.filename}")
        
        # Vérifier le type de fichier
        allowed_extensions = [".pdf", ".docx", ".txt"]
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            logger.warning(f"Extension de fichier non supportée: {file_ext}")
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
            # Essayer d'importer et d'utiliser le module parse_fdp_gpt
            try:
                # Importez votre script de parsing existant
                sys.path.append(os.path.dirname(os.path.abspath(__file__)))
                from parse_fdp_gpt import parse_job_posting
                logger.info("Module parse_fdp_gpt importé avec succès")
                
                # Utiliser la fonction de parsing réelle
                parsed_data = parse_job_posting(temp_file_path)
                logger.info("Analyse réelle effectuée avec succès")
                
            except ImportError:
                # Si le module n'est pas trouvé, utiliser la fonction de simulation
                logger.warning("Module parse_fdp_gpt non trouvé, utilisation du mode simulation")
                parsed_data = mock_parse_job_posting(temp_file_path)
            
            # Vérifier si les données extraites sont valides
            if not parsed_data or not isinstance(parsed_data, dict):
                logger.error("La fonction de parsing n'a pas retourné de données valides")
                raise ValueError("La fonction de parsing n'a pas retourné de données valides")
            
            # Log des données extraites pour le débogage
            logger.info(f"Données extraites: {json.dumps(parsed_data, ensure_ascii=False)}")
                
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
    
    except HTTPException:
        # Relancer les exceptions HTTP déjà formatées
        raise
        
    except Exception as e:
        logger.error(f"Erreur serveur: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Afficher un message d'information sur le démarrage du serveur
    print("=" * 50)
    print("Démarrage du serveur d'analyse de fiches de poste...")
    print("Accédez à l'API via: http://localhost:5055")
    print("Pour tester l'API: http://localhost:5055/status")
    print("=" * 50)
    
    # S'assurer que le répertoire de travail est correct
    print(f"Répertoire de travail actuel: {os.getcwd()}")
    
    # Démarrer le serveur
    uvicorn.run(app, host="0.0.0.0", port=5055)
