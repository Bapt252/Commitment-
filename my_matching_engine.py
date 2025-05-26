#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moteur de matching amélioré pour les candidats et les offres d'emploi

AMÉLIORATIONS APPORTÉES :
1. Analyse sémantique des compétences avec synonymes
2. Système de scoring multi-niveaux pour les compétences
3. Pondération dynamique basée sur le contexte
4. Gestion améliorée de la localisation
5. Bonus pour les compétences rares/demandées
6. Système de pénalités progressives
"""

import os
import json
import math
import datetime
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple, Union
from difflib import SequenceMatcher

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration de l'API Google Maps
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY")

class ImprovedMatchingEngine:
    """
    Moteur de matching amélioré entre candidats et offres d'emploi
    """
    
    def __init__(self):
        self.cv_data = {}
        self.questionnaire_data = {}
        self.job_data = {}
        
        # Dictionnaire de synonymes pour les compétences
        self.skills_synonyms = {
            'javascript': ['js', 'ecmascript', 'node.js', 'nodejs'],
            'python': ['py'],
            'react': ['reactjs', 'react.js'],
            'vue': ['vuejs', 'vue.js'],
            'angular': ['angularjs', 'angular.js'],
            'sql': ['mysql', 'postgresql', 'postgres', 'sqlite'],
            'nosql': ['mongodb', 'cassandra', 'couchdb'],
            'docker': ['containerization'],
            'kubernetes': ['k8s'],
            'aws': ['amazon web services'],
            'azure': ['microsoft azure'],
            'gcp': ['google cloud platform'],
            'machine learning': ['ml', 'artificial intelligence', 'ai'],
            'deep learning': ['neural networks', 'tensorflow', 'pytorch'],
            'devops': ['ci/cd', 'continuous integration'],
            'api': ['rest', 'restful', 'graphql'],
            'git': ['version control', 'github', 'gitlab'],
            'agile': ['scrum', 'kanban']
        }
        
        # Poids des compétences par rareté/demande
        self.skill_weights = {
            'high_demand': ['python', 'javascript', 'react', 'docker', 'kubernetes', 'aws', 'machine learning'],
            'medium_demand': ['java', 'sql', 'git', 'api', 'agile'],
            'specialized': ['tensorflow', 'pytorch', 'hadoop', 'spark', 'blockchain']
        }
        
    def load_candidate_data(self, cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> None:
        """Charge les données du candidat dans le moteur"""
        self.cv_data = cv_data
        self.questionnaire_data = questionnaire_data
        logger.info(f"Données candidat chargées: {len(self.cv_data)} éléments CV, {len(self.questionnaire_data)} éléments questionnaire")
    
    def load_job_data(self, job_data: List[Dict[str, Any]]) -> None:
        """Charge les données des offres d'emploi dans le moteur"""
        self.job_data = job_data
        logger.info(f"Données emploi chargées: {len(self.job_data)} offres")
    
    def calculate_matching_scores(self) -> List[Dict[str, Any]]:
        """Calcule les scores de matching pour toutes les offres chargées"""
        if not self.cv_data or not self.questionnaire_data or not self.job_data:
            logger.error("Données manquantes pour le calcul des scores")
            return []
        
        results = []
        
        for job in self.job_data:
            # Calcul des différents critères de matching avec amélioration
            skills_score = self._calculate_enhanced_skills_score(job)
            contract_score = self._calculate_contract_score(job)
            location_score = self._calculate_enhanced_location_score(job)
            date_score = self._calculate_availability_score(job)
            salary_score = self._calculate_enhanced_salary_score(job)
            experience_score = self._calculate_enhanced_experience_score(job)
            
            # Pondération dynamique basée sur le profil
            weights = self._get_dynamic_weights(job)
            
            # Calcul du score global avec bonus/malus
            base_score = (
                skills_score * weights['skills'] +
                contract_score * weights['contract'] +
                location_score * weights['location'] +
                date_score * weights['date'] +
                salary_score * weights['salary'] +
                experience_score * weights['experience']
            )
            
            # Application des bonus et malus
            final_score = self._apply_bonus_malus(base_score, job, {
                'skills': skills_score,
                'contract': contract_score,
                'location': location_score,
                'date': date_score,
                'salary': salary_score,
                'experience': experience_score
            })
            
            # Formatage du score final en pourcentage
            job_result = job.copy()
            job_result['matching_score'] = round(min(final_score * 100, 100))  # Cap à 100%
            
            # Détails des scores par critère
            job_result['matching_details'] = {
                'skills': round(skills_score * 100),
                'contract': round(contract_score * 100),
                'location': round(location_score * 100),
                'date': round(date_score * 100),
                'salary': round(salary_score * 100),
                'experience': round(experience_score * 100)
            }
            
            results.append(job_result)
        
        # Tri des résultats par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        
        return results
    
    def _get_dynamic_weights(self, job: Dict[str, Any]) -> Dict[str, float]:
        """
        Calcule des poids dynamiques basés sur le profil du candidat et de l'offre
        """
        base_weights = {
            'skills': 0.30,
            'contract': 0.15,
            'location': 0.20,
            'date': 0.10,
            'salary': 0.15,
            'experience': 0.10
        }
        
        # Ajustements basés sur l'expérience du candidat
        candidate_exp = self.cv_data.get('annees_experience', 0)
        
        if candidate_exp <= 2:  # Junior
            base_weights['skills'] = 0.35  # Plus d'importance aux compétences
            base_weights['salary'] = 0.10   # Moins d'importance au salaire
            base_weights['location'] = 0.25 # Plus d'importance à la localisation
        elif candidate_exp >= 8:  # Senior
            base_weights['salary'] = 0.20   # Plus d'importance au salaire
            base_weights['experience'] = 0.15 # Plus d'importance à l'expérience
            base_weights['skills'] = 0.25   # Moins d'importance aux compétences techniques
        
        # Ajustement si candidat a des préférences fortes sur le contrat
        preferred_contracts = self.questionnaire_data.get('contrats_recherches', [])
        if len(preferred_contracts) == 1:  # Préférence forte
            base_weights['contract'] = 0.20
            base_weights['skills'] = 0.25
        
        return base_weights
    
    def _calculate_enhanced_skills_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching des compétences avec analyse sémantique
        """
        cv_skills = [skill.lower().strip() for skill in self.cv_data.get('competences', [])]
        job_skills = [skill.lower().strip() for skill in job.get('competences', [])]
        
        if not job_skills:
            return 0.5
        
        # Score de base : correspondances exactes
        exact_matches = set(cv_skills).intersection(set(job_skills))
        base_score = len(exact_matches) / len(job_skills)
        
        # Bonus pour correspondances sémantiques (synonymes)
        semantic_matches = 0
        for job_skill in job_skills:
            if job_skill not in exact_matches:
                for cv_skill in cv_skills:
                    if self._are_skills_related(job_skill, cv_skill):
                        semantic_matches += 0.7  # Bonus partiel pour synonymes
                        break
        
        semantic_score = semantic_matches / len(job_skills)
        
        # Bonus pour compétences rares/demandées
        demand_bonus = 0
        for skill in exact_matches:
            if skill in self.skill_weights['high_demand']:
                demand_bonus += 0.1
            elif skill in self.skill_weights['specialized']:
                demand_bonus += 0.15
        
        final_score = min(base_score + semantic_score + demand_bonus, 1.0)
        return final_score
    
    def _are_skills_related(self, skill1: str, skill2: str) -> bool:
        """Vérifie si deux compétences sont liées (synonymes)"""
        # Vérification dans le dictionnaire de synonymes
        for main_skill, synonyms in self.skills_synonyms.items():
            if (skill1 == main_skill and skill2 in synonyms) or \
               (skill2 == main_skill and skill1 in synonyms) or \
               (skill1 in synonyms and skill2 in synonyms):
                return True
        
        # Vérification par similarité de chaîne
        similarity = SequenceMatcher(None, skill1, skill2).ratio()
        return similarity > 0.8
    
    def _calculate_enhanced_location_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de localisation avec gestion du télétravail
        """
        candidate_address = self.questionnaire_data.get('adresse', '')
        job_address = job.get('localisation', '')
        max_commute_time = self.questionnaire_data.get('temps_trajet_max', 60)
        
        # Vérification du télétravail - recherche plus large
        job_title = job.get('titre', '').lower()
        job_description = job.get('description', '').lower()
        job_location = job_address.lower()
        
        remote_keywords = [
            'télétravail', 'remote', 'home office', 'full remote', '100% remote',
            'distanciel', 'à distance', 'telecommute', 'work from home'
        ]
        
        is_remote = (
            any(keyword in job_title for keyword in remote_keywords) or
            any(keyword in job_description for keyword in remote_keywords) or
            any(keyword in job_location for keyword in remote_keywords) or
            job_location == 'remote'
        )
        
        if is_remote:
            return 1.0  # Score parfait pour télétravail
        
        # Si pas d'adresses, score moyen avec pénalité réduite
        if not candidate_address or not job_address:
            return 0.5  # Score neutre au lieu de pénalité
        
        # Correspondance exacte de ville (amélioration majeure)
        candidate_city = candidate_address.lower().strip()
        job_city = job_address.lower().strip()
        
        # Détection de correspondance directe
        if candidate_city == job_city:
            return 0.9  # Très bon score pour même ville
        
        # Vérification Paris/Île-de-France
        paris_aliases = ['paris', 'île-de-france', 'idf', 'région parisienne']
        candidate_in_paris = any(alias in candidate_city for alias in paris_aliases)
        job_in_paris = any(alias in job_city for alias in paris_aliases)
        
        if candidate_in_paris and job_in_paris:
            return 0.85  # Bon score pour région parisienne
        
        # Calcul du temps de trajet pour autres cas
        try:
            commute_time = self._get_enhanced_commute_time(candidate_address, job_address)
            
            if commute_time is None:
                return 0.5  # Score neutre si impossible à calculer
            
            # Score plus nuancé basé sur le temps de trajet
            if commute_time <= 15:
                return 1.0
            elif commute_time <= 30:
                return 0.8
            elif commute_time <= max_commute_time:
                # Score décroissant de manière linéaire
                ratio = commute_time / max_commute_time
                return max(0.3, 0.8 - (ratio * 0.5))
            else:
                # Pénalité progressive pour dépassement
                excess = commute_time - max_commute_time
                if excess <= 15:  # Tolérance de 15 minutes
                    return 0.2
                else:
                    return 0.1  # Score minimal au lieu de 0
                    
        except Exception as e:
            logger.error(f"Erreur calcul localisation: {str(e)}")
            return 0.5
    
    def _get_enhanced_commute_time(self, origin: str, destination: str) -> Optional[int]:
        """Calcul du temps de trajet avec simulation améliorée"""
        try:
            import random
            
            # Normalisation des adresses
            origin_lower = origin.lower().strip()
            destination_lower = destination.lower().strip()
            
            # Cas spéciaux : même ville
            cities_match = [
                ('paris', 'paris'),
                ('lyon', 'lyon'),
                ('marseille', 'marseille'),
                ('toulouse', 'toulouse'),
                ('bordeaux', 'bordeaux')
            ]
            
            for city1, city2 in cities_match:
                if city1 in origin_lower and city2 in destination_lower:
                    return random.randint(15, 30)  # Temps intra-urbain
            
            # Détection arrondissements parisiens
            def extract_arrondissement(address):
                import re
                match = re.search(r'750(\d{2})', address)
                if match:
                    return int(match.group(1))
                return None
            
            origin_arr = extract_arrondissement(origin)
            dest_arr = extract_arrondissement(destination)
            
            if origin_arr and dest_arr:
                # Calcul basé sur la distance entre arrondissements
                arr_distance = abs(origin_arr - dest_arr)
                base_time = 15 + (arr_distance * 3)  # 15 min base + 3 min par arrondissement
                
                # Ajout de variabilité
                variation = random.uniform(0.8, 1.3)
                return round(base_time * variation)
            
            # Différentes villes
            inter_city_patterns = [
                (['paris'], ['lyon', 'marseille', 'toulouse'], (180, 300)),
                (['lyon'], ['marseille', 'toulouse'], (120, 240)),
                (['paris'], ['banlieue', 'suburb'], (30, 90))
            ]
            
            for origins, dests, (min_time, max_time) in inter_city_patterns:
                if any(o in origin_lower for o in origins) and any(d in destination_lower for d in dests):
                    return random.randint(min_time, max_time)
            
            # Cas par défaut : simulation générique
            distance = random.uniform(10, 60)
            traffic_factor = random.uniform(1.2, 2.0)
            avg_speed = 25 / traffic_factor
            
            time_minutes = (distance / avg_speed) * 60
            return round(time_minutes)
                
        except Exception as e:
            logger.error(f"Erreur simulation trajet: {str(e)}")
            return None
    
    def _calculate_enhanced_salary_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de salaire avec gestion des fourchettes optimales
        """
        min_salary = self.questionnaire_data.get('salaire_min', 0)
        job_salary_str = job.get('salaire', '')
        
        if not min_salary or not job_salary_str:
            return 0.5
        
        try:
            import re
            
            # Extraction améliorée des salaires
            salary_clean = job_salary_str.replace(' ', '').replace('k', '000').replace('K', '000')
            numbers = re.findall(r'\d+', salary_clean)
            
            if len(numbers) >= 2:
                job_min_salary = int(numbers[0])
                job_max_salary = int(numbers[1])
            elif len(numbers) == 1:
                job_min_salary = int(numbers[0])
                job_max_salary = int(numbers[0]) * 1.15  # 15% de marge
            else:
                return 0.5
            
            # Calcul plus nuancé
            if job_max_salary < min_salary * 0.9:  # Tolerance 10%
                return 0.0
            elif job_min_salary >= min_salary * 1.2:  # 20% au-dessus = parfait
                return 1.0
            elif job_min_salary >= min_salary:
                # Score excellent si au-dessus du minimum
                excess_ratio = (job_min_salary - min_salary) / min_salary
                return min(1.0, 0.8 + excess_ratio)
            else:
                # Score proportionnel si partiellement dans la fourchette
                overlap = job_max_salary - min_salary
                total_range = job_max_salary - job_min_salary
                if total_range > 0:
                    return max(0.3, overlap / total_range)
                else:
                    return 0.3
                    
        except Exception as e:
            logger.error(f"Erreur calcul salaire: {str(e)}")
            return 0.5
    
    def _calculate_enhanced_experience_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score d'expérience avec gestion de la surqualification
        """
        candidate_experience = self.cv_data.get('annees_experience', 0)
        job_experience_str = job.get('experience', '')
        
        if not candidate_experience or not job_experience_str:
            return 0.5
        
        try:
            import re
            
            numbers = re.findall(r'\d+', job_experience_str)
            
            # Analyse textuelle améliorée
            experience_lower = job_experience_str.lower()
            
            if "débutant" in experience_lower or "junior" in experience_lower:
                job_min_exp, job_max_exp = 0, 3
            elif "confirmé" in experience_lower:
                job_min_exp, job_max_exp = 2, 6
            elif "senior" in experience_lower:
                job_min_exp, job_max_exp = 5, 12
            elif len(numbers) >= 2:
                job_min_exp = int(numbers[0])
                job_max_exp = int(numbers[1])
            elif len(numbers) == 1:
                job_min_exp = int(numbers[0])
                job_max_exp = job_min_exp + 3
            else:
                return 0.5
            
            # Calcul nuancé avec bonus/malus
            if candidate_experience < job_min_exp:
                # Insuffisant mais avec tolérance
                gap = job_min_exp - candidate_experience
                if gap <= 1:  # Tolérance 1 an
                    return 0.7
                else:
                    return max(0.2, candidate_experience / job_min_exp)
                    
            elif candidate_experience <= job_max_exp:
                # Dans la fourchette = parfait
                return 1.0
                
            elif candidate_experience <= job_max_exp * 1.3:
                # Légèrement surqualifié = encore très bien
                return 0.9
                
            elif candidate_experience <= job_max_exp * 2:
                # Surqualifié mais acceptable
                return 0.7
                
            else:
                # Très surqualifié = risque de départ
                return 0.4
                
        except Exception as e:
            logger.error(f"Erreur calcul expérience: {str(e)}")
            return 0.5
    
    def _apply_bonus_malus(self, base_score: float, job: Dict[str, Any], 
                          individual_scores: Dict[str, float]) -> float:
        """
        Applique des bonus et malus au score final
        """
        final_score = base_score
        
        # Bonus pour profil complet
        if all(score >= 0.7 for score in individual_scores.values()):
            final_score += 0.05  # Bonus 5% profil excellent
        
        # Bonus pour match parfait sur critères importants
        if individual_scores['skills'] >= 0.9 and individual_scores['experience'] >= 0.9:
            final_score += 0.03  # Bonus compétences + expérience
        
        # Malus pour critères bloquants
        if individual_scores['salary'] == 0.0:
            final_score *= 0.5  # Malus important si salaire insuffisant
        
        if individual_scores['location'] == 0.0:
            final_score *= 0.7  # Malus si localisation impossible
        
        # Bonus secteur d'activité (si données disponibles)
        interests = self.questionnaire_data.get('domaines_interets', [])
        job_title = job.get('titre', '').lower()
        
        for interest in interests:
            if interest.lower() in job_title:
                final_score += 0.02  # Petit bonus secteur d'intérêt
        
        return min(final_score, 1.0)  # Cap à 1.0
    
    # Méthodes inchangées (copiées de l'original)
    def _calculate_contract_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de matching du type de contrat (méthode originale)"""
        preferred_contracts = self.questionnaire_data.get('contrats_recherches', [])
        job_contract = job.get('type_contrat', '').lower()
        
        if not preferred_contracts or not job_contract:
            return 0.5
        
        contract_mapping = {
            'cdi': ['cdi', 'contrat à durée indéterminée', 'permanent'],
            'cdd': ['cdd', 'contrat à durée déterminée', 'temporary'],
            'interim': ['interim', 'intérim', 'temporary work'],
            'freelance': ['freelance', 'indépendant', 'contractor'],
            'stage': ['stage', 'internship'],
            'alternance': ['alternance', 'apprentissage', 'apprenticeship']
        }
        
        normalized_job_contract = None
        for key, values in contract_mapping.items():
            if any(val in job_contract for val in values):
                normalized_job_contract = key
                break
        
        if not normalized_job_contract:
            normalized_job_contract = job_contract
        
        normalized_preferences = []
        for pref in preferred_contracts:
            for key, values in contract_mapping.items():
                if any(val in pref.lower() for val in values):
                    normalized_preferences.append(key)
                    break
            else:
                normalized_preferences.append(pref.lower())
        
        return 1.0 if normalized_job_contract in normalized_preferences else 0.0
    
    def _calculate_availability_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de disponibilité (méthode originale)"""
        try:
            availability_date_str = self.questionnaire_data.get('date_disponibilite', '')
            job_start_date_str = job.get('date_debut', '')
            
            if not availability_date_str or not job_start_date_str:
                return 0.5
            
            try:
                availability_date = datetime.datetime.strptime(availability_date_str, "%d/%m/%Y").date()
                job_start_date = datetime.datetime.strptime(job_start_date_str, "%d/%m/%Y").date()
            except ValueError:
                try:
                    availability_date = datetime.datetime.strptime(availability_date_str, "%Y-%m-%d").date()
                    job_start_date = datetime.datetime.strptime(job_start_date_str, "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Format de date non reconnu: {availability_date_str}, {job_start_date_str}")
                    return 0.5
            
            delta = (job_start_date - availability_date).days
            
            if delta >= 0:
                return 1.0
            else:
                max_delay = 90
                delay = abs(delta)
                
                if delay > max_delay:
                    return 0.0
                else:
                    return 1.0 - (delay / max_delay)
        
        except Exception as e:
            logger.error(f"Erreur calcul disponibilité: {str(e)}")
            return 0.5
    
    def get_top_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les N meilleures offres correspondant au profil"""
        all_matches = self.calculate_matching_scores()
        return all_matches[:limit]

# Fonction d'entrée principale pour l'API
def match_candidate_with_jobs(cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any], 
                             job_data: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fonction principale améliorée qui calcule les matchings entre un candidat et des offres d'emploi
    """
    engine = ImprovedMatchingEngine()
    engine.load_candidate_data(cv_data, questionnaire_data)
    engine.load_job_data(job_data)
    
    return engine.get_top_matches(limit)
