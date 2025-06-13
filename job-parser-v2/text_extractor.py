#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📄 SuperSmartMatch V2.1 - Universal Text Extractor
Extraction de texte universelle pour tous formats de documents
"""

import os
import io
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Tuple, Optional, Dict, Any

# Imports pour différents formats
import PyPDF2
import pdfplumber
from PIL import Image
import pytesseract
from docx import Document
import mammoth
from bs4 import BeautifulSoup
from striprtf.striprtf import rtf_to_text
from odf import text, teletype
from odf.opendocument import load

logger = logging.getLogger(__name__)

class UniversalTextExtractor:
    """
    Extracteur de texte universel pour tous types de documents
    Supporte : PDF, Word, Images (OCR), Texte, HTML, RTF, OpenOffice
    """
    
    def __init__(self):
        """Initialisation de l'extracteur avec configuration OCR"""
        self.ocr_config = {
            'lang': 'fra+eng',  # Français + Anglais
            'config': '--psm 1 --oem 3'  # Page Segmentation Mode + OCR Engine Mode
        }
        
        # Vérification des dépendances critiques
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Vérifie la disponibilité des dépendances"""
        deps_status = {
            'tesseract': self._check_tesseract(),
            'pdfplumber': True,  # Déjà importé
            'docx': True,        # Déjà importé
            'mammoth': True,     # Déjà importé
            'PIL': True,         # Déjà importé
            'bs4': True,         # Déjà importé
            'striprtf': True,    # Déjà importé
            'odf': True          # Déjà importé
        }
        
        logger.info(f"📋 Status dépendances: {deps_status}")
        
        if not deps_status['tesseract']:
            logger.warning("⚠️ Tesseract non disponible - OCR désactivé")
    
    def _check_tesseract(self) -> bool:
        """Vérifie si Tesseract OCR est disponible"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception:
            return False
    
    def extract_text_universal(self, file_path: str, format_type: str, 
                             filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Extraction de texte universelle selon le format
        
        Args:
            file_path: Chemin vers le fichier
            format_type: Type de format détecté
            filename: Nom original du fichier
            
        Returns:
            Tuple[text, metadata]
            - text: Texte extrait
            - metadata: Métadonnées d'extraction
        """
        logger.info(f"📄 Extraction {format_type}: {filename or file_path}")
        
        try:
            # Dispatch vers la méthode appropriée
            extraction_methods = {
                'pdf': self._extract_pdf,
                'docx': self._extract_docx,
                'doc': self._extract_doc,
                'image': self._extract_image_ocr,
                'txt': self._extract_text,
                'html': self._extract_html,
                'rtf': self._extract_rtf,
                'odt': self._extract_odt
            }
            
            if format_type not in extraction_methods:
                raise ValueError(f"Format non supporté: {format_type}")
            
            # Extraction du texte
            text, metadata = extraction_methods[format_type](file_path)
            
            # Métadonnées communes
            metadata.update({
                'format_type': format_type,
                'filename': filename,
                'file_size': os.path.getsize(file_path),
                'text_length': len(text),
                'extraction_status': 'success'
            })
            
            logger.info(f"✅ Extraction réussie: {len(text)} caractères")
            return text, metadata
            
        except Exception as e:
            logger.error(f"❌ Erreur extraction {format_type}: {e}")
            
            # Tentative de fallback vers PDF si possible
            if format_type != 'pdf':
                logger.info("🔄 Tentative de conversion PDF fallback...")
                try:
                    pdf_path = self._convert_to_pdf_fallback(file_path, format_type)
                    text, metadata = self._extract_pdf(pdf_path)
                    metadata.update({
                        'format_type': f"{format_type}_via_pdf",
                        'extraction_method': 'pdf_fallback',
                        'extraction_status': 'success_fallback'
                    })
                    return text, metadata
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback PDF échoué: {fallback_error}")
            
            # Retour d'erreur avec métadonnées
            return "", {
                'format_type': format_type,
                'extraction_status': 'failed',
                'error': str(e),
                'text_length': 0
            }
    
    def _extract_pdf(self, file_path: str) -> Tuple[str, Dict]:
        """Extraction PDF avec pdfplumber (priorité) et PyPDF2 (fallback)"""
        text = ""
        metadata = {'extraction_method': 'pdfplumber', 'pages': 0}
        
        try:
            # Méthode 1: pdfplumber (meilleure qualité)
            with pdfplumber.open(file_path) as pdf:
                metadata['pages'] = len(pdf.pages)
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    logger.info(f"✅ PDF pdfplumber: {len(text)} caractères, {metadata['pages']} pages")
                    return text, metadata
        
        except Exception as e:
            logger.warning(f"⚠️ pdfplumber échoué: {e}")
        
        try:
            # Méthode 2: PyPDF2 (fallback)
            metadata['extraction_method'] = 'pypdf2'
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata['pages'] = len(pdf_reader.pages)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text += page.extract_text() + "\n"
                
                logger.info(f"✅ PDF PyPDF2: {len(text)} caractères, {metadata['pages']} pages")
                return text, metadata
        
        except Exception as e:
            raise Exception(f"Échec extraction PDF: {e}")
    
    def _extract_docx(self, file_path: str) -> Tuple[str, Dict]:
        """Extraction Word DOCX"""
        try:
            doc = Document(file_path)
            text = ""
            paragraphs = 0
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
                    paragraphs += 1
            
            metadata = {
                'extraction_method': 'python-docx',
                'paragraphs': paragraphs
            }
            
            logger.info(f"✅ DOCX: {len(text)} caractères, {paragraphs} paragraphes")
            return text, metadata
            
        except Exception as e:
            raise Exception(f"Échec extraction DOCX: {e}")
    
    def _extract_doc(self, file_path: str) -> Tuple[str, Dict]:
        """Extraction Word DOC avec mammoth"""
        try:
            with open(file_path, "rb") as docx_file:
                result = mammoth.extract_raw_text(docx_file)
                text = result.value
                
                metadata = {
                    'extraction_method': 'mammoth',
                    'warnings': len(result.messages)
                }
                
                logger.info(f"✅ DOC: {len(text)} caractères")
                return text, metadata
                
        except Exception as e:
            raise Exception(f"Échec extraction DOC: {e}")
    
    def _extract_image_ocr(self, file_path: str) -> Tuple[str, Dict]:
        """Extraction OCR pour images"""
        if not self._check_tesseract():
            raise Exception("Tesseract OCR non disponible")
        
        try:
            # Ouverture et préparation de l'image
            image = Image.open(file_path)
            
            # Conversion en RGB si nécessaire
            if image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')
            
            # OCR avec configuration optimisée
            text = pytesseract.image_to_string(
                image, 
                lang=self.ocr_config['lang'],
                config=self.ocr_config['config']
            )
            
            metadata = {
                'extraction_method': 'tesseract_ocr',
                'image_size': image.size,
                'image_mode': image.mode,
                'ocr_lang': self.ocr_config['lang']
            }
            
            logger.info(f"✅ OCR: {len(text)} caractères depuis image {image.size}")
            return text, metadata
            
        except Exception as e:
            raise Exception(f"Échec OCR image: {e}")
    
    def _extract_text(self, file_path: str) -> Tuple[str, Dict]:
        """Extraction fichier texte brut"""
        try:
            # Tentative avec différents encodages
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        text = file.read()
                        
                        metadata = {
                            'extraction_method': 'text_file',
                            'encoding': encoding,
                            'lines': text.count('\n') + 1
                        }
                        
                        logger.info(f"✅ TXT ({encoding}): {len(text)} caractères")
                        return text, metadata
                        
                except UnicodeDecodeError:
                    continue
            
            raise Exception("Impossible de décoder le fichier texte")
            
        except Exception as e:
            raise Exception(f"Échec extraction texte: {e}")
    
    def _extract_html(self, file_path: str) -> Tuple[str, Dict]:
        """Extraction HTML avec BeautifulSoup"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Suppression des scripts et styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extraction du texte
            text = soup.get_text()
            
            # Nettoyage des espaces multiples
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            metadata = {
                'extraction_method': 'beautifulsoup',
                'html_tags_removed': True
            }
            
            logger.info(f"✅ HTML: {len(text)} caractères")
            return text, metadata
            
        except Exception as e:
            raise Exception(f"Échec extraction HTML: {e}")
    
    def _extract_rtf(self, file_path: str) -> Tuple[str, Dict]:
        """Extraction RTF"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                rtf_content = file.read()
            
            text = rtf_to_text(rtf_content)
            
            metadata = {
                'extraction_method': 'striprtf'
            }
            
            logger.info(f"✅ RTF: {len(text)} caractères")
            return text, metadata
            
        except Exception as e:
            raise Exception(f"Échec extraction RTF: {e}")
    
    def _extract_odt(self, file_path: str) -> Tuple[str, Dict]:
        """Extraction OpenOffice ODT"""
        try:
            doc = load(file_path)
            text_elements = []
            
            # Extraction de tous les éléments texte
            for element in doc.getElementsByType(text.P):
                text_content = teletype.extractText(element)
                if text_content.strip():
                    text_elements.append(text_content)
            
            text = '\n'.join(text_elements)
            
            metadata = {
                'extraction_method': 'odf',
                'paragraphs': len(text_elements)
            }
            
            logger.info(f"✅ ODT: {len(text)} caractères, {len(text_elements)} paragraphes")
            return text, metadata
            
        except Exception as e:
            raise Exception(f"Échec extraction ODT: {e}")
    
    def _convert_to_pdf_fallback(self, file_path: str, format_type: str) -> str:
        """
        Conversion fallback vers PDF pour formats non supportés
        (Nécessite LibreOffice ou Pandoc)
        """
        output_dir = Path(tempfile.gettempdir()) / "conversion_fallback"
        output_dir.mkdir(exist_ok=True)
        
        output_pdf = output_dir / f"converted_{os.getpid()}.pdf"
        
        try:
            # Tentative avec LibreOffice (si disponible)
            if format_type in ['doc', 'docx', 'odt', 'rtf']:
                result = subprocess.run([
                    'libreoffice', '--headless', '--convert-to', 'pdf',
                    '--outdir', str(output_dir), file_path
                ], capture_output=True, timeout=60)
                
                if result.returncode == 0 and output_pdf.exists():
                    logger.info("✅ Conversion LibreOffice vers PDF réussie")
                    return str(output_pdf)
            
            raise Exception("Conversion PDF non disponible")
            
        except Exception as e:
            logger.error(f"❌ Conversion PDF fallback échouée: {e}")
            raise


# Instance globale pour utilisation dans les parsers
text_extractor = UniversalTextExtractor()
