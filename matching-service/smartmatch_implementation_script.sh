#!/bin/bash

# Script d'implémentation des améliorations pour SmartMatch
# Ce script applique toutes les modifications nécessaires pour rendre SmartMatch fonctionnel

echo "Début de l'implémentation des améliorations pour SmartMatch..."

# 1. Créer des répertoires de sauvegarde
mkdir -p backups

# 2. Sauvegarder les fichiers originaux
echo "Sauvegarde des fichiers originaux..."
cp app/smartmatch.py backups/smartmatch.py.bak
cp app/smartmatch_transport.py backups/smartmatch_transport.py.bak
cp test_smartmatch.py backups/test_smartmatch.py.bak
cp test_smartmatch_transport.py backups/test_smartmatch_transport.py.bak

# 3. Corriger l'erreur d'indentation dans smartmatch.py
echo "Correction de l'erreur d'indentation dans smartmatch.py..."
sed -i.tmp '/""" *$/ {
    N
    /"""\\ndef load_test_data():/,/"""/ {
        s/"""\\ndef load_test_data():\\n    """\\n    Fonction de compatibilité avec l'\''ancien code\\n    """/def load_test_data():\\n    """\\n    Fonction de compatibilité avec l'\''ancien code\\n    """/
    }
}' app/smartmatch.py

# 4. Créer le fichier de gestion des API keys
echo "Création du fichier de gestion des API keys..."
cat > app/api_keys.py << 'EOAPI'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des clés API
------------------------------
Fournit des fonctions pour récupérer les clés API depuis différentes sources.

Auteur: Claude
Date: 16/05/2025
"""

import os
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

def get_maps_api_key():
    """
    Récupère la clé API Google Maps depuis différentes sources
    
    Returns:
        str: Clé API Google Maps ou None
    """
    # Ordre de priorité: variable d'environnement, fichier .env, fichier de configuration
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    
    if not api_key:
        # Essayer de charger depuis le fichier .env
        try:
            if os.path.exists('.env'):
                with open('.env', 'r') as f:
                    for line in f:
                        if line.startswith('GOOGLE_MAPS_API_KEY='):
                            api_key = line.strip().split('=', 1)[1].strip('"\'')
                            break
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du fichier .env: {e}")
    
    if not api_key:
        # Essayer de charger depuis le fichier de configuration
        try:
            if os.path.exists('config.py'):
                import importlib.util
                spec = importlib.util.spec_from_file_location("config", "config.py")
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)
                
                if hasattr(config, 'GOOGLE_MAPS_API_KEY'):
                    api_key = config.GOOGLE_MAPS_API_KEY
        except Exception as e:
            logger.warning(f"Erreur lors du chargement du fichier de configuration: {e}")
    
    return api_key
EOAPI

# 5. Améliorer l'intégration SmartMatch Transport
echo "Amélioration de l'intégration SmartMatch Transport..."
cat > app/smartmatch_transport.py << 'EOTRANSPORT'
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
EOTRANSPORT

# 6. Créer l'API REST
echo "Création de l'API REST SmartMatch..."
mkdir -p app/api
cat > app/api/smartmatch_api.py << 'EOAPI'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API REST pour SmartMatch
------------------------
Expose les fonctionnalités du système SmartMatch via une API REST.

Auteur: Claude
Date: 16/05/2025
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import json
import time
import logging
import os
from typing import Dict, List, Any, Optional

from app.smartmatch import SmartMatcher
from app.smartmatch_transport import enhance_smartmatch_with_transport
from app.api_keys import get_maps_api_key

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Créer l'application FastAPI
app = FastAPI(
    title="SmartMatch API",
    description="API pour le système de matching avancé SmartMatch",
    version="1.0.0"
)

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser le SmartMatcher
api_key = get_maps_api_key()
matcher = SmartMatcher(api_key=api_key)
matcher = enhance_smartmatch_with_transport(matcher, api_key=api_key)

@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {"message": "Bienvenue sur l'API SmartMatch"}

@app.get("/health")
async def health():
    """Endpoint de vérification de l'état"""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/match/single")
async def match_single(candidate: Dict[str, Any], job: Dict[str, Any]):
    """
    Effectue un matching entre un candidat et une offre d'emploi
    
    Args:
        candidate: Profil du candidat
        job: Offre d'emploi
        
    Returns:
        Résultat du matching
    """
    try:
        result = matcher.calculate_match(candidate, job)
        return result
    except Exception as e:
        logger.error(f"Erreur lors du matching: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching: {str(e)}")

@app.post("/api/match/batch")
async def match_batch(candidates: List[Dict[str, Any]], jobs: List[Dict[str, Any]]):
    """
    Effectue un matching par lots entre plusieurs candidats et offres d'emploi
    
    Args:
        candidates: Liste des profils candidats
        jobs: Liste des offres d'emploi
        
    Returns:
        Résultats du matching pour toutes les paires
    """
    try:
        results = matcher.batch_match(candidates, jobs)
        return results
    except Exception as e:
        logger.error(f"Erreur lors du matching par lots: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching par lots: {str(e)}")

@app.post("/api/match/company")
async def match_with_company(candidates: List[Dict[str, Any]], companies: List[Dict[str, Any]]):
    """
    Effectue un matching entre des candidats et des entreprises
    
    Args:
        candidates: Liste des profils candidats
        companies: Liste des entreprises
        
    Returns:
        Résultats du matching
    """
    try:
        results = matcher.match(candidates, companies)
        return results
    except Exception as e:
        logger.error(f"Erreur lors du matching avec entreprises: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du matching avec entreprises: {str(e)}")

@app.get("/api/skills/expand")
async def expand_skills(skills: str):
    """
    Étend une liste de compétences avec des synonymes
    
    Args:
        skills: Liste de compétences séparées par des virgules
        
    Returns:
        Liste étendue avec synonymes
    """
    try:
        skills_list = [s.strip() for s in skills.split(",")]
        expanded = matcher.expand_skills(skills_list)
        return {"original": skills_list, "expanded": expanded}
    except Exception as e:
        logger.error(f"Erreur lors de l'expansion des compétences: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'expansion des compétences: {str(e)}")

@app.get("/api/travel/calculate")
async def calculate_travel(origin: str, destination: str, mode: str = "driving"):
    """
    Calcule le temps de trajet entre deux emplacements
    
    Args:
        origin: Emplacement d'origine (adresse ou coordonnées)
        destination: Emplacement de destination (adresse ou coordonnées)
        mode: Mode de transport (driving, transit, walking, bicycling)
        
    Returns:
        Temps de trajet en minutes
    """
    try:
        travel_time = matcher.commute_extension.maps_client.get_travel_time(
            origin, destination, mode=mode
        )
        return {"origin": origin, "destination": destination, "mode": mode, "time_minutes": travel_time}
    except Exception as e:
        logger.error(f"Erreur lors du calcul du temps de trajet: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur lors du calcul du temps de trajet: {str(e)}")
EOAPI

# 7. Mise à jour de test_smartmatch.py
echo "Mise à jour de test_smartmatch.py..."
cat > test_smartmatch.py << 'EOTEST'
#!/usr/bin/env python3
"""
Script de test pour Nexten SmartMatch
-------------------------------------
Teste le système SmartMatch avec des données simulées et affiche les résultats.

Auteur: Claude/Anthropic
Date: 16/05/2025
"""

import os
import sys
import json
import time
import logging
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Any

# Ajouter le répertoire parent au chemin de recherche pour l'importation
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importer les modules du projet
try:
    from app.smartmatch import SmartMatcher
    from app.smartmatch_transport import enhance_smartmatch_with_transport
    from app.api_keys import get_maps_api_key
except ImportError:
    print("Erreur: Impossible d'importer les modules. Vérifiez que vous exécutez le script depuis le bon répertoire.")
    sys.exit(1)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_comprehensive_test(api_key=None):
    """
    Exécute un test complet du système SmartMatch et analyse les résultats
    
    Args:
        api_key (str): Clé API Google Maps pour les calculs de distance
        
    Returns:
        pd.DataFrame: DataFrame pandas contenant les résultats du matching
    """
    logger.info("Démarrage du test complet SmartMatch")
    
    # Initialiser le SmartMatcher
    matcher = SmartMatcher(api_key=api_key)
    
    # Améliorer avec l'extension de transport
    matcher = enhance_smartmatch_with_transport(matcher, api_key=api_key)
    
    logger.info("SmartMatcher initialisé et amélioré avec l'extension transport")
    
    # Charger les données de test
    test_data = matcher.load_test_data()
    candidates = test_data["candidates"]
    jobs = test_data["jobs"]
    logger.info(f"Données de test chargées: {len(candidates)} candidats, {len(jobs)} emplois")
    
    # Exécuter le matching par lots
    start_time = time.time()
    results = matcher.batch_match(candidates, jobs)
    duration = time.time() - start_time
    logger.info(f"Matching terminé en {duration:.2f} secondes")
    
    # Convertir les résultats en DataFrame pandas
    df_results = pd.DataFrame(results)
    
    # Extraire les scores par catégorie
    category_scores = pd.DataFrame([
        {
            'candidate_id': row['candidate_id'],
            'job_id': row['job_id'],
            'overall': row['overall_score'],
            'skills': row['category_scores']['skills'],
            'location': row['category_scores']['location'],
            'experience': row['category_scores']['experience'],
            'education': row['category_scores']['education'],
            'preferences': row['category_scores']['preferences']
        }
        for _, row in df_results.iterrows()
    ])
    
    # Afficher les statistiques
    print("\n=== STATISTIQUES DU MATCHING ===")
    print(f"Nombre total de matchings: {len(df_results)}")
    print(f"Score moyen global: {df_results['overall_score'].mean():.2f}")
    print(f"Score médian global: {df_results['overall_score'].median():.2f}")
    print(f"Score maximum: {df_results['overall_score'].max():.2f}")
    print(f"Score minimum: {df_results['overall_score'].min():.2f}")
    
    # Afficher les scores moyens par catégorie
    print("\n=== SCORES MOYENS PAR CATÉGORIE ===")
    for category in ['skills', 'location', 'experience', 'education', 'preferences']:
        print(f"Score moyen {category}: {category_scores[category].mean():.2f}")
    
    # Afficher les meilleurs matchs
    print("\n=== TOP 3 DES MEILLEURS MATCHS ===")
    top_matches = df_results.sort_values('overall_score', ascending=False).head(3)
    for _, match in top_matches.iterrows():
        candidate_id = match['candidate_id']
        job_id = match['job_id']
        score = match['overall_score']
        
        # Trouver les noms correspondants
        candidate_name = next((c['name'] for c in candidates if c['id'] == candidate_id), candidate_id)
        job_title = next((j['title'] for j in jobs if j['id'] == job_id), job_id)
        
        print(f"Match: {candidate_name} - {job_title} (Score: {score:.2f})")
        
        # Afficher les insights
        if match['insights']:
            print("  Insights:")
            for insight in match['insights']:
                if 'category' in insight:
                    category = insight['category']
                    if category == 'strength':
                        print(f"  ✓ {insight['message']} ({insight['score']:.2f})")
                    elif category == 'weakness':
                        print(f"  ✗ {insight['message']} ({insight['score']:.2f})")
                    else:
                        print(f"  ! {insight['message']} ({insight.get('score', 0):.2f})")
                else:
                    print(f"  • {insight['message']}")
    
    return category_scores

def create_radar_chart(data: pd.DataFrame, candidate_id: str, job_id: str):
    """
    Crée un graphique radar pour visualiser les scores par catégorie d'un match
    
    Args:
        data (pd.DataFrame): DataFrame contenant les scores par catégorie
        candidate_id (str): ID du candidat
        job_id (str): ID de l'offre d'emploi
    """
    # Filtrer les données pour le match spécifié
    match_data = data[(data['candidate_id'] == candidate_id) & (data['job_id'] == job_id)]
    
    if match_data.empty:
        logger.warning(f"Aucune donnée trouvée pour le match {candidate_id}-{job_id}")
        return
    
    # Extraire les scores
    match_scores = match_data.iloc[0]
    categories = ['skills', 'location', 'experience', 'education', 'preferences']
    scores = [match_scores[cat] for cat in categories]
    
    # Créer le graphique radar
    angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
    angles += angles[:1]  # Boucler le graphique
    scores += scores[:1]  # Boucler les scores
    
    # Configurer la figure
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    
    # Dessiner le graphique
    ax.plot(angles, scores, linewidth=2, linestyle='solid', label=f"Match {candidate_id}-{job_id}")
    ax.fill(angles, scores, alpha=0.25)
    
    # Configurer les axes
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
    ax.set_ylim(0, 1)
    
    # Ajouter un titre
    plt.title(f"Profil du match {candidate_id}-{job_id} (Score global: {match_scores['overall']:.2f})", size=15)
    
    # Sauvegarder le graphique
    plt.tight_layout()
    filename = f"match_radar_{candidate_id}_{job_id}.png"
    plt.savefig(filename)
    logger.info(f"Graphique radar sauvegardé sous {filename}")
    plt.close()

def create_comparison_chart(data: pd.DataFrame):
    """
    Crée un graphique de comparaison des scores moyens par catégorie pour tous les matchs
    
    Args:
        data (pd.DataFrame): DataFrame contenant les scores par catégorie
    """
    # Calculer les scores moyens par catégorie
    categories = ['skills', 'location', 'experience', 'education', 'preferences']
    avg_scores = [data[cat].mean() for cat in categories]
    
    # Créer le graphique à barres
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(categories, avg_scores, color='skyblue')
    
    # Ajouter les valeurs au-dessus des barres
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                f'{height:.2f}', ha='center', va='bottom')
    
    # Configurer les axes
    ax.set_ylim(0, 1)
    ax.set_ylabel('Score moyen')
    ax.set_title('Scores moyens par catégorie pour tous les matchs')
    
    # Sauvegarder le graphique
    plt.tight_layout()
    filename = "category_comparison.png"
    plt.savefig(filename)
    logger.info(f"Graphique de comparaison sauvegardé sous {filename}")
    plt.close()

def create_heatmap(data: pd.DataFrame):
    """
    Crée une heatmap des scores globaux pour tous les candidats et offres d'emploi
    
    Args:
        data (pd.DataFrame): DataFrame contenant les scores par catégorie
    """
    # Pivoter les données pour créer la matrice de heatmap
    pivot_data = data.pivot_table(
        values='overall', 
        index='candidate_id', 
        columns='job_id'
    )
    
    # Créer la heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(pivot_data, cmap='YlGnBu', vmin=0, vmax=1)
    
    # Ajouter la barre de couleur
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel('Score', rotation=-90, va="bottom")
    
    # Configurer les ticks
    ax.set_xticks(range(len(pivot_data.columns)))
    ax.set_yticks(range(len(pivot_data.index)))
    ax.set_xticklabels(pivot_data.columns)
    ax.set_yticklabels(pivot_data.index)
    
    # Étiqueter les axes
    plt.ylabel('Candidat ID')
    plt.xlabel('Offre ID')
    plt.title('Heatmap des scores de matching')
    
    # Ajouter les valeurs dans les cellules
    for i in range(len(pivot_data.index)):
        for j in range(len(pivot_data.columns)):
            value = pivot_data.iloc[i, j]
            ax.text(j, i, f'{value:.2f}', ha="center", va="center", color="black" if value > 0.5 else "white")
    
    # Sauvegarder le graphique
    plt.tight_layout()
    filename = "matching_heatmap.png"
    plt.savefig(filename)
    logger.info(f"Heatmap sauvegardée sous {filename}")
    plt.close()

def main():
    """
    Fonction principale exécutant le test complet et générant les visualisations
    """
    # Récupérer la clé API Google Maps
    api_key = get_maps_api_key()
    
    # Exécuter le test complet
    try:
        results = run_comprehensive_test(api_key)
        
        # Sauvegarder les résultats
        results.to_csv('matching_results.csv', index=False)
        logger.info("Résultats sauvegardés dans matching_results.csv")
        
        # Générer des visualisations
        # 1. Graphique radar pour le meilleur match
        top_match = results.sort_values('overall', ascending=False).iloc[0]
        create_radar_chart(results, top_match['candidate_id'], top_match['job_id'])
        
        # 2. Graphique de comparaison des catégories
        create_comparison_chart(results)
        
        # 3. Heatmap des matchs
        create_heatmap(results)
        
        print("\nTest terminé avec succès. Consultez les fichiers CSV et PNG générés pour les résultats détaillés.")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du test: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
EOTEST

# 8. Créer le script shell de démarrage de l'API
echo "Création du script de démarrage de l'API..."
cat > start_smartmatch_api.sh << 'EOSTART'
#!/bin/bash

# Script de démarrage de l'API SmartMatch
echo "Démarrage de l'API SmartMatch..."

# Vérifier si une clé API Google Maps est définie
if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
    # Essayer de charger depuis .env
    if [ -f .env ]; then
        source .env
    fi
    
    # Si toujours pas définie, demander à l'utilisateur
    if [ -z "$GOOGLE_MAPS_API_KEY" ]; then
        echo "Aucune clé API Google Maps trouvée."
        read -p "Voulez-vous saisir une clé API Google Maps ? (o/n): " answer
        
        if [[ "$answer" == "o" || "$answer" == "O" || "$answer" == "oui" ]]; then
            read -p "Entrez votre clé API Google Maps: " api_key
            export GOOGLE_MAPS_API_KEY="$api_key"
            
            # Sauvegarder dans .env pour les prochaines utilisations
            echo "GOOGLE_MAPS_API_KEY=\"$api_key\"" >> .env
            echo "Clé API Google Maps sauvegardée dans .env"
        else
            echo "Aucune clé API Google Maps fournie. Certaines fonctionnalités seront limitées."
        fi
    fi
fi

# Démarrer l'API avec Uvicorn
echo "Lancement de l'API sur http://localhost:5052"
python -m uvicorn app.api.smartmatch_api:app --host 0.0.0.0 --port 5052 --reload
EOSTART

# Rendre les scripts exécutables
chmod +x start_smartmatch_api.sh
chmod +x test_smartmatch.py

echo "Implémentation terminée avec succès !"
echo "Pour tester SmartMatch, exécutez : ./test_smartmatch.py"
echo "Pour démarrer l'API SmartMatch, exécutez : ./start_smartmatch_api.sh"