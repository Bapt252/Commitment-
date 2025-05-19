#!/usr/bin/env python3
"""
Session 6: Intelligent Cost Matrix Generation
===========================================

Générateur intelligent de matrices de coûts pour le matching CV/Jobs.
Intègre avec les Sessions 4 et 5 pour des coûts sophistiqués.

🔥 Fonctionnalités:
- Calcul multi-critères (skills, experience, salary, location)
- Integration avec Enhanced Skills Matcher (Session 4)
- Pondération dynamique basée sur ML (Session 5)
- Normalisation et mise à l'échelle
- Support constraints hard/soft
"""

import numpy as np
import logging
from typing import List, Dict, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import math

# Configuration du logging
logger = logging.getLogger(__name__)

class CostFunction(Enum):
    """Types de fonctions de coût."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    SIGMOID = "sigmoid"
    CUSTOM = "custom"

@dataclass
class CriterionWeight:
    """Poids et configuration d'un critère."""
    name: str
    weight: float
    function: CostFunction = CostFunction.LINEAR
    normalize: bool = True
    invert: bool = False  # True if higher values = lower cost
    params: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validation des paramètres."""
        if not 0 <= self.weight <= 1:
            raise ValueError(f"Weight must be in [0,1]: {self.weight}")

@dataclass 
class CandidateProfile:
    """Profil d'un candidat pour le calcul de coût."""
    id: str
    skills: List[str] = field(default_factory=list)
    experience_years: float = 0.0
    salary_expectation: Optional[float] = None
    location: Optional[str] = None
    education_level: Optional[str] = None
    languages: List[str] = field(default_factory=list)
    availability: Optional[str] = None
    
    # Embeddings from Session 4
    skills_embedding: Optional[np.ndarray] = None
    profile_embedding: Optional[np.ndarray] = None
    
    # ML features from Session 5
    ml_features: Optional[Dict[str, float]] = field(default_factory=dict)
    predicted_performance: Optional[float] = None

@dataclass
class JobProfile:
    """Profil d'un job pour le calcul de coût."""
    id: str
    required_skills: List[str] = field(default_factory=list)
    min_experience: float = 0.0
    max_experience: Optional[float] = None
    salary_range: Optional[Tuple[float, float]] = None
    location: Optional[str] = None
    education_required: Optional[str] = None
    languages_required: List[str] = field(default_factory=list)
    urgency: str = "medium"  # low, medium, high
    
    # Embeddings from Session 4
    requirements_embedding: Optional[np.ndarray] = None
    job_embedding: Optional[np.ndarray] = None
    
    # ML features from Session 5
    historical_success_rate: Optional[float] = None
    difficulty_score: Optional[float] = None

class CostMatrixGenerator:
    """Générateur intelligent de matrices de coûts."""
    
    def __init__(self, 
                 criteria_weights: Optional[List[CriterionWeight]] = None,
                 enable_ml_integration: bool = True,
                 enable_embeddings: bool = True,
                 normalize_matrix: bool = True):
        """
        Initialise le générateur.
        
        Args:
            criteria_weights: Poids des critères personnalisés
            enable_ml_integration: Utilise Session 5 pour ML features
            enable_embeddings: Utilise Session 4 pour embeddings
            normalize_matrix: Normalise la matrice finale
        """
        self.enable_ml_integration = enable_ml_integration
        self.enable_embeddings = enable_embeddings
        self.normalize_matrix = normalize_matrix
        
        # Configuration par défaut des critères
        if criteria_weights is None:
            self.criteria_weights = self._get_default_criteria()
        else:
            self.criteria_weights = criteria_weights
        
        # Vérification des poids totaux
        total_weight = sum(c.weight for c in self.criteria_weights)
        if not np.isclose(total_weight, 1.0):
            logger.warning(f"Total weight is {total_weight}, should be 1.0")
        
        # Tentative d'import des modules des sessions précédentes
        self._import_session_modules()
        
        logger.info(f"CostMatrixGenerator initialized with {len(self.criteria_weights)} criteria")
    
    def _get_default_criteria(self) -> List[CriterionWeight]:
        """Configuration par défaut des critères."""
        return [
            CriterionWeight(
                name="skills_match",
                weight=0.35,
                function=CostFunction.EXPONENTIAL,
                invert=True  # Plus de match = moins de coût
            ),
            CriterionWeight(
                name="experience_match", 
                weight=0.20,
                function=CostFunction.LINEAR
            ),
            CriterionWeight(
                name="salary_compatibility",
                weight=0.15,
                function=CostFunction.SIGMOID
            ),
            CriterionWeight(
                name="location_match",
                weight=0.10, 
                function=CostFunction.LINEAR,
                invert=True
            ),
            CriterionWeight(
                name="overall_fit",
                weight=0.20,
                function=CostFunction.LINEAR,
                invert=True
            )
        ]
    
    def _import_session_modules(self) -> None:
        """Importe les modules des sessions précédentes."""
        self.skills_matcher = None
        self.ml_optimizer = None
        
        if self.enable_embeddings:
            try:
                from ..matchers.enhanced_skills_matcher import EnhancedSkillsMatcher
                self.skills_matcher = EnhancedSkillsMatcher()
                logger.info("✅ Session 4 Enhanced Skills Matcher loaded")
            except ImportError as e:
                logger.warning(f"❌ Cannot import Session 4 module: {e}")
                self.enable_embeddings = False
        
        if self.enable_ml_integration:
            try:
                from ..optimizers.ml_optimizer import MLOptimizer
                self.ml_optimizer = MLOptimizer()
                logger.info("✅ Session 5 ML Optimizer loaded")
            except ImportError as e:
                logger.warning(f"❌ Cannot import Session 5 module: {e}")
                self.enable_ml_integration = False
    
    def generate_cost_matrix(self, 
                           candidates: List[CandidateProfile],
                           jobs: List[JobProfile],
                           constraints: Optional[Any] = None) -> np.ndarray:
        """
        Génère la matrice de coûts pour le matching.
        
        Args:
            candidates: Liste des profils candidats
            jobs: Liste des profils jobs
            constraints: Contraintes à appliquer
            
        Returns:
            Matrice de coûts (candidates x jobs)
        """
        n_candidates = len(candidates)
        n_jobs = len(jobs)
        
        logger.info(f"Generating cost matrix: {n_candidates}x{n_jobs}")
        
        # Initialisation de la matrice
        cost_matrix = np.zeros((n_candidates, n_jobs))
        
        # Calcul des coûts pour chaque paire candidat-job
        for i, candidate in enumerate(candidates):
            for j, job in enumerate(jobs):
                cost = self._calculate_pair_cost(candidate, job)
                cost_matrix[i, j] = cost
        
        # Application des contraintes
        if constraints is not None:
            cost_matrix = self._apply_constraints(cost_matrix, candidates, jobs, constraints)
        
        # Normalisation finale
        if self.normalize_matrix:
            cost_matrix = self._normalize_matrix(cost_matrix)
        
        logger.info(f"Cost matrix generated: min={cost_matrix.min():.3f}, max={cost_matrix.max():.3f}")
        return cost_matrix
    
    def _calculate_pair_cost(self, candidate: CandidateProfile, job: JobProfile) -> float:
        """Calcule le coût pour une paire candidat-job."""
        total_cost = 0.0
        
        for criterion in self.criteria_weights:
            if criterion.weight == 0:
                continue
                
            # Calcul du coût pour ce critère
            raw_cost = self._calculate_criterion_cost(candidate, job, criterion)
            
            # Application de la fonction de transformation
            transformed_cost = self._apply_cost_function(raw_cost, criterion)
            
            # Inversion si nécessaire (pour les métriques positives)
            if criterion.invert:
                transformed_cost = 1.0 - transformed_cost
            
            # Ajout pondéré au coût total
            total_cost += criterion.weight * transformed_cost
        
        return total_cost
    
    def _calculate_criterion_cost(self, 
                                candidate: CandidateProfile, 
                                job: JobProfile, 
                                criterion: CriterionWeight) -> float:
        """Calcule le coût pour un critère spécifique."""
        if criterion.name == "skills_match":
            return self._calculate_skills_cost(candidate, job)
        elif criterion.name == "experience_match":
            return self._calculate_experience_cost(candidate, job)
        elif criterion.name == "salary_compatibility":
            return self._calculate_salary_cost(candidate, job)
        elif criterion.name == "location_match":
            return self._calculate_location_cost(candidate, job)
        elif criterion.name == "overall_fit":
            return self._calculate_overall_fit_cost(candidate, job)
        else:
            logger.warning(f"Unknown criterion: {criterion.name}")
            return 0.5  # Coût neutre
    
    def _calculate_skills_cost(self, candidate: CandidateProfile, job: JobProfile) -> float:
        """Calcule le coût basé sur les compétences."""
        # Session 4 embeddings si disponibles
        if (self.enable_embeddings and self.skills_matcher and 
            candidate.skills_embedding is not None and 
            job.requirements_embedding is not None):
            
            try:
                # Utilise les embeddings vectoriels
                similarity = self.skills_matcher.calculate_similarity(
                    candidate.skills_embedding, 
                    job.requirements_embedding
                )
                return 1.0 - similarity  # Convertit similarité en coût
            except Exception as e:
                logger.warning(f"Failed to use embeddings: {e}")
        
        # Fallback: calcul basique basé sur les compétences textuelles
        candidate_skills = set(candidate.skills)
        required_skills = set(job.required_skills)
        
        if not required_skills:
            return 0.0  # Pas de compétences requises
        
        # Jaccard similarity
        intersection = len(candidate_skills & required_skills)
        union = len(candidate_skills | required_skills)
        
        if union == 0:
            similarity = 1.0
        else:
            similarity = intersection / union
        
        # Bonus pour surqualification modérée
        if len(candidate_skills) > len(required_skills):
            bonus = min(0.1, 0.02 * (len(candidate_skills) - len(required_skills)))
            similarity += bonus
        
        return 1.0 - min(1.0, similarity)
    
    def _calculate_experience_cost(self, candidate: CandidateProfile, job: JobProfile) -> float:
        """Calcule le coût basé sur l'expérience."""
        candidate_exp = candidate.experience_years
        min_exp = job.min_experience
        max_exp = job.max_experience or float('inf')
        
        if candidate_exp < min_exp:
            # Pénalité pour manque d'expérience
            deficit = min_exp - candidate_exp
            return min(1.0, deficit / max(min_exp, 1.0))
        elif max_exp != float('inf') and candidate_exp > max_exp:
            # Pénalité pour surqualification
            excess = candidate_exp - max_exp
            return min(0.3, excess / max(max_exp, 1.0))  # Pénalité plus faible
        else:
            # Expérience dans la fourchette
            return 0.0
    
    def _calculate_salary_cost(self, candidate: CandidateProfile, job: JobProfile) -> float:
        """Calcule le coût basé sur la compatibilité salariale."""
        if not candidate.salary_expectation or not job.salary_range:
            return 0.5  # Coût neutre si information manquante
        
        expectation = candidate.salary_expectation
        min_salary, max_salary = job.salary_range
        
        if min_salary <= expectation <= max_salary:
            # Parfait match salarial
            return 0.0
        elif expectation < min_salary:
            # Candidat sous-évalué (risque de refus)
            gap = min_salary - expectation
            return min(1.0, gap / min_salary)
        else:
            # Candidat trop cher
            gap = expectation - max_salary
            return min(1.0, gap / max_salary)
    
    def _calculate_location_cost(self, candidate: CandidateProfile, job: JobProfile) -> float:
        """Calcule le coût basé sur la localisation."""
        if not candidate.location or not job.location:
            return 0.5  # Coût neutre si information manquante
        
        # Comparaison simple (peut être améliorée avec des APIs de géolocalisation)
        if candidate.location.lower() == job.location.lower():
            return 0.0  # Match parfait
        else:
            # Logique simple: même région, pays, etc.
            candidate_parts = candidate.location.lower().split(',')
            job_parts = job.location.lower().split(',')
            
            # Recherche de correspondances partielles
            matches = sum(1 for part in candidate_parts if any(part.strip() in jp for jp in job_parts))
            total_parts = max(len(candidate_parts), len(job_parts))
            
            if total_parts == 0:
                return 1.0
            
            similarity = matches / total_parts
            return 1.0 - similarity
    
    def _calculate_overall_fit_cost(self, candidate: CandidateProfile, job: JobProfile) -> float:
        """Calcule un score de fitness global (ML ou heuristique)."""
        # Session 5 ML prediction si disponible
        if (self.enable_ml_integration and self.ml_optimizer and 
            candidate.predicted_performance is not None):
            
            try:
                # Utilise les prédictions ML
                fit_score = self.ml_optimizer.predict_match_quality(
                    candidate, job
                )
                return 1.0 - fit_score  # Convertit score en coût
            except Exception as e:
                logger.warning(f"Failed to use ML prediction: {e}")
        
        # Fallback: score heuristique
        fit_factors = []
        
        # Education match
        if candidate.education_level and job.education_required:
            education_levels = {
                'high_school': 1, 'associate': 2, 'bachelor': 3, 
                'master': 4, 'phd': 5
            }
            candidate_edu = education_levels.get(candidate.education_level.lower(), 3)
            required_edu = education_levels.get(job.education_required.lower(), 3)
            
            if candidate_edu >= required_edu:
                fit_factors.append(1.0)
            else:
                fit_factors.append(candidate_edu / required_edu)
        
        # Language match
        if candidate.languages and job.languages_required:
            candidate_langs = set(lang.lower() for lang in candidate.languages)
            required_langs = set(lang.lower() for lang in job.languages_required)
            
            if required_langs:
                lang_match = len(candidate_langs & required_langs) / len(required_langs)
                fit_factors.append(lang_match)
        
        # Availability/urgency match
        urgency_weights = {'low': 0.3, 'medium': 0.7, 'high': 1.0}
        availability_weights = {'immediate': 1.0, 'flexible': 0.8, 'long_term': 0.5}
        
        if candidate.availability and job.urgency:
            urgency_score = urgency_weights.get(job.urgency, 0.7)
            availability_score = availability_weights.get(candidate.availability, 0.8)
            
            # Plus l'urgence est haute et la disponibilité immédiate, mieux c'est
            urgency_match = min(1.0, availability_score / urgency_score)
            fit_factors.append(urgency_match)
        
        # Score final
        if fit_factors:
            overall_fit = np.mean(fit_factors)
            return 1.0 - overall_fit
        else:
            return 0.5  # Neutre si pas assez d'information
    
    def _apply_cost_function(self, raw_cost: float, criterion: CriterionWeight) -> float:
        """Applique la fonction de transformation du coût."""
        # Assure que le coût est dans [0, 1]
        cost = np.clip(raw_cost, 0.0, 1.0)
        
        if criterion.function == CostFunction.LINEAR:
            return cost
        
        elif criterion.function == CostFunction.EXPONENTIAL:
            # Amplifie les grandes différences
            alpha = criterion.params.get('alpha', 2.0)
            return cost ** alpha
        
        elif criterion.function == CostFunction.LOGARITHMIC:
            # Atténue les grandes différences
            if cost == 0:
                return 0
            return math.log(1 + cost) / math.log(2)
        
        elif criterion.function == CostFunction.SIGMOID:
            # Transformation sigmoïde
            k = criterion.params.get('k', 10.0)  # Steepness
            x0 = criterion.params.get('x0', 0.5)  # Midpoint
            return 1 / (1 + math.exp(-k * (cost - x0)))
        
        elif criterion.function == CostFunction.CUSTOM:
            # Fonction personnalisée
            custom_func = criterion.params.get('function')
            if callable(custom_func):
                return custom_func(cost)
            else:
                logger.warning(f"No custom function provided for {criterion.name}")
                return cost
        
        else:
            logger.warning(f"Unknown cost function: {criterion.function}")
            return cost
    
    def _apply_constraints(self, 
                          cost_matrix: np.ndarray,
                          candidates: List[CandidateProfile],
                          jobs: List[JobProfile],
                          constraints: Any) -> np.ndarray:
        """Applique les contraintes à la matrice de coûts."""
        # Cette méthode sera étendue avec le système de contraintes
        # Pour l'instant, placeholder
        logger.info("Applying constraints to cost matrix")
        return cost_matrix
    
    def _normalize_matrix(self, cost_matrix: np.ndarray) -> np.ndarray:
        """Normalise la matrice de coûts."""
        # Normalisation min-max
        min_cost = cost_matrix.min()
        max_cost = cost_matrix.max()
        
        if max_cost == min_cost:
            # Matrice uniforme
            return np.ones_like(cost_matrix) * 0.5
        
        normalized = (cost_matrix - min_cost) / (max_cost - min_cost)
        
        logger.info(f"Matrix normalized: [{min_cost:.3f}, {max_cost:.3f}] -> [0, 1]")
        return normalized
    
    def get_cost_breakdown(self, 
                          candidate: CandidateProfile, 
                          job: JobProfile) -> Dict[str, float]:
        """Retourne la décomposition des coûts pour une paire."""
        breakdown = {}
        
        for criterion in self.criteria_weights:
            raw_cost = self._calculate_criterion_cost(candidate, job, criterion)
            transformed_cost = self._apply_cost_function(raw_cost, criterion)
            
            if criterion.invert:
                transformed_cost = 1.0 - transformed_cost
            
            weighted_cost = criterion.weight * transformed_cost
            
            breakdown[criterion.name] = {
                'raw_cost': raw_cost,
                'transformed_cost': transformed_cost,
                'weighted_cost': weighted_cost,
                'weight': criterion.weight
            }
        
        total_cost = sum(item['weighted_cost'] for item in breakdown.values())
        breakdown['total_cost'] = total_cost
        
        return breakdown
    
    def update_criterion_weight(self, criterion_name: str, new_weight: float) -> None:
        """Met à jour le poids d'un critère."""
        for criterion in self.criteria_weights:
            if criterion.name == criterion_name:
                old_weight = criterion.weight
                criterion.weight = new_weight
                logger.info(f"Updated {criterion_name}: {old_weight} -> {new_weight}")
                return
        
        logger.warning(f"Criterion not found: {criterion_name}")
    
    def add_custom_criterion(self, criterion: CriterionWeight) -> None:
        """Ajoute un critère personnalisé."""
        # Vérifier que le nom n'existe pas déjà
        existing_names = [c.name for c in self.criteria_weights]
        if criterion.name in existing_names:
            raise ValueError(f"Criterion already exists: {criterion.name}")
        
        self.criteria_weights.append(criterion)
        logger.info(f"Added custom criterion: {criterion.name} (weight={criterion.weight})")

# Fonctions utilitaires
def create_sample_candidates(n: int = 5) -> List[CandidateProfile]:
    """Crée des candidats d'exemple pour les tests."""
    candidates = []
    
    for i in range(n):
        candidate = CandidateProfile(
            id=f"candidate_{i}",
            skills=["python", "javascript", "react", "sql"][:np.random.randint(1, 5)],
            experience_years=np.random.uniform(0, 10),
            salary_expectation=np.random.uniform(40000, 100000),
            location=np.random.choice(["Paris", "Lyon", "Marseille", "Toulouse"]),
            education_level=np.random.choice(["bachelor", "master", "phd"]),
            languages=["French", "English"],
            availability=np.random.choice(["immediate", "flexible", "long_term"])
        )
        candidates.append(candidate)
    
    return candidates

def create_sample_jobs(n: int = 3) -> List[JobProfile]:
    """Crée des jobs d'exemple pour les tests."""
    jobs = []
    
    for i in range(n):
        job = JobProfile(
            id=f"job_{i}",
            required_skills=["python", "react", "sql", "aws"][:np.random.randint(2, 4)],
            min_experience=np.random.uniform(0, 5),
            max_experience=np.random.uniform(5, 15),
            salary_range=(np.random.uniform(40000, 60000), np.random.uniform(60000, 120000)),
            location=np.random.choice(["Paris", "Lyon", "Remote"]),
            education_required=np.random.choice(["bachelor", "master"]),
            languages_required=["French"],
            urgency=np.random.choice(["low", "medium", "high"])
        )
        jobs.append(job)
    
    return jobs

if __name__ == "__main__":
    # Test rapide
    print("🧪 Testing Cost Matrix Generator")
    
    # Création d'exemples
    candidates = create_sample_candidates(4)
    jobs = create_sample_jobs(3)
    
    print(f"Created {len(candidates)} candidates and {len(jobs)} jobs")
    
    # Génération de la matrice
    generator = CostMatrixGenerator()
    cost_matrix = generator.generate_cost_matrix(candidates, jobs)
    
    print(f"\n📊 Cost Matrix ({cost_matrix.shape}):")
    print(cost_matrix)
    
    # Analyse détaillée d'une paire
    breakdown = generator.get_cost_breakdown(candidates[0], jobs[0])
    print(f"\n🔍 Cost breakdown for {candidates[0].id} -> {jobs[0].id}:")
    for criterion, details in breakdown.items():
        if criterion != 'total_cost':
            print(f"   {criterion}: {details['weighted_cost']:.3f} (weight={details['weight']})")
    print(f"   TOTAL: {breakdown['total_cost']:.3f}")
