from typing import Dict, Any, Optional, List, Tuple
import logging
import time
import os
from pathlib import Path

# Importation des composants améliorés
from app.nlp.document_classifier import DocumentClassifier
from app.nlp.section_extractor import SectionExtractor
from app.nlp.skills_extractor import SkillsKnowledgeBase
from app.nlp.cv_parser import CVExtractor, parse_cv
from app.nlp.job_parser import JobPostingExtractor, parse_job_description

# Configuration du logging
logging_configured = False

def setup_logging():
    """Configure le logging pour le module de parsing"""
    global logging_configured
    if not logging_configured:
        # Créer le répertoire des logs s'il n'existe pas
        logs_dir = Path(__file__).resolve().parent.parent.parent / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Configuration de base
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(logs_dir / "document_parser.log"),
                logging.StreamHandler()
            ]
        )
        logging_configured = True


class DocumentParserPipeline:
    def __init__(self):
        """
        Pipeline de traitement des documents avec journalisation et gestion d'erreurs
        """
        # S'assurer que le logging est configuré
        setup_logging()
        
        # Initialiser les composants
        self.logger = logging.getLogger("document_parser")
        self.classifier = DocumentClassifier()
        self.section_extractor = SectionExtractor()
        self.skills_kb = SkillsKnowledgeBase()
        
        # Créer les extracteurs spécifiques - utiliser les versions existantes pour compatibilité
        # Mais on pourrait les remplacer par des versions améliorées à l'avenir
        try:
            self.cv_extractor = CVExtractor()
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de l'extracteur CV: {e}")
            self.cv_extractor = None
            
        try:
            self.job_extractor = JobPostingExtractor() if 'JobPostingExtractor' in globals() else None
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation de l'extracteur job: {e}")
            self.job_extractor = None
    
    def parse_document(self, text: str, doc_type: str = None) -> Dict[str, Any]:
        """
        Parse un document avec pipeline amélioré et gestion d'erreurs
        
        Args:
            text: Texte du document
            doc_type: Type du document (optionnel, sera détecté si non fourni)
            
        Returns:
            Dict: Résultats d'analyse avec données, scores de confiance et métadonnées
        """
        start_time = time.time()
        self.logger.info("Début du traitement du document")
        
        results = {
            "metadata": {
                "processing_time": None,
                "char_count": len(text),
                "errors": []
            }
        }
        
        try:
            # Prétraitement
            processed = self.classifier.preprocess_document(text)
            
            # Classification si non fournie
            if doc_type is None:
                doc_type = processed["doc_type"]
                self.logger.info(f"Type de document détecté: {doc_type}")
            else:
                processed["doc_type"] = doc_type
            
            # Extraction des sections
            sections = self.section_extractor.extract_sections(processed["text"], doc_type)
            processed["sections"] = sections
            
            # Extraction d'informations selon le type
            if doc_type == "cv":
                if self.cv_extractor:
                    # Utiliser l'extracteur existant pour compatibilité
                    extraction_results = self.cv_extractor.parse_cv(processed["text"])
                else:
                    # Fallback vers la fonction existante
                    extraction_results = parse_cv(processed["text"])
                    
                # Améliorer l'extraction des compétences si possible
                if "competences" in extraction_results.get("extracted_data", {}):
                    skills_section = sections.get("skills", [])
                    if skills_section:
                        categorized_skills = self.skills_kb.extract_skills_from_section(skills_section)
                        # Si des compétences catégorisées ont été trouvées, les utiliser
                        if categorized_skills:
                            extraction_results["extracted_data"]["competences_categories"] = categorized_skills
            else:  # job_posting
                if hasattr(self, 'job_extractor') and self.job_extractor:
                    # Utiliser l'extracteur d'offres d'emploi si disponible
                    extraction_results = self.job_extractor.extract_job_data(processed)
                else:
                    # Fallback vers la fonction existante
                    extraction_results = parse_job_description(processed["text"])
            
            # Résultats avec structure compatible avec l'existant
            results.update({
                "doc_type": doc_type,
                "extracted_data": extraction_results.get("extracted_data", {}),
                "confidence_scores": extraction_results.get("confidence_scores", {})
            })
            
            # Ajouter des métadonnées améliorées
            results["metadata"]["sections"] = list(sections.keys())
            results["metadata"]["language"] = processed.get("language", "fr")
            
        except Exception as e:
            self.logger.error(f"Erreur lors du traitement: {str(e)}", exc_info=True)
            results["metadata"]["errors"].append(str(e))
            
            # Assurer qu'un minimum d'information est retourné même en cas d'erreur
            if "doc_type" not in results:
                results["doc_type"] = doc_type or "unknown"
            if "extracted_data" not in results:
                results["extracted_data"] = {"error": "Extraction échouée"}
            if "confidence_scores" not in results:
                results["confidence_scores"] = {"global": 0.0}
        
        # Finalisation
        processing_time = time.time() - start_time
        results["metadata"]["processing_time"] = processing_time
        self.logger.info(f"Traitement terminé en {processing_time:.2f} secondes")
        
        return results


# Fonction d'interface compatible avec l'existant
def parse_document(text: str, doc_type: str = None) -> Dict[str, Any]:
    """
    Point d'entrée pour le parsing des documents (compatible avec l'API existante)
    
    Args:
        text: Texte du document à analyser
        doc_type: Type du document (optionnel)
        
    Returns:
        Dict: Résultats d'analyse
    """
    parser = DocumentParserPipeline()
    result = parser.parse_document(text, doc_type)
    
    # Assurer la compatibilité avec l'ancien format de retour
    if "metadata" in result:
        del result["metadata"]
    
    return result
