import os
import pyclamd
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime
from config import settings
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential


class AntivirusScanner:
    """
    Service d'analyse antivirus avec ClamAV
    """
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.host = host or settings.CLAMAV_HOST
        self.port = port or settings.CLAMAV_PORT
        self.clamd = None
    
    def _connect(self):
        """
        Établit une connexion avec le daemon ClamAV
        """
        if self.clamd is None:
            try:
                self.clamd = pyclamd.ClamdNetworkSocket(
                    host=self.host,
                    port=self.port
                )
                
                # Vérifier que le service est disponible
                if not self.clamd.ping():
                    logger.error("Service ClamAV non disponible")
                    self.clamd = None
                    raise ConnectionError("Service ClamAV non disponible")
                
                logger.info(f"Connexion établie avec ClamAV: {self.host}:{self.port}")
            
            except Exception as e:
                logger.error(f"Erreur de connexion à ClamAV: {str(e)}")
                self.clamd = None
                raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    def scan_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyse un fichier avec ClamAV
        """
        try:
            self._connect()
            
            # Vérifier que le fichier existe
            if not os.path.exists(file_path):
                logger.error(f"Fichier non trouvé: {file_path}")
                return {
                    "status": "error",
                    "message": "Fichier non trouvé",
                    "infected": False,
                    "threat_name": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Scanner le fichier
            scan_result = self.clamd.scan_file(file_path)
            
            if scan_result is None:
                # Fichier propre
                logger.info(f"Fichier analysé et propre: {file_path}")
                return {
                    "status": "success",
                    "infected": False,
                    "threat_name": None,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                # Fichier infecté
                _, threat = scan_result[file_path]
                logger.warning(f"Fichier infecté: {file_path}, menace: {threat}")
                return {
                    "status": "success",
                    "infected": True,
                    "threat_name": threat,
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Erreur d'analyse antivirus: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "infected": False,  # Par défaut, on considère le fichier comme propre en cas d'erreur
                "threat_name": None,
                "timestamp": datetime.utcnow().isoformat()
            }


class SecurityUtils:
    """
    Utilitaires de sécurité pour les documents
    """
    @staticmethod
    def compute_file_hash(file_path: str, algorithm: str = "sha256") -> str:
        """
        Calcule le hash d'un fichier
        """
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_obj.update(chunk)
        
        return hash_obj.hexdigest()
    
    @staticmethod
    async def compute_upload_file_hash(file, algorithm: str = "sha256") -> str:
        """
        Calcule le hash d'un fichier uploadé
        """
        hash_obj = hashlib.new(algorithm)
        content = await file.read()
        hash_obj.update(content)
        await file.seek(0)  # Réinitialiser le curseur du fichier
        return hash_obj.hexdigest()
    
    @staticmethod
    def validate_mime_type(mime_type: str) -> bool:
        """
        Vérifie si le type MIME est autorisé
        """
        return mime_type in settings.ALLOWED_MIME_TYPES
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Nettoie un nom de fichier pour éviter les attaques de chemin
        """
        # Supprimer les caractères dangereux
        safe_filename = os.path.basename(filename)
        # Remplacer les espaces par des underscores
        safe_filename = safe_filename.replace(" ", "_")
        return safe_filename


# Instance singleton du scanner antivirus
antivirus_scanner = AntivirusScanner()


def notify_security_team(document_id: str, threat_name: str):
    """
    Notifie l'équipe de sécurité en cas de menace détectée
    """
    # Implémentation à personnaliser selon vos besoins (email, Slack, etc.)
    logger.warning(f"ALERTE SÉCURITÉ: Document {document_id} infecté par {threat_name}")
    # TODO: Implémenter la notification réelle
