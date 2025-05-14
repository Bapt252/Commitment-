#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moteur de matching pour les candidats et les offres d'emploi

Ce module analyse les données du CV, du questionnaire et des offres d'emploi
pour calculer un score de correspondance basé sur plusieurs critères :
- Compétences techniques
- Type de contrat recherché
- Localisation et temps de trajet
- Disponibilité vs date de prise de poste
- Fourchette de rémunération
- Expérience requise
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

# Configuration de l'API Google Maps
GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY")

class MatchingEngine:
    """
    Moteur de matching entre candidats et offres d'emploi
    """
    
    def __init__(self):
        self.cv_data = {}
        self.questionnaire_data = {}
        self.job_data = {}
        
    def load_candidate_data(self, cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> None:
        """
        Charge les données du candidat dans le moteur
        
        Args:
            cv_data: Données extraites du CV
            questionnaire_data: Données extraites du questionnaire
        """
        self.cv_data = cv_data
        self.questionnaire_data = questionnaire_data
        logger.info(f"Données candidat chargées: {len(self.cv_data)} éléments CV, {len(self.questionnaire_data)} éléments questionnaire")
    
    def load_job_data(self, job_data: List[Dict[str, Any]]) -> None:
        """
        Charge les données des offres d'emploi dans le moteur
        
        Args:
            job_data: Liste des offres d'emploi à analyser
        """
        self.job_data = job_data
        logger.info(f"Données emploi chargées: {len(self.job_data)} offres")
    
    def calculate_matching_scores(self) -> List[Dict[str, Any]]:
        """
        Calcule les scores de matching pour toutes les offres chargées
        
        Returns:
            Liste des offres avec leurs scores de matching
        """
        if not self.cv_data or not self.questionnaire_data or not self.job_data:
            logger.error("Données manquantes pour le calcul des scores")
            return []
        
        results = []
        
        for job in self.job_data:
            # Calcul des différents critères de matching
            skills_score = self._calculate_skills_score(job)
            contract_score = self._calculate_contract_score(job)
            location_score = self._calculate_location_score(job)
            date_score = self._calculate_availability_score(job)
            salary_score = self._calculate_salary_score(job)
            experience_score = self._calculate_experience_score(job)
            
            # Calcul du score global (pondéré)
            weights = {
                'skills': 0.30,         # 30% pour les compétences
                'contract': 0.15,       # 15% pour le type de contrat
                'location': 0.20,       # 20% pour la localisation
                'date': 0.10,           # 10% pour la disponibilité
                'salary': 0.15,         # 15% pour le salaire
                'experience': 0.10      # 10% pour l'expérience
            }
            
            total_score = (
                skills_score * weights['skills'] +
                contract_score * weights['contract'] +
                location_score * weights['location'] +
                date_score * weights['date'] +
                salary_score * weights['salary'] +
                experience_score * weights['experience']
            )
            
            # Formatage du score final en pourcentage
            job_result = job.copy()  # Copie pour ne pas modifier l'original
            job_result['matching_score'] = round(total_score * 100)
            
            # Détails des scores par critère pour affichage détaillé
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
    
    def get_top_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retourne les N meilleures offres correspondant au profil
        
        Args:
            limit: Nombre d'offres à retourner
            
        Returns:
            Liste des meilleures offres avec leurs scores
        """
        all_matches = self.calculate_matching_scores()
        return all_matches[:limit]
    
    def _calculate_skills_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching des compétences
        
        Args:
            job: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Extraire les compétences du CV et du job
        cv_skills = set(skill.lower() for skill in self.cv_data.get('competences', []))
        job_skills = set(skill.lower() for skill in job.get('competences', []))
        
        # Si pas de compétences listées, retourner un score par défaut
        if not job_skills:
            return 0.5
        
        # Calculer l'intersection des compétences
        matching_skills = cv_skills.intersection(job_skills)
        
        # Calculer le score basé sur le pourcentage de compétences requises que le candidat possède
        if len(job_skills) == 0:
            return 0.0
        
        return len(matching_skills) / len(job_skills)
    
    def _calculate_contract_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching du type de contrat
        
        Args:
            job: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        preferred_contracts = self.questionnaire_data.get('contrats_recherches', [])
        job_contract = job.get('type_contrat', '').lower()
        
        # Si les données sont manquantes, retourner un score moyen
        if not preferred_contracts or not job_contract:
            return 0.5
        
        # Normalisation des types de contrat
        contract_mapping = {
            'cdi': ['cdi', 'contrat à durée indéterminée', 'permanent'],
            'cdd': ['cdd', 'contrat à durée déterminée', 'temporary'],
            'interim': ['interim', 'intérim', 'temporary work'],
            'freelance': ['freelance', 'indépendant', 'contractor'],
            'stage': ['stage', 'internship'],
            'alternance': ['alternance', 'apprentissage', 'apprenticeship']
        }
        
        # Convertir vers le format normalisé
        normalized_job_contract = None
        for key, values in contract_mapping.items():
            if any(val in job_contract for val in values):
                normalized_job_contract = key
                break
        
        # Si on n'a pas pu normaliser, utiliser la valeur originale
        if not normalized_job_contract:
            normalized_job_contract = job_contract
        
        # Normaliser aussi les préférences du candidat
        normalized_preferences = []
        for pref in preferred_contracts:
            for key, values in contract_mapping.items():
                if any(val in pref.lower() for val in values):
                    normalized_preferences.append(key)
                    break
            else:
                normalized_preferences.append(pref.lower())
        
        # Calcul du score
        if normalized_job_contract in normalized_preferences:
            return 1.0
        else:
            return 0.0
    
    def _calculate_location_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de la localisation
        
        Args:
            job: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        candidate_address = self.questionnaire_data.get('adresse', '')
        job_address = job.get('localisation', '')
        max_commute_time = self.questionnaire_data.get('temps_trajet_max', 60)  # Minutes
        
        # Si les données sont manquantes, retourner un score moyen
        if not candidate_address or not job_address:
            return 0.5
        
        # Calculer le temps de trajet via l'API Google Maps
        try:
            commute_time = self._get_commute_time(candidate_address, job_address)
            
            # Si on n'a pas pu calculer le temps de trajet, retourner un score moyen
            if commute_time is None:
                return 0.5
            
            # Calcul du score basé sur le temps de trajet maximum acceptable
            # Plus le temps est proche de 0, meilleur est le score
            # Plus le temps approche ou dépasse le maximum, plus le score baisse
            if commute_time <= max_commute_time:
                return 1.0 - (commute_time / max_commute_time)
            else:
                return 0.0
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps de trajet: {str(e)}")
            return 0.5
    
    def _get_commute_time(self, origin: str, destination: str) -> Optional[int]:
        """
        Calcule le temps de trajet entre deux adresses via l'API Google Maps
        
        Args:
            origin: Adresse de départ
            destination: Adresse d'arrivée
            
        Returns:
            Temps de trajet en minutes ou None si erreur
        """
        # Pour un MVP, on peut simuler le temps de trajet sans appeler l'API
        # En production, utiliser l'API Google Maps Distance Matrix
        
        try:
            # Pour une vraie implémentation, uncomment le code ci-dessous:
            """
            url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
            params = {
                'origins': origin,
                'destinations': destination,
                'mode': 'driving',
                'key': GOOGLE_MAPS_API_KEY
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get('status') == 'OK':
                elements = data.get('rows', [{}])[0].get('elements', [{}])
                if elements and elements[0].get('status') == 'OK':
                    duration_seconds = elements[0].get('duration', {}).get('value', 0)
                    return duration_seconds // 60  # Conversion en minutes
            
            return None
            """
            
            # Simulation pour le MVP:
            # Distance en km (calculée à partir de coordonnées géographiques fictives)
            import random
            
            # Simuler une distance aléatoire entre 1 et 50 km
            distance = random.uniform(1, 50)
            
            # Vitesse moyenne en km/h (en ville)
            avg_speed = 30
            
            # Temps en minutes (formule simple)
            time_minutes = (distance / avg_speed) * 60
            
            return round(time_minutes)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel à l'API Google Maps: {str(e)}")
            return None
    
    def _calculate_availability_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de la disponibilité
        
        Args:
            job: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        try:
            availability_date_str = self.questionnaire_data.get('date_disponibilite', '')
            job_start_date_str = job.get('date_debut', '')
            
            # Si les données sont manquantes, retourner un score moyen
            if not availability_date_str or not job_start_date_str:
                return 0.5
            
            # Parser les dates (format DD/MM/YYYY)
            try:
                availability_date = datetime.datetime.strptime(availability_date_str, "%d/%m/%Y").date()
                job_start_date = datetime.datetime.strptime(job_start_date_str, "%d/%m/%Y").date()
            except ValueError:
                # Essayer un autre format de date (YYYY-MM-DD)
                try:
                    availability_date = datetime.datetime.strptime(availability_date_str, "%Y-%m-%d").date()
                    job_start_date = datetime.datetime.strptime(job_start_date_str, "%Y-%m-%d").date()
                except ValueError:
                    logger.error(f"Format de date non reconnu: {availability_date_str}, {job_start_date_str}")
                    return 0.5
            
            # Calcul de la différence en jours
            delta = (job_start_date - availability_date).days
            
            # Si le candidat est disponible avant la date de début, score parfait
            if delta >= 0:
                return 1.0
            else:
                # Si le candidat est disponible après la date de début,
                # le score diminue en fonction du nombre de jours de retard
                # Limite à 90 jours de retard (3 mois)
                max_delay = 90
                delay = abs(delta)
                
                if delay > max_delay:
                    return 0.0
                else:
                    return 1.0 - (delay / max_delay)
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score de disponibilité: {str(e)}")
            return 0.5
    
    def _calculate_salary_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching du salaire
        
        Args:
            job: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        min_salary = self.questionnaire_data.get('salaire_min', 0)
        job_salary_str = job.get('salaire', '')
        
        # Si les données sont manquantes, retourner un score moyen
        if not min_salary or not job_salary_str:
            return 0.5
        
        # Extraire la fourchette de salaire
        try:
            # Patterns courants de salaire
            # Ex: "45K-55K€", "45000-55000 €", "45 000 € - 55 000 €"
            import re
            
            # Supprimer les espaces, remplacer K par 000
            salary_clean = job_salary_str.replace(' ', '').replace('k', '000').replace('K', '000')
            
            # Trouver les chiffres
            numbers = re.findall(r'\d+', salary_clean)
            
            if len(numbers) >= 2:
                job_min_salary = int(numbers[0])
                job_max_salary = int(numbers[1])
            elif len(numbers) == 1:
                job_min_salary = int(numbers[0])
                job_max_salary = int(numbers[0]) * 1.2  # Estimation: max = min + 20%
            else:
                return 0.5
            
            # Calcul du score
            if job_max_salary < min_salary:
                # Salaire proposé inférieur au minimum demandé
                return 0.0
            elif job_min_salary >= min_salary:
                # Salaire proposé supérieur au minimum demandé
                return 1.0
            else:
                # Salaire partiellement dans la fourchette
                # Plus le min du job est proche du min demandé, meilleur est le score
                return (job_min_salary / min_salary)
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score de salaire: {str(e)}")
            return 0.5
    
    def _calculate_experience_score(self, job: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de l'expérience
        
        Args:
            job: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        candidate_experience = self.cv_data.get('annees_experience', 0)
        job_experience_str = job.get('experience', '')
        
        # Si les données sont manquantes, retourner un score moyen
        if not candidate_experience or not job_experience_str:
            return 0.5
        
        # Extraire la fourchette d'expérience
        try:
            import re
            
            # Trouver les chiffres dans la chaîne d'expérience
            numbers = re.findall(r'\d+', job_experience_str)
            
            if len(numbers) >= 2:
                job_min_exp = int(numbers[0])
                job_max_exp = int(numbers[1])
            elif len(numbers) == 1:
                if "débutant" in job_experience_str.lower():
                    job_min_exp = 0
                    job_max_exp = int(numbers[0])
                else:
                    job_min_exp = int(numbers[0])
                    job_max_exp = int(numbers[0]) + 2  # Estimation: max = min + 2 ans
            else:
                # Pas de chiffres trouvés, analyse textuelle
                if "débutant" in job_experience_str.lower():
                    job_min_exp = 0
                    job_max_exp = 2
                elif "confirmé" in job_experience_str.lower():
                    job_min_exp = 3
                    job_max_exp = 5
                elif "senior" in job_experience_str.lower():
                    job_min_exp = 5
                    job_max_exp = 10
                else:
                    return 0.5
            
            # Calcul du score
            if candidate_experience < job_min_exp:
                # Expérience insuffisante
                if job_min_exp > 0:
                    # Score proportionnel à l'écart
                    return max(0, candidate_experience / job_min_exp)
                else:
                    return 1.0  # Pas d'expérience requise
            elif candidate_experience > job_max_exp * 1.5:
                # Candidat surqualifié (>150% de l'expérience max)
                # Le score diminue proportionnellement
                return max(0.5, 1.0 - (candidate_experience - job_max_exp) / (job_max_exp * 0.5))
            else:
                # Expérience dans la fourchette ou légèrement supérieure
                return 1.0
                
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score d'expérience: {str(e)}")
            return 0.5

# Fonction d'entrée principale pour l'API
def match_candidate_with_jobs(cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any], 
                             job_data: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fonction principale qui calcule les matchings entre un candidat et des offres d'emploi
    
    Args:
        cv_data: Données extraites du CV
        questionnaire_data: Données du questionnaire
        job_data: Liste des offres d'emploi
        limit: Nombre maximum d'offres à retourner
        
    Returns:
        Liste des meilleures offres avec leurs scores
    """
    engine = MatchingEngine()
    engine.load_candidate_data(cv_data, questionnaire_data)
    engine.load_job_data(job_data)
    
    return engine.get_top_matches(limit)

# Pour les tests
if __name__ == "__main__":
    # Données de test
    cv_data = {
        "competences": ["Python", "JavaScript", "React", "SQL", "Git"],
        "annees_experience": 4,
        "formation": "Bac+5 Informatique"
    }
    
    questionnaire_data = {
        "contrats_recherches": ["CDI", "CDD"],
        "adresse": "20 Avenue de Paris, 75015 Paris",
        "temps_trajet_max": 45,  # minutes
        "date_disponibilite": "01/06/2025",
        "salaire_min": 45000,
        "domaines_interets": ["Web", "Data"]
    }
    
    job_data = [
        {
            "id": 1,
            "titre": "Développeur Full-Stack",
            "entreprise": "TechVision",
            "localisation": "15 Rue de Rivoli, 75004 Paris",
            "type_contrat": "CDI",
            "competences": ["JavaScript", "React", "Node.js", "MongoDB"],
            "experience": "3-5 ans",
            "date_debut": "15/05/2025",
            "salaire": "45K-55K€"
        },
        {
            "id": 2,
            "titre": "Data Engineer",
            "entreprise": "DataInsight",
            "localisation": "92 Avenue des Champs-Élysées, 75008 Paris",
            "type_contrat": "CDD",
            "competences": ["Python", "SQL", "Hadoop", "Spark"],
            "experience": "2-4 ans",
            "date_debut": "01/07/2025",
            "salaire": "50K-60K€"
        }
    ]
    
    # Test du moteur de matching
    results = match_candidate_with_jobs(cv_data, questionnaire_data, job_data)
    
    # Affichage des résultats
    for i, job in enumerate(results):
        print(f"\nOffre #{i+1} - Score: {job['matching_score']}%")
        print(f"Titre: {job['titre']}")
        print(f"Entreprise: {job['entreprise']}")
        print(f"Détails des scores:")
        for criterion, score in job['matching_details'].items():
            print(f"  - {criterion}: {score}%")
