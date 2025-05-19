"""
Embeddings Service Implementation
=================================
Service d'embeddings vectoriels utilisant sentence-transformers
pour le matching sémantique de compétences et de textes.

Implémente l'interface NLPService avec des embeddings vectoriels haute performance.
"""

import os
import logging
import hashlib
import pickle
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Gestion des imports optionnels
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SentenceTransformer = None
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from ..core.interfaces import NLPService
from ..core.exceptions import SmartMatchNLPError, SmartMatchConfigurationError

logger = logging.getLogger(__name__)


class EmbeddingsService(NLPService):
    """
    Service d'embeddings vectoriels pour l'analyse sémantique.
    
    Utilise sentence-transformers pour calculer des embeddings vectoriels
    de haute qualité pour le matching sémantique.
    
    Fonctionnalités:
    - Cache intelligent des embeddings
    - Support multilingue (FR/EN)
    - Optimisations de performance
    - Fallback gracieux si sentence-transformers n'est pas disponible
    """
    
    # Modèles recommandés par ordre de préférence
    RECOMMENDED_MODELS = [
        "all-MiniLM-L6-v2",      # Compact, rapide, multilingue excellent
        "all-MiniLM-L12-v2",     # Plus précis mais plus lourd
        "all-mpnet-base-v2",     # Encore plus précis
        "paraphrase-multilingual-MiniLM-L12-v2"  # Spécialement multilingue
    ]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le service d'embeddings.
        
        Args:
            config: Configuration optionnelle
        """
        self.config = config or {}
        
        # Configuration
        self.model_name = self.config.get('model_name', self.RECOMMENDED_MODELS[0])
        self.cache_dir = Path(self.config.get('cache_dir', 'cache/embeddings'))
        self.device = self.config.get('device', 'cpu')  # 'cpu' ou 'cuda'
        self.batch_size = self.config.get('batch_size', 32)
        self.similarity_threshold = self.config.get('similarity_threshold', 0.75)
        self.enable_caching = self.config.get('enable_caching', True)
        self.max_cache_size = self.config.get('max_cache_size', 10000)
        
        # État interne
        self.model: Optional[SentenceTransformer] = None
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Créer le dossier de cache
        if self.enable_caching:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialiser le modèle
        self._initialize_model()
        
        logger.info(f"EmbeddingsService initialized with model: {self.model_name}")
    
    def _initialize_model(self) -> None:
        """
        Initialise le modèle sentence-transformers.
        
        Raises:
            SmartMatchConfigurationError: Si sentence-transformers n'est pas disponible
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise SmartMatchConfigurationError(
                "sentence-transformers is not installed. "
                "Please install it with: pip install sentence-transformers"
            )
        
        try:
            logger.info(f"Loading sentence transformer model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            logger.info(f"Model loaded successfully. Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
            
        except Exception as e:
            # Essayer avec un modèle de fallback
            for fallback_model in self.RECOMMENDED_MODELS[1:]:
                try:
                    logger.warning(f"Failed to load {self.model_name}, trying fallback: {fallback_model}")
                    self.model = SentenceTransformer(fallback_model, device=self.device)
                    self.model_name = fallback_model
                    logger.info(f"Fallback model loaded successfully: {fallback_model}")
                    break
                except Exception as fallback_error:
                    logger.warning(f"Fallback model {fallback_model} also failed: {fallback_error}")
                    continue
            else:
                raise SmartMatchNLPError(f"Failed to load any sentence transformer model: {str(e)}")
    
    def _get_cache_key(self, text: str) -> str:
        """
        Génère une clé de cache pour un texte.
        
        Args:
            text: Texte à encoder
            
        Returns:
            Clé de cache unique
        """
        # Normaliser le texte et générer un hash
        normalized_text = text.strip().lower()
        key = f"{self.model_name}_{hashlib.md5(normalized_text.encode()).hexdigest()}"
        return key
    
    def _load_cache_from_disk(self) -> None:
        """Charge le cache depuis le disque."""
        if not self.enable_caching:
            return
        
        cache_file = self.cache_dir / "embeddings_cache.pkl"
        
        try:
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                logger.info(f"Loaded {len(self.embeddings_cache)} embeddings from cache")
        except Exception as e:
            logger.warning(f"Failed to load cache from disk: {e}")
            self.embeddings_cache = {}
    
    def _save_cache_to_disk(self) -> None:
        """Sauvegarde le cache sur le disque."""
        if not self.enable_caching or not self.embeddings_cache:
            return
        
        cache_file = self.cache_dir / "embeddings_cache.pkl"
        
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            logger.debug(f"Saved {len(self.embeddings_cache)} embeddings to cache")
        except Exception as e:
            logger.warning(f"Failed to save cache to disk: {e}")
    
    def _manage_cache_size(self) -> None:
        """Gère la taille du cache en supprimant les anciens éléments."""
        if len(self.embeddings_cache) > self.max_cache_size:
            # Supprimer 20% des éléments les plus anciens (approximation simple)
            items_to_remove = len(self.embeddings_cache) - int(self.max_cache_size * 0.8)
            keys_to_remove = list(self.embeddings_cache.keys())[:items_to_remove]
            
            for key in keys_to_remove:
                del self.embeddings_cache[key]
            
            logger.debug(f"Removed {items_to_remove} items from cache")
    
    def get_embeddings(self, texts: Union[str, List[str]], 
                      use_cache: bool = True) -> np.ndarray:
        """
        Calcule les embeddings pour un ou plusieurs textes.
        
        Args:
            texts: Texte ou liste de textes
            use_cache: Utiliser le cache ou non
            
        Returns:
            Array numpy des embeddings
            
        Raises:
            SmartMatchNLPError: En cas d'erreur de calcul
        """
        if self.model is None:
            raise SmartMatchNLPError("Model not initialized")
        
        # Normaliser l'entrée
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False
        
        embeddings = []
        texts_to_compute = []
        indices_to_compute = []
        
        # Vérifier le cache
        if use_cache and self.enable_caching:
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                
                if cache_key in self.embeddings_cache:
                    embeddings.append(self.embeddings_cache[cache_key])
                    self.cache_hits += 1
                else:
                    texts_to_compute.append(text)
                    indices_to_compute.append(i)
                    embeddings.append(None)  # Placeholder
                    self.cache_misses += 1
        else:
            texts_to_compute = texts
            indices_to_compute = list(range(len(texts)))
            embeddings = [None] * len(texts)
        
        # Calculer les embeddings manquants
        if texts_to_compute:
            try:
                computed_embeddings = self.model.encode(
                    texts_to_compute,
                    batch_size=self.batch_size,
                    show_progress_bar=False,
                    convert_to_numpy=True
                )
                
                # Stocker les résultats
                for i, embedding in enumerate(computed_embeddings):
                    original_index = indices_to_compute[i]
                    embeddings[original_index] = embedding
                    
                    # Ajouter au cache
                    if use_cache and self.enable_caching:
                        cache_key = self._get_cache_key(texts_to_compute[i])
                        self.embeddings_cache[cache_key] = embedding
                
                # Gérer la taille du cache
                if self.enable_caching:
                    self._manage_cache_size()
                
            except Exception as e:
                raise SmartMatchNLPError(f"Failed to compute embeddings: {str(e)}")
        
        # Convertir en array numpy
        embeddings_array = np.vstack(embeddings)
        
        return embeddings_array[0] if single_text else embeddings_array
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calcule la similarité sémantique entre deux textes.
        
        Args:
            text1: Premier texte
            text2: Deuxième texte
            
        Returns:
            Score de similarité entre 0 et 1
        """
        try:
            # Vérifications d'entrée
            if not text1 or not text2:
                return 0.0
            
            if not text1.strip() or not text2.strip():
                return 0.0
            
            # Correspondance exacte
            if text1.strip().lower() == text2.strip().lower():
                return 1.0
            
            # Calculer les embeddings
            embeddings = self.get_embeddings([text1, text2])
            
            # Calculer la similarité cosinus
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            
            # Normaliser entre 0 et 1
            similarity = max(0.0, min(1.0, similarity))
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculating text similarity: {str(e)}")
            return 0.0
    
    def calculate_skills_similarity(self, skills1: List[str], skills2: List[str]) -> float:
        """
        Calcule la similarité entre deux listes de compétences.
        
        Args:
            skills1: Première liste de compétences
            skills2: Deuxième liste de compétences
            
        Returns:
            Score de similarité entre 0 et 1
        """
        try:
            # Vérifications d'entrée
            if not skills1 or not skills2:
                return 0.0
            
            # Normaliser les compétences
            skills1_normalized = [s.strip().lower() for s in skills1 if s.strip()]
            skills2_normalized = [s.strip().lower() for s in skills2 if s.strip()]
            
            if not skills1_normalized or not skills2_normalized:
                return 0.0
            
            # Calculer les embeddings pour toutes les compétences
            all_skills = skills1_normalized + skills2_normalized
            embeddings = self.get_embeddings(all_skills)
            
            # Séparer les embeddings
            skills1_embeddings = embeddings[:len(skills1_normalized)]
            skills2_embeddings = embeddings[len(skills1_normalized):]
            
            # Calculer la matrice de similarité
            similarity_matrix = cosine_similarity(skills1_embeddings, skills2_embeddings)
            
            # Trouver les meilleures correspondances
            matches_count = 0
            total_skills = max(len(skills1_normalized), len(skills2_normalized))
            
            # Pour chaque compétence de skills1, trouver la meilleure correspondance dans skills2
            for i in range(len(skills1_normalized)):
                max_similarity = np.max(similarity_matrix[i])
                if max_similarity >= self.similarity_threshold:
                    matches_count += 1
            
            # Calculer le score final
            similarity_score = matches_count / total_skills
            
            return min(1.0, similarity_score)
            
        except Exception as e:
            logger.error(f"Error calculating skills similarity: {str(e)}")
            return 0.0
    
    def expand_skills_with_synonyms(self, skills: List[str]) -> List[str]:
        """
        Étend une liste de compétences en trouvant des synonymes sémantiques.
        
        Args:
            skills: Liste de compétences
            
        Returns:
            Liste de compétences étendue avec les synonymes
        """
        # Pour cette implémentation, nous retournons les compétences originales
        # car l'expansion par synonymes sémantiques nécessiterait une base de données
        # de compétences plus large
        return skills
    
    def normalize_text(self, text: str) -> str:
        """
        Normalise un texte pour l'analyse.
        
        Args:
            text: Texte à normaliser
            
        Returns:
            Texte normalisé
        """
        if not text:
            return ""
        
        # Normalisation de base
        normalized = text.strip().lower()
        
        # Supprimer les caractères spéciaux multiples
        import re
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized.strip()
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """
        Extrait des compétences depuis un texte libre.
        
        Args:
            text: Texte à analyser
            
        Returns:
            Liste de compétences identifiées
        """
        # Pour cette implémentation, nous utilisons une approche simple
        # basée sur des mots-clés. Une implémentation plus avancée pourrait
        # utiliser un modèle NER (Named Entity Recognition) spécialisé.
        
        if not text:
            return []
        
        # Mots-clés techniques courants
        tech_keywords = {
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node',
            'django', 'flask', 'spring', 'express', 'laravel', 'symfony',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins',
            'git', 'github', 'gitlab', 'ci/cd', 'devops', 'agile', 'scrum',
            'machine learning', 'deep learning', 'tensorflow', 'pytorch',
            'html', 'css', 'sass', 'bootstrap', 'tailwind', 'api', 'rest',
            'graphql', 'microservices', 'serverless', 'linux', 'bash'
        }
        
        normalized_text = self.normalize_text(text)
        words = normalized_text.split()
        
        identified_skills = []
        
        # Recherche de correspondances exactes
        for keyword in tech_keywords:
            if keyword in normalized_text:
                identified_skills.append(keyword)
        
        # Recherche de correspondances partielles pour les mots composés
        for word in words:
            if len(word) > 3:  # Ignorer les mots trop courts
                for keyword in tech_keywords:
                    if word in keyword or keyword in word:
                        if keyword not in identified_skills:
                            identified_skills.append(keyword)
        
        return identified_skills
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du cache.
        
        Returns:
            Dictionnaire avec les statistiques
        """
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0
        
        return {
            'cache_enabled': self.enable_caching,
            'cache_size': len(self.embeddings_cache),
            'max_cache_size': self.max_cache_size,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests
        }
    
    def clear_cache(self) -> None:
        """Vide le cache d'embeddings."""
        self.embeddings_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Embeddings cache cleared")
    
    def save_cache(self) -> None:
        """Sauvegarde le cache sur le disque."""
        self._save_cache_to_disk()
    
    def load_cache(self) -> None:
        """Charge le cache depuis le disque."""
        self._load_cache_from_disk()
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Retourne la configuration du service.
        
        Returns:
            Dictionnaire de configuration
        """
        return {
            'model_name': self.model_name,
            'device': self.device,
            'batch_size': self.batch_size,
            'similarity_threshold': self.similarity_threshold,
            'enable_caching': self.enable_caching,
            'max_cache_size': self.max_cache_size,
            'cache_dir': str(self.cache_dir),
            'model_loaded': self.model is not None,
            'embedding_dimension': self.model.get_sentence_embedding_dimension() if self.model else None,
            'sentence_transformers_available': SENTENCE_TRANSFORMERS_AVAILABLE
        }
    
    def __enter__(self):
        """Support du context manager."""
        self.load_cache()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Support du context manager - sauvegarde du cache."""
        self.save_cache()
