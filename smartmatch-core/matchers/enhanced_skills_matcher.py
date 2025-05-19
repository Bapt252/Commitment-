"""
Enhanced Skills Matcher Implementation with Vector Embeddings
============================================================
Matcher spécialisé pour l'évaluation sémantique des compétences utilisant
des embeddings vectoriels pour un matching de haute qualité.

Combine l'ancien système TF-IDF avec les nouveaux embeddings vectoriels
pour un matching progressif et une compatibilité ascendante.
"""

import logging
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from enum import Enum

from .base_matcher import AbstractBaseMatcher
from ..core.models import Candidate, Job, MatchInsight
from ..core.interfaces import NLPService
from ..services.embeddings_service import EmbeddingsService
from ..services.skills_embeddings_db import SkillsEmbeddingsDB

# Import optionnel pour la compatibilité
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


class MatchingMode(Enum):
    """Modes de matching disponibles."""
    TFIDF_ONLY = "tfidf_only"           # Ancien système TF-IDF uniquement
    EMBEDDINGS_ONLY = "embeddings_only" # Nouveaux embeddings uniquement
    HYBRID = "hybrid"                    # Combinaison des deux (recommandé)
    AB_TESTING = "ab_testing"           # Test A/B entre les deux approches


class EnhancedSkillsMatcher(AbstractBaseMatcher):
    """
    Matcher de compétences amélioré avec support des embeddings vectoriels.
    
    Fonctionnalités principales:
    - Matching sémantique via embeddings vectoriels
    - Fallback vers TF-IDF pour la compatibilité
    - Mode hybride combinant les deux approches
    - A/B testing intégré pour comparer les performances
    - Métriques détaillées pour évaluation continue
    """
    
    def __init__(self, 
                 nlp_service: Optional[NLPService] = None,
                 embeddings_service: Optional[EmbeddingsService] = None,
                 skills_db: Optional[SkillsEmbeddingsDB] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialise le matcher de compétences amélioré.
        
        Args:
            nlp_service: Service NLP legacy (pour compatibilité)
            embeddings_service: Service d'embeddings vectoriels
            skills_db: Base de données vectorielle des compétences
            config: Configuration spécifique
        """
        super().__init__(config)
        
        # Services
        self.nlp_service = nlp_service
        self.embeddings_service = embeddings_service
        self.skills_db = skills_db
        
        # Configuration spécifique
        self.matching_mode = MatchingMode(
            self.config.get('matching_mode', MatchingMode.HYBRID.value)
        )
        self.embeddings_weight = self.config.get('embeddings_weight', 0.7)
        self.tfidf_weight = self.config.get('tfidf_weight', 0.3)
        self.semantic_threshold = self.config.get('semantic_threshold', 0.75)
        self.enable_skills_expansion = self.config.get('enable_skills_expansion', True)
        self.max_expanded_skills = self.config.get('max_expanded_skills', 5)
        self.ab_testing_ratio = self.config.get('ab_testing_ratio', 0.5)
        
        # Héritage de l'ancienne configuration
        self.essential_skill_bonus = self.config.get('essential_skill_bonus', 1.5)
        self.nice_to_have_factor = self.config.get('nice_to_have_factor', 0.7)
        self.synonym_threshold = self.config.get('synonym_threshold', 0.85)
        
        # État interne et métriques
        self.tfidf_vectorizer = None
        self.skill_synonyms = self._build_skill_synonyms_dict()
        
        # Métriques de performance
        self.matching_stats = {
            'tfidf_matches': 0,
            'embeddings_matches': 0,
            'hybrid_matches': 0,
            'total_time_tfidf': 0.0,
            'total_time_embeddings': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Initialisation des composants
        self._initialize_components()
        
        logger.info(f"EnhancedSkillsMatcher initialized with mode: {self.matching_mode.value}")
    
    def _get_default_weight(self) -> float:
        """Retourne le poids par défaut pour le matcher de compétences."""
        return 0.40  # 40% du score total
    
    def _initialize_components(self) -> None:
        """Initialise les composants selon le mode de matching."""
        if self.matching_mode in [MatchingMode.TFIDF_ONLY, MatchingMode.HYBRID, MatchingMode.AB_TESTING]:
            if SKLEARN_AVAILABLE:
                self.tfidf_vectorizer = TfidfVectorizer(
                    lowercase=True,
                    stop_words=None,
                    ngram_range=(1, 2),
                    max_features=5000
                )
            else:
                logger.warning("scikit-learn not available, TF-IDF matching disabled")
        
        # Initialisation automatique des services d'embeddings si pas fournis
        if (self.matching_mode in [MatchingMode.EMBEDDINGS_ONLY, MatchingMode.HYBRID, MatchingMode.AB_TESTING] 
            and not self.embeddings_service):
            try:
                self.embeddings_service = EmbeddingsService()
                if not self.skills_db:
                    self.skills_db = SkillsEmbeddingsDB(self.embeddings_service)
                logger.info("Auto-initialized embeddings service and skills database")
            except Exception as e:
                logger.warning(f"Failed to auto-initialize embeddings service: {e}")
    
    async def _calculate_specific_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score de correspondance des compétences selon le mode configuré.
        
        Args:
            candidate: Le candidat à évaluer
            job: L'offre d'emploi à évaluer
            
        Returns:
            Score entre 0 et 1
        """
        if self.matching_mode == MatchingMode.TFIDF_ONLY:
            return await self._calculate_tfidf_score(candidate, job)
        elif self.matching_mode == MatchingMode.EMBEDDINGS_ONLY:
            return await self._calculate_embeddings_score(candidate, job)
        elif self.matching_mode == MatchingMode.HYBRID:
            return await self._calculate_hybrid_score(candidate, job)
        elif self.matching_mode == MatchingMode.AB_TESTING:
            return await self._calculate_ab_testing_score(candidate, job)
        else:
            logger.warning(f"Unknown matching mode: {self.matching_mode}")
            return await self._calculate_hybrid_score(candidate, job)
    
    async def _calculate_tfidf_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score avec l'ancienne méthode TF-IDF.
        
        Args:
            candidate: Le candidat à évaluer
            job: L'offre d'emploi à évaluer
            
        Returns:
            Score entre 0 et 1
        """
        start_time = time.time()
        
        try:
            # Utiliser l'ancienne méthode comme fallback
            score = await self._calculate_legacy_score(candidate, job)
            
            # Mise à jour des métriques
            self.matching_stats['tfidf_matches'] += 1
            self.matching_stats['total_time_tfidf'] += time.time() - start_time
            
            return score
            
        except Exception as e:
            logger.error(f"Error in TF-IDF scoring: {e}")
            return 0.5
    
    async def _calculate_embeddings_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score avec les embeddings vectoriels.
        
        Args:
            candidate: Le candidat à évaluer
            job: L'offre d'emploi à évaluer
            
        Returns:
            Score entre 0 et 1
        """
        start_time = time.time()
        
        try:
            if not self.embeddings_service or not self.skills_db:
                logger.warning("Embeddings service or skills DB not available, falling back to TF-IDF")
                return await self._calculate_tfidf_score(candidate, job)
            
            # Extraire et normaliser les compétences
            candidate_skills = self._extract_and_normalize_skills(candidate)
            required_skills = self._normalize_skills(job.required_skills)
            preferred_skills = self._normalize_skills(job.preferred_skills)
            
            if not candidate_skills:
                return 0.5
            
            if not required_skills and not preferred_skills:
                return 0.5
            
            # Expansion sémantique des compétences du candidat
            if self.enable_skills_expansion:
                candidate_skills = await self._expand_skills_semantically(candidate_skills)
            
            # Calculer les correspondances sémantiques
            required_matches = await self._calculate_semantic_matches(
                candidate_skills, required_skills
            )
            preferred_matches = await self._calculate_semantic_matches(
                candidate_skills, preferred_skills
            )
            
            # Calculer les scores
            required_score = len(required_matches) / len(required_skills) if required_skills else 0
            preferred_score = len(preferred_matches) / len(preferred_skills) if preferred_skills else 0
            
            # Pondération finale
            if required_skills and preferred_skills:
                total_score = (required_score * 0.7) + (preferred_score * 0.3)
            elif required_skills:
                total_score = required_score
            else:
                total_score = preferred_score
            
            # Bonus pour couverture élevée
            total_skills = len(required_skills) + len(preferred_skills)
            total_matches = len(required_matches) + len(preferred_matches)
            coverage_ratio = total_matches / total_skills if total_skills > 0 else 0
            
            if coverage_ratio >= 0.8:
                total_score = min(1.0, total_score * 1.15)  # 15% de bonus
            elif coverage_ratio >= 0.6:
                total_score = min(1.0, total_score * 1.08)  # 8% de bonus
            
            # Mise à jour des métriques
            self.matching_stats['embeddings_matches'] += 1
            self.matching_stats['total_time_embeddings'] += time.time() - start_time
            
            return total_score
            
        except Exception as e:
            logger.error(f"Error in embeddings scoring: {e}")
            return await self._calculate_tfidf_score(candidate, job)
    
    async def _calculate_hybrid_score(self, candidate: Candidate, job: Job) -> float:
        """
        Calcule le score en combinant TF-IDF et embeddings.
        
        Args:
            candidate: Le candidat à évaluer
            job: L'offre d'emploi à évaluer
            
        Returns:
            Score entre 0 et 1
        """
        try:
            # Calculer les deux scores
            tfidf_score = await self._calculate_tfidf_score(candidate, job)
            embeddings_score = await self._calculate_embeddings_score(candidate, job)
            
            # Combiner avec pondération
            hybrid_score = (
                (tfidf_score * self.tfidf_weight) + 
                (embeddings_score * self.embeddings_weight)
            )
            
            self.matching_stats['hybrid_matches'] += 1
            
            return hybrid_score
            
        except Exception as e:
            logger.error(f"Error in hybrid scoring: {e}")
            return 0.5
    
    async def _calculate_ab_testing_score(self, candidate: Candidate, job: Job) -> float:
        """
        Effectue un test A/B entre TF-IDF et embeddings.
        
        Args:
            candidate: Le candidat à évaluer
            job: L'offre d'emploi à évaluer
            
        Returns:
            Score entre 0 et 1
        """
        # Déterminant quelle méthode utiliser basé sur l'ID
        import hashlib
        hash_key = f"{candidate.id}_{job.id}"
        hash_value = int(hashlib.md5(hash_key.encode()).hexdigest(), 16)
        use_embeddings = (hash_value % 100) < (self.ab_testing_ratio * 100)
        
        if use_embeddings and self.embeddings_service:
            return await self._calculate_embeddings_score(candidate, job)
        else:
            return await self._calculate_tfidf_score(candidate, job)
    
    async def _calculate_legacy_score(self, candidate: Candidate, job: Job) -> float:
        """Implémentation legacy de l'ancien SkillsMatcher."""
        # Exactement la même logique que l'ancien matcher
        candidate_skills = self._extract_and_normalize_skills(candidate)
        required_skills = self._normalize_skills(job.required_skills)
        preferred_skills = self._normalize_skills(job.preferred_skills)
        
        if not candidate_skills:
            return 0.5
        
        if not required_skills and not preferred_skills:
            return 0.5
        
        # Calculer les correspondances avec la méthode legacy
        required_matches = await self._find_skill_matches_legacy(candidate_skills, required_skills)
        preferred_matches = await self._find_skill_matches_legacy(candidate_skills, preferred_skills)
        
        required_score = len(required_matches) / len(required_skills) if required_skills else 0
        preferred_score = len(preferred_matches) / len(preferred_skills) if preferred_skills else 0
        
        if required_skills and preferred_skills:
            total_score = (required_score * 0.7) + (preferred_score * 0.3)
        elif required_skills:
            total_score = required_score
        else:
            total_score = preferred_score
        
        # Bonus pour couverture
        total_skills = len(required_skills) + len(preferred_skills)
        total_matches = len(required_matches) + len(preferred_matches)
        coverage_ratio = total_matches / total_skills if total_skills > 0 else 0
        
        if coverage_ratio >= 0.8:
            total_score = min(1.0, total_score * 1.1)
        elif coverage_ratio >= 0.6:
            total_score = min(1.0, total_score * 1.05)
        
        return total_score
    
    async def _expand_skills_semantically(self, skills: List[str]) -> List[str]:
        """
        Étend sémantiquement les compétences en trouvant des compétences similaires.
        
        Args:
            skills: Compétences de base
            
        Returns:
            Compétences étendues avec synonymes sémantiques
        """
        if not self.skills_db or not self.enable_skills_expansion:
            return skills
        
        expanded_skills = skills.copy()
        
        try:
            for skill in skills:
                similar_skills = self.skills_db.search_similar_skills(
                    skill, 
                    threshold=self.semantic_threshold,
                    max_results=3
                )
                
                # Ajouter les compétences similaires trouvées
                for similar_skill, similarity in similar_skills:
                    if similar_skill not in expanded_skills:
                        expanded_skills.append(similar_skill)
                        
                        # Limiter le nombre total de compétences
                        if len(expanded_skills) >= len(skills) + self.max_expanded_skills:
                            break
                
                if len(expanded_skills) >= len(skills) + self.max_expanded_skills:
                    break
            
            logger.debug(f"Expanded {len(skills)} skills to {len(expanded_skills)}")
            return expanded_skills
            
        except Exception as e:
            logger.warning(f"Error in semantic expansion: {e}")
            return skills
    
    async def _calculate_semantic_matches(self, candidate_skills: List[str], 
                                        target_skills: List[str]) -> List[str]:
        """
        Calcule les correspondances sémantiques entre compétences.
        
        Args:
            candidate_skills: Compétences du candidat
            target_skills: Compétences cibles
            
        Returns:
            Liste des compétences correspondantes
        """
        matches = []
        
        if not self.embeddings_service:
            # Fallback vers l'ancienne méthode
            return await self._find_skill_matches_legacy(candidate_skills, target_skills)
        
        try:
            for target_skill in target_skills:
                # Chercher dans la base de données vectorielle d'abord
                if self.skills_db:
                    db_matches = self.skills_db.search_similar_skills(
                        target_skill,
                        threshold=self.semantic_threshold,
                        max_results=5
                    )
                    
                    # Vérifier si les compétences du candidat correspondent
                    for candidate_skill in candidate_skills:
                        for db_skill, similarity in db_matches:
                            if (candidate_skill == db_skill or 
                                self._is_skill_similar(candidate_skill, db_skill)):
                                matches.append(target_skill)
                                break
                        else:
                            continue
                        break
                    else:
                        # Calcul direct de similarité si pas trouvé dans la DB
                        for candidate_skill in candidate_skills:
                            similarity = self.embeddings_service.calculate_text_similarity(
                                target_skill, candidate_skill
                            )
                            if similarity >= self.semantic_threshold:
                                matches.append(target_skill)
                                break
                else:
                    # Calcul direct sans base de données
                    for candidate_skill in candidate_skills:
                        similarity = self.embeddings_service.calculate_text_similarity(
                            target_skill, candidate_skill
                        )
                        if similarity >= self.semantic_threshold:
                            matches.append(target_skill)
                            break
            
            return matches
            
        except Exception as e:
            logger.error(f"Error in semantic matching: {e}")
            return await self._find_skill_matches_legacy(candidate_skills, target_skills)
    
    async def _find_skill_matches_legacy(self, candidate_skills: List[str], 
                                       target_skills: List[str]) -> List[str]:
        """Méthode legacy de correspondance des compétences."""
        matches = []
        
        for target_skill in target_skills:
            # Correspondance exacte
            if target_skill in candidate_skills:
                matches.append(target_skill)
                continue
            
            # Correspondance par synonymes
            if self._find_synonym_match(target_skill, candidate_skills):
                matches.append(target_skill)
                continue
            
            # Correspondance sémantique via NLP legacy si disponible
            if self.nlp_service:
                try:
                    for candidate_skill in candidate_skills:
                        similarity = self.nlp_service.calculate_text_similarity(
                            target_skill, candidate_skill
                        )
                        if similarity >= self.synonym_threshold:
                            matches.append(target_skill)
                            break
                except Exception as e:
                    logger.warning(f"Legacy NLP matching failed: {e}")
        
        return matches
    
    def _is_skill_similar(self, skill1: str, skill2: str) -> bool:
        """Vérifie si deux compétences sont similaires avec des règles simples."""
        # Normaliser
        s1 = skill1.lower().strip()
        s2 = skill2.lower().strip()
        
        # Correspondance exacte
        if s1 == s2:
            return True
        
        # Correspondance partielle pour mots courts
        if len(s1) >= 3 and len(s2) >= 3:
            if s1 in s2 or s2 in s1:
                return True
        
        # Vérifier les synonymes
        return self._find_synonym_match(skill1, [skill2])
    
    def _generate_specific_insights(self, candidate: Candidate, job: Job, 
                                  score: float) -> List[MatchInsight]:
        """
        Génère des insights spécifiques incluant les informations d'embeddings.
        
        Args:
            candidate: Le candidat évalué
            job: L'offre d'emploi évaluée
            score: Le score calculé
            
        Returns:
            Liste d'insights enrichis
        """
        insights = []
        
        try:
            candidate_skills = self._extract_and_normalize_skills(candidate)
            required_skills = self._normalize_skills(job.required_skills)
            preferred_skills = self._normalize_skills(job.preferred_skills)
            
            # Insights standard (hérités)
            standard_insights = self._generate_legacy_insights(
                candidate, job, score, candidate_skills, required_skills, preferred_skills
            )
            insights.extend(standard_insights)
            
            # Insights spécifiques aux embeddings
            if self.embeddings_service and self.matching_mode != MatchingMode.TFIDF_ONLY:
                embeddings_insights = await self._generate_embeddings_insights(
                    candidate_skills, required_skills, preferred_skills
                )
                insights.extend(embeddings_insights)
            
            # Insights sur les métriques de performance
            performance_insights = self._generate_performance_insights()
            insights.extend(performance_insights)
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            insights.append(MatchInsight(
                type='error',
                category='skills',
                message="Erreur lors de l'analyse avancée des compétences",
                priority=1
            ))
        
        return insights
    
    def _generate_legacy_insights(self, candidate: Candidate, job: Job, score: float,
                                candidate_skills: List[str], required_skills: List[str],
                                preferred_skills: List[str]) -> List[MatchInsight]:
        """Génère les insights classiques."""
        insights = []
        
        # Analyse des compétences manquantes et présentes
        missing_required = self._find_missing_skills(candidate_skills, required_skills)
        missing_preferred = self._find_missing_skills(candidate_skills, preferred_skills)
        common_required = self._find_common_skills(candidate_skills, required_skills)
        common_preferred = self._find_common_skills(candidate_skills, preferred_skills)
        
        if missing_required:
            insights.append(MatchInsight(
                type='weakness',
                category='skills',
                message=f"Compétences requises manquantes: {', '.join(missing_required[:3])}",
                priority=3
            ))
        
        if common_required:
            insights.append(MatchInsight(
                type='strength',
                category='skills',
                message=f"Compétences requises maîtrisées: {', '.join(common_required[:3])}",
                priority=3
            ))
        
        if common_preferred:
            insights.append(MatchInsight(
                type='strength',
                category='skills',
                message=f"Compétences préférées présentes: {', '.join(common_preferred[:2])}",
                priority=2
            ))
        
        # Couverture globale
        total_skills = len(required_skills) + len(preferred_skills)
        matched_skills = len(common_required) + len(common_preferred)
        
        if total_skills > 0:
            coverage = matched_skills / total_skills
            if coverage >= 0.8:
                insights.append(MatchInsight(
                    type='strength',
                    category='skills',
                    message=f"Excellente couverture des compétences ({coverage:.0%})",
                    priority=3
                ))
            elif coverage <= 0.3:
                insights.append(MatchInsight(
                    type='weakness',
                    category='skills',
                    message=f"Couverture insuffisante des compétences ({coverage:.0%})",
                    priority=3
                ))
        
        return insights
    
    async def _generate_embeddings_insights(self, candidate_skills: List[str],
                                          required_skills: List[str],
                                          preferred_skills: List[str]) -> List[MatchInsight]:
        """Génère des insights spécifiques aux embeddings."""
        insights = []
        
        try:
            # Insights sur les correspondances sémantiques
            if self.skills_db:
                semantic_matches = 0
                for skill in candidate_skills:
                    db_matches = self.skills_db.search_similar_skills(skill, max_results=1)
                    if db_matches:
                        semantic_matches += 1
                
                coverage_ratio = semantic_matches / len(candidate_skills) if candidate_skills else 0
                
                if coverage_ratio >= 0.7:
                    insights.append(MatchInsight(
                        type='strength',
                        category='skills_semantic',
                        message=f"Compétences reconnues sémantiquement ({coverage_ratio:.0%})",
                        priority=2
                    ))
            
            # Insights sur l'expansion sémantique
            if self.enable_skills_expansion:
                expanded_skills = await self._expand_skills_semantically(candidate_skills)
                expansion_ratio = len(expanded_skills) / len(candidate_skills) if candidate_skills else 0
                
                if expansion_ratio > 1.2:  # Au moins 20% d'expansion
                    insights.append(MatchInsight(
                        type='neutral',
                        category='skills_semantic',
                        message=f"Compétences étendues sémantiquement (+{len(expanded_skills) - len(candidate_skills)})",
                        priority=1
                    ))
            
        except Exception as e:
            logger.warning(f"Error generating embeddings insights: {e}")
        
        return insights
    
    def _generate_performance_insights(self) -> List[MatchInsight]:
        """Génère des insights sur les performances du matching."""
        insights = []
        
        # Insight sur le mode de matching utilisé
        mode_message = {
            MatchingMode.TFIDF_ONLY: "Matching classique TF-IDF",
            MatchingMode.EMBEDDINGS_ONLY: "Matching sémantique par embeddings",
            MatchingMode.HYBRID: "Matching hybride (TF-IDF + embeddings)",
            MatchingMode.AB_TESTING: "Mode test A/B actif"
        }
        
        insights.append(MatchInsight(
            type='neutral',
            category='matching_mode',
            message=mode_message.get(self.matching_mode, "Mode de matching inconnu"),
            priority=1
        ))
        
        return insights
    
    # Méthodes utilitaires héritées de l'ancien matcher
    def _extract_and_normalize_skills(self, candidate: Candidate) -> List[str]:
        """Extrait et normalise toutes les compétences d'un candidat."""
        skills = []
        
        if candidate.skills:
            skills.extend(candidate.skills)
        
        if self.nlp_service:
            try:
                if candidate.summary:
                    extracted = self.nlp_service.extract_skills_from_text(candidate.summary)
                    skills.extend(extracted)
                
                if candidate.experience_description:
                    extracted = self.nlp_service.extract_skills_from_text(candidate.experience_description)
                    skills.extend(extracted)
            except Exception as e:
                logger.warning(f"Failed to extract skills via NLP: {e}")
        
        return self._normalize_skills(skills)
    
    def _normalize_skills(self, skills: List[str]) -> List[str]:
        """Normalise une liste de compétences."""
        if not skills:
            return []
        
        normalized = []
        seen = set()
        
        for skill in skills:
            if not skill or not skill.strip():
                continue
            
            normalized_skill = skill.strip().lower()
            normalized_skill = ''.join(c for c in normalized_skill if c.isalnum() or c.isspace())
            normalized_skill = ' '.join(normalized_skill.split())
            
            if normalized_skill and normalized_skill not in seen:
                normalized.append(normalized_skill)
                seen.add(normalized_skill)
        
        return normalized
    
    def _find_missing_skills(self, candidate_skills: List[str], 
                           target_skills: List[str]) -> List[str]:
        """Trouve les compétences cibles que le candidat n'a pas."""
        missing = []
        
        for target_skill in target_skills:
            if target_skill in candidate_skills:
                continue
            
            if self._find_synonym_match(target_skill, candidate_skills):
                continue
            
            missing.append(target_skill)
        
        return missing
    
    def _find_common_skills(self, candidate_skills: List[str], 
                          target_skills: List[str]) -> List[str]:
        """Trouve les compétences communes."""
        common = []
        
        for target_skill in target_skills:
            if target_skill in candidate_skills:
                common.append(target_skill)
                continue
            
            if self._find_synonym_match(target_skill, candidate_skills):
                common.append(target_skill)
        
        return common
    
    def _find_synonym_match(self, target_skill: str, candidate_skills: List[str]) -> bool:
        """Vérifie s'il y a une correspondance par synonymes."""
        for skill_group, synonyms in self.skill_synonyms.items():
            if target_skill == skill_group or target_skill in synonyms:
                for candidate_skill in candidate_skills:
                    if (candidate_skill == skill_group or 
                        candidate_skill in synonyms or
                        any(syn in candidate_skill for syn in synonyms) or
                        any(candidate_skill in syn for syn in synonyms)):
                        return True
        
        for candidate_skill in candidate_skills:
            if (target_skill in candidate_skill or 
                candidate_skill in target_skill):
                if len(target_skill) >= 3 and len(candidate_skill) >= 3:
                    return True
        
        return False
    
    def _build_skill_synonyms_dict(self) -> Dict[str, List[str]]:
        """Construit le dictionnaire de synonymes (identique à l'ancien)."""
        return {
            "javascript": [
                "js", "ecmascript", "node.js", "nodejs", "react.js", "reactjs", 
                "vue.js", "vuejs", "angular", "jquery", "typescript", "ts"
            ],
            "python": [
                "py", "python3", "django", "flask", "fastapi", "pandas", 
                "numpy", "scipy", "pytorch", "tensorflow", "scikit-learn"
            ],
            "java": [
                "spring", "hibernate", "j2ee", "javase", "javaee", "spring boot",
                "maven", "gradle", "junit", "jpa", "jsp", "servlet"
            ],
            "php": [
                "laravel", "symfony", "wordpress", "drupal", "codeigniter",
                "zend", "cake php", "yii", "composer"
            ],
            "c#": [
                "csharp", ".net", "dotnet", "asp.net", "aspnet", "mvc", 
                "entity framework", "wpf", "xamarin", "unity"
            ],
            "c++": [
                "cpp", "cplusplus", "c plus plus", "stl", "boost", "qt"
            ],
            "ruby": [
                "ror", "rails", "ruby on rails", "sinatra", "gem", "bundler"
            ],
            "go": [
                "golang", "go lang"
            ],
            "rust": [
                "rust lang", "cargo"
            ],
            "machine learning": [
                "ml", "ai", "artificial intelligence", "deep learning", 
                "neural networks", "tensorflow", "pytorch", "keras", "scikit-learn",
                "nlp", "computer vision", "data science"
            ],
            "devops": [
                "ci/cd", "continuous integration", "continuous deployment", 
                "docker", "kubernetes", "k8s", "jenkins", "gitlab ci", "github actions",
                "terraform", "ansible", "chef", "puppet", "aws", "azure", "gcp"
            ],
            "frontend": [
                "front-end", "ui", "user interface", "ux", "user experience",
                "html", "css", "sass", "less", "responsive design", "bootstrap",
                "tailwind", "material ui", "chakra ui"
            ],
            "backend": [
                "back-end", "server-side", "api", "rest api", "graphql", 
                "middleware", "microservices", "serverless"
            ],
            "fullstack": [
                "full-stack", "full stack", "frontend and backend", 
                "front-end and back-end", "isomorphic", "universal"
            ],
            "database": [
                "sql", "mysql", "postgresql", "postgres", "sqlite", "oracle",
                "mongodb", "redis", "elasticsearch", "cassandra", "dynamodb",
                "nosql", "acid", "oltp", "olap", "etl"
            ],
            "cloud": [
                "aws", "amazon web services", "azure", "microsoft azure",
                "gcp", "google cloud platform", "cloud computing", "saas",
                "paas", "iaas", "serverless", "lambda", "ec2", "s3"
            ]
        }
    
    def get_configuration(self) -> Dict[str, Any]:
        """Retourne la configuration étendue du matcher."""
        config = super().get_configuration()
        config.update({
            'matching_mode': self.matching_mode.value,
            'embeddings_weight': self.embeddings_weight,
            'tfidf_weight': self.tfidf_weight,
            'semantic_threshold': self.semantic_threshold,
            'enable_skills_expansion': self.enable_skills_expansion,
            'max_expanded_skills': self.max_expanded_skills,
            'has_embeddings_service': self.embeddings_service is not None,
            'has_skills_db': self.skills_db is not None,
            'has_nlp_service': self.nlp_service is not None,
            'synonym_groups_count': len(self.skill_synonyms),
            'matching_stats': self.matching_stats.copy()
        })
        return config
    
    def get_matching_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques détaillées de matching."""
        stats = self.matching_stats.copy()
        
        # Calculer les moyennes
        total_matches = (stats['tfidf_matches'] + stats['embeddings_matches'] + 
                        stats['hybrid_matches'])
        
        if total_matches > 0:
            stats['avg_time_tfidf_ms'] = (stats['total_time_tfidf'] / 
                                         max(1, stats['tfidf_matches'])) * 1000
            stats['avg_time_embeddings_ms'] = (stats['total_time_embeddings'] / 
                                               max(1, stats['embeddings_matches'])) * 1000
        else:
            stats['avg_time_tfidf_ms'] = 0
            stats['avg_time_embeddings_ms'] = 0
        
        stats['total_matches'] = total_matches
        
        # Ajouter les stats des sous-services
        if self.embeddings_service:
            stats['embeddings_cache_stats'] = self.embeddings_service.get_cache_stats()
        
        if self.skills_db:
            stats['skills_db_stats'] = self.skills_db.get_stats()
        
        return stats
    
    def reset_stats(self) -> None:
        """Remet à zéro les statistiques de matching."""
        self.matching_stats = {
            'tfidf_matches': 0,
            'embeddings_matches': 0,
            'hybrid_matches': 0,
            'total_time_tfidf': 0.0,
            'total_time_embeddings': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        logger.info("Matching statistics reset")
