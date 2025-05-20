#!/usr/bin/env python3
"""
Session 6: Bidirectional Matcher with Stable Marriage Algorithm
==============================================================

Implémentation du matching bidirectionnel inspiré du Stable Marriage Problem.
Équilibre les préférences des candidats ET des jobs pour un matching optimal.

🔥 Fonctionnalités:
- Stable Marriage Algorithm adapté pour CV ↔ Jobs
- Gestion des préférences bidirectionnelles
- Priorisation par score et contraintes
- Support pour matching partiel et multiples assignments
- Intégration avec le système de contraintes

Architecture:
- BidirectionalMatcher: Classe principale
- PreferenceCalculator: Calcul des préférences
- StabilityChecker: Vérification de la stabilité
- MatchingResult: Résultat détaillé du matching
"""

import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import time

# Configuration du logging
logger = logging.getLogger(__name__)

class MatchingStrategy(Enum):
    """Stratégies de matching disponibles."""
    CANDIDATE_OPTIMAL = "candidate_optimal"  # Favorise les candidats
    EMPLOYER_OPTIMAL = "employer_optimal"    # Favorise les employeurs
    BALANCED = "balanced"                    # Équilibré

class StabilityLevel(Enum):
    """Niveaux de stabilité du matching."""
    STABLE = "stable"        # Matching stable
    WEAK_STABLE = "weak_stable"  # Faiblement stable
    UNSTABLE = "unstable"    # Instable

@dataclass
class Preference:
    """Préférence d'un acteur pour un autre."""
    actor_id: str
    target_id: str
    score: float
    rank: int
    reasons: List[str] = field(default_factory=list)

@dataclass
class MatchPair:
    """Paire de matching résultante."""
    candidate_id: str
    job_id: str
    candidate_score: float  # Score du job pour le candidat
    job_score: float       # Score du candidat pour le job
    stability_score: float # Score de stabilité
    constraint_violations: List[str] = field(default_factory=list)
    
    @property
    def mutual_score(self) -> float:
        """Score mutuel (moyenne harmonique)."""
        if self.candidate_score == 0 or self.job_score == 0:
            return 0.0
        return 2 * (self.candidate_score * self.job_score) / (self.candidate_score + self.job_score)

@dataclass
class MatchingResult:
    """Résultat complet du matching bidirectionnel."""
    matches: List[MatchPair]
    unmatched_candidates: List[str]
    unmatched_jobs: List[str]
    stability_level: StabilityLevel
    total_score: float
    execution_time: float
    statistics: Dict[str, Any] = field(default_factory=dict)

class PreferenceCalculator:
    """Calculateur de préférences pour le matching bidirectionnel."""
    
    def __init__(self, cost_matrix_generator=None):
        self.cost_matrix_generator = cost_matrix_generator
        self.preference_cache = {}
        
    def calculate_candidate_preferences(self, 
                                      candidates: List[Any], 
                                      jobs: List[Any],
                                      cost_matrix: Optional[np.ndarray] = None) -> Dict[str, List[Preference]]:
        """
        Calcule les préférences des candidats pour les jobs.
        
        Args:
            candidates: Liste des candidats
            jobs: Liste des jobs
            cost_matrix: Matrice de coûts (optionnelle)
            
        Returns:
            Dict mapping candidate_id -> sorted preferences
        """
        preferences = {}
        
        # Génération de la matrice de coûts si nécessaire
        if cost_matrix is None and self.cost_matrix_generator:
            cost_matrix = self.cost_matrix_generator.generate_matrix(candidates, jobs)
        elif cost_matrix is None:
            # Matrice par défaut basée sur des scores aléatoires
            cost_matrix = np.random.rand(len(candidates), len(jobs))
        
        for i, candidate in enumerate(candidates):
            candidate_id = getattr(candidate, 'id', str(i))
            candidate_prefs = []
            
            for j, job in enumerate(jobs):
                job_id = getattr(job, 'id', str(j))
                
                # Convertir coût en score (1 - coût normalisé)
                cost = cost_matrix[i, j]
                max_cost = np.max(cost_matrix)
                score = 1.0 - (cost / max_cost) if max_cost > 0 else 1.0
                
                # Création de la préférence
                preference = Preference(
                    actor_id=candidate_id,
                    target_id=job_id,
                    score=score,
                    rank=0,  # Sera calculé après tri
                    reasons=self._get_preference_reasons(candidate, job, score)
                )
                candidate_prefs.append(preference)
            
            # Tri par score décroissant et assignation des rangs
            candidate_prefs.sort(key=lambda p: p.score, reverse=True)
            for rank, pref in enumerate(candidate_prefs):
                pref.rank = rank + 1
            
            preferences[candidate_id] = candidate_prefs
            
        return preferences
    
    def calculate_job_preferences(self, 
                                 candidates: List[Any], 
                                 jobs: List[Any],
                                 cost_matrix: Optional[np.ndarray] = None) -> Dict[str, List[Preference]]:
        """
        Calcule les préférences des jobs pour les candidats.
        
        Args:
            candidates: Liste des candidats
            jobs: Liste des jobs
            cost_matrix: Matrice de coûts (optionnelle)
            
        Returns:
            Dict mapping job_id -> sorted preferences
        """
        preferences = {}
        
        # Génération de la matrice de coûts si nécessaire
        if cost_matrix is None and self.cost_matrix_generator:
            cost_matrix = self.cost_matrix_generator.generate_matrix(candidates, jobs)
        elif cost_matrix is None:
            # Matrice par défaut basée sur des scores aléatoires
            cost_matrix = np.random.rand(len(candidates), len(jobs))
        
        for j, job in enumerate(jobs):
            job_id = getattr(job, 'id', str(j))
            job_prefs = []
            
            for i, candidate in enumerate(candidates):
                candidate_id = getattr(candidate, 'id', str(i))
                
                # Convertir coût en score (1 - coût normalisé)
                cost = cost_matrix[i, j]
                max_cost = np.max(cost_matrix)
                score = 1.0 - (cost / max_cost) if max_cost > 0 else 1.0
                
                # Bonus pour Job si candidat surqualifié (inversement proportionnel au coût)
                score = self._apply_job_preference_bias(candidate, job, score)
                
                # Création de la préférence
                preference = Preference(
                    actor_id=job_id,
                    target_id=candidate_id,
                    score=score,
                    rank=0,  # Sera calculé après tri
                    reasons=self._get_preference_reasons(job, candidate, score)
                )
                job_prefs.append(preference)
            
            # Tri par score décroissant et assignation des rangs
            job_prefs.sort(key=lambda p: p.score, reverse=True)
            for rank, pref in enumerate(job_prefs):
                pref.rank = rank + 1
            
            preferences[job_id] = job_prefs
            
        return preferences
    
    def _get_preference_reasons(self, actor: Any, target: Any, score: float) -> List[str]:
        """Génère des raisons pour une préférence."""
        reasons = []
        
        if score > 0.8:
            reasons.append("Excellent match")
        elif score > 0.6:
            reasons.append("Good compatibility")
        elif score > 0.4:
            reasons.append("Moderate fit")
        else:
            reasons.append("Low compatibility")
            
        # Ajout de raisons spécifiques si possible
        if hasattr(actor, 'skills') and hasattr(target, 'required_skills'):
            skill_overlap = set(getattr(actor, 'skills', [])) & set(getattr(target, 'required_skills', []))
            if skill_overlap:
                reasons.append(f"Skills match: {len(skill_overlap)} skills")
        
        return reasons
    
    def _apply_job_preference_bias(self, candidate: Any, job: Any, base_score: float) -> float:
        """Applique un biais de préférence du côté job."""
        # Les jobs préfèrent généralement des candidats avec plus d'expérience
        if hasattr(candidate, 'experience_years') and hasattr(job, 'min_experience'):
            candidate_exp = candidate.experience_years
            min_exp = job.min_experience
            
            if candidate_exp > min_exp * 1.5:  # Surqualifié
                return min(base_score * 1.1, 1.0)  # Léger bonus
            elif candidate_exp < min_exp:  # Sous-qualifié
                return base_score * 0.9  # Légère pénalité
        
        return base_score

class StabilityChecker:
    """Vérificateur de stabilité des matchings."""
    
    def __init__(self):
        self.blocking_pairs = []
        
    def check_stability(self, 
                       matches: List[MatchPair],
                       candidate_preferences: Dict[str, List[Preference]],
                       job_preferences: Dict[str, List[Preference]]) -> Tuple[StabilityLevel, List[Tuple[str, str]]]:
        """
        Vérifie la stabilité d'un matching.
        
        Args:
            matches: Liste des paires matchées
            candidate_preferences: Préférences des candidats
            job_preferences: Préférences des jobs
            
        Returns:
            Tuple (stability_level, blocking_pairs)
        """
        self.blocking_pairs = []
        current_matching = {match.candidate_id: match.job_id for match in matches}
        reverse_matching = {match.job_id: match.candidate_id for match in matches}
        
        # Vérifier toutes les paires possibles pour des blocking pairs
        for candidate_id, candidate_prefs in candidate_preferences.items():
            current_job = current_matching.get(candidate_id)
            
            for pref in candidate_prefs:
                job_id = pref.target_id
                
                # Si le candidat préfère ce job à son job actuel
                if self._prefers_over_current(candidate_id, job_id, current_job, candidate_preferences):
                    current_candidate = reverse_matching.get(job_id)
                    
                    # Si le job préfère ce candidat à son candidat actuel
                    if self._prefers_over_current(job_id, candidate_id, current_candidate, job_preferences):
                        self.blocking_pairs.append((candidate_id, job_id))
        
        # Déterminer le niveau de stabilité
        if not self.blocking_pairs:
            return StabilityLevel.STABLE, []
        elif len(self.blocking_pairs) <= len(matches) * 0.1:  # Moins de 10% de blocking pairs
            return StabilityLevel.WEAK_STABLE, self.blocking_pairs
        else:
            return StabilityLevel.UNSTABLE, self.blocking_pairs
    
    def _prefers_over_current(self, 
                             actor_id: str, 
                             target_id: str, 
                             current_target_id: Optional[str],
                             preferences: Dict[str, List[Preference]]) -> bool:
        """Vérifie si l'acteur préfère target à current_target."""
        if current_target_id is None:
            return True  # N'importe quoi est mieux que rien
        
        if target_id == current_target_id:
            return False  # Même target
        
        actor_prefs = preferences.get(actor_id, [])
        
        target_rank = None
        current_rank = None
        
        for pref in actor_prefs:
            if pref.target_id == target_id:
                target_rank = pref.rank
            elif pref.target_id == current_target_id:
                current_rank = pref.rank
        
        # Rang plus bas = meilleure préférence
        if target_rank is not None and current_rank is not None:
            return target_rank < current_rank
        elif target_rank is not None:
            return True
        else:
            return False

class BidirectionalMatcher:
    """
    Matcher bidirectionnel principal utilisant une adaptation du Stable Marriage Algorithm.
    """
    
    def __init__(self, 
                 preference_calculator: Optional[PreferenceCalculator] = None,
                 constraint_system=None):
        self.preference_calculator = preference_calculator or PreferenceCalculator()
        self.constraint_system = constraint_system
        self.stability_checker = StabilityChecker()
        
        # Paramètres de matching
        self.max_iterations = 1000
        self.stability_threshold = 0.1
        
        logger.info("BidirectionalMatcher initialized")
    
    def match(self, 
              candidates: List[Any], 
              jobs: List[Any],
              strategy: MatchingStrategy = MatchingStrategy.BALANCED,
              cost_matrix: Optional[np.ndarray] = None) -> MatchingResult:
        """
        Effectue le matching bidirectionnel.
        
        Args:
            candidates: Liste des candidats
            jobs: Liste des jobs
            strategy: Stratégie de matching
            cost_matrix: Matrice de coûts (optionnelle)
            
        Returns:
            MatchingResult avec tous les détails
        """
        start_time = time.time()
        
        logger.info(f"Starting bidirectional matching: {len(candidates)} candidates, {len(jobs)} jobs")
        
        # Calcul des préférences
        candidate_preferences = self.preference_calculator.calculate_candidate_preferences(
            candidates, jobs, cost_matrix
        )
        job_preferences = self.preference_calculator.calculate_job_preferences(
            candidates, jobs, cost_matrix
        )
        
        # Application de la stratégie de matching
        if strategy == MatchingStrategy.CANDIDATE_OPTIMAL:
            matches = self._gale_shapley_candidate_optimal(candidate_preferences, job_preferences)
        elif strategy == MatchingStrategy.EMPLOYER_OPTIMAL:
            matches = self._gale_shapley_employer_optimal(candidate_preferences, job_preferences)
        else:  # BALANCED
            matches = self._balanced_matching(candidate_preferences, job_preferences)
        
        # Conversion en MatchPair avec scores
        match_pairs = self._create_match_pairs(matches, candidate_preferences, job_preferences)
        
        # Application des contraintes si disponibles
        if self.constraint_system:
            match_pairs = self._apply_constraints(match_pairs, candidates, jobs)
        
        # Vérification de la stabilité
        stability_level, blocking_pairs = self.stability_checker.check_stability(
            match_pairs, candidate_preferences, job_preferences
        )
        
        # Identification des non-matchés
        matched_candidates = {match.candidate_id for match in match_pairs}
        matched_jobs = {match.job_id for match in match_pairs}
        
        unmatched_candidates = [
            getattr(c, 'id', str(i)) for i, c in enumerate(candidates)
            if getattr(c, 'id', str(i)) not in matched_candidates
        ]
        unmatched_jobs = [
            getattr(j, 'id', str(i)) for i, j in enumerate(jobs)
            if getattr(j, 'id', str(i)) not in matched_jobs
        ]
        
        # Calcul du score total
        total_score = sum(match.mutual_score for match in match_pairs)
        
        # Statistiques
        execution_time = time.time() - start_time
        statistics = {
            'matching_strategy': strategy.value,
            'blocking_pairs_count': len(blocking_pairs),
            'average_mutual_score': total_score / len(match_pairs) if match_pairs else 0,
            'match_rate_candidates': len(matched_candidates) / len(candidates),
            'match_rate_jobs': len(matched_jobs) / len(jobs),
            'constraint_violations': sum(len(match.constraint_violations) for match in match_pairs)
        }
        
        result = MatchingResult(
            matches=match_pairs,
            unmatched_candidates=unmatched_candidates,
            unmatched_jobs=unmatched_jobs,
            stability_level=stability_level,
            total_score=total_score,
            execution_time=execution_time,
            statistics=statistics
        )
        
        logger.info(f"Matching completed: {len(match_pairs)} matches, stability={stability_level.value}")
        return result
    
    def _gale_shapley_candidate_optimal(self, 
                                       candidate_preferences: Dict[str, List[Preference]],
                                       job_preferences: Dict[str, List[Preference]]) -> Dict[str, str]:
        """Algorithme Gale-Shapley optimal pour les candidats."""
        current_matches = {}  # candidate_id -> job_id
        job_current_candidate = {}  # job_id -> candidate_id
        candidate_next_proposal = {cid: 0 for cid in candidate_preferences}
        
        free_candidates = set(candidate_preferences.keys())
        
        iterations = 0
        while free_candidates and iterations < self.max_iterations:
            iterations += 1
            candidate_id = free_candidates.pop()
            
            # Candidat propose au job suivant dans sa liste de préférences
            candidate_prefs = candidate_preferences[candidate_id]
            proposal_index = candidate_next_proposal[candidate_id]
            
            if proposal_index >= len(candidate_prefs):
                continue  # Candidat a épuisé ses options
            
            job_id = candidate_prefs[proposal_index].target_id
            candidate_next_proposal[candidate_id] += 1
            
            # Vérifier si le job est libre ou préfère ce candidat
            current_candidate = job_current_candidate.get(job_id)
            
            if current_candidate is None:
                # Job libre, accepte la proposition
                current_matches[candidate_id] = job_id
                job_current_candidate[job_id] = candidate_id
            else:
                # Job occupé, vérifier préférence
                if self._job_prefers_candidate(job_id, candidate_id, current_candidate, job_preferences):
                    # Job préfère le nouveau candidat
                    current_matches[candidate_id] = job_id
                    job_current_candidate[job_id] = candidate_id
                    
                    # Ancien candidat redevient libre
                    del current_matches[current_candidate]
                    free_candidates.add(current_candidate)
                else:
                    # Job préfère son candidat actuel
                    free_candidates.add(candidate_id)
        
        return current_matches
    
    def _gale_shapley_employer_optimal(self, 
                                      candidate_preferences: Dict[str, List[Preference]],
                                      job_preferences: Dict[str, List[Preference]]) -> Dict[str, str]:
        """Algorithme Gale-Shapley optimal pour les employeurs."""
        current_matches = {}  # candidate_id -> job_id
        candidate_current_job = {}  # candidate_id -> job_id
        job_next_proposal = {jid: 0 for jid in job_preferences}
        
        free_jobs = set(job_preferences.keys())
        
        iterations = 0
        while free_jobs and iterations < self.max_iterations:
            iterations += 1
            job_id = free_jobs.pop()
            
            # Job propose au candidat suivant dans sa liste de préférences
            job_prefs = job_preferences[job_id]
            proposal_index = job_next_proposal[job_id]
            
            if proposal_index >= len(job_prefs):
                continue  # Job a épuisé ses options
            
            candidate_id = job_prefs[proposal_index].target_id
            job_next_proposal[job_id] += 1
            
            # Vérifier si le candidat est libre ou préfère ce job
            current_job = candidate_current_job.get(candidate_id)
            
            if current_job is None:
                # Candidat libre, accepte la proposition
                current_matches[candidate_id] = job_id
                candidate_current_job[candidate_id] = job_id
            else:
                # Candidat occupé, vérifier préférence
                if self._candidate_prefers_job(candidate_id, job_id, current_job, candidate_preferences):
                    # Candidat préfère le nouveau job
                    current_matches[candidate_id] = job_id
                    candidate_current_job[candidate_id] = job_id
                    
                    # Ancien job redevient libre
                    free_jobs.add(current_job)
                else:
                    # Candidat préfère son job actuel
                    free_jobs.add(job_id)
        
        return current_matches
    
    def _balanced_matching(self, 
                          candidate_preferences: Dict[str, List[Preference]],
                          job_preferences: Dict[str, List[Preference]]) -> Dict[str, str]:
        """Matching équilibré combinant les deux optimums."""
        # Exécuter les deux algorithmes
        candidate_optimal = self._gale_shapley_candidate_optimal(candidate_preferences, job_preferences)
        employer_optimal = self._gale_shapley_employer_optimal(candidate_preferences, job_preferences)
        
        # Calculer les scores pour chaque matching
        candidate_optimal_score = self._calculate_total_satisfaction(
            candidate_optimal, candidate_preferences, job_preferences
        )
        employer_optimal_score = self._calculate_total_satisfaction(
            employer_optimal, candidate_preferences, job_preferences
        )
        
        # Sélectionner le meilleur ou créer un hybride
        if abs(candidate_optimal_score - employer_optimal_score) < self.stability_threshold:
            # Scores similaires, retourner candidate optimal
            return candidate_optimal
        elif candidate_optimal_score > employer_optimal_score:
            return candidate_optimal
        else:
            return employer_optimal
    
    def _job_prefers_candidate(self, 
                              job_id: str, 
                              candidate1_id: str, 
                              candidate2_id: str,
                              job_preferences: Dict[str, List[Preference]]) -> bool:
        """Vérifie si un job préfère candidate1 à candidate2."""
        job_prefs = job_preferences.get(job_id, [])
        
        candidate1_rank = None
        candidate2_rank = None
        
        for pref in job_prefs:
            if pref.target_id == candidate1_id:
                candidate1_rank = pref.rank
            elif pref.target_id == candidate2_id:
                candidate2_rank = pref.rank
        
        if candidate1_rank is not None and candidate2_rank is not None:
            return candidate1_rank < candidate2_rank
        elif candidate1_rank is not None:
            return True
        else:
            return False
    
    def _candidate_prefers_job(self, 
                              candidate_id: str, 
                              job1_id: str, 
                              job2_id: str,
                              candidate_preferences: Dict[str, List[Preference]]) -> bool:
        """Vérifie si un candidat préfère job1 à job2."""
        candidate_prefs = candidate_preferences.get(candidate_id, [])
        
        job1_rank = None
        job2_rank = None
        
        for pref in candidate_prefs:
            if pref.target_id == job1_id:
                job1_rank = pref.rank
            elif pref.target_id == job2_id:
                job2_rank = pref.rank
        
        if job1_rank is not None and job2_rank is not None:
            return job1_rank < job2_rank
        elif job1_rank is not None:
            return True
        else:
            return False
    
    def _calculate_total_satisfaction(self, 
                                    matches: Dict[str, str],
                                    candidate_preferences: Dict[str, List[Preference]],
                                    job_preferences: Dict[str, List[Preference]]) -> float:
        """Calcule la satisfaction totale d'un matching."""
        total_score = 0.0
        
        for candidate_id, job_id in matches.items():
            # Score du candidat pour ce job
            candidate_prefs = candidate_preferences.get(candidate_id, [])
            candidate_score = 0.0
            for pref in candidate_prefs:
                if pref.target_id == job_id:
                    candidate_score = pref.score
                    break
            
            # Score du job pour ce candidat
            job_prefs = job_preferences.get(job_id, [])
            job_score = 0.0
            for pref in job_prefs:
                if pref.target_id == candidate_id:
                    job_score = pref.score
                    break
            
            # Moyenne harmonique
            if candidate_score > 0 and job_score > 0:
                mutual_score = 2 * (candidate_score * job_score) / (candidate_score + job_score)
                total_score += mutual_score
        
        return total_score
    
    def _create_match_pairs(self, 
                           matches: Dict[str, str],
                           candidate_preferences: Dict[str, List[Preference]],
                           job_preferences: Dict[str, List[Preference]]) -> List[MatchPair]:
        """Crée des MatchPair à partir des matches."""
        match_pairs = []
        
        for candidate_id, job_id in matches.items():
            # Récupérer les scores
            candidate_score = 0.0
            job_score = 0.0
            
            # Score du candidat pour ce job
            candidate_prefs = candidate_preferences.get(candidate_id, [])
            for pref in candidate_prefs:
                if pref.target_id == job_id:
                    candidate_score = pref.score
                    break
            
            # Score du job pour ce candidat
            job_prefs = job_preferences.get(job_id, [])
            for pref in job_prefs:
                if pref.target_id == candidate_id:
                    job_score = pref.score
                    break
            
            # Calcul du score de stabilité (inversement proportionnel aux rangs)
            candidate_rank = next((pref.rank for pref in candidate_prefs if pref.target_id == job_id), len(candidate_prefs))
            job_rank = next((pref.rank for pref in job_prefs if pref.target_id == candidate_id), len(job_prefs))
            
            max_rank = max(len(candidate_prefs), len(job_prefs))
            stability_score = 1.0 - (candidate_rank + job_rank) / (2 * max_rank) if max_rank > 0 else 1.0
            
            match_pair = MatchPair(
                candidate_id=candidate_id,
                job_id=job_id,
                candidate_score=candidate_score,
                job_score=job_score,
                stability_score=stability_score
            )
            match_pairs.append(match_pair)
        
        return match_pairs
    
    def _apply_constraints(self, 
                          match_pairs: List[MatchPair], 
                          candidates: List[Any], 
                          jobs: List[Any]) -> List[MatchPair]:
        """Applique les contraintes aux matches."""
        if not self.constraint_system:
            return match_pairs
        
        # Créer des mappings pour faciliter la recherche
        candidate_map = {getattr(c, 'id', str(i)): c for i, c in enumerate(candidates)}
        job_map = {getattr(j, 'id', str(i)): j for i, j in enumerate(jobs)}
        
        validated_matches = []
        
        for match in match_pairs:
            candidate = candidate_map.get(match.candidate_id)
            job = job_map.get(match.job_id)
            
            if candidate and job:
                is_valid, penalty, messages = self.constraint_system.evaluate_pair(candidate, job)
                
                if is_valid:
                    # Match valide, ajuster les scores en fonction des pénalités
                    match.candidate_score = max(0, match.candidate_score - penalty)
                    match.job_score = max(0, match.job_score - penalty)
                    match.constraint_violations = messages
                    validated_matches.append(match)
                else:
                    # Match invalide en raison de contraintes hard
                    logger.info(f"Match {match.candidate_id}->{match.job_id} rejected due to hard constraints")
        
        return validated_matches

# ===========================================
# FONCTIONS UTILITAIRES
# ===========================================

def create_sample_bidirectional_matcher(constraint_system=None) -> BidirectionalMatcher:
    """Crée un matcher bidirectionnel d'exemple."""
    try:
        from .cost_matrix import CostMatrixGenerator
        cost_generator = CostMatrixGenerator()
        preference_calculator = PreferenceCalculator(cost_generator)
    except ImportError:
        preference_calculator = PreferenceCalculator()
    
    return BidirectionalMatcher(
        preference_calculator=preference_calculator,
        constraint_system=constraint_system
    )

if __name__ == "__main__":
    # Test rapide
    print("🧪 Testing Bidirectional Matcher")
    
    try:
        from .cost_matrix import create_sample_candidates, create_sample_jobs
        from .constraint_system import create_sample_constraint_system
        
        # Création d'exemples
        candidates = create_sample_candidates(5)
        jobs = create_sample_jobs(4)
        constraint_system = create_sample_constraint_system()
        
        # Création du matcher
        matcher = create_sample_bidirectional_matcher(constraint_system)
        
        print(f"Created {len(candidates)} candidates and {len(jobs)} jobs")
        
        # Test de matching avec différentes stratégies
        strategies = [MatchingStrategy.CANDIDATE_OPTIMAL, MatchingStrategy.EMPLOYER_OPTIMAL, MatchingStrategy.BALANCED]
        
        for strategy in strategies:
            print(f"\n🎯 Testing {strategy.value} strategy:")
            result = matcher.match(candidates, jobs, strategy)
            
            print(f"   Matches: {len(result.matches)}")
            print(f"   Unmatched candidates: {len(result.unmatched_candidates)}")
            print(f"   Unmatched jobs: {len(result.unmatched_jobs)}")
            print(f"   Stability: {result.stability_level.value}")
            print(f"   Total score: {result.total_score:.3f}")
            print(f"   Execution time: {result.execution_time:.3f}s")
            
            # Afficher quelques matches
            for i, match in enumerate(result.matches[:3]):
                print(f"   Match {i+1}: {match.candidate_id} -> {match.job_id} "
                      f"(mutual: {match.mutual_score:.3f}, stability: {match.stability_score:.3f})")
        
    except ImportError as e:
        print(f"⚠️  Cannot import required modules for testing: {e}")
        print("Testing basic matcher functionality...")
        
        # Test basique sans dépendances
        matcher = BidirectionalMatcher()
        
        # Mock candidates et jobs
        class MockCandidate:
            def __init__(self, id_val):
                self.id = f"candidate_{id_val}"
        
        class MockJob:
            def __init__(self, id_val):
                self.id = f"job_{id_val}"
        
        candidates = [MockCandidate(i) for i in range(3)]
        jobs = [MockJob(i) for i in range(2)]
        
        result = matcher.match(candidates, jobs)
        print(f"Basic test completed: {len(result.matches)} matches")
