"""
Tests unitaires pour le système amélioré de parsing.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest

# Importer les modules à tester
from app.nlp.adaptive_parser import AdaptiveParser, extract_text_from_file
from app.nlp.parser_feedback_system import ParserFeedbackSystem
from app.nlp.enhanced_parsing_system import EnhancedParsingSystem, parse_document


# Tests pour le parseur adaptatif
class TestAdaptiveParser:
    """
    Tests unitaires pour le module adaptive_parser.
    """
    
    def setup_method(self):
        self.parser = AdaptiveParser()
        
        # Créer un fichier texte de test
        self.test_content = "Ceci est un document de test.\nIl contient plusieurs lignes.\nPour tester le parsing."
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            f.write(self.test_content)
    
    def teardown_method(self):
        # Nettoyer le fichier temporaire
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_detect_file_format(self):
        # Vérifier la détection du format de fichier
        format_name = self.parser.detect_file_format(self.temp_file.name)
        assert format_name == "text", f"Format détecté incorrectement: {format_name} au lieu de 'text'"
    
    def test_extract_text_from_file(self):
        # Vérifier l'extraction de texte
        extracted_text = self.parser.extract_text_from_file(self.temp_file.name)
        assert extracted_text == self.test_content, "Le texte extrait ne correspond pas au contenu original"
    
    def test_preprocess_document(self):
        # Vérifier le prétraitement du document
        preprocessed = self.parser.preprocess_document(self.test_content)
        assert isinstance(preprocessed, dict), "Le résultat du prétraitement devrait être un dictionnaire"
        assert "text" in preprocessed, "Le texte prétraité devrait être inclus dans le résultat"


# Tests pour le système de feedback
class TestParserFeedbackSystem:
    """
    Tests unitaires pour le module parser_feedback_system.
    """
    
    def setup_method(self):
        # Utiliser un répertoire temporaire pour les tests
        self.temp_dir = tempfile.TemporaryDirectory()
        self.feedback_system = ParserFeedbackSystem(storage_dir=self.temp_dir.name)
        
        # Données de test
        self.original_data = {"nom": "Dupont", "competences": ["Python", "Java"]}
        self.corrected_data = {"nom": "Dupont", "competences": ["Python", "Java", "SQL"]}
        self.doc_type = "cv"
        self.text = "CV de Jean Dupont, compétences: Python, Java, SQL"
    
    def teardown_method(self):
        # Nettoyer le répertoire temporaire
        self.temp_dir.cleanup()
    
    def test_save_parsing_correction(self):
        # Vérifier l'enregistrement d'une correction
        correction_id = self.feedback_system.save_parsing_correction(
            original_data=self.original_data,
            corrected_data=self.corrected_data,
            doc_type=self.doc_type,
            original_text=self.text
        )
        
        # Vérifier que l'ID n'est pas vide
        assert correction_id, "L'ID de correction ne devrait pas être vide"
        
        # Vérifier que la correction est récupérable
        correction = self.feedback_system.get_correction(correction_id)
        assert correction, "La correction devrait être récupérable"
        assert correction.get("doc_type") == self.doc_type, "Le type de document devrait être préservé"
        assert correction.get("original_extraction") == self.original_data, "Les données originales devraient être préservées"
        assert correction.get("corrected_extraction") == self.corrected_data, "Les données corrigées devraient être préservées"
        assert "original_text" in correction, "Le texte original devrait être inclus"
    
    def test_get_training_data(self):
        # Ajouter une correction
        self.feedback_system.save_parsing_correction(
            original_data=self.original_data,
            corrected_data=self.corrected_data,
            doc_type=self.doc_type,
            original_text=self.text
        )
        
        # Récupérer les données d'entraînement
        training_data = self.feedback_system.get_training_data(doc_type=self.doc_type)
        
        # Vérifier qu'il y a des données
        assert training_data, "Des données d'entraînement devraient être disponibles"
        assert len(training_data) >= 1, "Il devrait y avoir au moins une entrée"
        assert "corrected_extraction" in training_data[0], "Les données d'entraînement devraient contenir les extractions corrigées"
    
    def test_export_training_dataset(self):
        # Ajouter une correction
        self.feedback_system.save_parsing_correction(
            original_data=self.original_data,
            corrected_data=self.corrected_data,
            doc_type=self.doc_type,
            original_text=self.text
        )
        
        # Créer un répertoire temporaire pour l'export
        export_dir = tempfile.TemporaryDirectory()
        
        # Exporter les données
        result = self.feedback_system.export_training_dataset(export_dir.name, self.doc_type)
        
        # Vérifier le résultat
        assert result, "L'exportation devrait réussir"
        
        # Vérifier que le fichier existe
        expected_file = Path(export_dir.name) / f"training_data_{self.doc_type}.json"
        assert expected_file.exists(), "Le fichier d'exportation devrait exister"
        
        # Nettoyer
        export_dir.cleanup()
    
    def test_update_extraction_with_feedback(self):
        # Ajouter une correction
        self.feedback_system.save_parsing_correction(
            original_data=self.original_data,
            corrected_data=self.corrected_data,
            doc_type=self.doc_type,
            original_text=self.text
        )
        
        # Créer un résultat similaire à celui déjà corrigé
        test_result = {
            "doc_type": self.doc_type,
            "extracted_data": self.original_data.copy()
        }
        
        # Appliquer les corrections
        updated_result = self.feedback_system.update_extraction_with_feedback(test_result)
        
        # Vérifier que des corrections ont été appliquées ou des suggestions faites
        assert updated_result != test_result, "Le résultat devrait être modifié"
        assert "feedback_applied" in updated_result or "improvement_suggestions" in updated_result, \
               "Des corrections ou suggestions devraient être présentes"


# Tests pour le système de parsing amélioré
@patch('app.nlp.advanced_nlp.has_advanced_nlp_capabilities', return_value=False)
class TestEnhancedParsingSystem:
    """
    Tests unitaires pour le module enhanced_parsing_system.
    Note: nous simulons l'absence des capacités NLP avancées pour simplifier les tests.
    """
    
    def setup_method(self):
        self.parser = EnhancedParsingSystem()
        
        # Créer un fichier texte de test
        self.test_content = "Ceci est un CV de test.\nNom: Jean Dupont\nCompétences: Python, Java"
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        with open(self.temp_file.name, 'w', encoding='utf-8') as f:
            f.write(self.test_content)
    
    def teardown_method(self):
        # Nettoyer le fichier temporaire
        if hasattr(self, 'temp_file') and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_parse_document_from_file(self, mock_has_advanced_nlp):
        # Simuler l'extraction de données CV
        with patch('app.nlp.enhanced_parsing_system.extract_work_preferences') as mock_extract_prefs, \
             patch('app.nlp.cv_parser.extract_cv_data', return_value={
                 "extracted_data": {"nom": "Jean Dupont", "competences": ["Python", "Java"]},
                 "confidence_scores": {"extraction": 0.8}
             }) as mock_extract_cv:
            
            # Mock des préférences
            mock_extract_prefs.return_value = {
                "environment_preferences": {"remote": 0.7},
                "work_style_preferences": {"autonomy": 0.8},
                "confidence_scores": {"environment": 0.6, "work_style": 0.7}
            }
            
            # Tester le parsing du document
            result = self.parser.parse_document(
                file_path=self.temp_file.name,
                doc_type="cv"
            )
            
            # Vérifier le résultat
            assert result, "Le parsing devrait réussir"
            assert "id" in result, "Le résultat devrait avoir un ID"
            assert "original_text" in result, "Le résultat devrait contenir le texte original"
            assert "extracted_data" in result, "Le résultat devrait contenir des données extraites"
            assert "confidence_scores" in result, "Le résultat devrait contenir des scores de confiance"
            assert result["doc_type"] == "cv", "Le type de document devrait être préservé"
    
    def test_parse_document_from_text(self, mock_has_advanced_nlp):
        # Tester le parsing à partir d'un texte
        with patch('app.nlp.enhanced_parsing_system.extract_work_preferences') as mock_extract_prefs, \
             patch('app.nlp.document_classifier.DocumentClassifier.classify_document', return_value="cv"), \
             patch('app.nlp.cv_parser.extract_cv_data', return_value={
                 "extracted_data": {"nom": "Jean Dupont"},
                 "confidence_scores": {"extraction": 0.8}
             }) as mock_extract_cv:
            
            result = self.parser.parse_document(
                text_content=self.test_content
            )
            
            # Vérifier le résultat
            assert result, "Le parsing devrait réussir"
            assert "extracted_data" in result, "Le résultat devrait contenir des données extraites"
    
    def test_save_feedback(self, mock_has_advanced_nlp):
        # Tester l'enregistrement de feedback
        original_result = {
            "doc_type": "cv",
            "original_text": self.test_content,
            "extracted_data": {"nom": "Jean Dupont", "competences": ["Python"]}
        }
        
        corrected_result = {
            "doc_type": "cv",
            "original_text": self.test_content,
            "extracted_data": {"nom": "Jean Dupont", "competences": ["Python", "Java", "SQL"]}
        }
        
        # Mock l'enregistrement du feedback
        with patch('app.nlp.parser_feedback_system.ParserFeedbackSystem.save_parsing_correction', 
                  return_value="test_feedback_id") as mock_save:
            
            feedback_id = self.parser.save_feedback(original_result, corrected_result, "test_user")
            
            # Vérifier que la méthode a été appelée
            mock_save.assert_called_once()
            
            # Vérifier l'ID retourné
            assert feedback_id == "test_feedback_id", "L'ID de feedback devrait correspondre"


# Fonction de test principal
def test_integration():
    """
    Test d'intégration simple pour vérifier que les composants peuvent fonctionner ensemble.
    """
    # Créer un fichier texte de test
    test_content = "Ceci est un CV de test.\nNom: Jean Dupont\nCompétences: Python, Java"
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    
    try:
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # Simuler le processus complet avec des mocks
        with patch('app.nlp.advanced_nlp.has_advanced_nlp_capabilities', return_value=False), \
             patch('app.nlp.document_classifier.DocumentClassifier.classify_document', return_value="cv"), \
             patch('app.nlp.cv_parser.extract_cv_data', return_value={
                 "extracted_data": {"nom": "Jean Dupont", "competences": ["Python", "Java"]},
                 "confidence_scores": {"extraction": 0.8}
             }), \
             patch('app.nlp.environment_preference_extractor.WorkPreferenceExtractor.extract_preferences_from_cv',
                  return_value={
                     "environment_preferences": {"remote": 0.7},
                     "work_style_preferences": {"autonomy": 0.8},
                     "confidence_scores": {"environment": 0.6, "work_style": 0.7}
                 }), \
             patch('app.nlp.parser_feedback_system.ParserFeedbackSystem.update_extraction_with_feedback',
                  side_effect=lambda x: x):
            
            # Utiliser la fonction d'interface principale
            result = parse_document(file_path=temp_file.name)
            
            # Vérifier que le résultat est correct
            assert result, "Le parsing devrait réussir"
            assert "extracted_data" in result, "Le résultat devrait contenir des données extraites"
            assert result.get("doc_type") == "cv", "Le type de document devrait être détecté correctement"
    
    finally:
        # Nettoyer
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)