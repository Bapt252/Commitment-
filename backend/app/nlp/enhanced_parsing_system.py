"""
Module d'intégration du système amélioré de parsing

Ce module orchestre tous les composants du système amélioré de parsing:
- adaptive_parser: Détection automatique du format et du type de document
- advanced_nlp: Extraction d'informations implicites avec BERT
- environment_preference_extractor: Déduction des préférences d'environnement/travail
- parser_feedback_system: Collection et utilisation des feedbacks utilisateurs
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union, BinaryIO
import tempfile
import uuid

# Importation des composants
from app.nlp.adaptive_parser import AdaptiveParser, extract_text_from_file, preprocess_document_adaptive
from app.nlp.advanced_nlp import BERTExtractor, has_advanced_nlp_capabilities
from app.nlp.environment_preference_extractor import WorkPreferenceExtractor, extract_work_preferences
from app.nlp.parser_feedback_system import ParserFeedbackSystem, improve_extraction_with_feedback

# Configuration du logging
logger = logging.getLogger(__name__)

class EnhancedParsingSystem:
    """
    Système de parsing amélioré intégrant tous les composants avancés.
    Cette classe fournit une interface unifiée pour le parsing de documents.
    """
    
    def __init__(self):
        """
        Initialise le système de parsing amélioré avec tous ses composants.
        """
        # Initialiser les composants
        self.adaptive_parser = AdaptiveParser()
        self.feedback_system = ParserFeedbackSystem()
        self.preference_extractor = WorkPreferenceExtractor()
        
        # Initialiser le module NLP avancé conditionnellement
        self.has_advanced_nlp = has_advanced_nlp_capabilities()
        if self.has_advanced_nlp:
            self.bert_extractor = BERTExtractor()
            logger.info("Système de parsing amélioré initialisé avec capacités NLP avancées.")
        else:
            self.bert_extractor = None
            logger.info("Système de parsing amélioré initialisé avec capacités NLP de base uniquement.")
    
    def parse_document(self, 
                       file_path: Optional[str] = None, 
                       file_content: Optional[BinaryIO] = None, 
                       text_content: Optional[str] = None,
                       file_name: Optional[str] = None,
                       doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse un document avec le système amélioré.
        
        Args:
            file_path: Chemin vers le fichier (optionnel)
            file_content: Contenu binaire du fichier (optionnel)
            text_content: Contenu textuel si déjà disponible (optionnel)
            file_name: Nom du fichier pour détection de format (optionnel)
            doc_type: Type de document si connu ('cv', 'job_posting', etc.) (optionnel)
            
        Returns:
            Dict: Résultat complet du parsing avec métadonnées
        """
        # Vérifier qu'au moins une source de données est fournie
        if not file_path and not file_content and not text_content:
            raise ValueError("Aucune source de données fournie pour le parsing.")
        
        # Récupérer le contenu textuel
        text = None
        file_format = None
        temp_file = None
        
        try:
            # 1. Traitement des fichiers fournis comme binary content
            if file_content and not text_content:
                # Créer un fichier temporaire pour le traitement
                temp_file = tempfile.NamedTemporaryFile(delete=False)
                temp_file_path = temp_file.name
                
                # Si un nom de fichier est fourni, ajouter l'extension
                if file_name:
                    extension = os.path.splitext(file_name)[1]
                    if extension:
                        temp_file_path += extension
                
                # Écrire le contenu dans le fichier temporaire
                try:
                    temp_file.write(file_content.read())
                    temp_file.close()  # Fermer pour que le contenu soit flushé
                    
                    # Détecter le format et extraire le texte
                    file_format = self.adaptive_parser.detect_file_format(temp_file_path)
                    text = self.adaptive_parser.extract_text_from_file(temp_file_path)
                except Exception as e:
                    logger.error(f"Erreur lors du traitement du contenu binaire: {e}")
                    raise ValueError(f"Impossible de traiter le contenu du fichier: {str(e)}")
            
            # 2. Traitement des fichiers fournis comme chemin
            elif file_path and not text_content:
                try:
                    # Détecter le format et extraire le texte
                    file_format = self.adaptive_parser.detect_file_format(file_path)
                    text = self.adaptive_parser.extract_text_from_file(file_path)
                except Exception as e:
                    logger.error(f"Erreur lors du traitement du fichier {file_path}: {e}")
                    raise ValueError(f"Impossible de traiter le fichier: {str(e)}")
            
            # 3. Utiliser directement le contenu textuel si fourni
            else:
                text = text_content
                # Essayer de détecter le format à partir du nom de fichier si disponible
                if file_name:
                    try:
                        temp_file = tempfile.NamedTemporaryFile(delete=False)
                        temp_file_path = temp_file.name
                        
                        with open(temp_file_path, 'w', encoding='utf-8') as f:
                            f.write(str(text))
                        
                        file_format = self.adaptive_parser.detect_file_format(temp_file_path)
                    except Exception as e:
                        logger.warning(f"Impossible de détecter le format à partir du nom: {e}")
            
            # Vérifier que nous avons du texte à traiter
            if not text or not text.strip():
                raise ValueError("Aucun contenu textuel extrait pour le parsing.")
            
            # 4. Prétraitement du document
            preprocessed = self.adaptive_parser.preprocess_document(text, file_format, doc_type)
            
            # 5. Déterminer le type de document s'il n'est pas fourni
            if not doc_type and "doc_type" in preprocessed:
                doc_type = preprocessed["doc_type"]
            
            # 6. Créer le résultat de base
            result = {
                "id": str(uuid.uuid4()),
                "original_text": text,
                "file_format": file_format,
                "doc_type": doc_type,
                "preprocessing": {
                    "paragraph_count": preprocessed.get("paragraph_count", 0),
                    "token_count": preprocessed.get("token_count", 0),
                    "language": preprocessed.get("language", "unknown")
                },
                "extracted_data": {},
                "confidence_scores": {}
            }
            
            # 7. Extraction d'informations basée sur le type de document
            if doc_type:
                result = self._extract_document_data(result, doc_type)
            
            # 8. Enrichir avec des analyses NLP avancées si disponibles
            if self.has_advanced_nlp and self.bert_extractor:
                result = self._enrich_with_advanced_nlp(result)
            
            # 9. Extraire les préférences d'environnement de travail
            result = self._extract_work_preferences(result)
            
            # 10. Appliquer des corrections basées sur le feedback précédent
            result = self.feedback_system.update_extraction_with_feedback(result)
            
            return result
            
        finally:
            # Nettoyer les fichiers temporaires si nécessaire
            if temp_file:
                try:
                    temp_file.close()
                except:
                    pass
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def _extract_document_data(self, result: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """
        Extrait les données spécifiques au type de document.
        
        Args:
            result: Résultat de parsing en cours
            doc_type: Type de document
            
        Returns:
            Dict: Résultat enrichi avec les données extraites
        """
        try:
            # Utiliser les parseurs spécifiques selon le type de document
            if doc_type == "cv":
                from app.nlp.cv_parser import extract_cv_data
                extracted_data = extract_cv_data(result["original_text"])
                result["extracted_data"].update(extracted_data.get("extracted_data", {}))
                if "confidence_scores" in extracted_data:
                    result["confidence_scores"].update(extracted_data["confidence_scores"])
            
            elif doc_type == "job_posting":
                from app.nlp.job_parser import extract_job_data
                extracted_data = extract_job_data(result["original_text"])
                result["extracted_data"].update(extracted_data.get("extracted_data", {}))
                if "confidence_scores" in extracted_data:
                    result["confidence_scores"].update(extracted_data["confidence_scores"])
            
            elif doc_type == "company_questionnaire":
                from app.nlp.company_questionnaire_parser import extract_questionnaire_data
                extracted_data = extract_questionnaire_data(result["original_text"])
                result["extracted_data"].update(extracted_data.get("extracted_data", {}))
                if "confidence_scores" in extracted_data:
                    result["confidence_scores"].update(extracted_data["confidence_scores"])
            
            else:
                # Pour les types de documents non spécifiquement gérés, extraire au moins les sections
                from app.nlp.section_extractor import extract_sections
                sections = extract_sections(result["original_text"])
                result["extracted_data"]["sections"] = sections
                result["confidence_scores"]["sections"] = 0.5  # Score de confiance moyen
            
            # Extraire les compétences indépendamment du type de document
            from app.nlp.skills_extractor import extract_skills
            skills = extract_skills(result["original_text"])
            result["extracted_data"]["skills"] = skills
            
            return result
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des données pour le type {doc_type}: {e}")
            # Éviter d'échouer complètement, retourner le résultat inchangé
            return result
    
    def _enrich_with_advanced_nlp(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrichit le résultat avec des analyses NLP avancées.
        
        Args:
            result: Résultat de parsing en cours
            
        Returns:
            Dict: Résultat enrichi avec les analyses avancées
        """
        try:
            if not self.has_advanced_nlp or not self.bert_extractor:
                return result
            
            text = result["original_text"]
            
            # 1. Extraire les entités nommées
            entities = self.bert_extractor.extract_entities(text)
            if entities:
                result["extracted_data"]["named_entities"] = entities
            
            # 2. Analyse de sentiment global
            sentiment = self.bert_extractor.extract_sentiment(text)
            if sentiment:
                result["extracted_data"]["sentiment"] = sentiment
            
            # 3. Répondre à des questions spécifiques selon le type de document
            doc_type = result.get("doc_type")
            
            if doc_type == "cv":
                # Questions pertinentes pour un CV
                questions = [
                    "Quel est le niveau d'expérience de cette personne?",
                    "Quels langages informatiques maîtrise cette personne?",
                    "Quelles sont les compétences principales de cette personne?"
                ]
            elif doc_type == "job_posting":
                # Questions pertinentes pour une offre d'emploi
                questions = [
                    "Quel est le niveau d'expérience requis pour ce poste?",
                    "Quels sont les avantages offerts pour ce poste?",
                    "Ce poste requiert-il des déplacements?"
                ]
            else:
                questions = []
            
            if questions:
                qa_results = {}
                for question in questions:
                    answer = self.bert_extractor.answer_question(text, question)
                    if answer and answer.get("answer") and answer.get("score", 0) > 0.3:
                        qa_results[question] = answer
                
                if qa_results:
                    if "advanced_analysis" not in result:
                        result["advanced_analysis"] = {}
                    result["advanced_analysis"]["qa_results"] = qa_results
            
            # 4. Classification du document si pertinent
            if doc_type in ["cv", "job_posting"]:
                # Par exemple, classifier un CV par niveau de séniorité ou domaine
                # ou classifier une offre d'emploi par secteur
                classification = self.bert_extractor.classify_text(text)
                if classification:
                    if "advanced_analysis" not in result:
                        result["advanced_analysis"] = {}
                    result["advanced_analysis"]["classification"] = classification
            
            return result
        except Exception as e:
            logger.error(f"Erreur lors de l'enrichissement avec NLP avancé: {e}")
            return result
    
    def _extract_work_preferences(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrait les préférences d'environnement de travail.
        
        Args:
            result: Résultat de parsing en cours
            
        Returns:
            Dict: Résultat enrichi avec les préférences de travail
        """
        try:
            # Seuls les CV sont concernés par l'extraction de préférences
            if result.get("doc_type") == "cv":
                preferences = self.preference_extractor.extract_preferences_from_cv(result["original_text"])
                
                if preferences:
                    if "extracted_data" not in result:
                        result["extracted_data"] = {}
                    
                    result["extracted_data"]["preferences"] = {
                        "environment": preferences["environment_preferences"],
                        "work_style": preferences["work_style_preferences"]
                    }
                    
                    if "confidence_scores" not in result:
                        result["confidence_scores"] = {}
                    
                    result["confidence_scores"]["preferences"] = preferences["confidence_scores"]
            
            return result
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des préférences de travail: {e}")
            return result
    
    def save_feedback(self, 
                       original_result: Dict[str, Any], 
                       corrected_result: Dict[str, Any], 
                       user_id: Optional[str] = None) -> str:
        """
        Enregistre le feedback d'un utilisateur sur un résultat de parsing.
        
        Args:
            original_result: Résultat original produit par le système
            corrected_result: Résultat corrigé par l'utilisateur
            user_id: Identifiant de l'utilisateur (optionnel)
            
        Returns:
            str: Identifiant du feedback enregistré
        """
        try:
            # Extraire les données originales et corrigées
            original_data = original_result.get("extracted_data", {})
            corrected_data = corrected_result.get("extracted_data", {})
            doc_type = original_result.get("doc_type", "unknown")
            original_text = original_result.get("original_text")
            
            # Enregistrer la correction
            correction_id = self.feedback_system.save_parsing_correction(
                original_data=original_data,
                corrected_data=corrected_data,
                doc_type=doc_type,
                user_id=user_id,
                original_text=original_text
            )
            
            return correction_id
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du feedback: {e}")
            return ""
    
    def export_training_data(self, output_dir: str, doc_type: Optional[str] = None) -> bool:
        """
        Exporte les données d'entraînement pour le fine-tuning des modèles.
        
        Args:
            output_dir: Répertoire de sortie
            doc_type: Type de document à exporter (optionnel)
            
        Returns:
            bool: True si l'exportation a réussi
        """
        return self.feedback_system.export_training_dataset(output_dir, doc_type)


# Fonctions d'interface pour utilisation dans d'autres modules
def parse_document(file_path: Optional[str] = None, 
                   file_content: Optional[BinaryIO] = None, 
                   text_content: Optional[str] = None,
                   file_name: Optional[str] = None,
                   doc_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Fonction d'interface pour parser un document avec le système amélioré.
    
    Args:
        file_path: Chemin vers le fichier (optionnel)
        file_content: Contenu binaire du fichier (optionnel)
        text_content: Contenu textuel si déjà disponible (optionnel)
        file_name: Nom du fichier pour détection de format (optionnel)
        doc_type: Type de document si connu (optionnel)
        
    Returns:
        Dict: Résultat complet du parsing
    """
    parser = EnhancedParsingSystem()
    return parser.parse_document(
        file_path=file_path,
        file_content=file_content,
        text_content=text_content,
        file_name=file_name,
        doc_type=doc_type
    )

def save_parsing_feedback(original_result: Dict[str, Any], 
                         corrected_result: Dict[str, Any], 
                         user_id: Optional[str] = None) -> str:
    """
    Fonction d'interface pour enregistrer le feedback d'un utilisateur.
    
    Args:
        original_result: Résultat original
        corrected_result: Résultat corrigé
        user_id: Identifiant de l'utilisateur (optionnel)
        
    Returns:
        str: Identifiant du feedback
    """
    parser = EnhancedParsingSystem()
    return parser.save_feedback(original_result, corrected_result, user_id)

def export_training_dataset(output_dir: str, doc_type: Optional[str] = None) -> bool:
    """
    Fonction d'interface pour exporter les données d'entraînement.
    
    Args:
        output_dir: Répertoire de sortie
        doc_type: Type de document (optionnel)
        
    Returns:
        bool: Résultat de l'opération
    """
    parser = EnhancedParsingSystem()
    return parser.export_training_data(output_dir, doc_type)