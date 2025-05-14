"""
Module d'extension de SmartMatch pour la prise en compte des transports en commun
--------------------------------------------------------------------------------
Ajoute des fonctionnalités pour améliorer le matching géographique en considérant
différents modes de transport et les préférences des candidats.
Auteur: Claude/Anthropic
Date: 14/05/2025
"""

import os
import logging
from typing import Dict, List, Any, Optional, Tuple
import json

# Import du client Google Maps
from app.google_maps_client import GoogleMapsClient

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


def enhance_smartmatch_with_transport(smartmatch_instance, api_key: str = None):
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
    original_calculate_location_score = getattr(smartmatch_instance, 'calculate_location_score', None)
    
    # Définir la nouvelle fonction de calcul qui utilise l'extension
    def enhanced_calculate_location_score(instance, candidate, company):
        # Si l'original existe, l'appeler d'abord
        base_score = 0.5
        if original_calculate_location_score:
            try:
                base_score = original_calculate_location_score(instance, candidate, company)
            except Exception as e:
                logger.warning(f"Erreur lors du calcul du score de localisation original: {e}")
        
        # Calculer le score amélioré avec l'extension
        try:
            enhanced_result = instance.commute_extension.calculate_commute_score(candidate, company)
            enhanced_score = enhanced_result['score']
            
            # Combiner les scores (donner plus de poids au score amélioré)
            combined_score = 0.3 * base_score + 0.7 * enhanced_score
            
            # Ajouter les détails au résultat
            if not hasattr(instance, 'matching_details'):
                instance.matching_details = {}
            
            candidate_id = candidate.get('id', 'unknown')
            company_id = company.get('id', 'unknown')
            key = f"{candidate_id}_{company_id}"
            
            if key not in instance.matching_details:
                instance.matching_details[key] = {}
            
            instance.matching_details[key]['commute'] = enhanced_result['details']
            
            return combined_score
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score de trajet amélioré: {e}", exc_info=True)
            return base_score
    
    # Remplacer la méthode
    if hasattr(smartmatch_instance, 'calculate_location_score'):
        setattr(smartmatch_instance, 'calculate_location_score', 
                lambda candidate, company: enhanced_calculate_location_score(smartmatch_instance, candidate, company))
    
    # Ajouter une nouvelle méthode pour générer des insights sur les trajets
    def generate_commute_insights(instance, matches):
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
            
            if hasattr(instance, 'matching_details') and key in instance.matching_details:
                details = instance.matching_details[key].get('commute', {})
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
                'data': {'avg_commute_time': avg_time}
            })
        
        # Analyser les modes de transport préférés
        mode_counts = {}
        for match in matches:
            candidate_id = match.get('candidate_id', '')
            company_id = match.get('company_id', '')
            key = f"{candidate_id}_{company_id}"
            
            if hasattr(instance, 'matching_details') and key in instance.matching_details:
                details = instance.matching_details[key].get('commute', {})
                if details:
                    mode = details.get('preferred_mode', 'driving')
                    mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        if mode_counts:
            most_common_mode = max(mode_counts.items(), key=lambda x: x[1])[0]
            insights.append({
                'type': 'transport_mode',
                'message': f"Le mode de transport le plus courant est {most_common_mode}.",
                'data': {'mode_counts': mode_counts}
            })
        
        # Identifier les opportunités de covoiturage
        carpooling_opportunities = []
        processed_companies = set()
        
        for i, match1 in enumerate(matches):
            company_id1 = match1.get('company_id', '')
            if company_id1 in processed_companies:
                continue
            
            candidate_location1 = match1.get('candidate_location', '')
            company_location1 = match1.get('company_location', '')
            
            same_company_candidates = []
            
            for j, match2 in enumerate(matches):
                if i == j:
                    continue
                
                company_id2 = match2.get('company_id', '')
                candidate_location2 = match2.get('candidate_location', '')
                
                if company_id1 == company_id2 and candidate_location1 and candidate_location2:
                    # Vérifier si les candidats sont proches
                    try:
                        travel_time = instance.commute_extension.maps_client.get_travel_time(
                            candidate_location1, candidate_location2
                        )
                        
                        if 0 < travel_time <= 15:  # 15 minutes max entre candidats
                            same_company_candidates.append({
                                'candidate_id': match2.get('candidate_id', ''),
                                'distance_minutes': travel_time
                            })
                    except Exception as e:
                        logger.error(f"Erreur lors du calcul de la distance entre candidats: {e}")
            
            if len(same_company_candidates) >= 2:
                carpooling_opportunities.append({
                    'company_id': company_id1,
                    'company_location': company_location1,
                    'candidates': same_company_candidates
                })
            
            processed_companies.add(company_id1)
        
        if carpooling_opportunities:
            insights.append({
                'type': 'carpooling',
                'message': f"Opportunité de covoiturage identifiée pour {len(carpooling_opportunities)} entreprises.",
                'data': {'opportunities': carpooling_opportunities}
            })
        
        return insights
    
    # Ajouter la méthode au SmartMatcher
    setattr(smartmatch_instance, 'generate_commute_insights', 
            lambda matches: generate_commute_insights(smartmatch_instance, matches))
    
    # Étendre la méthode de génération d'insights si elle existe
    original_generate_insights = getattr(smartmatch_instance, 'generate_insights', None)
    
    if original_generate_insights:
        def enhanced_generate_insights(instance, matches):
            # Appeler la méthode originale
            insights = original_generate_insights(instance, matches)
            
            # Ajouter les insights de trajet
            commute_insights = instance.generate_commute_insights(matches)
            insights.extend(commute_insights)
            
            return insights
        
        # Remplacer la méthode
        setattr(smartmatch_instance, 'generate_insights', 
                lambda matches: enhanced_generate_insights(smartmatch_instance, matches))
    
    return smartmatch_instance
