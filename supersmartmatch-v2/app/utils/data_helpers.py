"""
Utilitaires pour la validation et transformation des données

Fournit des helpers pour :
- Validation des données d'entrée
- Transformation des formats
- Nettoyage et normalisation
- Détection d'anomalies
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..models.matching_models import CVData, JobData

logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validateur de données pour SuperSmartMatch V2
    
    Valide et nettoie les données d'entrée pour assurer
    la qualité et la cohérence.
    """
    
    @staticmethod
    def validate_cv_data(cv_data: CVData) -> Tuple[bool, List[str]]:
        """
        Valide les données CV
        
        Args:
            cv_data: Données CV à valider
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        # Validation des compétences
        if not cv_data.competences:
            errors.append("Aucune compétence spécifiée")
        else:
            # Vérifier la qualité des compétences
            for skill in cv_data.competences:
                if len(skill.strip()) < 2:
                    errors.append(f"Compétence trop courte: '{skill}'")
                if len(skill) > 100:
                    errors.append(f"Compétence trop longue: '{skill[:20]}...'")
        
        # Validation de l'expérience
        if cv_data.experience is not None:
            if cv_data.experience < 0:
                errors.append("L'expérience ne peut pas être négative")
            if cv_data.experience > 70:
                errors.append("Expérience irréaliste (> 70 ans)")
        
        # Validation de l'âge
        if cv_data.age is not None:
            if cv_data.age < 16 or cv_data.age > 100:
                errors.append(f"Âge invalide: {cv_data.age}")
        
        # Validation de la localisation
        if cv_data.localisation:
            if len(cv_data.localisation.strip()) < 2:
                errors.append("Localisation trop courte")
        
        # Validation de la mobilité
        if cv_data.mobilite_km is not None:
            if cv_data.mobilite_km < 0 or cv_data.mobilite_km > 1000:
                errors.append(f"Mobilité irréaliste: {cv_data.mobilite_km} km")
        
        # Cohérence âge/expérience
        if cv_data.age and cv_data.experience:
            if cv_data.experience > (cv_data.age - 16):
                errors.append("Expérience incohérente avec l'âge")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_jobs_data(jobs: List[JobData]) -> Tuple[bool, List[str]]:
        """
        Valide les données des jobs
        
        Args:
            jobs: Liste des jobs à valider
            
        Returns:
            Tuple (is_valid, list_of_errors)
        """
        errors = []
        
        if not jobs:
            errors.append("Aucun job fourni")
            return False, errors
        
        if len(jobs) > 100:  # Limite configurable
            errors.append(f"Trop de jobs: {len(jobs)} (max: 100)")
        
        # Vérifier les IDs uniques
        job_ids = [job.id for job in jobs]
        if len(job_ids) != len(set(job_ids)):
            errors.append("IDs de jobs non uniques")
        
        # Validation individuelle des jobs
        for i, job in enumerate(jobs):
            job_errors = DataValidator._validate_single_job(job, i)
            errors.extend(job_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_single_job(job: JobData, index: int) -> List[str]:
        """Valide un job individuel"""
        errors = []
        job_prefix = f"Job {index + 1} (ID: {job.id})"
        
        # ID obligatoire
        if not job.id or not job.id.strip():
            errors.append(f"{job_prefix}: ID manquant")
        
        # Validation des compétences
        if job.competences:
            for skill in job.competences:
                if len(skill.strip()) < 2:
                    errors.append(f"{job_prefix}: Compétence trop courte '{skill}'")
        
        # Validation de l'expérience requise
        if job.experience_requise is not None:
            if job.experience_requise < 0 or job.experience_requise > 50:
                errors.append(f"{job_prefix}: Expérience requise irréaliste")
        
        # Validation des salaires
        if job.salaire_min and job.salaire_max:
            if job.salaire_min > job.salaire_max:
                errors.append(f"{job_prefix}: Salaire min > max")
            if job.salaire_min < 0 or job.salaire_max < 0:
                errors.append(f"{job_prefix}: Salaires négatifs")
        
        return errors


class DataTransformer:
    """
    Transformateur de données pour SuperSmartMatch V2
    
    Nettoie, normalise et enrichit les données d'entrée.
    """
    
    @staticmethod
    def clean_cv_data(cv_data: CVData) -> CVData:
        """
        Nettoie et normalise les données CV
        
        Args:
            cv_data: Données CV à nettoyer
            
        Returns:
            CVData nettoyées
        """
        # Copie pour éviter la mutation
        cleaned_data = cv_data.copy(deep=True)
        
        # Nettoyage des compétences
        if cleaned_data.competences:
            cleaned_data.competences = DataTransformer._clean_skills_list(
                cleaned_data.competences
            )
        
        # Nettoyage de la localisation
        if cleaned_data.localisation:
            cleaned_data.localisation = DataTransformer._normalize_location(
                cleaned_data.localisation
            )
        
        # Nettoyage des certifications
        if cleaned_data.certifications:
            cleaned_data.certifications = DataTransformer._clean_skills_list(
                cleaned_data.certifications
            )
        
        # Nettoyage des noms
        if cleaned_data.nom:
            cleaned_data.nom = DataTransformer._clean_text(cleaned_data.nom)
        if cleaned_data.prenom:
            cleaned_data.prenom = DataTransformer._clean_text(cleaned_data.prenom)
        
        logger.debug(f"CV nettoyé: {len(cleaned_data.competences)} compétences")
        return cleaned_data
    
    @staticmethod
    def clean_jobs_data(jobs: List[JobData]) -> List[JobData]:
        """
        Nettoie et normalise les données des jobs
        
        Args:
            jobs: Liste des jobs à nettoyer
            
        Returns:
            Liste des JobData nettoyées
        """
        cleaned_jobs = []
        
        for job in jobs:
            cleaned_job = job.copy(deep=True)
            
            # Nettoyage des compétences
            if cleaned_job.competences:
                cleaned_job.competences = DataTransformer._clean_skills_list(
                    cleaned_job.competences
                )
            
            # Nettoyage de la localisation
            if cleaned_job.localisation:
                cleaned_job.localisation = DataTransformer._normalize_location(
                    cleaned_job.localisation
                )
            
            # Nettoyage des certifications
            if cleaned_job.certifications_requises:
                cleaned_job.certifications_requises = DataTransformer._clean_skills_list(
                    cleaned_job.certifications_requises
                )
            
            # Nettoyage des textes
            if cleaned_job.titre:
                cleaned_job.titre = DataTransformer._clean_text(cleaned_job.titre)
            if cleaned_job.entreprise:
                cleaned_job.entreprise = DataTransformer._clean_text(cleaned_job.entreprise)
            if cleaned_job.description:
                cleaned_job.description = DataTransformer._clean_text(cleaned_job.description)
            
            cleaned_jobs.append(cleaned_job)
        
        logger.debug(f"{len(cleaned_jobs)} jobs nettoyés")
        return cleaned_jobs
    
    @staticmethod
    def _clean_skills_list(skills: List[str]) -> List[str]:
        """Nettoie une liste de compétences"""
        cleaned_skills = []
        
        for skill in skills:
            # Nettoyage de base
            cleaned_skill = skill.strip()
            
            # Supprimer les compétences trop courtes
            if len(cleaned_skill) < 2:
                continue
            
            # Normalisation de la casse
            cleaned_skill = DataTransformer._normalize_skill_case(cleaned_skill)
            
            # Éviter les doublons (insensible à la casse)
            if not any(existing.lower() == cleaned_skill.lower() for existing in cleaned_skills):
                cleaned_skills.append(cleaned_skill)
        
        return cleaned_skills
    
    @staticmethod
    def _normalize_skill_case(skill: str) -> str:
        """Normalise la casse d'une compétence"""
        # Technologies connues avec casse spécifique
        known_cases = {
            'javascript': 'JavaScript',
            'typescript': 'TypeScript',
            'python': 'Python',
            'java': 'Java',
            'c++': 'C++',
            'c#': 'C#',
            'html': 'HTML',
            'css': 'CSS',
            'sql': 'SQL',
            'react': 'React',
            'angular': 'Angular',
            'vue': 'Vue.js',
            'nodejs': 'Node.js',
            'php': 'PHP',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'aws': 'AWS',
            'azure': 'Azure',
            'gcp': 'GCP'
        }
        
        skill_lower = skill.lower()
        
        # Vérifier si c'est une technologie connue
        for key, value in known_cases.items():
            if key in skill_lower:
                return skill.replace(key, value, 1)
        
        # Par défaut, capitaliser la première lettre
        return skill.capitalize()
    
    @staticmethod
    def _normalize_location(location: str) -> str:
        """Normalise une localisation"""
        # Nettoyage de base
        location = location.strip()
        
        # Suppression des caractères spéciaux multiples
        location = re.sub(r'[,;]{2,}', ',', location)
        location = re.sub(r'\s{2,}', ' ', location)
        
        # Capitalisation
        parts = [part.strip().capitalize() for part in location.split(',')]
        
        return ', '.join(parts)
    
    @staticmethod
    def _clean_text(text: str) -> str:
        """Nettoie un texte générique"""
        if not text:
            return text
        
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Suppression des caractères de contrôle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        return text
    
    @staticmethod
    def enrich_cv_data(cv_data: CVData) -> CVData:
        """
        Enrichit les données CV avec des informations calculées
        
        Args:
            cv_data: Données CV à enrichir
            
        Returns:
            CVData enrichies
        """
        enriched_data = cv_data.copy(deep=True)
        
        # Calcul du score de complétude
        if not enriched_data.score_completude:
            enriched_data.score_completude = DataTransformer._calculate_completeness_score(cv_data)
        
        # Mise à jour timestamp
        if not enriched_data.derniere_mise_a_jour:
            enriched_data.derniere_mise_a_jour = datetime.now()
        
        logger.debug(f"CV enrichi - Score complétude: {enriched_data.score_completude:.1f}%")
        return enriched_data
    
    @staticmethod
    def _calculate_completeness_score(cv_data: CVData) -> float:
        """Calcule un score de complétude du CV"""
        score = 0.0
        max_score = 100.0
        
        # Compétences (30 points)
        if cv_data.competences:
            skill_score = min(len(cv_data.competences) / 5 * 30, 30)
            score += skill_score
        
        # Expérience (20 points)
        if cv_data.experience is not None:
            score += 20
        
        # Localisation (15 points)
        if cv_data.localisation:
            score += 15
        
        # Niveau d'études (10 points)
        if cv_data.niveau_etudes:
            score += 10
        
        # Certifications (10 points)
        if cv_data.certifications:
            cert_score = min(len(cv_data.certifications) / 3 * 10, 10)
            score += cert_score
        
        # Préférences (10 points)
        pref_score = 0
        if cv_data.salaire_souhaite:
            pref_score += 3
        if cv_data.type_contrat_souhaite:
            pref_score += 3
        if cv_data.mobilite_km is not None:
            pref_score += 2
        if cv_data.teletravail_accepte is not None:
            pref_score += 2
        score += pref_score
        
        # Questionnaire (5 points)
        if cv_data.questionnaire_complete:
            score += 5
        
        return min(score, max_score)


class DataAnalyzer:
    """
    Analyseur de données pour détecter des patterns et anomalies
    """
    
    @staticmethod
    def analyze_skills_overlap(cv_skills: List[str], job_skills: List[str]) -> Dict[str, Any]:
        """
        Analyse le chevauchement des compétences
        
        Args:
            cv_skills: Compétences du CV
            job_skills: Compétences requises pour le job
            
        Returns:
            Analyse détaillée du chevauchement
        """
        cv_skills_lower = [skill.lower() for skill in cv_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        # Matches exacts
        exact_matches = []
        for job_skill in job_skills:
            if job_skill.lower() in cv_skills_lower:
                exact_matches.append(job_skill)
        
        # Matches partiels
        partial_matches = []
        for cv_skill in cv_skills:
            for job_skill in job_skills:
                if (cv_skill.lower() in job_skill.lower() or 
                    job_skill.lower() in cv_skill.lower()) and \
                   job_skill.lower() not in [m.lower() for m in exact_matches]:
                    partial_matches.append((cv_skill, job_skill))
        
        # Compétences manquantes
        missing_skills = [skill for skill in job_skills if skill.lower() not in cv_skills_lower]
        
        # Calcul des scores
        if job_skills:
            exact_match_rate = len(exact_matches) / len(job_skills)
            coverage_rate = (len(exact_matches) + len(partial_matches) * 0.5) / len(job_skills)
        else:
            exact_match_rate = 0.0
            coverage_rate = 0.0
        
        return {
            "exact_matches": exact_matches,
            "partial_matches": partial_matches,
            "missing_skills": missing_skills,
            "exact_match_rate": exact_match_rate,
            "coverage_rate": coverage_rate,
            "total_cv_skills": len(cv_skills),
            "total_job_skills": len(job_skills)
        }
    
    @staticmethod
    def detect_data_quality_issues(cv_data: CVData, jobs: List[JobData]) -> List[str]:
        """
        Détecte les problèmes de qualité des données
        
        Args:
            cv_data: Données CV
            jobs: Liste des jobs
            
        Returns:
            Liste des problèmes détectés
        """
        issues = []
        
        # Problèmes CV
        if len(cv_data.competences) < 3:
            issues.append("Peu de compétences renseignées (< 3)")
        
        if not cv_data.localisation:
            issues.append("Localisation manquante")
        
        if cv_data.experience is None:
            issues.append("Expérience non renseignée")
        
        # Problèmes jobs
        jobs_without_skills = sum(1 for job in jobs if not job.competences)
        if jobs_without_skills > len(jobs) * 0.5:
            issues.append(f"{jobs_without_skills} jobs sans compétences spécifiées")
        
        jobs_without_location = sum(1 for job in jobs if not job.localisation)
        if jobs_without_location > len(jobs) * 0.3:
            issues.append(f"{jobs_without_location} jobs sans localisation")
        
        return issues
