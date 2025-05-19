"""
Tests for Session 4 - Vector Embeddings Implementation
======================================================
Tests complets pour les services d'embeddings, la base de données vectorielle
et le matcher de compétences amélioré.
"""

import unittest
import asyncio
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import numpy as np

# Import des modules à tester
try:
    from services.embeddings_service import EmbeddingsService
    from services.skills_embeddings_db import SkillsEmbeddingsDB
    from matchers.enhanced_skills_matcher import EnhancedSkillsMatcher, MatchingMode
    from core.models import Candidate, Job, Experience
    from core.exceptions import SmartMatchNLPError, SmartMatchConfigurationError
    IMPORTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import modules for testing: {e}")
    IMPORTS_AVAILABLE = False


@unittest.skipUnless(IMPORTS_AVAILABLE, "Required modules not available")
class TestEmbeddingsService(unittest.TestCase):
    """Tests pour le service d'embeddings vectoriels."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            'cache_dir': self.temp_dir,
            'enable_caching': True,
            'batch_size': 4,
            'similarity_threshold': 0.7,
            'max_cache_size': 100
        }
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        shutil.rmtree(self.temp_dir)
    
    @patch('services.embeddings_service.SENTENCE_TRANSFORMERS_AVAILABLE', False)
    def test_initialization_without_sentence_transformers(self):
        """Test d'initialisation sans sentence-transformers."""
        with self.assertRaises(SmartMatchConfigurationError):
            EmbeddingsService(self.config)
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_initialization_success(self, mock_transformer):
        """Test d'initialisation réussie."""
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        service = EmbeddingsService(self.config)
        
        self.assertIsNotNone(service.model)
        self.assertEqual(service.model_name, "all-MiniLM-L6-v2")
        self.assertEqual(service.batch_size, 4)
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_get_embeddings_single_text(self, mock_transformer):
        """Test de calcul d'embedding pour un seul texte."""
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model
        
        service = EmbeddingsService(self.config)
        embedding = service.get_embeddings("python programming")
        
        self.assertIsInstance(embedding, np.ndarray)
        self.assertEqual(embedding.shape, (3,))
        mock_model.encode.assert_called_once()
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_get_embeddings_multiple_texts(self, mock_transformer):
        """Test de calcul d'embeddings pour plusieurs textes."""
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_transformer.return_value = mock_model
        
        service = EmbeddingsService(self.config)
        embeddings = service.get_embeddings(["python", "javascript"])
        
        self.assertIsInstance(embeddings, np.ndarray)
        self.assertEqual(embeddings.shape, (2, 3))
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_caching_functionality(self, mock_transformer):
        """Test du système de cache."""
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model
        
        service = EmbeddingsService(self.config)
        
        # Premier appel - calcul
        service.get_embeddings("python")
        self.assertEqual(mock_model.encode.call_count, 1)
        self.assertEqual(service.cache_misses, 1)
        
        # Deuxième appel - cache
        service.get_embeddings("python")
        self.assertEqual(mock_model.encode.call_count, 1)  # Pas d'appel supplémentaire
        self.assertEqual(service.cache_hits, 1)
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_text_similarity_calculation(self, mock_transformer):
        """Test de calcul de similarité textuelle."""
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        # Embeddings qui donneront une similarité cosinus de 0.8
        embedding1 = np.array([1.0, 0.0, 0.0])
        embedding2 = np.array([0.8, 0.6, 0.0])
        mock_model.encode.side_effect = [[embedding1], [embedding2]]
        mock_transformer.return_value = mock_model
        
        service = EmbeddingsService(self.config)
        similarity = service.calculate_text_similarity("python", "javascript")
        
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_skills_similarity_calculation(self, mock_transformer):
        """Test de calcul de similarité entre listes de compétences."""
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        # Embeddings simulés
        embeddings = np.array([
            [1.0, 0.0, 0.0],  # python
            [0.8, 0.6, 0.0],  # javascript
            [0.9, 0.0, 0.4],  # programming
            [0.7, 0.7, 0.0]   # development
        ])
        mock_model.encode.return_value = embeddings
        mock_transformer.return_value = mock_model
        
        service = EmbeddingsService(self.config)
        similarity = service.calculate_skills_similarity(
            ["python", "javascript"],
            ["programming", "development"]
        )
        
        self.assertIsInstance(similarity, float)
        self.assertGreaterEqual(similarity, 0.0)
        self.assertLessEqual(similarity, 1.0)
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_normalize_text(self, mock_transformer):
        """Test de normalisation de texte."""
        # Mock minimal
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        service = EmbeddingsService(self.config)
        
        normalized = service.normalize_text("  Python Programming!@#  ")
        self.assertEqual(normalized, "python programming")
        
        normalized = service.normalize_text("")
        self.assertEqual(normalized, "")
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_extract_skills_from_text(self, mock_transformer):
        """Test d'extraction de compétences depuis un texte."""
        # Mock minimal
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        service = EmbeddingsService(self.config)
        
        text = "I have experience with Python, JavaScript and machine learning"
        skills = service.extract_skills_from_text(text)
        
        self.assertIsInstance(skills, list)
        self.assertIn("python", skills)
        self.assertIn("javascript", skills)
        self.assertIn("machine learning", skills)
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_cache_stats(self, mock_transformer):
        """Test des statistiques de cache."""
        # Mock minimal
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
        mock_transformer.return_value = mock_model
        
        service = EmbeddingsService(self.config)
        
        # Faire quelques calculs
        service.get_embeddings("python")
        service.get_embeddings("python")  # Cache hit
        service.get_embeddings("java")    # Cache miss
        
        stats = service.get_cache_stats()
        
        self.assertEqual(stats['cache_hits'], 1)
        self.assertEqual(stats['cache_misses'], 2)
        self.assertEqual(stats['total_requests'], 3)
        self.assertAlmostEqual(stats['hit_rate'], 1/3)
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_context_manager(self, mock_transformer):
        """Test du support du context manager."""
        # Mock minimal
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        mock_transformer.return_value = mock_model
        
        with EmbeddingsService(self.config) as service:
            self.assertIsNotNone(service.model)
            # Le cache devrait être chargé/sauvegardé automatiquement


@unittest.skipUnless(IMPORTS_AVAILABLE, "Required modules not available")
class TestSkillsEmbeddingsDB(unittest.TestCase):
    """Tests pour la base de données vectorielle de compétences."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock du service d'embeddings
        self.mock_embeddings_service = Mock(spec=EmbeddingsService)
        self.mock_embeddings_service.model_name = "test-model"
        self.mock_embeddings_service.batch_size = 4
        
        self.config = {
            'db_dir': self.temp_dir,
            'similarity_threshold': 0.7,
            'max_results': 5,
            'auto_build': False  # Pour éviter la construction automatique
        }
    
    def tearDown(self):
        """Nettoyage après chaque test."""
        shutil.rmtree(self.temp_dir)
    
    def test_initialization_without_auto_build(self):
        """Test d'initialisation sans construction automatique."""
        db = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        
        self.assertEqual(db.embeddings_service, self.mock_embeddings_service)
        self.assertFalse(db.is_loaded)
        self.assertEqual(len(db.skills_list), 0)
    
    def test_build_index_from_skills(self):
        """Test de construction d'index à partir de compétences."""
        # Mock des embeddings retournés
        embeddings = np.array([
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6],
            [0.7, 0.8, 0.9]
        ])
        self.mock_embeddings_service.get_embeddings.return_value = embeddings
        
        db = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        
        skills = ["python", "javascript", "machine learning"]
        db._build_index_from_skills(skills)
        
        self.assertTrue(db.is_loaded)
        self.assertEqual(len(db.skills_list), 3)
        self.assertEqual(db.skills_embeddings.shape, (3, 3))
        self.assertIn("python", db.skills_list)
        self.assertIn("javascript", db.skills_list)
        self.assertIn("machine learning", db.skills_list)
    
    def test_search_similar_skills(self):
        """Test de recherche de compétences similaires."""
        # Préparer la DB avec des compétences
        skills = ["python", "javascript", "java"]
        embeddings = np.array([
            [1.0, 0.0, 0.0],  # python
            [0.8, 0.6, 0.0],  # javascript
            [0.6, 0.8, 0.0]   # java
        ])
        self.mock_embeddings_service.get_embeddings.side_effect = [
            embeddings,  # Pour la construction
            np.array([0.9, 0.1, 0.0])  # Pour la requête
        ]
        
        db = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        db._build_index_from_skills(skills)
        
        # Rechercher des compétences similaires
        results = db.search_similar_skills("programming")
        
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        
        # Vérifier le format des résultats
        for skill, similarity in results:
            self.assertIsInstance(skill, str)
            self.assertIsInstance(similarity, float)
            self.assertGreaterEqual(similarity, 0.7)  # Au-dessus du seuil
    
    def test_add_skills(self):
        """Test d'ajout de nouvelles compétences."""
        # Construire un index initial
        initial_skills = ["python", "javascript"]
        initial_embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])
        self.mock_embeddings_service.get_embeddings.return_value = initial_embeddings
        
        db = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        db._build_index_from_skills(initial_skills)
        
        # Ajouter de nouvelles compétences
        new_embeddings = np.array([[0.5, 0.6]])
        self.mock_embeddings_service.get_embeddings.return_value = new_embeddings
        
        db.add_skills(["java"], rebuild_index=False)
        
        self.assertEqual(len(db.skills_list), 3)
        self.assertIn("java", db.skills_list)
        self.assertEqual(db.skills_embeddings.shape, (3, 2))
    
    def test_remove_skills(self):
        """Test de suppression de compétences."""
        # Construire un index initial
        skills = ["python", "javascript", "java"]
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]])
        self.mock_embeddings_service.get_embeddings.return_value = embeddings
        
        db = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        db._build_index_from_skills(skills)
        
        # Supprimer une compétence
        db.remove_skills(["javascript"], rebuild_index=False)
        
        self.assertEqual(len(db.skills_list), 2)
        self.assertNotIn("javascript", db.skills_list)
        self.assertIn("python", db.skills_list)
        self.assertIn("java", db.skills_list)
        self.assertEqual(db.skills_embeddings.shape, (2, 2))
    
    def test_save_and_load_index(self):
        """Test de sauvegarde et chargement d'index."""
        # Construire un index
        skills = ["python", "javascript"]
        embeddings = np.array([[0.1, 0.2], [0.3, 0.4]])
        self.mock_embeddings_service.get_embeddings.return_value = embeddings
        
        db = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        db._build_index_from_skills(skills)
        
        # Sauvegarder
        db._save_index()
        
        # Créer une nouvelle DB et charger
        db2 = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        loaded = db2._load_index()
        
        self.assertTrue(loaded)
        self.assertTrue(db2.is_loaded)
        self.assertEqual(db2.skills_list, skills)
        np.testing.assert_array_equal(db2.skills_embeddings, embeddings)
    
    def test_export_import_index(self):
        """Test d'export et import d'index."""
        # Construire un index
        skills = ["python", "javascript"]
        self.mock_embeddings_service.get_embeddings.return_value = np.array([[0.1, 0.2], [0.3, 0.4]])
        
        db = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        db._build_index_from_skills(skills)
        
        # Exporter
        export_file = Path(self.temp_dir) / "export.json"
        db.export_index(str(export_file))
        
        self.assertTrue(export_file.exists())
        
        # Vérifier le contenu
        with open(export_file, 'r') as f:
            export_data = json.load(f)
        
        self.assertEqual(export_data['skills_list'], skills)
        self.assertIn('metadata', export_data)
        self.assertIn('config', export_data)
        
        # Importer dans une nouvelle DB
        db2 = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        db2.import_index(str(export_file), rebuild=False)
        
        self.assertEqual(db2.skills_list, skills)
        self.assertTrue(db2.is_loaded)
    
    def test_get_stats(self):
        """Test des statistiques de la DB."""
        # Construire un index minimal
        self.mock_embeddings_service.get_embeddings.return_value = np.array([[0.1, 0.2]])
        
        db = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        db._build_index_from_skills(["python"])
        
        stats = db.get_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertTrue(stats['is_loaded'])
        self.assertEqual(stats['skills_count'], 1)
        self.assertEqual(stats['embedding_dimension'], 2)
        self.assertIn('metadata', stats)
    
    def test_contains_skill(self):
        """Test de vérification de présence de compétence."""
        self.mock_embeddings_service.get_embeddings.return_value = np.array([[0.1, 0.2]])
        
        db = SkillsEmbeddingsDB(self.mock_embeddings_service, self.config)
        db._build_index_from_skills(["python"])
        
        self.assertTrue(db.contains_skill("python"))
        self.assertTrue(db.contains_skill("PYTHON"))  # Test case insensitive
        self.assertFalse(db.contains_skill("javascript"))


@unittest.skipUnless(IMPORTS_AVAILABLE, "Required modules not available")
class TestEnhancedSkillsMatcher(unittest.TestCase):
    """Tests pour le matcher de compétences amélioré."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        # Mock des services
        self.mock_nlp_service = Mock()
        self.mock_embeddings_service = Mock(spec=EmbeddingsService)
        self.mock_skills_db = Mock(spec=SkillsEmbeddingsDB)
        
        # Configuration de test
        self.config = {
            'matching_mode': 'hybrid',
            'embeddings_weight': 0.7,
            'tfidf_weight': 0.3,
            'semantic_threshold': 0.75,
            'enable_skills_expansion': True,
            'max_expanded_skills': 3
        }
        
        # Candidat et job de test
        self.candidate = Candidate(
            id="cand_123",
            name="John Doe",
            skills=["Python", "JavaScript", "Docker"],
            experience_years=5,
            experience_description="Full-stack developer with Python and JavaScript experience"
        )
        
        self.job = Job(
            id="job_456",
            title="Senior Python Developer",
            required_skills=["Python", "Django", "PostgreSQL"],
            preferred_skills=["Docker", "AWS", "React"],
            experience_required=3
        )
    
    def test_initialization_different_modes(self):
        """Test d'initialisation avec différents modes."""
        # Mode TF-IDF only
        config_tfidf = self.config.copy()
        config_tfidf['matching_mode'] = 'tfidf_only'
        matcher_tfidf = EnhancedSkillsMatcher(config=config_tfidf)
        self.assertEqual(matcher_tfidf.matching_mode, MatchingMode.TFIDF_ONLY)
        
        # Mode embeddings only
        config_emb = self.config.copy()
        config_emb['matching_mode'] = 'embeddings_only'
        matcher_emb = EnhancedSkillsMatcher(
            embeddings_service=self.mock_embeddings_service,
            skills_db=self.mock_skills_db,
            config=config_emb
        )
        self.assertEqual(matcher_emb.matching_mode, MatchingMode.EMBEDDINGS_ONLY)
        
        # Mode hybrid
        matcher_hybrid = EnhancedSkillsMatcher(
            nlp_service=self.mock_nlp_service,
            embeddings_service=self.mock_embeddings_service,
            skills_db=self.mock_skills_db,
            config=self.config
        )
        self.assertEqual(matcher_hybrid.matching_mode, MatchingMode.HYBRID)
    
    @patch('matchers.enhanced_skills_matcher.SKLEARN_AVAILABLE', True)
    async def test_calculate_tfidf_score(self):
        """Test du calcul de score TF-IDF."""
        matcher = EnhancedSkillsMatcher(
            nlp_service=self.mock_nlp_service,
            config={'matching_mode': 'tfidf_only'}
        )
        
        # Mock de la méthode legacy
        with patch.object(matcher, '_calculate_legacy_score', return_value=0.8) as mock_legacy:
            score = await matcher._calculate_tfidf_score(self.candidate, self.job)
            
            self.assertEqual(score, 0.8)
            mock_legacy.assert_called_once_with(self.candidate, self.job)
            self.assertEqual(matcher.matching_stats['tfidf_matches'], 1)
    
    async def test_calculate_embeddings_score(self):
        """Test du calcul de score avec embeddings."""
        # Mock des méthodes nécessaires
        self.mock_embeddings_service.get_embeddings.return_value = np.array([0.1, 0.2, 0.3])
        self.mock_skills_db.search_similar_skills.return_value = [("python", 0.9)]
        
        matcher = EnhancedSkillsMatcher(
            embeddings_service=self.mock_embeddings_service,
            skills_db=self.mock_skills_db,
            config={'matching_mode': 'embeddings_only'}
        )
        
        # Mock des méthodes internes
        with patch.object(matcher, '_extract_and_normalize_skills', return_value=["python", "javascript"]):
            with patch.object(matcher, '_normalize_skills', side_effect=lambda x: x):
                with patch.object(matcher, '_calculate_semantic_matches', return_value=["python"]):
                    score = await matcher._calculate_embeddings_score(self.candidate, self.job)
                    
                    self.assertIsInstance(score, float)
                    self.assertGreaterEqual(score, 0.0)
                    self.assertLessEqual(score, 1.0)
                    self.assertEqual(matcher.matching_stats['embeddings_matches'], 1)
    
    async def test_calculate_hybrid_score(self):
        """Test du calcul de score hybride."""
        matcher = EnhancedSkillsMatcher(
            nlp_service=self.mock_nlp_service,
            embeddings_service=self.mock_embeddings_service,
            skills_db=self.mock_skills_db,
            config=self.config
        )
        
        # Mock des calculs de score individuels
        with patch.object(matcher, '_calculate_tfidf_score', return_value=0.6) as mock_tfidf:
            with patch.object(matcher, '_calculate_embeddings_score', return_value=0.8) as mock_emb:
                score = await matcher._calculate_hybrid_score(self.candidate, self.job)
                
                # Score hybride = 0.6 * 0.3 + 0.8 * 0.7 = 0.18 + 0.56 = 0.74
                expected_score = (0.6 * 0.3) + (0.8 * 0.7)
                self.assertAlmostEqual(score, expected_score, places=2)
                self.assertEqual(matcher.matching_stats['hybrid_matches'], 1)
    
    async def test_ab_testing_score(self):
        """Test du score en mode A/B testing."""
        matcher = EnhancedSkillsMatcher(
            nlp_service=self.mock_nlp_service,
            embeddings_service=self.mock_embeddings_service,
            skills_db=self.mock_skills_db,
            config={'matching_mode': 'ab_testing', 'ab_testing_ratio': 0.5}
        )
        
        # Mock des calculs de score
        with patch.object(matcher, '_calculate_tfidf_score', return_value=0.6):
            with patch.object(matcher, '_calculate_embeddings_score', return_value=0.8):
                score = await matcher._calculate_ab_testing_score(self.candidate, self.job)
                
                # Devrait retourner soit 0.6 soit 0.8
                self.assertIn(score, [0.6, 0.8])
    
    async def test_semantic_skills_expansion(self):
        """Test de l'expansion sémantique des compétences."""
        self.mock_skills_db.search_similar_skills.side_effect = [
            [("django", 0.8), ("flask", 0.75)],  # Similar to python
            [("nodejs", 0.9), ("react", 0.8)],   # Similar to javascript
        ]
        
        matcher = EnhancedSkillsMatcher(
            embeddings_service=self.mock_embeddings_service,
            skills_db=self.mock_skills_db,
            config=self.config
        )
        
        skills = ["python", "javascript"]
        expanded = await matcher._expand_skills_semantically(skills)
        
        self.assertGreater(len(expanded), len(skills))
        self.assertIn("python", expanded)
        self.assertIn("javascript", expanded)
        # Devrait contenir au moins quelques compétences similaires
        self.assertTrue(any(skill in expanded for skill in ["django", "flask", "nodejs", "react"]))
    
    def test_normalize_skills(self):
        """Test de normalisation des compétences."""
        matcher = EnhancedSkillsMatcher(config=self.config)
        
        skills = ["  Python  ", "JavaScript", "DOCKER", "", None, "Machine Learning"]
        normalized = matcher._normalize_skills(skills)
        
        expected = ["python", "javascript", "docker", "machine learning"]
        self.assertEqual(normalized, expected)
    
    def test_find_synonym_match(self):
        """Test de correspondance par synonymes."""
        matcher = EnhancedSkillsMatcher(config=self.config)
        
        # Test de correspondance directe
        self.assertTrue(matcher._find_synonym_match("javascript", ["js", "python"]))
        
        # Test de correspondance par synonyme
        self.assertTrue(matcher._find_synonym_match("js", ["javascript", "python"]))
        
        # Test sans correspondance
        self.assertFalse(matcher._find_synonym_match("cobol", ["python", "javascript"]))
    
    async def test_insights_generation(self):
        """Test de génération d'insights."""
        matcher = EnhancedSkillsMatcher(
            embeddings_service=self.mock_embeddings_service,
            skills_db=self.mock_skills_db,
            config=self.config
        )
        
        # Mock des méthodes nécessaires
        with patch.object(matcher, '_extract_and_normalize_skills', return_value=["python", "javascript"]):
            with patch.object(matcher, '_normalize_skills', side_effect=lambda x: x):
                with patch.object(matcher, '_find_missing_skills', return_value=["django"]):
                    with patch.object(matcher, '_find_common_skills', return_value=["python"]):
                        insights = matcher._generate_specific_insights(self.candidate, self.job, 0.7)
                        
                        self.assertIsInstance(insights, list)
                        self.assertGreater(len(insights), 0)
                        
                        # Vérifier qu'il y a différents types d'insights
                        insight_types = [insight.type for insight in insights]
                        self.assertIn('strength', insight_types)
                        self.assertIn('weakness', insight_types)
    
    def test_get_configuration(self):
        """Test de récupération de configuration."""
        matcher = EnhancedSkillsMatcher(
            embeddings_service=self.mock_embeddings_service,
            skills_db=self.mock_skills_db,
            config=self.config
        )
        
        config = matcher.get_configuration()
        
        self.assertEqual(config['matching_mode'], 'hybrid')
        self.assertEqual(config['embeddings_weight'], 0.7)
        self.assertEqual(config['tfidf_weight'], 0.3)
        self.assertTrue(config['has_embeddings_service'])
        self.assertTrue(config['has_skills_db'])
    
    def test_get_matching_stats(self):
        """Test de récupération des statistiques de matching."""
        matcher = EnhancedSkillsMatcher(
            embeddings_service=self.mock_embeddings_service,
            skills_db=self.mock_skills_db,
            config=self.config
        )
        
        # Mock des stats des services
        self.mock_embeddings_service.get_cache_stats.return_value = {
            'cache_hits': 10,
            'cache_misses': 5
        }
        self.mock_skills_db.get_stats.return_value = {
            'search_count': 20
        }
        
        # Modifier les stats internes
        matcher.matching_stats['hybrid_matches'] = 5
        matcher.matching_stats['total_time_embeddings'] = 100.0
        
        stats = matcher.get_matching_stats()
        
        self.assertEqual(stats['hybrid_matches'], 5)
        self.assertEqual(stats['total_matches'], 5)
        self.assertIn('embeddings_cache_stats', stats)
        self.assertIn('skills_db_stats', stats)
    
    def test_reset_stats(self):
        """Test de remise à zéro des statistiques."""
        matcher = EnhancedSkillsMatcher(config=self.config)
        
        # Modifier quelques statistiques
        matcher.matching_stats['tfidf_matches'] = 10
        matcher.matching_stats['embeddings_matches'] = 5
        
        # Reset
        matcher.reset_stats()
        
        # Vérifier que tout est remis à zéro
        self.assertEqual(matcher.matching_stats['tfidf_matches'], 0)
        self.assertEqual(matcher.matching_stats['embeddings_matches'], 0)
        self.assertEqual(matcher.matching_stats['hybrid_matches'], 0)


@unittest.skipUnless(IMPORTS_AVAILABLE, "Required modules not available")
class TestIntegrationEmbeddings(unittest.TestCase):
    """Tests d'intégration pour l'ensemble du système d'embeddings."""
    
    def setUp(self):
        """Configuration avant chaque test."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.temp_dir)
    
    @patch('services.embeddings_service.SentenceTransformer')
    def test_full_integration_workflow(self, mock_transformer):
        """Test du workflow complet d'intégration."""
        # Mock du modèle
        mock_model = MagicMock()
        mock_model.get_sentence_embedding_dimension.return_value = 384
        
        # Embeddings simulés pour différentes compétences
        embeddings_map = {
            "python": np.array([1.0, 0.0, 0.0]),
            "django": np.array([0.9, 0.1, 0.0]),
            "javascript": np.array([0.0, 1.0, 0.0]),
            "react": np.array([0.1, 0.9, 0.0]),
            "programming": np.array([0.8, 0.2, 0.0])
        }
        
        def mock_encode(texts, **kwargs):
            if isinstance(texts, str):
                texts = [texts]
            return np.array([embeddings_map.get(text.lower(), np.random.rand(3)) for text in texts])
        
        mock_model.encode.side_effect = mock_encode
        mock_transformer.return_value = mock_model
        
        # 1. Créer le service d'embeddings
        embeddings_config = {
            'cache_dir': f"{self.temp_dir}/embeddings_cache",
            'enable_caching': True
        }
        embeddings_service = EmbeddingsService(embeddings_config)
        
        # 2. Créer la base de données de compétences
        db_config = {
            'db_dir': f"{self.temp_dir}/skills_db",
            'similarity_threshold': 0.7,
            'auto_build': False
        }
        skills_db = SkillsEmbeddingsDB(embeddings_service, db_config)
        skills_db._build_index_from_skills(["python", "django", "javascript", "react"])
        
        # 3. Créer le matcher amélioré
        matcher_config = {
            'matching_mode': 'embeddings_only',
            'semantic_threshold': 0.7
        }
        matcher = EnhancedSkillsMatcher(
            embeddings_service=embeddings_service,
            skills_db=skills_db,
            config=matcher_config
        )
        
        # 4. Créer des données de test
        candidate = Candidate(
            id="cand_123",
            name="Test Candidate",
            skills=["python", "programming"],
            experience_years=3
        )
        
        job = Job(
            id="job_456",
            title="Python Developer",
            required_skills=["python", "django"],
            preferred_skills=["javascript"],
            experience_required=2
        )
        
        # 5. Effectuer le matching
        async def run_test():
            score = await matcher._calculate_specific_score(candidate, job)
            insights = matcher._generate_specific_insights(candidate, job, score)
            
            # Vérifications
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)
            
            self.assertIsInstance(insights, list)
            self.assertGreater(len(insights), 0)
            
            # Vérifier les statistics
            stats = matcher.get_matching_stats()
            self.assertGreater(stats['embeddings_matches'], 0)
            
            # Vérifier que les services ont été utilisés
            cache_stats = embeddings_service.get_cache_stats()
            self.assertGreater(cache_stats['total_requests'], 0)
            
            db_stats = skills_db.get_stats()
            self.assertTrue(db_stats['is_loaded'])
            self.assertGreater(db_stats['skills_count'], 0)
        
        # Exécuter le test asynchrone
        asyncio.run(run_test())


if __name__ == '__main__':
    # Configuration du logging pour les tests
    logging.basicConfig(level=logging.WARNING)
    
    # Lancer les tests
    unittest.main(verbosity=2)
