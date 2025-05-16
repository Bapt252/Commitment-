"""
SmartMatch - Système de matching bidirectionnel avancé
-------------------------------------------------------------
Système de matching bidirectionnel prenant en compte le temps de trajet,
l'analyse des compétences et générant des insights détaillés.

"""

import os
import json
import logging
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache
try:
    import nltk
    from nltk.corpus import wordnet
    nltk_available = True
except ImportError:
    nltk_available = False

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Téléchargement des ressources NLTK si disponibles
if nltk_available:
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')

class SmartMatcher:
    """
    Système avancé de matching bidirectionnel pour mettre en relation les candidats et les offres d'emploi.
    """
    
    def __init__(self, api_key: str = None, use_cache: bool = True, cache_size: int = 1000):
        """
        Initialisation du SmartMatcher
        
        Args:
            api_key (str): Clé API Google Maps pour les calculs de distance
            use_cache (bool): Activer le cache pour les calculs de distance
            cache_size (int): Taille du cache pour les calculs de distance
        """
        # Utiliser la clé API fournie ou la variable d'environnement
        self.api_key = api_key or os.environ.get("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            logger.warning("Aucune clé API Google Maps fournie. Les calculs de distance seront simplifiés.")
        
        self.use_cache = use_cache
        self.cache_size = cache_size
        
        # Initialisation des outils NLP
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
        # Dictionnaire de synonymes pour les compétences
        self.skill_synonyms = self._build_skill_synonyms()
        
        # Facteurs de pondération
        self.weights = {
            "skills": 0.40,
            "location": 0.25,
            "experience": 0.15,
            "education": 0.10,
            "preferences": 0.10
        }
        
        logger.info("SmartMatcher initialisé avec succès")
    
    def _build_skill_synonyms(self) -> Dict[str, List[str]]:
        """
        Construit un dictionnaire de synonymes pour les compétences techniques courantes
        
        Returns:
            Dict[str, List[str]]: Dictionnaire de compétences avec leurs synonymes
        """
        synonyms = {
            "javascript": ["js", "ecmascript", "node.js", "nodejs", "react.js", "reactjs", "vue.js", "vuejs"],
            "python": ["py", "python3", "django", "flask", "pytorch", "tensorflow"],
            "java": ["spring", "hibernate", "j2ee", "javase", "javaee"],
            "php": ["laravel", "symfony", "wordpress", "drupal"],
            "csharp": ["c#", ".net", "dotnet", "asp.net", "aspnet"],
            "cplusplus": ["c++", "cpp"],
            "ruby": ["ror", "rails", "ruby on rails"],
            "machine learning": ["ml", "ai", "artificial intelligence", "deep learning", "tensorflow", "pytorch", "keras"],
            "devops": ["ci/cd", "continuous integration", "continuous deployment", "docker", "kubernetes", "k8s"],
            "frontend": ["front-end", "ui", "user interface", "html", "css", "javascript", "js"],
            "backend": ["back-end", "server-side", "api", "middleware"],
            "fullstack": ["full-stack", "full stack", "frontend and backend", "front-end and back-end"]
        }
        
        # Ajouter des synonymes à partir de WordNet si disponible
        if nltk_available:
            for skill, syn_list in synonyms.items():
                for synset in wordnet.synsets(skill):
                    for lemma in synset.lemmas():
                        if lemma.name() not in syn_list and lemma.name() != skill:
                            syn_list.append(lemma.name())
        
        logger.info(f"Dictionnaire de {len(synonyms)} compétences avec synonymes créé")
        return synonyms
    
    def expand_skills(self, skills_list: List[str]) -> List[str]:
        """
        Étend une liste de compétences avec des synonymes
        
        Args:
            skills_list (List[str]): Liste originale de compétences
            
        Returns:
            List[str]: Liste étendue avec synonymes
        """
        expanded = []
        for skill in skills_list:
            skill_lower = skill.lower()
            expanded.append(skill)
            
            # Ajouter les synonymes directs
            for main_skill, synonyms in self.skill_synonyms.items():
                if skill_lower == main_skill or skill_lower in [s.lower() for s in synonyms]:
                    expanded.extend([s for s in synonyms if s.lower() != skill_lower])
                    expanded.append(main_skill)
        
        # Supprimer les doublons et préserver l'ordre
        expanded_unique = []
        seen = set()
        for skill in expanded:
            if skill.lower() not in seen:
                expanded_unique.append(skill)
                seen.add(skill.lower())
        
        return expanded_unique
    
    @lru_cache(maxsize=1000)
    def calculate_travel_time(self, origin: str, destination: str) -> int:
        """
        Calcule le temps de trajet entre deux emplacements en utilisant Google Maps API
        
        Args:
            origin (str): Emplacement d'origine (adresse ou coordonnées)
            destination (str): Emplacement de destination (adresse ou coordonnées)
            
        Returns:
            int: Temps de trajet en minutes, ou estimation simplifiée si pas de clé API
        """
        if not self.api_key:
            # Mode de secours avec estimation simplifiée basée sur la distance euclidienne
            try:
                # Extraire les coordonnées (format attendu: "latitude,longitude")
                orig_lat, orig_lng = map(float, origin.split(','))
                dest_lat, dest_lng = map(float, destination.split(','))
                
                # Calculer une distance euclidienne grossière
                # (approximation, ne prend pas en compte la courbure terrestre)
                distance = ((orig_lat - dest_lat) ** 2 + (orig_lng - dest_lng) ** 2) ** 0.5
                
                # Conversion approximative en minutes (60 km/h en moyenne)
                # 1 degré ~ 111 km à l'équateur
                distance_km = distance * 111
                time_minutes = (distance_km / 60) * 60
                
                return int(time_minutes)
                
            except Exception as e:
                logger.error(f"Erreur lors de l'estimation simplifiée du temps de trajet: {str(e)}")
                return 30  # Valeur par défaut en minutes
        
        try:
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
            params = {
                "origins": origin,
                "destinations": destination,
                "mode": "driving",
                "key": self.api_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data["status"] == "OK":
                elements = data["rows"][0]["elements"]
                if elements[0]["status"] == "OK":
                    duration_seconds = elements[0]["duration"]["value"]
                    duration_minutes = duration_seconds // 60
                    return duration_minutes
            
            logger.warning(f"Erreur dans la réponse de l'API Google Maps: {data['status']}")
            return 30  # Valeur par défaut en minutes
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps de trajet: {str(e)}")
            return 30  # Valeur par défaut en minutes
    
    def calculate_skill_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance des compétences entre un candidat et une offre d'emploi
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Extraire les compétences
        candidate_skills = candidate.get("skills", [])
        job_skills = job.get("required_skills", []) + job.get("preferred_skills", [])
        
        if not candidate_skills or not job_skills:
            logger.warning("Compétences manquantes pour le candidat ou l'offre")
            return 0.5  # Score neutre si pas de compétences disponibles
        
        # Étendre les compétences avec des synonymes
        candidate_skills_expanded = self.expand_skills(candidate_skills)
        job_skills_expanded = self.expand_skills(job_skills)
        
        # Créer des documents pour l'analyse vectorielle
        candidate_doc = " ".join(candidate_skills_expanded)
        job_doc = " ".join(job_skills_expanded)
        
        # Calculer la similarité
        try:
            X = self.vectorizer.fit_transform([candidate_doc, job_doc])
            similarity = cosine_similarity(X[0:1], X[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la similarité des compétences: {str(e)}")
            return 0.5  # Score neutre en cas d'erreur
    
    def calculate_location_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance de localisation entre un candidat et une offre d'emploi
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Si les deux proposent le travail à distance, le score est parfait
        if candidate.get("remote_work", False) and job.get("offers_remote", False):
            return 1.0
        
        candidate_location = candidate.get("location", "")
        job_location = job.get("location", "")
        
        if not candidate_location or not job_location:
            logger.warning("Information de localisation manquante")
            return 0.5  # Score neutre si pas de localisation disponible
        
        # Calculer le temps de trajet
        travel_time = self.calculate_travel_time(candidate_location, job_location)
        
        # Convertir le temps de trajet en score
        # Moins de 30 min = excellent, 1-2h = acceptable, >2h = mauvais
        if travel_time <= 30:
            score = 1.0
        elif travel_time <= 60:
            score = 0.8
        elif travel_time <= 90:
            score = 0.6
        elif travel_time <= 120:
            score = 0.4
        else:
            score = 0.2
        
        return score
    
    def calculate_experience_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance d'expérience entre un candidat et une offre d'emploi
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        candidate_years = candidate.get("years_of_experience", 0)
        min_years = job.get("min_years_of_experience", 0)
        max_years = job.get("max_years_of_experience", 100)  # Valeur par défaut très haute
        
        # Si le candidat a moins que le minimum requis
        if candidate_years < min_years:
            gap = min_years - candidate_years
            if gap >= 5:
                return 0.2  # Trop peu d'expérience
            else:
                return 0.5 - (gap * 0.06)  # Score dégressif
        
        # Si le candidat a plus que le maximum requis (surqualifié)
        if max_years < 100 and candidate_years > max_years:
            gap = candidate_years - max_years
            if gap >= 10:
                return 0.5  # Très surqualifié, mais toujours considéré
            else:
                return 0.9 - (gap * 0.04)  # Score légèrement dégressif
        
        # Dans la fourchette idéale
        return 1.0
    
    def calculate_education_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance d'éducation entre un candidat et une offre d'emploi
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        # Mapping des niveaux d'éducation à des valeurs numériques
        education_levels = {
            "none": 0,
            "high_school": 1,
            "associate": 2,
            "bachelor": 3,
            "master": 4,
            "phd": 5
        }
        
        candidate_education = candidate.get("education_level", "none").lower()
        required_education = job.get("required_education", "none").lower()
        
        # Convertir en valeurs numériques
        candidate_level = education_levels.get(candidate_education, 0)
        required_level = education_levels.get(required_education, 0)
        
        # Si le candidat a un niveau inférieur au requis
        if candidate_level < required_level:
            return 0.3  # Score faible
        
        # Si le candidat a exactement le niveau requis
        if candidate_level == required_level:
            return 1.0  # Score parfait
        
        # Si le candidat a un niveau supérieur au requis
        gap = candidate_level - required_level
        if gap == 1:
            return 0.9  # Un niveau au-dessus
        elif gap == 2:
            return 0.7  # Deux niveaux au-dessus
        else:
            return 0.5  # Trois niveaux ou plus au-dessus
    
    def calculate_preference_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> float:
        """
        Calcule le score de correspondance des préférences entre un candidat et une offre d'emploi
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            float: Score de correspondance entre 0 et 1
        """
        scores = []
        
        # Vérifier si le travail à distance correspond aux attentes
        if "remote_work" in candidate and "offers_remote" in job:
            candidate_wants_remote = candidate["remote_work"]
            job_offers_remote = job["offers_remote"]
            
            if candidate_wants_remote and job_offers_remote:
                scores.append(1.0)  # Match parfait
            elif candidate_wants_remote and not job_offers_remote:
                scores.append(0.2)  # Le candidat veut du remote mais pas offert
            elif not candidate_wants_remote and job_offers_remote:
                scores.append(0.8)  # Le poste offre du remote mais pas demandé
            else:
                scores.append(1.0)  # Les deux ne veulent pas de remote
        
        # Vérifier si les attentes salariales correspondent
        if "salary_expectation" in candidate and "salary_range" in job:
            candidate_salary = candidate["salary_expectation"]
            job_min_salary = job["salary_range"].get("min", 0)
            job_max_salary = job["salary_range"].get("max", 0)
            
            if job_min_salary <= candidate_salary <= job_max_salary:
                scores.append(1.0)  # Dans la fourchette
            elif candidate_salary < job_min_salary:
                # Le candidat demande moins que le minimum offert
                if job_min_salary > 0:
                    ratio = candidate_salary / job_min_salary
                    scores.append(min(1.0, 0.7 + ratio * 0.3))
                else:
                    scores.append(0.5)
            else:
                # Le candidat demande plus que le maximum offert
                if job_max_salary > 0:
                    if candidate_salary > job_max_salary * 1.5:
                        scores.append(0.1)  # Beaucoup trop élevé
                    else:
                        ratio = job_max_salary / candidate_salary
                        scores.append(max(0.1, ratio * 0.9))
                else:
                    scores.append(0.5)
        
        # Vérifier si le type de contrat correspond
        if "job_type" in candidate and "job_type" in job:
            if candidate["job_type"] == job["job_type"]:
                scores.append(1.0)
            else:
                scores.append(0.3)
        
        # Vérifier si le secteur d'activité correspond
        if "industry" in candidate and "industry" in job:
            if candidate["industry"] == job["industry"]:
                scores.append(1.0)
            else:
                # Vérifier si le secteur est dans les préférences alternatives
                if "alternative_industries" in candidate and job["industry"] in candidate["alternative_industries"]:
                    scores.append(0.7)
                else:
                    scores.append(0.3)
        
        # Calculer le score moyen, ou retourner un score neutre si aucune préférence n'est évaluée
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.5
    
    def calculate_match(self, candidate: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le score global de correspondance entre un candidat et une offre d'emploi
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            
        Returns:
            Dict: Résultat du matching avec scores et insights
        """
        # Calculer les scores par catégorie
        skill_score = self.calculate_skill_match(candidate, job)
        location_score = self.calculate_location_match(candidate, job)
        experience_score = self.calculate_experience_match(candidate, job)
        education_score = self.calculate_education_match(candidate, job)
        preference_score = self.calculate_preference_match(candidate, job)
        
        # Calculer le score global pondéré
        overall_score = (
            skill_score * self.weights["skills"] +
            location_score * self.weights["location"] +
            experience_score * self.weights["experience"] +
            education_score * self.weights["education"] +
            preference_score * self.weights["preferences"]
        )
        
        # Générer des insights
        insights = self.generate_insights(
            candidate, job,
            skill_score, location_score, experience_score, 
            education_score, preference_score
        )
        
        # Retourner le résultat complet
        return {
            "candidate_id": candidate.get("id", ""),
            "job_id": job.get("id", ""),
            "overall_score": round(overall_score, 2),
            "category_scores": {
                "skills": round(skill_score, 2),
                "location": round(location_score, 2),
                "experience": round(experience_score, 2),
                "education": round(education_score, 2),
                "preferences": round(preference_score, 2)
            },
            "insights": insights
        }
    
    def generate_insights(self, 
                         candidate: Dict[str, Any], 
                         job: Dict[str, Any],
                         skill_score: float,
                         location_score: float,
                         experience_score: float,
                         education_score: float,
                         preference_score: float) -> List[Dict[str, Any]]:
        """
        Génère des insights détaillés sur le match entre un candidat et une offre d'emploi
        
        Args:
            candidate (Dict): Profil du candidat
            job (Dict): Offre d'emploi
            skill_score (float): Score de compétences
            location_score (float): Score de localisation
            experience_score (float): Score d'expérience
            education_score (float): Score d'éducation
            preference_score (float): Score de préférences
            
        Returns:
            List[Dict]: Liste d'insights avec type, message et score
        """
        insights = []
        
        # Insights sur les compétences
        if skill_score >= 0.8:
            insights.append({
                "type": "skill_match",
                "message": "Excellente correspondance des compétences techniques",
                "score": skill_score,
                "category": "strength"
            })
        elif skill_score >= 0.6:
            insights.append({
                "type": "skill_match",
                "message": "Bonne correspondance des compétences techniques",
                "score": skill_score,
                "category": "strength"
            })
        elif skill_score <= 0.4:
            insights.append({
                "type": "skill_gap",
                "message": "Écart important dans les compétences techniques requises",
                "score": skill_score,
                "category": "weakness"
            })
        
        # Insights sur la localisation
        if candidate.get("remote_work", False) and job.get("offers_remote", False):
            insights.append({
                "type": "remote_match",
                "message": "Compatibilité parfaite pour le travail à distance",
                "score": 1.0,
                "category": "strength"
            })
        elif location_score >= 0.8:
            insights.append({
                "type": "location_match",
                "message": "Temps de trajet optimal",
                "score": location_score,
                "category": "strength"
            })
        elif location_score <= 0.4:
            insights.append({
                "type": "location_issue",
                "message": "Distance de trajet importante",
                "score": location_score,
                "category": "weakness"
            })
        
        # Insights sur l'expérience
        candidate_years = candidate.get("years_of_experience", 0)
        min_years = job.get("min_years_of_experience", 0)
        
        if candidate_years < min_years:
            insights.append({
                "type": "experience_gap",
                "message": f"Expérience inférieure au minimum requis ({candidate_years} vs {min_years} ans)",
                "score": experience_score,
                "category": "weakness"
            })
        elif experience_score >= 0.9:
            insights.append({
                "type": "experience_match",
                "message": "Niveau d'expérience idéal pour ce poste",
                "score": experience_score,
                "category": "strength"
            })
        
        # Insights sur l'éducation
        if education_score <= 0.5:
            insights.append({
                "type": "education_gap",
                "message": "Niveau d'éducation inférieur aux prérequis",
                "score": education_score,
                "category": "weakness"
            })
        elif education_score >= 0.9:
            insights.append({
                "type": "education_match",
                "message": "Niveau d'éducation parfait pour ce poste",
                "score": education_score,
                "category": "strength"
            })
        
        # Insights sur les préférences
        if "remote_work" in candidate and "offers_remote" in job:
            if candidate["remote_work"] and not job["offers_remote"]:
                insights.append({
                    "type": "remote_mismatch",
                    "message": "Le candidat préfère le travail à distance, mais ce n'est pas offert",
                    "score": 0.2,
                    "category": "mismatch"
                })
        
        if "salary_expectation" in candidate and "salary_range" in job:
            candidate_salary = candidate["salary_expectation"]
            job_max_salary = job["salary_range"].get("max", 0)
            
            if job_max_salary > 0 and candidate_salary > job_max_salary:
                insights.append({
                    "type": "salary_mismatch",
                    "message": "Attentes salariales supérieures au budget du poste",
                    "score": min(0.5, job_max_salary / candidate_salary) if candidate_salary > 0 else 0.5,
                    "category": "mismatch"
                })
        
        return insights
    
    def batch_match(self, candidates: List[Dict[str, Any]], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Effectue un matching par lots entre plusieurs candidats et offres d'emploi
        
        Args:
            candidates (List[Dict]): Liste des profils candidats
            jobs (List[Dict]): Liste des offres d'emploi
            
        Returns:
            List[Dict]: Résultats de matching pour toutes les paires
        """
        results = []
        
        # Logging
        start_time = time.time()
        total_pairs = len(candidates) * len(jobs)
        logger.info(f"Démarrage du batch matching pour {len(candidates)} candidats et {len(jobs)} offres ({total_pairs} paires)")
        
        # Effectuer le matching pour chaque paire
        for candidate in candidates:
            for job in jobs:
                match_result = self.calculate_match(candidate, job)
                results.append(match_result)
        
        # Logging
        duration = time.time() - start_time
        avg_time = duration / total_pairs if total_pairs > 0 else 0
        logger.info(f"Batch matching terminé en {duration:.2f}s ({avg_time:.4f}s par paire)")
        
        return results
    
    def load_test_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Charge des données de test pour le matching
        
        Returns:
            Dict: Dictionnaire contenant des candidats et des offres de test
        """
        # Données candidates de test
        candidates = [
            {
                "id": "c1",
                "name": "Jean Dupont",
                "skills": ["Python", "Django", "JavaScript", "React", "SQL", "Git"],
                "location": "48.8566,2.3522",  # Paris
                "years_of_experience": 5,
                "education_level": "master",
                "remote_work": True,
                "salary_expectation": 65000,
                "job_type": "full_time",
                "industry": "tech"
            },
            {
                "id": "c2",
                "name": "Marie Martin",
                "skills": ["Java", "Spring", "Hibernate", "PostgreSQL", "Docker", "Kubernetes"],
                "location": "45.7640,4.8357",  # Lyon
                "years_of_experience": 8,
                "education_level": "bachelor",
                "remote_work": False,
                "salary_expectation": 70000,
                "job_type": "full_time",
                "industry": "finance",
                "alternative_industries": ["tech", "consulting"]
            },
            {
                "id": "c3",
                "name": "Thomas Petit",
                "skills": ["JavaScript", "Vue.js", "Node.js", "Express", "MongoDB", "AWS"],
                "location": "43.2965,5.3698",  # Marseille
                "years_of_experience": 3,
                "education_level": "bachelor",
                "remote_work": True,
                "salary_expectation": 52000,
                "job_type": "contract",
                "industry": "tech"
            }
        ]
        
        # Données d'offres d'emploi de test
        jobs = [
            {
                "id": "j1",
                "title": "Développeur Python Senior",
                "required_skills": ["Python", "Django", "SQL"],
                "preferred_skills": ["React", "Docker", "AWS"],
                "location": "48.8847,2.2967",  # Levallois-Perret
                "min_years_of_experience": 4,
                "max_years_of_experience": 8,
                "required_education": "bachelor",
                "offers_remote": True,
                "salary_range": {"min": 55000, "max": 75000},
                "job_type": "full_time",
                "industry": "tech"
            },
            {
                "id": "j2",
                "title": "Architecte Java",
                "required_skills": ["Java", "Spring", "Microservices", "Kubernetes"],
                "preferred_skills": ["AWS", "CI/CD", "Terraform"],
                "location": "48.8566,2.3522",  # Paris
                "min_years_of_experience": 5,
                "max_years_of_experience": 10,
                "required_education": "master",
                "offers_remote": False,
                "salary_range": {"min": 65000, "max": 85000},
                "job_type": "full_time",
                "industry": "finance"
            },
            {
                "id": "j3",
                "title": "Développeur Frontend",
                "required_skills": ["JavaScript", "HTML", "CSS", "React"],
                "preferred_skills": ["TypeScript", "Redux", "GraphQL"],
                "location": "43.6043,1.4437",  # Toulouse
                "min_years_of_experience": 2,
                "max_years_of_experience": 5,
                "required_education": "bachelor",
                "offers_remote": True,
                "salary_range": {"min": 45000, "max": 60000},
                "job_type": "contract",
                "industry": "tech"
            }
        ]
        
        return {"candidates": candidates, "jobs": jobs}

# Pour compatibilité avec d'autres codes
def load_test_data():
    """
    Fonction utilitaire pour charger des données de test
    """
    matcher = SmartMatcher()
    return matcher.load_test_data()