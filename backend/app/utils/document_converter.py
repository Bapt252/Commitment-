import os
import io
import re
import tempfile
import magic
from html import unescape
from typing import Tuple, Dict, Any, Optional, Union
import logging

class DocumentConverter:
    """
    Convertit différents formats de document en texte brut
    """
    
    @staticmethod
    def detect_format(file_content: bytes, filename: str = None) -> Tuple[str, str]:
        """
        Détecte le format du document à partir du contenu binaire
        
        Args:
            file_content: Contenu binaire du fichier
            filename: Nom du fichier (optionnel)
            
        Returns:
            Tuple: (format_type, mime_type)
        """
        # Utilisation de python-magic pour la détection du MIME type
        try:
            mime_type = magic.Magic(mime=True).from_buffer(file_content)
        except Exception as e:
            logging.warning(f"Erreur lors de la détection du type MIME: {e}")
            mime_type = "application/octet-stream"
        
        # Correspondance entre MIME type et format interne
        mime_to_format = {
            'application/pdf': 'pdf',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
            'text/html': 'html',
            'text/plain': 'txt'
        }
        
        # Si le MIME type est reconnu directement
        if mime_type in mime_to_format:
            return mime_to_format[mime_type], mime_type
        
        # Signatures de fichiers pour détection de secours
        signatures = {
            b'%PDF': ('pdf', 'application/pdf'),
            b'PK\x03\x04': ('docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            b'\xd0\xcf\x11\xe0': ('doc', 'application/msword'),
            b'<!DOCTYPE html': ('html', 'text/html'),
            b'<html': ('html', 'text/html')
        }
        
        for signature, (format_type, signature_mime) in signatures.items():
            if file_content.startswith(signature):
                return format_type, signature_mime
        
        # Analyse du nom de fichier si disponible
        if filename:
            extension = os.path.splitext(filename)[1].lower()
            ext_to_format = {
                '.pdf': ('pdf', 'application/pdf'),
                '.docx': ('docx', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
                '.doc': ('doc', 'application/msword'),
                '.html': ('html', 'text/html'),
                '.htm': ('html', 'text/html'),
                '.txt': ('txt', 'text/plain'),
                '.md': ('txt', 'text/plain'),
                '.csv': ('txt', 'text/csv'),
                '.json': ('txt', 'application/json')
            }
            if extension in ext_to_format:
                return ext_to_format[extension]
        
        # Par défaut, traiter comme du texte
        return 'txt', 'text/plain'
    
    @staticmethod
    def convert_to_text(file_content: bytes, filename: str = None) -> Tuple[str, str, Dict[str, Any]]:
        """
        Convertit le contenu du fichier en texte brut
        
        Args:
            file_content: Contenu binaire du fichier
            filename: Nom du fichier (optionnel)
            
        Returns:
            Tuple: (texte extrait, mime_type, métadonnées)
        """
        file_format, mime_type = DocumentConverter.detect_format(file_content, filename)
        metadata = {"format": file_format, "mime_type": mime_type}
        
        if file_format == 'pdf':
            try:
                text = DocumentConverter._extract_from_pdf(file_content)
                metadata["pages"] = text.count("\f") + 1  # Approximation du nombre de pages
                return text, mime_type, metadata
            except Exception as e:
                logging.error(f"Erreur lors de l'extraction du PDF: {e}")
                return "", mime_type, metadata
        
        elif file_format in ['docx', 'doc']:
            try:
                text = DocumentConverter._extract_from_docx(file_content)
                return text, mime_type, metadata
            except Exception as e:
                logging.error(f"Erreur lors de l'extraction du document Word: {e}")
                return "", mime_type, metadata
        
        elif file_format == 'html':
            try:
                text = DocumentConverter._extract_from_html(file_content)
                return text, mime_type, metadata
            except Exception as e:
                logging.error(f"Erreur lors de l'extraction du HTML: {e}")
                return "", mime_type, metadata
        
        else:  # txt ou autre
            try:
                # Essayer différents encodages
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        text = file_content.decode(encoding)
                        metadata["encoding"] = encoding
                        return text, mime_type, metadata
                    except UnicodeDecodeError:
                        continue
                
                # Si aucun encodage ne fonctionne, utiliser un repli avec remplacement
                text = file_content.decode('utf-8', errors='replace')
                metadata["encoding"] = "utf-8 (with replacements)"
                return text, mime_type, metadata
            except Exception as e:
                logging.error(f"Erreur lors du décodage du texte: {e}")
                return "", mime_type, metadata
    
    @staticmethod
    def _extract_from_pdf(file_content: bytes) -> str:
        """
        Extrait le texte d'un PDF
        
        Args:
            file_content: Contenu binaire du PDF
            
        Returns:
            str: Texte extrait
        """
        from pdfminer.high_level import extract_text
        with io.BytesIO(file_content) as pdf_file:
            text = extract_text(pdf_file)
        
        # Nettoyage du texte extrait
        text = re.sub(r'\s+', ' ', text)  # Normaliser les espaces
        text = re.sub(r'\f', '\n\n', text)  # Remplacer les sauts de page par des lignes vides
        
        return text
    
    @staticmethod
    def _extract_from_docx(file_content: bytes) -> str:
        """
        Extrait le texte d'un document Word
        
        Args:
            file_content: Contenu binaire du document Word
            
        Returns:
            str: Texte extrait
        """
        import docx2txt
        
        # Utiliser un fichier temporaire (nécessaire pour docx2txt)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        try:
            text = docx2txt.process(temp_file_path)
            return text
        finally:
            # Nettoyer le fichier temporaire
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    @staticmethod
    def _extract_from_html(file_content: bytes) -> str:
        """
        Extrait le texte d'un document HTML
        
        Args:
            file_content: Contenu binaire du HTML
            
        Returns:
            str: Texte extrait
        """
        # Décodage du contenu HTML
        try:
            html_text = file_content.decode('utf-8')
        except UnicodeDecodeError:
            html_text = file_content.decode('latin-1', errors='replace')
        
        # Supprimer les scripts et styles
        html_text = re.sub(r'<script.*?>.*?</script>', ' ', html_text, flags=re.DOTALL)
        html_text = re.sub(r'<style.*?>.*?</style>', ' ', html_text, flags=re.DOTALL)
        
        # Remplacer les balises par des espaces ou sauts de ligne
        html_text = re.sub(r'<(br|p|div|h\d)[^>]*>', '\n', html_text)
        html_text = re.sub(r'<li[^>]*>', '\n• ', html_text)
        html_text = re.sub(r'<td[^>]*>', ' ', html_text)
        html_text = re.sub(r'<tr[^>]*>', '\n', html_text)
        html_text = re.sub(r'<[^>]*>', ' ', html_text)
        
        # Nettoyer les espaces multiples
        html_text = re.sub(r'\s+', ' ', html_text)
        
        # Décoder les entités HTML
        html_text = unescape(html_text)
        
        return html_text


# Fonction de compatibilité avec l'ancienne API
def extract_text_from_file(file_content: bytes, filename: str = None) -> Tuple[str, str]:
    """
    Extrait le texte de différents formats de fichiers (Compatible avec l'API existante)
    
    Args:
        file_content: Contenu binaire du fichier
        filename: Nom du fichier
        
    Returns:
        Tuple: (texte extrait, type mime)
    """
    text, mime_type, _ = DocumentConverter.convert_to_text(file_content, filename)
    return text, mime_type
