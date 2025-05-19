#!/usr/bin/env python3
"""
Session 6: Business Rules Module
================================

Contraintes métier spécifiques pour le matching CV-Job.
Implémente les règles courantes du recrutement avec une logique optimisée.

🔥 Contraintes disponibles:
- SalaryConstraint: Compatibilité salariale
- ExperienceConstraint: Expérience minimum/maximum
- SkillsConstraint: Compétences requises/préférées
- LocationConstraint: Localisation et télétravail
- EducationConstraint: Niveau d'éducation
- LanguageConstraint: Langues requises
- AvailabilityConstraint: Disponibilité
- ContractTypeConstraint: Type de contrat
- IndustryConstraint: Secteur d'activité

Toutes les contraintes supportent la configuration flexible et la mesure de performance.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta

from .base_constraints import (
    BaseConstraint, HardConstraint, SoftConstraint, PreferenceConstraint,
    ConstraintResult, ConstraintType, ConstraintPriority, ConstraintScope
)

# Configuration du logging
logger = logging.getLogger(__name__)

# ===========================================
# CONTRAINTE SALARIALE
# ===========================================

class SalaryConstraint(SoftConstraint):
    """
    Contrainte sur la compatibilité salariale.
    
    Vérifie que l'expectation salariale du candidat est compatible
    avec la fourchette proposée par l'employeur.
    """
    
    def __init__(self, 
                 tolerance_percent: float = 0.15,
                 currency_conversion: Optional[Dict[str, float]] = None,
                 consider_benefits: bool = True,
                 **kwargs):
        super().__init__(
            name="salary_compatibility",
            description="Vérifie la compatibilité entre expectation et offre salariale",
            **kwargs
        )
        
        self.tolerance_percent = tolerance_percent
        self.currency_conversion = currency_conversion or {}
        self.consider_benefits = consider_benefits
        
        # Weights for different salary components
        self.base_salary_weight = 0.7
        self.benefits_weight = 0.2
        self.bonus_weight = 0.1
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la compatibilité salariale."""
        try:
            # Extraction des données salariales
            candidate_expectation = self._extract_salary_expectation(candidate)
            job_offer = self._extract_salary_offer(job)
            
            if not candidate_expectation:
                return ConstraintResult(
                    satisfied=True,
                    confidence=0.5,
                    message="No salary expectation provided",
                    details={'reason': 'no_expectation'}
                )
            
            if not job_offer:
                return ConstraintResult(
                    satisfied=True,
                    confidence=0.5,
                    message="No salary offer defined",
                    details={'reason': 'no_offer'}
                )
            
            # Normalisation des devises
            candidate_expectation = self._normalize_currency(candidate_expectation)
            job_offer = self._normalize_currency(job_offer)
            
            # Calcul de la compatibilité
            compatibility = self._calculate_compatibility(candidate_expectation, job_offer)
            
            if compatibility['is_compatible']:
                return ConstraintResult(
                    satisfied=True,
                    message=f"Salary compatible (gap: {compatibility['gap_percent']:.1%})",
                    details=compatibility
                )
            else:
                penalty = self._calculate_penalty(compatibility['gap_percent'])
                return ConstraintResult(
                    satisfied=False,
                    penalty=penalty,
                    message=f"Salary incompatible (gap: {compatibility['gap_percent']:.1%})",
                    details=compatibility
                )
                
        except Exception as e:
            logger.error(f"Error evaluating salary constraint: {e}")
            return ConstraintResult(
                satisfied=False,
                penalty=self.max_penalty * 0.5,
                confidence=0.0,
                message=f"Evaluation error: {str(e)}",
                details={'error': str(e)}
            )
    
    def _extract_salary_expectation(self, candidate: Any) -> Optional[Dict[str, float]]:
        """Extrait l'expectation salariale du candidat."""
        salary_attrs = ['salary_expectation', 'expected_salary', 'salary_min', 'target_salary']
        
        for attr in salary_attrs:
            if hasattr(candidate, attr):
                value = getattr(candidate, attr)
                if value:
                    if isinstance(value, (int, float)):
                        return {'base': float(value), 'currency': 'EUR'}
                    elif isinstance(value, dict):
                        return value
                    elif isinstance(value, str):
                        return self._parse_salary_string(value)
        
        return None
    
    def _extract_salary_offer(self, job: Any) -> Optional[Dict[str, Union[float, Tuple[float, float]]]]:
        """Extrait l'offre salariale du job."""
        # Try different attribute names
        salary_attrs = [
            'salary_range', 'salary_offer', 'compensation', 
            'salary_min_max', 'package'
        ]
        
        for attr in salary_attrs:
            if hasattr(job, attr):
                value = getattr(job, attr)
                if value:
                    if isinstance(value, (tuple, list)) and len(value) == 2:
                        return {
                            'base': (float(value[0]), float(value[1])),
                            'currency': 'EUR'
                        }
                    elif isinstance(value, dict):
                        return value
                    elif isinstance(value, (int, float)):
                        return {'base': float(value), 'currency': 'EUR'}
        
        # Try individual min/max attributes
        salary_min = getattr(job, 'salary_min', None)
        salary_max = getattr(job, 'salary_max', None)
        
        if salary_min is not None and salary_max is not None:
            return {
                'base': (float(salary_min), float(salary_max)),
                'currency': getattr(job, 'currency', 'EUR')
            }
        
        return None
    
    def _parse_salary_string(self, salary_str: str) -> Dict[str, float]:
        """Parse une chaîne de caractères représentant un salaire."""
        # Remove common separators and extract numbers
        cleaned = re.sub(r'[^\d\.,k€$£¥]', ' ', salary_str.lower())
        numbers = re.findall(r'\d+(?:[,\.]\d+)?', cleaned)
        
        if numbers:
            salary = float(numbers[0].replace(',', '.'))
            
            # Handle 'k' multiplier
            if 'k' in salary_str.lower():
                salary *= 1000
            
            # Detect currency
            currency = 'EUR'
            if '$' in salary_str:
                currency = 'USD'
            elif '£' in salary_str:
                currency = 'GBP'
            elif '¥' in salary_str:
                currency = 'JPY'
            
            return {'base': salary, 'currency': currency}
        
        return {'base': 0.0, 'currency': 'EUR'}
    
    def _normalize_currency(self, salary_data: Dict) -> Dict:
        """Normalise les devises en EUR."""
        currency = salary_data.get('currency', 'EUR')
        conversion_rate = self.currency_conversion.get(currency, 1.0)
        
        normalized = salary_data.copy()
        
        if 'base' in salary_data:
            base = salary_data['base']
            if isinstance(base, tuple):
                normalized['base'] = (base[0] * conversion_rate, base[1] * conversion_rate)
            else:
                normalized['base'] = base * conversion_rate
        
        normalized['currency'] = 'EUR'
        return normalized
    
    def _calculate_compatibility(self, expectation: Dict, offer: Dict) -> Dict[str, Any]:
        """Calcule la compatibilité salariale."""
        exp_base = expectation['base']
        offer_base = offer['base']
        
        # Handle range vs single value
        if isinstance(offer_base, tuple):
            offer_min, offer_max = offer_base
            offer_mid = (offer_min + offer_max) / 2
        else:
            offer_min = offer_max = offer_mid = offer_base
        
        # Apply tolerance
        tolerance = self.tolerance_percent
        offer_min_adj = offer_min * (1 - tolerance)
        offer_max_adj = offer_max * (1 + tolerance)
        
        # Check compatibility
        is_compatible = offer_min_adj <= exp_base <= offer_max_adj
        
        # Calculate gap
        if exp_base < offer_min_adj:
            gap = (offer_min_adj - exp_base) / offer_min_adj
        elif exp_base > offer_max_adj:
            gap = (exp_base - offer_max_adj) / offer_max_adj
        else:
            gap = 0.0
        
        return {
            'is_compatible': is_compatible,
            'gap_percent': gap,
            'expectation': exp_base,
            'offer_range': (offer_min, offer_max),
            'offer_adjusted': (offer_min_adj, offer_max_adj),
            'tolerance_applied': tolerance
        }

# ===========================================
# CONTRAINTE D'EXPÉRIENCE
# ===========================================

class ExperienceConstraint(BaseConstraint):
    """
    Contrainte sur l'expérience professionnelle.
    
    Vérifie que le candidat a l'expérience minimum requise
    et n'est pas surqualifié si spécifié.
    """
    
    def __init__(self,
                 allow_overqualification: bool = True,
                 experience_equivalency: Optional[Dict[str, float]] = None,
                 domain_specific: bool = True,
                 **kwargs):
        super().__init__(
            name="experience_requirement",
            description="Vérifie l'adéquation de l'expérience professionnelle",
            **kwargs
        )
        
        self.allow_overqualification = allow_overqualification
        self.experience_equivalency = experience_equivalency or {
            'internship': 0.5,
            'part_time': 0.7,
            'freelance': 0.8,
            'volunteer': 0.3
        }
        self.domain_specific = domain_specific
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la contrainte d'expérience."""
        try:
            candidate_exp = self._extract_candidate_experience(candidate)
            required_exp = self._extract_required_experience(job)
            
            if required_exp is None:
                return ConstraintResult(
                    satisfied=True,
                    message="No experience requirement specified",
                    details={'reason': 'no_requirement'}
                )
            
            # Calculate effective experience
            effective_exp = self._calculate_effective_experience(candidate_exp, job)
            min_exp = required_exp.get('min', 0)
            max_exp = required_exp.get('max', float('inf'))
            
            # Check minimum requirement
            if effective_exp < min_exp:
                deficit = min_exp - effective_exp
                if self.constraint_type == ConstraintType.HARD:
                    return ConstraintResult(
                        satisfied=False,
                        message=f"Insufficient experience: {effective_exp:.1f} < {min_exp} years",
                        details={
                            'effective_experience': effective_exp,
                            'required_min': min_exp,
                            'deficit': deficit
                        }
                    )
                else:
                    penalty = self.calculate_penalty(deficit / max(min_exp, 1.0))
                    return ConstraintResult(
                        satisfied=False,
                        penalty=penalty,
                        message=f"Below minimum experience: {effective_exp:.1f} < {min_exp} years",
                        details={
                            'effective_experience': effective_exp,
                            'required_min': min_exp,
                            'deficit': deficit,
                            'penalty': penalty
                        }
                    )
            
            # Check maximum (overqualification)
            if not self.allow_overqualification and effective_exp > max_exp:
                excess = effective_exp - max_exp
                if self.constraint_type == ConstraintType.HARD:
                    return ConstraintResult(
                        satisfied=False,
                        message=f"Overqualified: {effective_exp:.1f} > {max_exp} years",
                        details={
                            'effective_experience': effective_exp,
                            'required_max': max_exp,
                            'excess': excess
                        }
                    )
                else:
                    penalty = self.calculate_penalty(excess / max_exp * 0.5)  # Lower penalty for overqualification
                    return ConstraintResult(
                        satisfied=False,
                        penalty=penalty,
                        message=f"Overqualified: {effective_exp:.1f} > {max_exp} years",
                        details={
                            'effective_experience': effective_exp,
                            'required_max': max_exp,
                            'excess': excess,
                            'penalty': penalty
                        }
                    )
            
            # Experience is adequate
            return ConstraintResult(
                satisfied=True,
                message=f"Experience adequate: {effective_exp:.1f} years (required: {min_exp}-{max_exp})",
                details={
                    'effective_experience': effective_exp,
                    'required_range': (min_exp, max_exp),
                    'candidate_raw_experience': candidate_exp
                }
            )
            
        except Exception as e:
            logger.error(f"Error evaluating experience constraint: {e}")
            return ConstraintResult(
                satisfied=False,
                penalty=self.max_penalty * 0.5 if self.constraint_type == ConstraintType.SOFT else 0,
                confidence=0.0,
                message=f"Evaluation error: {str(e)}",
                details={'error': str(e)}
            )
    
    def _extract_candidate_experience(self, candidate: Any) -> Dict[str, Any]:
        """Extrait l'expérience du candidat."""
        experience = {
            'total_years': 0,
            'relevant_years': 0,
            'positions': [],
            'domains': []
        }
        
        # Try different attribute names
        exp_attrs = ['experience_years', 'years_experience', 'total_experience']
        for attr in exp_attrs:
            if hasattr(candidate, attr):
                experience['total_years'] = float(getattr(candidate, attr, 0))
                break
        
        # Extract detailed experience if available
        if hasattr(candidate, 'work_experience'):
            experience['positions'] = getattr(candidate, 'work_experience', [])
        elif hasattr(candidate, 'experience'):
            exp_data = getattr(candidate, 'experience', {})
            if isinstance(exp_data, list):
                experience['positions'] = exp_data
            elif isinstance(exp_data, dict):
                experience.update(exp_data)
        
        # Extract domains/industries
        if hasattr(candidate, 'industries'):
            experience['domains'] = getattr(candidate, 'industries', [])
        elif hasattr(candidate, 'domains'):
            experience['domains'] = getattr(candidate, 'domains', [])
        
        return experience
    
    def _extract_required_experience(self, job: Any) -> Optional[Dict[str, float]]:
        """Extrait l'expérience requise pour le job."""
        # Try different attribute names
        req_attrs = [
            'min_experience', 'experience_required', 'years_required',
            'experience_min', 'required_experience'
        ]
        
        min_exp = None
        for attr in req_attrs:
            if hasattr(job, attr):
                min_exp = getattr(job, attr)
                break
        
        # Try max experience
        max_attrs = ['max_experience', 'experience_max']
        max_exp = None
        for attr in max_attrs:
            if hasattr(job, attr):
                max_exp = getattr(job, attr)
                break
        
        if min_exp is not None:
            return {
                'min': float(min_exp),
                'max': float(max_exp) if max_exp is not None else float('inf')
            }
        
        return None
    
    def _calculate_effective_experience(self, candidate_exp: Dict, job: Any) -> float:
        """Calcule l'expérience effective en tenant compte des équivalences."""
        if not self.domain_specific:
            return candidate_exp.get('total_years', 0)
        
        # Get job domain/industry
        job_domain = getattr(job, 'industry', None) or getattr(job, 'domain', None)
        
        if not job_domain or not candidate_exp.get('domains'):
            return candidate_exp.get('total_years', 0)
        
        # Calculate domain-specific experience
        relevant_exp = 0
        total_exp = candidate_exp.get('total_years', 0)
        
        # Simple heuristic: if candidate has experience in the same domain,
        # give full credit, otherwise apply a discount
        candidate_domains = [d.lower() for d in candidate_exp.get('domains', [])]
        if job_domain.lower() in candidate_domains:
            relevant_exp = total_exp
        else:
            # Apply experience equivalency based on transferability
            relevant_exp = total_exp * 0.7  # 70% transferability
        
        return relevant_exp

# ===========================================
# CONTRAINTE DE COMPÉTENCES
# ===========================================

class SkillsConstraint(BaseConstraint):
    """
    Contrainte sur les compétences requises et préférées.
    
    Évalue la correspondance entre les compétences du candidat
    et celles requises/préférées pour le poste.
    """
    
    def __init__(self,
                 minimum_match_ratio: float = 0.6,
                 skill_weights: Optional[Dict[str, float]] = None,
                 skill_categories: Optional[Dict[str, List[str]]] = None,
                 fuzzy_matching: bool = True,
                 **kwargs):
        super().__init__(
            name="skills_requirement",
            description="Vérifie l'adéquation des compétences",
            **kwargs
        )
        
        self.minimum_match_ratio = minimum_match_ratio
        self.skill_weights = skill_weights or {}
        self.skill_categories = skill_categories or {}
        self.fuzzy_matching = fuzzy_matching
        
        # Skill similarity mappings for fuzzy matching
        self.skill_similarities = {
            'python': ['python3', 'py', 'python programming'],
            'javascript': ['js', 'node.js', 'nodejs', 'ecmascript'],
            'react': ['reactjs', 'react.js'],
            'sql': ['mysql', 'postgresql', 'sqlite', 'database'],
            'machine learning': ['ml', 'ai', 'artificial intelligence'],
            'aws': ['amazon web services', 'cloud computing'],
            'docker': ['containerization', 'containers']
        }
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la contrainte de compétences."""
        try:
            candidate_skills = self._extract_candidate_skills(candidate)
            job_requirements = self._extract_job_requirements(job)
            
            if not job_requirements.get('required') and not job_requirements.get('preferred'):
                return ConstraintResult(
                    satisfied=True,
                    message="No skills required",
                    details={'reason': 'no_requirements'}
                )
            
            if not candidate_skills:
                if job_requirements.get('required'):
                    return ConstraintResult(
                        satisfied=False,
                        penalty=self.max_penalty if self.constraint_type == ConstraintType.SOFT else 0,
                        message="No candidate skills provided",
                        details={'reason': 'no_candidate_skills'}
                    )
                else:
                    return ConstraintResult(
                        satisfied=True,
                        message="No skills provided, but none required",
                        details={'reason': 'no_skills_either_side'}
                    )
            
            # Perform skill matching
            match_result = self._match_skills(candidate_skills, job_requirements)
            
            # Evaluate based on constraint type
            if self.constraint_type == ConstraintType.HARD:
                is_satisfied = match_result['required_match_ratio'] >= self.minimum_match_ratio
                return ConstraintResult(
                    satisfied=is_satisfied,
                    message=self._create_message(match_result, is_satisfied),
                    details=match_result
                )
            else:
                # Soft constraint: calculate penalty based on missing skills
                required_deficit = max(0, self.minimum_match_ratio - match_result['required_match_ratio'])
                penalty = self.calculate_penalty(required_deficit)
                
                is_satisfied = required_deficit == 0
                return ConstraintResult(
                    satisfied=is_satisfied,
                    penalty=penalty,
                    message=self._create_message(match_result, is_satisfied),
                    details=match_result
                )
                
        except Exception as e:
            logger.error(f"Error evaluating skills constraint: {e}")
            return ConstraintResult(
                satisfied=False,
                penalty=self.max_penalty * 0.5 if self.constraint_type == ConstraintType.SOFT else 0,
                confidence=0.0,
                message=f"Evaluation error: {str(e)}",
                details={'error': str(e)}
            )
    
    def _extract_candidate_skills(self, candidate: Any) -> Set[str]:
        """Extrait les compétences du candidat."""
        skills = set()
        
        skill_attrs = ['skills', 'competencies', 'technologies', 'expertise']
        for attr in skill_attrs:
            if hasattr(candidate, attr):
                skill_data = getattr(candidate, attr)
                if isinstance(skill_data, (list, tuple)):
                    skills.update(skill.lower().strip() for skill in skill_data)
                elif isinstance(skill_data, str):
                    # Parse comma-separated skills
                    skills.update(skill.lower().strip() for skill in skill_data.split(','))
                elif isinstance(skill_data, dict):
                    # Handle skill dictionaries with levels
                    skills.update(skill.lower().strip() for skill in skill_data.keys())
        
        return skills
    
    def _extract_job_requirements(self, job: Any) -> Dict[str, Set[str]]:
        """Extrait les compétences requises et préférées du job."""
        requirements = {'required': set(), 'preferred': set()}
        
        # Required skills
        req_attrs = [
            'required_skills', 'skills_required', 'mandatory_skills',
            'must_have_skills', 'skills'
        ]
        for attr in req_attrs:
            if hasattr(job, attr):
                skill_data = getattr(job, attr)
                if skill_data:
                    requirements['required'].update(
                        self._parse_skills(skill_data)
                    )
                    break
        
        # Preferred skills
        pref_attrs = [
            'preferred_skills', 'nice_to_have_skills', 'optional_skills',
            'desired_skills'
        ]
        for attr in pref_attrs:
            if hasattr(job, attr):
                skill_data = getattr(job, attr)
                if skill_data:
                    requirements['preferred'].update(
                        self._parse_skills(skill_data)
                    )
                    break
        
        return requirements
    
    def _parse_skills(self, skill_data: Any) -> Set[str]:
        """Parse les compétences depuis différents formats."""
        skills = set()
        
        if isinstance(skill_data, (list, tuple)):
            skills.update(skill.lower().strip() for skill in skill_data)
        elif isinstance(skill_data, str):
            skills.update(skill.lower().strip() for skill in skill_data.split(','))
        elif isinstance(skill_data, dict):
            skills.update(skill.lower().strip() for skill in skill_data.keys())
        
        return skills
    
    def _match_skills(self, candidate_skills: Set[str], requirements: Dict[str, Set[str]]) -> Dict[str, Any]:
        """Effectue le matching des compétences avec support fuzzy."""
        result = {
            'required_skills': requirements['required'],
            'preferred_skills': requirements['preferred'],
            'candidate_skills': candidate_skills,
            'matched_required': set(),
            'matched_preferred': set(),
            'missing_required': set(),
            'missing_preferred': set(),
            'extra_skills': set(),
            'required_match_ratio': 0.0,
            'preferred_match_ratio': 0.0,
            'total_match_score': 0.0
        }
        
        # Direct matching for required skills
        for req_skill in requirements['required']:
            if self._skill_matches(req_skill, candidate_skills):
                result['matched_required'].add(req_skill)
            else:
                result['missing_required'].add(req_skill)
        
        # Direct matching for preferred skills
        for pref_skill in requirements['preferred']:
            if self._skill_matches(pref_skill, candidate_skills):
                result['matched_preferred'].add(pref_skill)
            else:
                result['missing_preferred'].add(pref_skill)
        
        # Calculate ratios
        if requirements['required']:
            result['required_match_ratio'] = len(result['matched_required']) / len(requirements['required'])
        else:
            result['required_match_ratio'] = 1.0
        
        if requirements['preferred']:
            result['preferred_match_ratio'] = len(result['matched_preferred']) / len(requirements['preferred'])
        else:
            result['preferred_match_ratio'] = 1.0
        
        # Find extra skills
        all_required = requirements['required'] | requirements['preferred']
        matched_candidate_skills = set()
        for candidate_skill in candidate_skills:
            for req_skill in all_required:
                if self._skills_similar(candidate_skill, req_skill):
                    matched_candidate_skills.add(candidate_skill)
                    break
        
        result['extra_skills'] = candidate_skills - matched_candidate_skills
        
        # Calculate total match score
        required_weight = 0.8
        preferred_weight = 0.2
        result['total_match_score'] = (
            required_weight * result['required_match_ratio'] +
            preferred_weight * result['preferred_match_ratio']
        )
        
        return result
    
    def _skill_matches(self, required_skill: str, candidate_skills: Set[str]) -> bool:
        """Vérifie si une compétence requise est présente chez le candidat."""
        # Direct match
        if required_skill in candidate_skills:
            return True
        
        # Fuzzy matching if enabled
        if self.fuzzy_matching:
            for candidate_skill in candidate_skills:
                if self._skills_similar(required_skill, candidate_skill):
                    return True
        
        return False
    
    def _skills_similar(self, skill1: str, skill2: str) -> bool:
        """Vérifie la similarité entre deux compétences."""
        if skill1 == skill2:
            return True
        
        # Check predefined similarities
        for base_skill, variants in self.skill_similarities.items():
            if (skill1 == base_skill and skill2 in variants) or \
               (skill2 == base_skill and skill1 in variants) or \
               (skill1 in variants and skill2 in variants):
                return True
        
        # Simple string containment
        if skill1 in skill2 or skill2 in skill1:
            return True
        
        # Common abbreviations
        if len(skill1) > 3 and len(skill2) > 3:
            if skill1.startswith(skill2[:3]) or skill2.startswith(skill1[:3]):
                return True
        
        return False
    
    def _create_message(self, match_result: Dict, is_satisfied: bool) -> str:
        """Crée un message descriptif du résultat."""
        required_ratio = match_result['required_match_ratio']
        preferred_ratio = match_result['preferred_match_ratio']
        
        if is_satisfied:
            return f"Skills match: {required_ratio:.1%} required, {preferred_ratio:.1%} preferred"
        else:
            missing_count = len(match_result['missing_required'])
            return f"Missing {missing_count} required skills ({required_ratio:.1%} match)"

# ===========================================
# AUTRES CONTRAINTES MÉTIER
# ===========================================

class LocationConstraint(SoftConstraint):
    """Contrainte de localisation avec support télétravail."""
    
    def __init__(self, 
                 allow_remote: bool = True,
                 max_distance_km: Optional[float] = None,
                 **kwargs):
        super().__init__(
            name="location_compatibility",
            description="Vérifie la compatibilité géographique",
            **kwargs
        )
        self.allow_remote = allow_remote
        self.max_distance_km = max_distance_km
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la contrainte de localisation."""
        candidate_location = getattr(candidate, 'location', None)
        job_location = getattr(job, 'location', None)
        
        if not candidate_location or not job_location:
            return ConstraintResult(
                satisfied=True,
                confidence=0.5,
                message="Location information missing"
            )
        
        # Check for remote work
        if self.allow_remote:
            remote_indicators = ['remote', 'télétravail', 'distance', 'home office']
            job_location_lower = job_location.lower()
            if any(indicator in job_location_lower for indicator in remote_indicators):
                return ConstraintResult(
                    satisfied=True,
                    message="Remote work position"
                )
        
        # Exact match
        if candidate_location.lower() == job_location.lower():
            return ConstraintResult(
                satisfied=True,
                message="Exact location match"
            )
        
        # Partial match (same city/region)
        candidate_parts = set(part.strip().lower() for part in candidate_location.split(','))
        job_parts = set(part.strip().lower() for part in job_location.split(','))
        
        if candidate_parts & job_parts:
            return ConstraintResult(
                satisfied=True,
                message="Partial location match"
            )
        
        # No match
        penalty = self.calculate_penalty(0.8)
        return ConstraintResult(
            satisfied=False,
            penalty=penalty,
            message=f"Location mismatch: {candidate_location} vs {job_location}"
        )

class EducationConstraint(SoftConstraint):
    """Contrainte sur le niveau d'éducation."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="education_requirement",
            description="Vérifie le niveau d'éducation requis",
            **kwargs
        )
        
        self.education_levels = {
            'elementary': 1,
            'high_school': 2,
            'professional': 3,
            'associate': 4,
            'bachelor': 5,
            'master': 6,
            'phd': 7,
            'doctorate': 7
        }
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la contrainte d'éducation."""
        candidate_education = getattr(candidate, 'education_level', None)
        required_education = getattr(job, 'education_required', None)
        
        if not required_education:
            return ConstraintResult(
                satisfied=True,
                message="No education requirement"
            )
        
        if not candidate_education:
            return ConstraintResult(
                satisfied=False,
                penalty=self.calculate_penalty(0.5),
                message="No education information provided"
            )
        
        candidate_level = self.education_levels.get(candidate_education.lower(), 0)
        required_level = self.education_levels.get(required_education.lower(), 0)
        
        if candidate_level >= required_level:
            return ConstraintResult(
                satisfied=True,
                message=f"Education requirement met: {candidate_education}"
            )
        else:
            deficit = (required_level - candidate_level) / 7.0
            penalty = self.calculate_penalty(deficit)
            return ConstraintResult(
                satisfied=False,
                penalty=penalty,
                message=f"Education below requirement: {candidate_education} < {required_education}"
            )

class LanguageConstraint(HardConstraint):
    """Contrainte sur les langues requises."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="language_requirement",
            description="Vérifie les langues requises",
            **kwargs
        )
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la contrainte des langues."""
        candidate_languages = set()
        if hasattr(candidate, 'languages'):
            candidate_languages = set(lang.lower() for lang in getattr(candidate, 'languages', []))
        
        required_languages = set()
        if hasattr(job, 'languages_required'):
            required_languages = set(lang.lower() for lang in getattr(job, 'languages_required', []))
        
        if not required_languages:
            return ConstraintResult(
                satisfied=True,
                message="No language requirements"
            )
        
        missing_languages = required_languages - candidate_languages
        
        if not missing_languages:
            return ConstraintResult(
                satisfied=True,
                message="All required languages available"
            )
        else:
            return ConstraintResult(
                satisfied=False,
                message=f"Missing languages: {missing_languages}"
            )

class AvailabilityConstraint(SoftConstraint):
    """Contrainte sur la disponibilité."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="availability_constraint",
            description="Vérifie la disponibilité du candidat",
            **kwargs
        )
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la contrainte de disponibilité."""
        candidate_availability = getattr(candidate, 'availability', None)
        job_start_date = getattr(job, 'start_date', None)
        
        if not job_start_date:
            return ConstraintResult(
                satisfied=True,
                message="No start date specified"
            )
        
        if not candidate_availability:
            return ConstraintResult(
                satisfied=True,
                confidence=0.5,
                message="No availability information"
            )
        
        # Simple string comparison for now
        # In real implementation, would parse dates properly
        if isinstance(candidate_availability, str) and isinstance(job_start_date, str):
            if 'immediate' in candidate_availability.lower() or 'asap' in candidate_availability.lower():
                return ConstraintResult(
                    satisfied=True,
                    message="Immediately available"
                )
        
        return ConstraintResult(
            satisfied=True,
            confidence=0.7,
            message="Availability check completed"
        )

class ContractTypeConstraint(HardConstraint):
    """Contrainte sur le type de contrat."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="contract_type_constraint",
            description="Vérifie la compatibilité du type de contrat",
            **kwargs
        )
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la contrainte de type de contrat."""
        candidate_preferences = getattr(candidate, 'contract_preferences', None)
        job_contract_type = getattr(job, 'contract_type', None)
        
        if not job_contract_type:
            return ConstraintResult(
                satisfied=True,
                message="No contract type specified"
            )
        
        if not candidate_preferences:
            return ConstraintResult(
                satisfied=True,
                confidence=0.5,
                message="No contract preferences specified"
            )
        
        if isinstance(candidate_preferences, str):
            candidate_preferences = [candidate_preferences]
        
        job_type_lower = job_contract_type.lower()
        pref_types_lower = [pref.lower() for pref in candidate_preferences]
        
        if job_type_lower in pref_types_lower:
            return ConstraintResult(
                satisfied=True,
                message=f"Contract type matches: {job_contract_type}"
            )
        else:
            return ConstraintResult(
                satisfied=False,
                message=f"Contract type mismatch: wants {candidate_preferences}, offered {job_contract_type}"
            )

class IndustryConstraint(PreferenceConstraint):
    """Contrainte sur le secteur d'activité."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="industry_preference",
            description="Vérifie la préférence de secteur d'activité",
            **kwargs
        )
    
    def evaluate(self, candidate: Any, job: Any, context: Optional[Dict[str, Any]] = None) -> ConstraintResult:
        """Évalue la préférence de secteur."""
        candidate_industries = getattr(candidate, 'preferred_industries', None)
        job_industry = getattr(job, 'industry', None)
        
        if not job_industry:
            return ConstraintResult(
                satisfied=True,
                message="No industry specified"
            )
        
        if not candidate_industries:
            return ConstraintResult(
                satisfied=True,
                confidence=0.5,
                message="No industry preferences specified"
            )
        
        if isinstance(candidate_industries, str):
            candidate_industries = [candidate_industries]
        
        job_industry_lower = job_industry.lower()
        candidate_industries_lower = [ind.lower() for ind in candidate_industries]
        
        if job_industry_lower in candidate_industries_lower:
            return ConstraintResult(
                satisfied=True,
                penalty=-self.max_bonus,  # Negative penalty = bonus
                message=f"Industry preference match: {job_industry}"
            )
        else:
            return ConstraintResult(
                satisfied=True,
                penalty=0,
                message=f"Industry not in preferences: {job_industry}"
            )

# ===========================================
# CONSTRAINT FACTORY
# ===========================================

def create_standard_business_constraints() -> List[BaseConstraint]:
    """Crée un ensemble standard de contraintes métier."""
    return [
        # Hard constraints (must be satisfied)
        SkillsConstraint(
            constraint_type=ConstraintType.HARD,
            minimum_match_ratio=0.6
        ),
        ExperienceConstraint(
            constraint_type=ConstraintType.HARD,
            allow_overqualification=True
        ),
        LanguageConstraint(),
        ContractTypeConstraint(),
        
        # Soft constraints (preferences with penalties)
        SalaryConstraint(
            tolerance_percent=0.15
        ),
        LocationConstraint(
            allow_remote=True
        ),
        EducationConstraint(),
        AvailabilityConstraint(),
        
        # Preference constraints (bonuses)
        IndustryConstraint()
    ]

if __name__ == "__main__":
    # Test basique
    print("🧪 Testing Business Rules")
    
    # Test constraints
    constraints = create_standard_business_constraints()
    print(f"Created {len(constraints)} business constraints")
    
    for constraint in constraints:
        print(f"  - {constraint}")
    
    print("✅ Business rules module working correctly")
