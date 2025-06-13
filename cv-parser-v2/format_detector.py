#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 SuperSmartMatch V2.1 - Format Detector Universal
Détection automatique du format de fichier pour parsing universel
"""

import magic
import mimetypes
import logging
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class UniversalFormatDetector:
    """
    Détecteur de format universel pour tous types de documents
    Supporte : PDF, Word, Images, Texte, HTML, RTF, OpenOffice
    """
    
    # Mapping des types MIME vers les formats supportés
    SUPPORTED_FORMATS = {
        # PDF
        'application/pdf': 'pdf',
        
        # Microsoft Word
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/msword': 'doc',
        
        # Images (pour OCR)
        'image/jpeg': 'image',
        'image/jpg': 'image', 
        'image/png': 'image',
        'image/tiff': 'image',
        'image/bmp': 'image',
        'image/webp': 'image',
        
        # Texte
        'text/plain': 'txt',
        'text/csv': 'txt',
        
        # HTML
        'text/html': 'html',
        'application/xhtml+xml': 'html',
        
        # RTF
        'application/rtf': 'rtf',
        'text/rtf': 'rtf',
        
        # OpenOffice
        'application/vnd.oasis.opendocument.text': 'odt',
        
        # Fallbacks
        'application/octet-stream': 'unknown'
    }
    
    # Extensions de fichiers comme fallback
    EXTENSION_MAPPING = {
        '.pdf': 'pdf',
        '.docx': 'docx',
        '.doc': 'doc',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.tiff': 'image',
        '.tif': 'image',
        '.bmp': 'image',
        '.webp': 'image',
        '.txt': 'txt',
        '.csv': 'txt',
        '.html': 'html',
        '.htm': 'html',
        '.rtf': 'rtf',
        '.odt': 'odt'
    }
    
    def __init__(self):
        """Initialisation du détecteur"""
        try:
            self.magic_mime = magic.Magic(mime=True)
            self.magic_available = True
            logger.info("✅ python-magic disponible pour détection précise")
        except Exception as e:
            self.magic_available = False
            logger.warning(f"⚠️ python-magic non disponible, fallback sur extension: {e}")
    
    def detect_format(self, file_path: str, filename: Optional[str] = None) -> Tuple[str, str, bool]:
        """
        Détecte le format d'un fichier
        
        Args:
            file_path: Chemin vers le fichier
            filename: Nom original du fichier (optionnel)
            
        Returns:
            Tuple[format, mime_type, is_supported]
            - format: Format détecté ('pdf', 'docx', 'image', etc.)
            - mime_type: Type MIME détecté
            - is_supported: Si le format est supporté pour parsing
        """
        try:
            # Méthode 1: Détection via python-magic (plus fiable)
            if self.magic_available:
                mime_type = self.magic_mime.from_file(file_path)
                logger.info(f"🔍 Type MIME détecté: {mime_type}")
                
                # Recherche directe dans nos formats supportés
                if mime_type in self.SUPPORTED_FORMATS:
                    format_type = self.SUPPORTED_FORMATS[mime_type]
                    return format_type, mime_type, True
            
            # Méthode 2: Fallback via mimetypes Python
            mime_type, _ = mimetypes.guess_type(filename or file_path)
            if mime_type and mime_type in self.SUPPORTED_FORMATS:
                format_type = self.SUPPORTED_FORMATS[mime_type]
                logger.info(f"🔍 Format via mimetypes: {format_type}")
                return format_type, mime_type, True
            
            # Méthode 3: Fallback via extension de fichier
            file_ext = Path(filename or file_path).suffix.lower()
            if file_ext in self.EXTENSION_MAPPING:
                format_type = self.EXTENSION_MAPPING[file_ext]
                logger.info(f"🔍 Format via extension {file_ext}: {format_type}")
                return format_type, f"extension/{file_ext[1:]}", True
            
            # Format non supporté
            logger.warning(f"❌ Format non supporté: {mime_type or 'unknown'}, extension: {file_ext}")
            return 'unknown', mime_type or 'unknown', False
            
        except Exception as e:
            logger.error(f"❌ Erreur détection format: {e}")
            return 'unknown', 'error', False
    
    def is_format_supported(self, file_path: str, filename: Optional[str] = None) -> bool:
        """
        Vérifie si le format est supporté
        
        Args:
            file_path: Chemin vers le fichier
            filename: Nom original du fichier
            
        Returns:
            bool: True si supporté, False sinon
        """
        _, _, is_supported = self.detect_format(file_path, filename)
        return is_supported
    
    def get_supported_formats(self) -> dict:
        """
        Retourne la liste des formats supportés
        
        Returns:
            dict: Mapping des formats supportés avec descriptions
        """
        return {
            'pdf': 'Portable Document Format',
            'docx': 'Microsoft Word (nouveau format)',
            'doc': 'Microsoft Word (ancien format)', 
            'image': 'Images (JPG, PNG, TIFF, BMP, WebP) avec OCR',
            'txt': 'Fichiers texte brut',
            'html': 'Pages web HTML',
            'rtf': 'Rich Text Format',
            'odt': 'OpenOffice Document Text'
        }
    
    def get_supported_extensions(self) -> list:
        """
        Retourne la liste des extensions supportées
        
        Returns:
            list: Liste des extensions de fichiers supportées
        """
        return list(self.EXTENSION_MAPPING.keys())
    
    def validate_file_for_parsing(self, file_path: str, filename: str) -> dict:
        """
        Validation complète d'un fichier pour parsing
        
        Args:
            file_path: Chemin vers le fichier
            filename: Nom original du fichier
            
        Returns:
            dict: Résultat de validation avec détails
        """
        file_size = Path(file_path).stat().st_size
        format_type, mime_type, is_supported = self.detect_format(file_path, filename)
        
        validation_result = {
            'filename': filename,
            'file_size': file_size,
            'file_size_mb': round(file_size / (1024 * 1024), 2),
            'detected_format': format_type,
            'mime_type': mime_type,
            'is_supported': is_supported,
            'validation_status': 'success' if is_supported else 'unsupported_format',
            'can_parse': is_supported and file_size > 0,
            'errors': []
        }
        
        # Vérifications supplémentaires
        if file_size == 0:
            validation_result['errors'].append('Fichier vide')
            validation_result['can_parse'] = False
            validation_result['validation_status'] = 'empty_file'
        
        if file_size > 50 * 1024 * 1024:  # 50MB
            validation_result['errors'].append('Fichier trop volumineux (>50MB)')
            validation_result['can_parse'] = False
            validation_result['validation_status'] = 'file_too_large'
        
        if not is_supported:
            supported_extensions = ', '.join(self.get_supported_extensions())
            validation_result['errors'].append(
                f'Format non supporté. Formats acceptés: {supported_extensions}'
            )
        
        logger.info(f"📋 Validation: {filename} -> {validation_result['validation_status']}")
        return validation_result


# Instance globale pour utilisation dans les parsers
format_detector = UniversalFormatDetector()
