"""
Module de pré-traitement adaptatif pour le parsing de documents
Ce module implémente un système qui détecte le format/type de document
avant d'appliquer la stratégie de parsing appropriée.
"""

import re
import os
import logging
from typing import Dict, Any, List, Tuple, Optional, Union
import importlib.util
from pathlib import Path

# Importations pour la détection de formats
import magic  # python-magic pour la détection de type MIME
import PyPDF2
import docx
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# Importer les composants existants
from app.nlp.document_classifier import DocumentClassifier

class AdaptiveParser:
    """
    Parseur adaptatif qui détecte le format et le type de document
    puis applique la stratégie de parsing appropriée.
    """
    
    def __init__(self):
        """
        Initialise le parseur adaptatif avec les détecteurs et les parseurs.
        """
        # Configuration du logging
        self.logger = logging.getLogger(__name__)
        
        # Initialisation du classificateur de documents
        self.document_classifier = DocumentClassifier()
        
        # Formats supportés et leurs extensions
        self.supported_formats = {
            'pdf': ['.pdf'],
            'docx': ['.docx', '.doc'],
            'text': ['.txt', '.text', '.md', '.rst'],
            'html': ['.html', '.htm'],
            'json': ['.json'],
            'xml': ['.xml']
        }
        
        # Correspondance format -> fonction d'extraction
        self.format_extractors = {
            'pdf': self._extract_text_from_pdf,
            'docx': self._extract_text_from_docx,
            'text': self._extract_text_from_txt,
            'html': self._extract_text_from_html,
            'json': self._extract_text_from_json,
            'xml': self._extract_text_from_xml
        }
        
        # Charger les parseurs spécifiques aux formats
        self.load_format_specific_parsers()

    def load_format_specific_parsers(self):
        """
        Charge dynamiquement les parseurs spécifiques aux formats s'ils existent.
        """
        try:
            # Chemin vers le répertoire des parseurs spécifiques aux formats
            parsers_dir = Path(__file__).resolve().parent / "format_parsers"
            
            if parsers_dir.exists():
                for parser_file in parsers_dir.glob("*_parser.py"):
                    module_name = parser_file.stem
                    
                    spec = importlib.util.spec_from_file_location(
                        module_name, str(parser_file)
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        
                        # Enregistrer les parseurs spécifiques s'ils existent
                        if hasattr(module, "register_parsers"):
                            module.register_parsers(self)
                
                self.logger.info(f"Parseurs spécifiques aux formats chargés.")
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement des parseurs spécifiques: {e}")

    def detect_file_format(self, file_path: str) -> str:
        """
        Détecte le format du fichier basé sur son extension et son contenu.
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            str: Format détecté ('pdf', 'docx', etc.)
        """
        # 1. Vérifier l'extension du fichier
        ext = os.path.splitext(file_path)[1].lower()
        for format_name, extensions in self.supported_formats.items():
            if ext in extensions:
                format_guess = format_name
                break
        else:
            format_guess = 'unknown'
            
        # 2. Vérifier le type MIME pour confirmation
        try:
            mime_type = magic.from_file(file_path, mime=True)
            
            # Mapper les types MIME courants
            mime_format_map = {
                'application/pdf': 'pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
                'application/msword': 'docx',
                'text/plain': 'text',
                'text/html': 'html',
                'application/json': 'json',
                'application/xml': 'xml',
                'text/xml': 'xml'
            }
            
            mime_format = mime_format_map.get(mime_type, None)
            
            # Si le MIME type et l'extension ne correspondent pas, se fier au MIME
            if mime_format and mime_format != format_guess:
                self.logger.info(f"Extension ({format_guess}) ne correspond pas au MIME ({mime_format}). Utilisation du MIME.")
                return mime_format
        except Exception as e:
            self.logger.warning(f"Impossible de détecter le type MIME: {e}")
        
        return format_guess

    def extract_text_from_file(self, file_path: str) -> str:
        """
        Extrait le texte d'un fichier en fonction de son format.
        
        Args:
            file_path: Chemin vers le fichier
            
        Returns:
            str: Texte extrait du fichier
        """
        format_name = self.detect_file_format(file_path)
        
        if format_name in self.format_extractors:
            return self.format_extractors[format_name](file_path)
        else:
            self.logger.error(f"Format non supporté: {format_name}")
            raise ValueError(f"Format non supporté: {format_name}")

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extrait le texte d'un PDF"""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction du texte du PDF: {e}")
        return text

    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extrait le texte d'un fichier DOCX"""
        text = ""
        try:
            doc = docx.Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction du texte du DOCX: {e}")
        return text

    def _extract_text_from_txt(self, file_path: str) -> str:
        """Extrait le texte d'un fichier texte"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Essayer avec une autre encodage si utf-8 échoue
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                self.logger.error(f"Erreur lors de l'extraction du texte: {e}")
                return ""
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction du texte: {e}")
            return ""

    def _extract_text_from_html(self, file_path: str) -> str:
        """Extrait le texte d'un fichier HTML"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                soup = BeautifulSoup(file.read(), 'html.parser')
                # Supprimer les scripts, styles, et autres éléments non textuels
                for script in soup(["script", "style", "meta", "head"]):
                    script.extract()
                return soup.get_text()
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction du texte HTML: {e}")
            return ""

    def _extract_text_from_json(self, file_path: str) -> str:
        """Extrait le texte d'un fichier JSON"""
        import json
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # Tenter d'extraire les champs textuels pertinents
                if isinstance(data, dict):
                    text_fields = []
                    for key, value in data.items():
                        if isinstance(value, str):
                            text_fields.append(f"{key}: {value}")
                        elif isinstance(value, (list, dict)):
                            text_fields.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
                    return "\n".join(text_fields)
                else:
                    return json.dumps(data, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction du texte JSON: {e}")
            return ""

    def _extract_text_from_xml(self, file_path: str) -> str:
        """Extrait le texte d'un fichier XML"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extraction récursive de texte des éléments XML
            def extract_text_from_element(element):
                text = element.text or ""
                for child in element:
                    text += extract_text_from_element(child)
                    if child.tail:
                        text += child.tail
                return text
            
            return extract_text_from_element(root)
        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction du texte XML: {e}")
            return ""

    def preprocess_document(self, text: str, file_format: Optional[str] = None, doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Prétraite le document en fonction de son format et de son type.
        
        Args:
            text: Texte du document
            file_format: Format du fichier ('pdf', 'docx', etc.) si connu
            doc_type: Type du document ('cv', 'job_posting') si connu
            
        Returns:
            Dict: Document prétraité avec métadonnées
        """
        # Utiliser le classificateur de documents pour le prétraitement de base
        processed = self.document_classifier.preprocess_document(text)
        
        # Ajouter des informations supplémentaires
        if file_format:
            processed["file_format"] = file_format
        
        if doc_type:
            processed["doc_type"] = doc_type
        
        # Appliquer des traitements spécifiques au format si nécessaire
        if file_format == 'pdf':
            # Traitement spécifique aux PDF
            processed = self._preprocess_pdf_document(processed)
        elif file_format == 'docx':
            # Traitement spécifique aux DOCX
            processed = self._preprocess_docx_document(processed)
        
        return processed

    def _preprocess_pdf_document(self, processed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prétraitement spécifique aux documents PDF.
        Par exemple, amélioration de la gestion des sauts de page.
        """
        if "text" in processed:
            # Identifier des sauts de page et les nettoyer
            processed["text"] = re.sub(r'\f', '\n\n', processed["text"])
            
            # Éliminer les numéros de page isolés
            processed["text"] = re.sub(r'\n\s*\d+\s*\n', '\n\n', processed["text"])
            
            # Corriger les coupures de mots en fin de ligne avec tiret
            processed["text"] = re.sub(r'(\w+)-\n(\w+)', r'\1\2', processed["text"])
        
        return processed

    def _preprocess_docx_document(self, processed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prétraitement spécifique aux documents DOCX.
        Par exemple, meilleure gestion des tableaux et des styles.
        """
        # À compléter selon les besoins spécifiques
        return processed


# Point d'entrée pour utilisation externe
def preprocess_document_adaptive(text: str, file_format: Optional[str] = None, doc_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Fonction d'interface pour le prétraitement adaptatif de documents.
    
    Args:
        text: Texte du document
        file_format: Format du fichier ('pdf', 'docx', etc.) si connu
        doc_type: Type du document ('cv', 'job_posting') si connu
        
    Returns:
        Dict: Document prétraité avec métadonnées
    """
    parser = AdaptiveParser()
    return parser.preprocess_document(text, file_format, doc_type)

def extract_text_from_file(file_path: str) -> str:
    """
    Fonction d'interface pour extraire le texte d'un fichier.
    
    Args:
        file_path: Chemin vers le fichier
        
    Returns:
        str: Texte extrait du fichier
    """
    parser = AdaptiveParser()
    return parser.extract_text_from_file(file_path)