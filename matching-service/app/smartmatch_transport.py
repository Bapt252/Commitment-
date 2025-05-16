"""
Module d'extension de SmartMatch pour la prise en compte des transports en commun
--------------------------------------------------------------------------------
Ajoute des fonctionnalités pour améliorer le matching géographique en considérant
différents modes de transport et les préférences des candidats.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import json

# Import du client Google Maps
from app.google_maps_client import GoogleMapsClient
from app.api_keys import get_maps_api_key

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommuteMatchExtension:
    """
    Extension pour ajouter la prise en compte avancée des trajets
    dans le système de matching SmartMatch.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialise l'extension avec une clé API Google Maps.
        
        Args:
            api_key (str, optional): Clé API Google Maps
        """
        if api_key is None:
            api_key = get_maps_api_key()
            
        self.maps_client = GoogleMapsClient(api_key=api_key)
        logger.info("Extension CommuteMatch initialisée")
    
    def calculate_commute_score(self, candidate: Dict[str, Any], 
                              company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcule un score de trajet en tenant compte des préférences du candidat
        et des options de transport disponibles pour l'entreprise.
        
        Args:
            candidate (Dict): Données du candidat
            company (Dict): Données de l'entreprise
            
        Returns:
            Dict: Score et détails du trajet
        """
        candidate_location = candidate.get('location', '')
        company_location = company.get('location', '')
        
        # Récupérer les préférences du candidat
        preferred_mode = candidate.get('preferred_transport_mode', 'driving')
        max_time = candidate.get('preferred_commute_time', 60)  # 60 minutes par défaut
        
        # Si la politique de travail à distance est "full", le score est parfait
        if company.get('remote_policy') == 'full' and candidate.get('remote_preference') in ['full', 'hybrid']:
            return {
                'score': 1.0,
                'details': {
                    'is_remote': True,
                    'remote_match': True,
                    'travel_times': {},
                    'preferred_mode': preferred_mode,
                    'preferred_time': max_time,
                    'explanation': "Travail entièrement à distance possible, pas besoin de déplacement."
                }
            }
        
        # Calculer les temps de trajet pour différents modes de transport
        travel_times = {}
        
        # Temps de conduite (toujours calculé)
        travel_times['driving'] = self.maps_client.get_travel_time(
            candidate_location, company_location, mode="driving")
        
        # Temps en transport en commun (si l'entreprise est accessible)
        if company.get('transit_friendly', False):
            travel_times['transit'] = self.maps_client.get_travel_time(
                candidate_location, company_location, mode="transit")
        else:
            travel_times['transit'] = -1  # Non disponible
        
        # Temps à vélo (si l'entreprise a des installations)
        if company.get('bicycle_facilities', False):
            travel_times['bicycling'] = self.maps_client.get_travel_time(
                candidate_location, company_location, mode="bicycling")
        else:
            travel_times['bicycling'] = -1  # Non disponible
        
        # Temps de marche (pour les courtes distances)
        travel_times['walking'] = self.maps_client.get_travel_time(
            candidate_location, company_location, mode="walking")
        
        # Obtenir le temps pour le mode préféré
        preferred_time = travel_times.get(preferred_mode, -1)
        
        # Si le mode préféré n'est pas disponible, essayer les alternatives
        if preferred_time <= 0:
            # Chercher le meilleur temps parmi les modes disponibles
            best_time = float('inf')
            best_mode = None
            
            for mode, time in travel_times.items():
                if time > 0 and time < best_time:
                    best_time = time
                    best_mode = mode
            
            if best_mode:
                preferred_mode = best_mode
                preferred_time = best_time
            else:
                preferred_time = -1
        
        # Calculer le score
        if preferred_time <= 0:
            # Aucun trajet viable trouvé
            score = 0.1  # Score minimal mais pas nul
            explanation = "Aucun trajet viable trouvé entre le candidat et l'entreprise."
        else:
            # Normaliser le temps par rapport à la préférence
            time_ratio = preferred_time / max_time
            
            if time_ratio <= 0.5:  # Moins de la moitié du temps max
                score = 1.0
                explanation = f"Excellent temps de trajet en {preferred_mode}: {preferred_time} minutes."
            elif time_ratio <= 1.0:  # Entre la moitié et le temps max
                score = 1.0 - 0.5 * (time_ratio - 0.5) / 0.5
                explanation = f"Bon temps de trajet en {preferred_mode}: {preferred_time} minutes."
            else:  # Plus que le temps max
                score = 0.5 * max(0, 2.0 - time_ratio)
                explanation = f"Temps de trajet en {preferred_mode} ({preferred_time} min) supérieur à la préférence du candidat ({max_time} min)."
            
            # Bonus pour les options multiples de transport
            available_options = sum(1 for t in travel_times.values() if t > 0 and t <= max_time * 1.5)
            if available_options > 1:
                option_bonus = min(0.2, (available_options - 1) * 0.1)  # Max 0.2 de bonus
                score = min(1.0, score + option_bonus)
                explanation += f" Bonus pour {available_options} options de transport disponibles."
        
        return {
            'score': score,
            'details': {
                'is_remote': False,
                'travel_times': travel_times,
                'preferred_mode': preferred_mode,
                'preferred_time': max_time,
                'actual_time': preferred_time,
                'explanation': explanation
            }
        }
    
    def analyze_transport_compatibility(self, 
                                       candidate: Dict[str, Any], 
                                       company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse la compatibilité des préférences de transport entre candidat et entreprise.
        
        Args:
            candidate (Dict): Données du candidat
            company (Dict): Données de l'entreprise
            
        Returns:
            Dict: Analyse détaillée de la compatibilité
        """
        commute_score = self.calculate_commute_score(candidate, company)
        
        # Vérifier les préférences de transport en commun
        transport_match = False
        if candidate.get('preferred_transport_mode') == 'transit' and company.get('transit_friendly', False):
            transport_match = True
        
        # Vérifier les préférences de vélo
        bicycle_match = False
        if candidate.get('preferred_transport_mode') == 'bicycling' and company.get('bicycle_facilities', False):
            bicycle_match = True
        
        # Vérifier la politique de travail à distance
        remote_match = False
        if candidate.get('remote_preference') == 'full' and company.get('remote_policy') == 'full':
            remote_match = True
        elif candidate.get('remote_preference') == 'hybrid' and company.get('remote_policy') in ['hybrid', 'full']:
            remote_match = True
        elif candidate.get('remote_preference') == 'office_only' and company.get('remote_policy') in ['office_only', 'hybrid']:
            remote_match = True
        
        # Calculer un score d'accessibilité global
        accessibility_score = commute_score['score']
        if remote_match:
            accessibility_score = max(accessibility_score, 0.8)  # Bon score minimal si compatible en télétravail
        
        if transport_match or bicycle_match:
            accessibility_score = min(1.0, accessibility_score + 0.1)  # Bonus pour les modes de transport préférés
        
        return {
            'commute_score': commute_score['score'],
            'accessibility_score': accessibility_score,
            'remote_match': remote_match,
            'transport_match': transport_match,
            'bicycle_match': bicycle_match,
            'travel_times': commute_score['details']['travel_times'],
            'explanation': commute_score['details']['explanation']
        }


def enhance_smartmatch_with_transport(smartmatch_instance, api_key=None):
    """
    Améliore une instance SmartMatch existante avec la prise en compte des transports.
    
    Args:
        smartmatch_instance: Instance de SmartMatcher à améliorer
        api_key (str, optional): Clé API Google Maps
        
    Returns:
        Le SmartMatcher amélioré
    """
    # Créer l'extension
    extension = CommuteMatchExtension(api_key=api_key)
    
    # Ajouter l'extension comme attribut
    smartmatch_instance.commute_extension = extension
    
    # Stocker la fonction originale de calcul de score
    original_calculate_location_match = smartmatch_instance.calculate_location_match
    
    # Définir la nouvelle fonction de calcul qui utilise l'extension
    def enhanced_calculate_location_match(candidate, company):
        # Si l'original existe, l'appeler d'abord
        base_score = 0.5
        try:
            base_score = original_calculate_location_match(candidate, company)
        except Exception as e:
            logger.warning(f"Erreur lors du calcul du score de localisation original: {e}")
        
        # Calculer le score amélioré avec l'extension
        try:
            # Adapter les noms de champs entre job et company
            company_adapted = adapt_job_to_company(company)
            
            enhanced_result = smartmatch_instance.commute_extension.calculate_commute_score(candidate, company_adapted)
            enhanced_score = enhanced_result['score']
            
            # Combiner les scores (donner plus de poids au score amélioré)
            combined_score = 0.3 * base_score + 0.7 * enhanced_score
            
            # Ajouter les détails au résultat
            if not hasattr(smartmatch_instance, 'matching_details'):
                smartmatch_instance.matching_details = {}
            
            candidate_id = candidate.get('id', 'unknown')
            company_id = company.get('id', 'unknown')
            key = f"{candidate_id}_{company_id}"
            
            if key not in smartmatch_instance.matching_details:
                smartmatch_instance.matching_details[key] = {}
            
            smartmatch_instance.matching_details[key]['commute'] = enhanced_result['details']
            
            return combined_score
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score de trajet amélioré: {e}", exc_info=True)
            return base_score
    
    # Remplacer la méthode
    smartmatch_instance.calculate_location_match = enhanced_calculate_location_match
    
    # Ajouter une méthode match pour la compatibilité avec l'extension
    def match(candidates, companies):
        """
        Effectue un matching entre plusieurs candidats et entreprises
        
        Args:
            candidates (List[Dict]): Liste des profils candidats
            companies (List[Dict]): Liste des offres d'emploi/entreprises
            
        Returns:
            List[Dict]: Résultats de matching
        """
        results = []
        
        for candidate in candidates:
            for company in companies:
                # Adapter l'entreprise au format attendu par calculate_match
                job = adapt_company_to_job(company)
                
                # Calculer le match
                match_result = smartmatch_instance.calculate_match(candidate, job)
                
                # Adapter le résultat pour inclure les IDs d'entreprise
                match_result['company_id'] = company.get('id', '')
                match_result['candidate_location'] = candidate.get('location', '')
                match_result['company_location'] = company.get('location', '')
                
                results.append(match_result)
        
        return results
    
    # Ajouter la méthode match
    smartmatch_instance.match = match
    
    # Stocker la fonction originale de génération d'insights
    original_generate_insights = smartmatch_instance.generate_insights
    
    # Créer une nouvelle fonction compatible avec le format de l'extension
    def generate_commute_insights(matches):
        """
        Génère des insights sur les trajets pour une liste de matchs
        
        Args:
            matches (List[Dict]): Liste de résultats de matching
            
        Returns:
            List[Dict]: Liste d'insights sur les trajets
        """
        insights = []
        
        # Si aucun match, retourner liste vide
        if not matches:
            return insights
        
        # Analyser les temps de trajet moyens
        total_time = 0
        count = 0
        
        for match in matches:
            candidate_id = match.get('candidate_id', '')
            company_id = match.get('company_id', '')
            key = f"{candidate_id}_{company_id}"
            
            if hasattr(smartmatch_instance, 'matching_details') and key in smartmatch_instance.matching_details:
                details = smartmatch_instance.matching_details[key].get('commute', {})
                if 'travel_times' in details:
                    preferred_mode = details.get('preferred_mode', 'driving')
                    time = details['travel_times'].get(preferred_mode, -1)
                    
                    if time > 0:
                        total_time += time
                        count += 1
        
        if count > 0:
            avg_time = total_time / count
            insights.append({
                'type': 'commute',
                'message': f"Le temps de trajet moyen pour les matchings est de {avg_time:.0f} minutes.",
                'data': {'avg_commute_time': avg_time},
                'category': 'info'
            })
        
        # Analyser les modes de transport préférés
        mode_counts = {}
        for match in matches:
            candidate_id = match.get('candidate_id', '')
            company_id = match.get('company_id', '')
            key = f"{candidate_id}_{company_id}"
            
            if hasattr(smartmatch_instance, 'matching_details') and key in smartmatch_instance.matching_details:
                details = smartmatch_instance.matching_details[key].get('commute', {})
                if details:
                    mode = details.get('preferred_mode', 'driving')
                    mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        if mode_counts:
            most_common_mode = max(mode_counts.items(), key=lambda x: x[1])[0]
            insights.append({
                'type': 'transport_mode',
                'message': f"Le mode de transport le plus courant est {most_common_mode}.",
                'data': {'mode_counts': mode_counts},
                'category': 'info'
            })
        
        return insights
    
    # Ajouter la méthode au SmartMatcher
    smartmatch_instance.generate_commute_insights = generate_commute_insights
    
    # Définir une nouvelle fonction de génération d'insights
    def enhanced_generate_insights(*args, **kwargs):
        """
        Version améliorée de la fonction generate_insights qui combine les insights d'origine
        avec les insights de trajet
        """
        # Déterminer le format d'appel correct
        if len(args) >= 5:  # Format original: generate_insights(candidate, job, skill_score, location_score, ...)
            insights = original_generate_insights(*args, **kwargs)
            return insights
        else:  # Format extension: generate_insights(matches)
            matches = args[0] if args else kwargs.get('matches', [])
            
            # Générer des insights de trajet
            commute_insights = smartmatch_instance.generate_commute_insights(matches)
            
            return commute_insights
    
    # Remplacer la méthode generate_insights
    smartmatch_instance.generate_insights_extended = enhanced_generate_insights
    
    return smartmatch_instance


def adapt_company_to_job(company):
    """
    Adapte une structure d'entreprise au format attendu par calculate_match
    
    Args:
        company (Dict): Données de l'entreprise
        
    Returns:
        Dict: Format compatible avec calculate_match
    """
    job = company.copy()
    
    # Correspondances des champs
    if 'title' not in job and 'name' in company:
        job['title'] = company['name']
    
    if 'required_skills' not in job and 'skills' in company:
        job['required_skills'] = company['skills']
    
    if 'preferred_skills' not in job and 'nice_to_have_skills' in company:
        job['preferred_skills'] = company['nice_to_have_skills']
    
    if 'min_years_of_experience' not in job and 'experience_required' in company:
        job['min_years_of_experience'] = company['experience_required']
    
    if 'required_education' not in job and 'education_level' in company:
        job['required_education'] = company['education_level']
    
    if 'offers_remote' not in job and 'remote_policy' in company:
        job['offers_remote'] = company['remote_policy'] in ['full', 'hybrid']
    
    if 'salary_range' not in job and 'salary' in company:
        salary = company['salary']
        if isinstance(salary, dict) and 'min' in salary and 'max' in salary:
            job['salary_range'] = salary
        else:
            # Estimer une fourchette basée sur une valeur unique
            if isinstance(salary, (int, float)):
                job['salary_range'] = {'min': int(salary * 0.9), 'max': int(salary * 1.1)}
            else:
                job['salary_range'] = {'min': 0, 'max': 0}
    
    return job


def adapt_job_to_company(job):
    """
    Adapte une structure de job au format attendu par calculate_commute_score
    
    Args:
        job (Dict): Données du job
        
    Returns:
        Dict: Format compatible avec calculate_commute_score
    """
    company = job.copy()
    
    # Correspondances des champs
    if 'name' not in company and 'title' in job:
        company['name'] = job['title']
    
    if 'skills' not in company and 'required_skills' in job:
        company['skills'] = job['required_skills']
    
    if 'nice_to_have_skills' not in company and 'preferred_skills' in job:
        company['nice_to_have_skills'] = job['preferred_skills']
    
    if 'experience_required' not in company and 'min_years_of_experience' in job:
        company['experience_required'] = job['min_years_of_experience']
    
    if 'education_level' not in company and 'required_education' in job:
        company['education_level'] = job['required_education']
    
    if 'remote_policy' not in company and 'offers_remote' in job:
        company['remote_policy'] = 'hybrid' if job['offers_remote'] else 'office_only'
    
    if 'transit_friendly' not in company:
        company['transit_friendly'] = True  # Par défaut, considérer que l'entreprise est accessible en transport
    
    if 'bicycle_facilities' not in company:
        company['bicycle_facilities'] = True  # Par défaut, considérer que l'entreprise a des installations pour vélos
    
    return company