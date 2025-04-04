import numpy as np
from typing import Dict, List, Any, Tuple, Optional
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from pathlib import Path

class MatchingEngine:
    """
    Moteur de matching entre candidats et entreprises pour 
    générer des recommandations personnalisées.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Chargement des configurations de matching
        self.load_matching_config()
        
        # Vectorizer pour le calcul de similarité textuelle
        self.vectorizer = TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            min_df=2,
            stop_words='english',
            use_idf=True
        )
    
    def load_matching_config(self):
        """
        Charge les paramètres de pondération pour le matching
        """
        try:
            config_path = Path(__file__).resolve().parent.parent.parent / "data" / "matching_config.json"
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.weights = config.get("weights", {})
            else:
                # Configuration par défaut si le fichier n'existe pas
                self.weights = {
                    "skills": 0.35,
                    "experience": 0.20,
                    "values": 0.20,
                    "work_environment": 0.15,
                    "education": 0.10
                }
                
                # Créer le répertoire data s'il n'existe pas
                data_dir = Path(__file__).resolve().parent.parent.parent / "data"
                data_dir.mkdir(exist_ok=True)
                
                # Sauvegarder la configuration par défaut
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump({"weights": self.weights}, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Erreur lors du chargement de la configuration de matching: {e}")
            # Utiliser des valeurs par défaut
            self.weights = {
                "skills": 0.35,
                "experience": 0.20,
                "values": 0.20,
                "work_environment": 0.15,
                "education": 0.10
            }
    
    def calculate_match_score(self, 
                              candidate_profile: Dict[str, Any], 
                              company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule le score de matching entre un candidat et une entreprise
        
        Args:
            candidate_profile: Profil du candidat avec données extraites
            company_profile: Profil de l'entreprise avec données extraites
            
        Returns:
            Dict: Score global et scores par catégorie
        """
        try:
            scores = {}
            
            # 1. Score de compétences
            skills_score = self.calculate_skills_match(
                candidate_profile.get("competences", []),
                company_profile.get("technologies", [])
            )
            scores["skills"] = skills_score
            
            # 2. Score d'expérience
            experience_score = self.calculate_experience_match(
                candidate_profile.get("experience", []),
                company_profile.get("extracted_data", {}).get("experience", "")
            )
            scores["experience"] = experience_score
            
            # 3. Score de valeurs
            values_score = self.calculate_values_match(
                candidate_profile.get("values", {}),
                company_profile.get("extracted_data", {}).get("values", {})
            )
            scores["values"] = values_score
            
            # 4. Score d'environnement de travail
            environment_score = self.calculate_environment_match(
                candidate_profile.get("work_preferences", {}),
                company_profile.get("extracted_data", {}).get("work_environment", {})
            )
            scores["work_environment"] = environment_score
            
            # 5. Score de formation
            education_score = self.calculate_education_match(
                candidate_profile.get("formation", {}),
                company_profile.get("extracted_data", {}).get("education", {})
            )
            scores["education"] = education_score
            
            # Calcul du score global pondéré
            global_score = 0
            for category, score in scores.items():
                if category in self.weights:
                    global_score += score * self.weights[category]
            
            # Normaliser en pourcentage
            global_score = min(100, max(0, global_score * 100))
            
            return {
                "global_score": round(global_score, 1),
                "category_scores": {k: round(v * 100, 1) for k, v in scores.items()}
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul du score de matching: {e}")
            return {
                "global_score": 0,
                "category_scores": {},
                "error": str(e)
            }
    
    def calculate_skills_match(self, 
                               candidate_skills: List[str], 
                               company_skills: List[str]) -> float:
        """
        Compare les compétences du candidat avec celles demandées par l'entreprise
        
        Args:
            candidate_skills: Liste des compétences du candidat
            company_skills: Liste des compétences recherchées par l'entreprise
            
        Returns:
            float: Score de 0 à 1
        """
        if not candidate_skills or not company_skills:
            return 0.0
        
        # Normaliser les compétences
        candidate_skills_norm = [s.lower() for s in candidate_skills if s != "Non spécifié"]
        company_skills_norm = [s.lower() for s in company_skills if s != "Non spécifié"]
        
        if not candidate_skills_norm or not company_skills_norm:
            return 0.0
        
        # Compter les compétences correspondantes
        matched_skills = 0
        for skill in company_skills_norm:
            if any(skill in candidate_skill or candidate_skill in skill for candidate_skill in candidate_skills_norm):
                matched_skills += 1
        
        # Calculer le pourcentage de correspondance 
        # (basé sur les compétences de l'entreprise que possède le candidat)
        match_percentage = matched_skills / len(company_skills_norm)
        
        # Bonus pour compétences supplémentaires pertinentes
        unique_candidate_skills = sum(1 for skill in candidate_skills_norm 
                               if not any(skill in company_skill for company_skill in company_skills_norm))
        
        # Limiter le bonus à 20%
        skills_bonus = min(0.2, unique_candidate_skills * 0.02)
        
        return min(1.0, match_percentage + skills_bonus)
    
    def calculate_experience_match(self, 
                                  candidate_experience: List[Dict[str, str]], 
                                  required_experience: str) -> float:
        """
        Compare l'expérience du candidat avec celle demandée par l'entreprise
        
        Args:
            candidate_experience: Expérience professionnelle du candidat
            required_experience: Expérience requise par l'entreprise
            
        Returns:
            float: Score de 0 à 1
        """
        if not candidate_experience or not required_experience:
            return 0.5  # Score neutre en cas d'absence d'information
        
        # Extraire les années d'expérience requises
        import re
        years_required = 0
        
        # Patterns pour l'extraction des années d'expérience
        exp_patterns = [
            r'(\d+)[\s\-+]*ans?',
            r'(\d+)[\s\-+]*year',
            r'(\d+)[\s\-+]*année'
        ]
        
        for pattern in exp_patterns:
            matches = re.findall(pattern, required_experience)
            if matches:
                years_required = int(matches[0])
                break
        
        # Si on n'a pas trouvé de nombre d'années explicite
        if years_required == 0:
            # Chercher des indications qualitatives
            if any(x in required_experience.lower() for x in ["junior", "débutant", "entry"]):
                years_required = 1
            elif any(x in required_experience.lower() for x in ["confirmé", "intermédiaire", "mid"]):
                years_required = 3
            elif any(x in required_experience.lower() for x in ["senior", "expert", "expérimenté"]):
                years_required = 5
            else:
                years_required = 2  # Valeur par défaut modérée
        
        # Calculer l'expérience totale du candidat (approximative)
        candidate_years = 0
        for exp in candidate_experience:
            if isinstance(exp, dict) and "period" in exp:
                period = exp["period"]
                # Patterns pour les périodes
                year_patterns = [
                    r'(\d{4})\s*[-–]\s*(\d{4}|présent|aujourd|actuel)',
                    r'(\d{4})\s*[-–]\s*(\d{4}|present|current|now)'
                ]
                
                for pattern in year_patterns:
                    matches = re.findall(pattern, period)
                    if matches:
                        start_year = int(matches[0][0])
                        
                        if any(x in matches[0][1].lower() for x in ["présent", "aujourd", "actuel", "present", "current", "now"]):
                            from datetime import datetime
                            end_year = datetime.now().year
                        else:
                            end_year = int(matches[0][1])
                        
                        candidate_years += (end_year - start_year)
                        break
            
            # Si on n'a pas pu extraire des années mais qu'on a une expérience
            if candidate_years == 0 and len(candidate_experience) > 0:
                candidate_years = len(candidate_experience) * 1.5  # Approximation
        
        # Calcul du score
        if years_required > 0:
            # Si le candidat a au moins l'expérience requise
            if candidate_years >= years_required:
                # Pleine correspondance, avec légère pénalité si trop d'expérience
                if candidate_years > years_required * 2:
                    return 0.9  # Légère pénalité pour surqualification
                else:
                    return 1.0
            else:
                # Score proportionnel à l'expérience
                return min(0.9, candidate_years / years_required)
        else:
            # Si pas d'exigence explicite, score basé sur l'expérience absolue
            return min(1.0, candidate_years / 5)  # 5 ans = score max
    
    def calculate_values_match(self, 
                              candidate_values: Dict[str, Any], 
                              company_values: Dict[str, Any]) -> float:
        """
        Compare les valeurs personnelles du candidat avec la culture d'entreprise
        
        Args:
            candidate_values: Valeurs du candidat
            company_values: Valeurs et culture de l'entreprise
            
        Returns:
            float: Score de 0 à 1
        """
        if not candidate_values or not company_values:
            return 0.5  # Score neutre en cas d'absence d'information
        
        # Extraction des valeurs explicites
        candidate_explicit = []
        company_explicit = []
        
        if "explicit_values" in candidate_values:
            candidate_explicit = candidate_values["explicit_values"]
        elif "detected_values" in candidate_values:
            candidate_explicit = list(candidate_values["detected_values"].keys())
        
        if "explicit_values" in company_values:
            company_explicit = company_values["explicit_values"]
        elif "detected_values" in company_values:
            company_explicit = list(company_values["detected_values"].keys())
        
        # Si on a des valeurs explicites des deux côtés
        if candidate_explicit and company_explicit:
            # Normalisation
            candidate_norm = [v.lower() for v in candidate_explicit]
            company_norm = [v.lower() for v in company_explicit]
            
            # Calcul de correspondance directe
            matches = sum(1 for v in company_norm if any(v in c or c in v for c in candidate_norm))
            match_score = matches / max(len(company_norm), 1)
            
            return min(1.0, match_score)
        else:
            # Valeur par défaut modérée en cas d'absence de données explicites
            return 0.5
    
    def calculate_environment_match(self, 
                                   candidate_preferences: Dict[str, Any], 
                                   company_environment: Dict[str, Any]) -> float:
        """
        Compare les préférences de travail du candidat avec l'environnement offert
        
        Args:
            candidate_preferences: Préférences du candidat
            company_environment: Environnement de travail de l'entreprise
            
        Returns:
            float: Score de 0 à 1
        """
        if not candidate_preferences or not company_environment:
            return 0.5  # Score neutre
        
        match_points = 0
        total_points = 0
        
        # Mode de travail (remote, hybrid, office)
        if "preferred_work_mode" in candidate_preferences and "work_mode" in company_environment:
            total_points += 3
            candidate_mode = candidate_preferences["preferred_work_mode"]
            company_modes = company_environment["work_mode"]
            
            if isinstance(candidate_mode, str):
                if candidate_mode in company_modes:
                    match_points += 3
                elif "hybrid" in company_modes:  # Hybrid est un compromis acceptable
                    match_points += 2
                else:
                    match_points += 0.5  # Légère correspondance même si pas exact
            elif isinstance(candidate_mode, list):
                if any(mode in company_modes for mode in candidate_mode):
                    match_points += 3
                elif "hybrid" in company_modes and any(mode != "office" for mode in candidate_mode):
                    match_points += 2
        
        # Localisation
        if "preferred_location" in candidate_preferences and "locations" in company_environment:
            total_points += 2
            candidate_locations = candidate_preferences["preferred_location"]
            company_locations = company_environment["locations"]
            
            if isinstance(candidate_locations, str):
                candidate_locations = [candidate_locations]
            if isinstance(company_locations, str):
                company_locations = [company_locations]
            
            for loc in candidate_locations:
                if any(loc.lower() in c.lower() or c.lower() in loc.lower() for c in company_locations):
                    match_points += 2
                    break
            
            # Si remote est une option, la localisation est moins importante
            if "remote" in company_environment.get("work_mode", []):
                match_points += 1
        
        # Calcul du score final
        if total_points > 0:
            return min(1.0, match_points / total_points)
        else:
            return 0.5
    
    def calculate_education_match(self, 
                                 candidate_education: Dict[str, Any], 
                                 company_requirements: Dict[str, Any]) -> float:
        """
        Compare la formation du candidat avec les exigences de l'entreprise
        
        Args:
            candidate_education: Formation du candidat
            company_requirements: Exigences de formation de l'entreprise
            
        Returns:
            float: Score de 0 à 1
        """
        if not candidate_education or not company_requirements:
            return 0.5  # Score neutre
        
        # Extraction du niveau d'éducation
        candidate_level = self._extract_education_level(candidate_education)
        required_level = self._extract_education_level(company_requirements)
        
        if candidate_level and required_level:
            # Niveaux d'éducation ordonnés
            education_levels = {
                "high_school": 1,
                "associate": 2,
                "bachelor": 3,
                "master": 4,
                "phd": 5
            }
            
            candidate_score = education_levels.get(candidate_level, 3)
            required_score = education_levels.get(required_level, 3)
            
            # Si le candidat a au moins le niveau requis
            if candidate_score >= required_score:
                # Score complet avec légère pénalité pour surqualification
                if candidate_score > required_score + 1:
                    return 0.9
                else:
                    return 1.0
            else:
                # Score partiel
                return 0.7 * (candidate_score / required_score)
        else:
            return 0.5
    
    def _extract_education_level(self, education_data: Dict[str, Any]) -> Optional[str]:
        """
        Extrait le niveau d'éducation à partir des données
        
        Args:
            education_data: Données de formation
            
        Returns:
            str: Niveau d'éducation normalisé ou None
        """
        # Patterns de recherche pour les niveaux d'éducation
        level_patterns = {
            "high_school": ["bac", "lycée", "high school", "secondary"],
            "associate": ["bac+2", "dut", "bts", "associate", "iut"],
            "bachelor": ["bac+3", "licence", "bachelor", "grad", "bsc"],
            "master": ["bac+5", "master", "msc", "mba"],
            "phd": ["doctorat", "phd", "doctorate", "thèse"]
        }
        
        # Extraire le texte à analyser
        education_text = ""
        
        if isinstance(education_data, dict):
            for key, value in education_data.items():
                if isinstance(value, str):
                    education_text += value + " "
                elif isinstance(value, list):
                    education_text += " ".join([str(item) for item in value]) + " "
        elif isinstance(education_data, list):
            for item in education_data:
                if isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, str):
                            education_text += v + " "
                elif isinstance(item, str):
                    education_text += item + " "
        elif isinstance(education_data, str):
            education_text = education_data
        
        education_text = education_text.lower()
        
        # Rechercher le niveau le plus élevé mentionné
        highest_level = None
        highest_score = 0
        
        for level, patterns in level_patterns.items():
            level_score = sum(1 for pattern in patterns if pattern in education_text)
            
            if level_score > 0:
                level_value = {"high_school": 1, "associate": 2, "bachelor": 3, "master": 4, "phd": 5}[level]
                
                if level_value > highest_score:
                    highest_score = level_value
                    highest_level = level
        
        return highest_level
    
    def generate_recommendations(self, 
                                candidate_profile: Dict[str, Any],
                                company_profiles: List[Dict[str, Any]], 
                                limit: int = 10) -> List[Dict[str, Any]]:
        """
        Génère des recommandations d'entreprises pour un candidat
        
        Args:
            candidate_profile: Profil du candidat
            company_profiles: Liste des profils d'entreprises
            limit: Nombre maximum de recommandations à retourner
            
        Returns:
            List: Entreprises recommandées avec scores de matching
        """
        try:
            recommendations = []
            
            for company in company_profiles:
                # Calcul du score de matching
                match_result = self.calculate_match_score(candidate_profile, company)
                
                # Ajouter à la liste de recommandations
                recommendations.append({
                    "company_id": company.get("id", "unknown"),
                    "company_name": company.get("name", "Entreprise sans nom"),
                    "match_score": match_result["global_score"],
                    "category_scores": match_result["category_scores"],
                    "job_title": company.get("job_title", "Poste non spécifié")
                })
            
            # Trier par score de matching
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Limiter le nombre de résultats
            return recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des recommandations: {e}")
            return []
    
    def generate_candidate_recommendations(self, 
                                         company_profile: Dict[str, Any],
                                         candidate_profiles: List[Dict[str, Any]], 
                                         limit: int = 10) -> List[Dict[str, Any]]:
        """
        Génère des recommandations de candidats pour une entreprise
        
        Args:
            company_profile: Profil de l'entreprise
            candidate_profiles: Liste des profils de candidats
            limit: Nombre maximum de recommandations à retourner
            
        Returns:
            List: Candidats recommandés avec scores de matching
        """
        try:
            recommendations = []
            
            for candidate in candidate_profiles:
                # Calcul du score de matching
                match_result = self.calculate_match_score(candidate, company_profile)
                
                # Ajouter à la liste de recommandations
                recommendations.append({
                    "candidate_id": candidate.get("id", "unknown"),
                    "candidate_name": candidate.get("name", "Candidat sans nom"),
                    "match_score": match_result["global_score"],
                    "category_scores": match_result["category_scores"],
                    "title": candidate.get("titre", "Titre non spécifié")
                })
            
            # Trier par score de matching
            recommendations.sort(key=lambda x: x["match_score"], reverse=True)
            
            # Limiter le nombre de résultats
            return recommendations[:limit]
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération des recommandations de candidats: {e}")
            return []

# Instance singleton du moteur de matching
_matching_engine = None

def get_matching_engine():
    """
    Récupère l'instance unique du moteur de matching
    
    Returns:
        MatchingEngine: Instance du moteur de matching
    """
    global _matching_engine
    if _matching_engine is None:
        _matching_engine = MatchingEngine()
    return _matching_engine
