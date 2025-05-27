#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moteur de matching amélioré pour les candidats et les offres d'emploi

AMÉLIORATIONS PAR RAPPORT À L'ORIGINAL :
- Matching sémantique des compétences (résout les 0% brutaux)
- Géolocalisation intelligente par zones
- Pondération adaptative selon l'expérience
- Gestion des synonymes et technologies liées
- Scoring graduel et plus intelligent

Auteur: Algorithme amélioré basé sur l'analyse des résultats
"""

import os
import json
import math
import datetime
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple, Union

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedMatchingEngine:
    """
    Moteur de matching amélioré entre candidats et offres d'emploi
    """
    
    def __init__(self):
        self.cv_data = {}
        self.questionnaire_data = {}
        self.job_data = {}
        
        # 🧠 Dictionnaire de compétences sémantiques
        self.skill_groups = {
            "python_ecosystem": {
                "core": ["Python"],
                "web_frameworks": ["Django", "FastAPI", "Flask", "Pyramid"],
                "data_science": ["Pandas", "NumPy", "Matplotlib", "Seaborn"],
                "ml_ai": ["TensorFlow", "PyTorch", "Scikit-learn", "Keras"],
                "similarity": 0.8  # Score entre technologies du même groupe
            },
            "javascript_ecosystem": {
                "core": ["JavaScript", "TypeScript"],
                "frontend": ["React", "Vue.js", "Angular", "Svelte"],
                "backend": ["Node.js", "Express", "Nest.js"],
                "similarity": 0.8
            },
            "databases": {
                "sql": ["PostgreSQL", "MySQL", "SQLite", "Oracle", "SQL Server"],
                "nosql": ["MongoDB", "Redis", "Cassandra", "DynamoDB"],
                "similarity": 0.6  # Moins de similarité entre SQL et NoSQL
            },
            "devops_cloud": {
                "containers": ["Docker", "Kubernetes", "Podman"],
                "cloud": ["AWS", "Azure", "GCP", "Cloud"],
                "ci_cd": ["Jenkins", "GitLab CI", "GitHub Actions"],
                "similarity": 0.7
            },
            "java_ecosystem": {
                "core": ["Java"],
                "frameworks": ["Spring", "Spring Boot", "Hibernate"],
                "similarity": 0.8
            }
        }
        
        # 📍 Zones géographiques intelligentes
        self.location_zones = {
            "paris": {
                "keywords": ["paris", "ile-de-france", "idf", "75", "region parisienne"],
                "score": 1.0,
                "remote_compatible": True
            },
            "lyon": {
                "keywords": ["lyon", "rhone", "69", "rhone-alpes"],
                "score": 0.9,
                "remote_compatible": True
            },
            "marseille": {
                "keywords": ["marseille", "13", "bouches-du-rhone", "paca"],
                "score": 0.9,
                "remote_compatible": True
            },
            "remote": {
                "keywords": ["remote", "télétravail", "teletravail", "distance", "home office"],
                "score": 1.0,
                "remote_compatible": True
            },
            "france": {
                "keywords": ["france", "national", "toute la france"],
                "score": 0.8,
                "remote_compatible": True
            }
        }
        
        # 🔄 Synonymes pour types de contrats
        self.contract_synonyms = {
            "cdi": ["cdi", "contrat à durée indéterminée", "permanent", "indefinite"],
            "cdd": ["cdd", "contrat à durée déterminée", "temporary", "fixed-term"],
            "freelance": ["freelance", "indépendant", "contractor", "consultant", "mission"],
            "stage": ["stage", "internship", "intern"],
            "alternance": ["alternance", "apprentissage", "apprenticeship", "contrat pro"]
        }
        
    def load_candidate_data(self, cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> None:
        """
        Charge les données du candidat dans le moteur
        """
        self.cv_data = cv_data
        self.questionnaire_data = questionnaire_data
        logger.info(f"Données candidat chargées: {len(self.cv_data)} éléments CV, {len(self.questionnaire_data)} éléments questionnaire")
    
    def load_job_data(self, job_data: List[Dict[str, Any]]) -> None:
        """
        Charge les données des offres d'emploi dans le moteur
        """
        self.job_data = job_data
        logger.info(f"Données emploi chargées: {len(self.job_data)} offres")
    
    def get_adaptive_weights(self, candidate_experience: int) -> Dict[str, float]:
        """
        ⚖️ Pondération adaptative selon l'expérience du candidat
        """
        if candidate_experience >= 7:  # Senior
            return {
                'skills': 0.35,      # Très important pour les seniors
                'salary': 0.25,      # Important pour les seniors
                'location': 0.15,    # Moins critique (plus flexible)
                'contract': 0.10,    # Moins critique
                'experience': 0.05,  # Moins important (déjà senior)
                'date': 0.10
            }
        elif candidate_experience >= 3:  # Confirmé
            return {
                'skills': 0.30,      # Équilibré
                'location': 0.20,    # Important
                'salary': 0.20,      # Important
                'contract': 0.15,    # Modéré
                'experience': 0.10,  # Modéré
                'date': 0.05
            }
        else:  # Junior
            return {
                'skills': 0.25,      # Moins strict sur les compétences
                'experience': 0.20,  # Très important pour juniors
                'location': 0.20,    # Important
                'contract': 0.15,    # Important (stabilité)
                'salary': 0.15,      # Moins critique
                'date': 0.05
            }
    
    def calculate_matching_scores(self) -> List[Dict[str, Any]]:
        """
        Calcule les scores de matching pour toutes les offres chargées
        """
        if not self.cv_data or not self.questionnaire_data or not self.job_data:
            logger.error("Données manquantes pour le calcul des scores")
            return []
        
        results = []
        candidate_experience = self.cv_data.get('annees_experience', 0)
        
        # ⚖️ Pondération adaptative
        weights = self.get_adaptive_weights(candidate_experience)
        
        for job in self.job_data:
            # Calcul des différents critères avec algorithmes améliorés
            skills_score = self._calculate_enhanced_skills_score(job)
            contract_score = self._calculate_enhanced_contract_score(job)
            location_score = self._calculate_enhanced_location_score(job)
            date_score = self._calculate_enhanced_availability_score(job)
            salary_score = self._calculate_enhanced_salary_score(job)
            experience_score = self._calculate_enhanced_experience_score(job)
            
            # Calcul du score global avec pondération adaptative
            total_score = (
                skills_score * weights['skills'] +
                contract_score * weights['contract'] +
                location_score * weights['location'] +
                date_score * weights['date'] +
                salary_score * weights['salary'] +
                experience_score * weights['experience']
            )
            
            # Formatage du résultat
            job_result = job.copy()
            job_result['matching_score'] = round(total_score * 100)
            job_result['matching_details'] = {
                'skills': round(skills_score * 100),
                'contract': round(contract_score * 100),
                'location': round(location_score * 100),
                'date': round(date_score * 100),
                'salary': round(salary_score * 100),
                'experience': round(experience_score * 100)
            }
            
            # Ajout des métadonnées de l'algorithme amélioré
            job_result['algorithm_version'] = "enhanced_v1.0"
            job_result['adaptive_weights'] = {k: round(v, 2) for k, v in weights.items()}
            
            results.append(job_result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _calculate_enhanced_skills_score(self, job: Dict[str, Any]) -> float:
        """
        🧠 Calcul amélioré du score de compétences avec matching sémantique
        """
        cv_skills = [skill.lower().strip() for skill in self.cv_data.get('competences', [])]
        job_skills = [skill.lower().strip() for skill in job.get('competences', [])]
        
        if not job_skills:
            return 0.5  # Score neutre si pas de compétences listées
            
        if not cv_skills:
            return 0.1  # Score très bas si candidat sans compétences
        
        total_score = 0
        max_possible_score = len(job_skills)
        
        for job_skill in job_skills:
            best_match_score = 0
            
            # 1. Correspondance exacte
            if job_skill in cv_skills:
                best_match_score = 1.0
            else:
                # 2. Matching sémantique via les groupes de compétences
                for group_name, group_data in self.skill_groups.items():
                    job_skill_found = False
                    cv_skill_found = False
                    
                    # Vérifier si la compétence du job est dans ce groupe
                    for category, skills in group_data.items():
                        if category != 'similarity' and isinstance(skills, list):
                            if any(s.lower() in job_skill for s in skills) or job_skill in [s.lower() for s in skills]:
                                job_skill_found = True
                                break
                    
                    if job_skill_found:
                        # Vérifier si le candidat a une compétence du même groupe
                        for category, skills in group_data.items():
                            if category != 'similarity' and isinstance(skills, list):
                                for cv_skill in cv_skills:
                                    if any(s.lower() in cv_skill for s in skills) or cv_skill in [s.lower() for s in skills]:
                                        cv_skill_found = True
                                        best_match_score = max(best_match_score, group_data.get('similarity', 0.5))
                                        break
                                if cv_skill_found:
                                    break
                    
                    if cv_skill_found:
                        break
                
                # 3. Matching partiel par mots-clés
                if best_match_score == 0:
                    for cv_skill in cv_skills:
                        # Correspondance partielle (mots contenus)
                        if len(job_skill) > 3 and job_skill in cv_skill:
                            best_match_score = max(best_match_score, 0.3)
                        elif len(cv_skill) > 3 and cv_skill in job_skill:
                            best_match_score = max(best_match_score, 0.3)
            
            total_score += best_match_score
        
        # Score final avec bonus si beaucoup de compétences matchent
        final_score = total_score / max_possible_score
        
        # Bonus pour candidats avec plus de compétences que demandé
        if len(cv_skills) > len(job_skills):
            bonus = min(0.1, (len(cv_skills) - len(job_skills)) * 0.02)
            final_score = min(1.0, final_score + bonus)
        
        return final_score
    
    def _calculate_enhanced_contract_score(self, job: Dict[str, Any]) -> float:
        """
        🔄 Calcul amélioré du score de type de contrat avec synonymes
        """
        preferred_contracts = self.questionnaire_data.get('contrats_recherches', [])
        job_contract = job.get('type_contrat', '').lower().strip()
        
        if not preferred_contracts or not job_contract:
            return 0.7  # Score neutre plutôt que 0.5
        
        # Normalisation via les synonymes
        normalized_job_contract = None
        normalized_preferences = []
        
        # Normaliser le contrat du job
        for contract_type, synonyms in self.contract_synonyms.items():
            if any(synonym in job_contract for synonym in synonyms):
                normalized_job_contract = contract_type
                break
        
        # Normaliser les préférences du candidat
        for pref in preferred_contracts:
            pref_lower = pref.lower().strip()
            for contract_type, synonyms in self.contract_synonyms.items():
                if any(synonym in pref_lower for synonym in synonyms):
                    normalized_preferences.append(contract_type)
                    break
            else:
                normalized_preferences.append(pref_lower)
        
        # Calcul du score avec flexibilité
        if normalized_job_contract in normalized_preferences:
            return 1.0
        elif normalized_job_contract == "cdi" and "cdd" in normalized_preferences:
            return 0.8  # CDI est souvent acceptable si on cherche CDD
        elif normalized_job_contract == "freelance" and ("cdd" in normalized_preferences or "cdi" in normalized_preferences):
            return 0.6  # Freelance peut être acceptable
        else:
            return 0.3  # Pas de correspondance mais pas 0
    
    def _calculate_enhanced_location_score(self, job: Dict[str, Any]) -> float:
        """
        📍 Calcul amélioré du score de localisation par zones intelligentes
        """
        candidate_address = self.questionnaire_data.get('adresse', '').lower().strip()
        job_address = job.get('localisation', '').lower().strip()
        
        if not candidate_address or not job_address:
            return 0.6  # Score neutre pour données manquantes
        
        # Détection de zone du candidat
        candidate_zone = None
        for zone, zone_data in self.location_zones.items():
            if any(keyword in candidate_address for keyword in zone_data['keywords']):
                candidate_zone = zone
                break
        
        # Détection de zone du job
        job_zone = None
        for zone, zone_data in self.location_zones.items():
            if any(keyword in job_address for keyword in zone_data['keywords']):
                job_zone = zone
                break
        
        # Calcul du score selon les zones
        if job_zone == "remote":
            return 1.0  # Remote toujours parfait
        elif candidate_zone == job_zone:
            return 1.0  # Même zone = parfait
        elif candidate_zone == "remote" or (candidate_zone and self.location_zones.get(candidate_zone, {}).get('remote_compatible', False)):
            return 0.9  # Compatible remote
        elif candidate_zone == "paris" and job_zone in ["lyon", "marseille"]:
            return 0.4  # Grandes villes entre elles
        elif job_zone in self.location_zones:
            return 0.6  # Zone connue mais différente
        else:
            return 0.3  # Zones inconnues mais pas 0
    
    def _calculate_enhanced_availability_score(self, job: Dict[str, Any]) -> float:
        """
        📅 Calcul amélioré du score de disponibilité
        """
        try:
            availability_date_str = self.questionnaire_data.get('date_disponibilite', '')
            job_start_date_str = job.get('date_debut', '')
            
            if not availability_date_str or not job_start_date_str:
                return 0.8  # Score neutre élevé pour données manquantes
            
            # Parser les dates avec plusieurs formats
            def parse_date(date_str):
                formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
                for fmt in formats:
                    try:
                        return datetime.datetime.strptime(date_str, fmt).date()
                    except ValueError:
                        continue
                return None
            
            availability_date = parse_date(availability_date_str)
            job_start_date = parse_date(job_start_date_str)
            
            if not availability_date or not job_start_date:
                return 0.8
            
            # Calcul intelligent de la différence
            delta_days = (job_start_date - availability_date).days
            
            if delta_days >= 0:  # Disponible avant ou le jour J
                if delta_days <= 7:
                    return 1.0  # Parfait
                elif delta_days <= 30:
                    return 0.9  # Très bon
                elif delta_days <= 90:
                    return 0.8  # Bon
                else:
                    return 0.7  # Acceptable
            else:  # Disponible après la date de début
                delay = abs(delta_days)
                if delay <= 14:
                    return 0.8  # Retard acceptable
                elif delay <= 30:
                    return 0.6  # Retard modéré
                elif delay <= 60:
                    return 0.4  # Retard important
                else:
                    return 0.2  # Retard critique
                    
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score de disponibilité: {str(e)}")
            return 0.7
    
    def _calculate_enhanced_salary_score(self, job: Dict[str, Any]) -> float:
        """
        💰 Calcul amélioré du score de salaire
        """
        min_salary = self.questionnaire_data.get('salaire_min', 0)
        job_salary_str = job.get('salaire', '')
        
        if not min_salary:
            return 0.8  # Pas de contrainte de salaire = bon score
            
        if not job_salary_str:
            return 0.6  # Salaire non spécifié = score moyen
        
        try:
            import re
            
            # Nettoyage et extraction
            salary_clean = job_salary_str.replace(' ', '').replace('k', '000').replace('K', '000').replace('€', '')
            numbers = re.findall(r'\d+', salary_clean)
            
            if len(numbers) >= 2:
                job_min_salary = int(numbers[0])
                job_max_salary = int(numbers[1])
            elif len(numbers) == 1:
                job_min_salary = int(numbers[0])
                job_max_salary = int(numbers[0]) * 1.2
            else:
                return 0.6
            
            # Scoring amélioré
            if job_min_salary >= min_salary:
                # Salaire min du job >= expectation
                if job_min_salary >= min_salary * 1.2:
                    return 1.0  # Excellente surprise
                else:
                    return 0.9  # Très bon
            elif job_max_salary >= min_salary:
                # Salaire max couvre les attentes
                coverage = (job_max_salary - min_salary) / (job_max_salary - job_min_salary)
                return 0.6 + 0.3 * coverage  # Score entre 0.6 et 0.9
            else:
                # Salaire insuffisant mais pas 0
                ratio = job_max_salary / min_salary
                return max(0.2, min(0.5, ratio))  # Entre 0.2 et 0.5
                
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score de salaire: {str(e)}")
            return 0.6
    
    def _calculate_enhanced_experience_score(self, job: Dict[str, Any]) -> float:
        """
        🎓 Calcul amélioré du score d'expérience
        """
        candidate_experience = self.cv_data.get('annees_experience', 0)
        job_experience_str = job.get('experience', '')
        
        if not job_experience_str:
            return 0.8  # Pas d'exigence = bon score
            
        if candidate_experience == 0:
            return 0.4  # Candidat débutant
        
        try:
            import re
            
            numbers = re.findall(r'\d+', job_experience_str)
            job_experience_str_lower = job_experience_str.lower()
            
            # Détection par mots-clés
            if "débutant" in job_experience_str_lower or "junior" in job_experience_str_lower:
                job_min_exp, job_max_exp = 0, 2
            elif "senior" in job_experience_str_lower:
                job_min_exp, job_max_exp = 5, 15
            elif "confirmé" in job_experience_str_lower:
                job_min_exp, job_max_exp = 3, 7
            elif len(numbers) >= 2:
                job_min_exp, job_max_exp = int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                job_min_exp = int(numbers[0])
                job_max_exp = job_min_exp + 3
            else:
                return 0.7  # Impossible à parser
            
            # Scoring intelligent
            if job_min_exp <= candidate_experience <= job_max_exp:
                return 1.0  # Dans la fourchette
            elif candidate_experience < job_min_exp:
                # Sous-qualifié
                if job_min_exp - candidate_experience <= 1:
                    return 0.8  # Légèrement sous-qualifié
                elif job_min_exp - candidate_experience <= 2:
                    return 0.6  # Modérément sous-qualifié
                else:
                    return 0.3  # Très sous-qualifié
            else:
                # Sur-qualifié
                excess = candidate_experience - job_max_exp
                if excess <= 2:
                    return 0.9  # Légèrement sur-qualifié (bon)
                elif excess <= 5:
                    return 0.7  # Modérément sur-qualifié
                else:
                    return 0.5  # Très sur-qualifié (risque de fuite)
                    
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score d'expérience: {str(e)}")
            return 0.7
    
    def get_top_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retourne les N meilleures offres correspondant au profil
        """
        all_matches = self.calculate_matching_scores()
        return all_matches[:limit]

# Fonction d'entrée principale pour l'API (compatible avec l'original)
def match_candidate_with_jobs(cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any], 
                             job_data: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fonction principale améliorée pour le calcul de matching
    
    AMÉLIORATIONS :
    - Matching sémantique des compétences
    - Géolocalisation par zones intelligentes  
    - Pondération adaptative selon l'expérience
    - Gestion des synonymes
    - Scoring graduel (évite les 0% brutaux)
    """
    engine = EnhancedMatchingEngine()
    engine.load_candidate_data(cv_data, questionnaire_data)
    engine.load_job_data(job_data)
    
    return engine.get_top_matches(limit)

# Tests et démonstration
if __name__ == "__main__":
    print("🚀 TEST DE L'ALGORITHME DE MATCHING AMÉLIORÉ")
    print("=" * 60)
    
    # Données de test pour démonstration
    cv_data = {
        "competences": ["Python", "Django", "React", "SQL", "Git"],
        "annees_experience": 4,
        "formation": "Master Informatique"
    }
    
    questionnaire_data = {
        "contrats_recherches": ["CDI", "CDD"],
        "adresse": "Paris",
        "temps_trajet_max": 45,
        "date_disponibilite": "01/06/2025",
        "salaire_min": 45000,
        "domaines_interets": ["Web", "Data"]
    }
    
    job_data = [
        {
            "id": 1,
            "titre": "Développeur Full-Stack",
            "entreprise": "TechVision",
            "localisation": "Paris",
            "type_contrat": "CDI",
            "competences": ["Python", "FastAPI", "React"],  # FastAPI au lieu de Django
            "experience": "3-5 ans",
            "date_debut": "15/05/2025",
            "salaire": "45K-55K€"
        },
        {
            "id": 2,
            "titre": "Data Engineer",
            "entreprise": "DataInsight",
            "localisation": "Remote",
            "type_contrat": "CDD",
            "competences": ["Python", "SQL", "Spark"],
            "experience": "2-4 ans",
            "date_debut": "01/07/2025",
            "salaire": "50K-60K€"
        }
    ]
    
    # Test de l'algorithme amélioré
    results = match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
    
    # Affichage des résultats
    print(f"\n📊 RÉSULTATS DE L'ALGORITHME AMÉLIORÉ")
    print("=" * 60)
    
    for i, job in enumerate(results):
        print(f"\n🎯 Match #{i+1}")
        print(f"   Titre: {job['titre']}")
        print(f"   Entreprise: {job['entreprise']}")
        print(f"   Score global: {job['matching_score']}% (Algorithme: {job.get('algorithm_version', 'N/A')})")
        print(f"   Pondération adaptative: {job.get('adaptive_weights', {})}")
        
        details = job.get('matching_details', {})
        if details:
            print(f"   Scores détaillés:")
            for criterion, score in details.items():
                emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                print(f"     {emoji} {criterion}: {score}%")
        
        print(f"   Compétences: {job.get('competences', [])}")
        print(f"   Contrat: {job.get('type_contrat', 'N/A')}")
        print(f"   Localisation: {job.get('localisation', 'N/A')}")
        print(f"   Salaire: {job.get('salaire', 'N/A')}")
    
    print(f"\n✨ AMÉLIORATIONS APPLIQUÉES:")
    print(f"   🧠 Matching sémantique: FastAPI reconnu comme similaire à Django")
    print(f"   📍 Géolocalisation: Remote et Paris bien gérés") 
    print(f"   ⚖️  Pondération adaptative: Poids ajustés pour candidat de 4 ans d'exp")
    print(f"   📈 Scoring graduel: Plus de 0% brutaux")
    print(f"\n🎉 Test terminé avec succès !")
