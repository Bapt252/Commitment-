"""
SmartMatch Questionnaire Connector - Module d'intégration des questionnaires
-------------------------------------------------------------------
Ce module assure la connexion entre les questionnaires HTML et l'algorithme SmartMatch.
Il permet de transformer les réponses des questionnaires en structure de données
compatible avec l'algorithme de matching.

Version: 1.0.0
Date: 16/05/2025
"""

import logging
import json
import re
import os
from typing import Dict, Any, List, Union, Optional
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuestionnaireConnector:
    """
    Connecteur entre les questionnaires HTML et SmartMatch
    
    Cette classe permet de:
    1. Récupérer et parser les réponses des questionnaires
    2. Transformer les données au format attendu par SmartMatch
    3. Créer une interface entre les formulaires HTML et l'algorithme
    """
    
    def __init__(self, smartmatch_adapter=None):
        """
        Initialisation du connecteur
        
        Args:
            smartmatch_adapter: Instance de SmartMatchDataAdapter à utiliser (optionnel)
        """
        self.smartmatch_adapter = smartmatch_adapter
        
        # Mapping des valeurs spécifiques
        self.transport_method_mapping = {
            'public-transport': 'transports en commun',
            'vehicle': 'véhicule personnel', 
            'bike': 'vélo',
            'walking': 'marche à pied'
        }
        
        self.structure_type_mapping = {
            'startup': 'startup',
            'pme': 'PME',
            'midsize': 'ETI',
            'corporate': 'Grand Groupe',
            'no-preference': 'Pas de préférence'
        }
        
        # Initialisation des mappings pour normaliser les réponses aux questionnaires
        self._init_mappings()
        
        logger.info("QuestionnaireConnector initialisé avec succès")
    
    def _init_mappings(self):
        """
        Initialise les mappings de normalisation des données des questionnaires
        """
        # Mapping des questions du questionnaire candidat vers les champs SmartMatch
        self.candidate_field_mapping = {
            'transport-method': 'mobility.transport_methods',
            'address': 'exact_address',
            'address-lat': 'location.lat',
            'address-lng': 'location.lng',
            'office-preference': 'work_environment_preference',
            'motivation-order': 'motivations',
            'other-motivation': 'other_motivation',
            'structure-type': 'preferred_structure_types',
            'has-sector-preference': 'has_sector_preference',
            'sector-preference': 'preferred_sectors',
            'has-prohibited-sector': 'has_prohibited_sectors',
            'prohibited-sector': 'prohibited_sectors',
            'salary-range': 'salary_expectation',
            'availability': 'availability_days',
            'currently-employed': 'currently_employed',
            'listening-reason': 'change_reason',
            'contract-end-reason': 'end_reason',
            'notice-period': 'notice_period_days',
            'notice-negotiable': 'notice_negotiable',
            'recruitment-status': 'recruitment_status'
        }
        
        # Mapping pour les temps de trajet par méthode de transport
        self.commute_time_fields = {
            'commute-time-public-transport': 'public-transport',
            'commute-time-vehicle': 'vehicle',
            'commute-time-bike': 'bike',
            'commute-time-walking': 'walking'
        }
        
        # Mappings des valeurs spécifiques
        self.availability_days_mapping = {
            'immediate': 0,
            '1month': 30,
            '2months': 60,
            '3months': 90
        }
        
        self.notice_period_days_mapping = {
            'none': 0,
            'trial': 15,
            '1month': 30,
            '2months': 60,
            '3months': 90
        }
        
        # Mapping des questions du questionnaire client/entreprise vers les champs SmartMatch
        self.client_field_mapping = {
            'company-name': 'company',
            'company-address': 'exact_location',
            'company-website': 'company_website',
            'company-description': 'company_description',
            'company-size': 'company_size',
            'recruitment-delay': 'recruitment_delay_days',
            'can-handle-notice': 'can_handle_notice',
            'notice-duration': 'max_notice_period_days',
            'recruitment-context': 'recruitment_context',
            'experience-required': 'experience_years',
            'sector-knowledge': 'requires_sector_knowledge',
            'sector-list': 'required_sector',
            'work-environment': 'work_environment',
            'team-composition': 'team_composition',
            'evolution-perspectives': 'evolution_perspectives',
            'salary': 'salary_range',
            'benefits': 'benefits',
            'contract-type': 'contract_details'
        }
        
        # Mapping pour les délais de recrutement
        self.recruitment_delay_mapping = {
            'immediate': 0,
            '2weeks': 14,
            '1month': 30,
            '2months': 60,
            '3months': 90
        }
        
        # Mapping pour l'expérience requise
        self.experience_years_mapping = {
            'junior': 1,
            '2-3': 3,
            '5-10': 8,
            '10plus': 12
        }
    
    def parse_questionnaire_form_data(self, form_data: Dict[str, Any], questionnaire_type: str) -> Dict[str, Any]:
        """
        Parse les données brutes d'un formulaire de questionnaire
        
        Args:
            form_data (Dict): Données brutes du formulaire
            questionnaire_type (str): Type de questionnaire ('candidate' ou 'client')
            
        Returns:
            Dict: Données structurées du questionnaire
        """
        parsed_data = {}
        
        # Déterminer le mapping à utiliser selon le type de questionnaire
        if questionnaire_type == 'candidate':
            field_mapping = self.candidate_field_mapping
        elif questionnaire_type == 'client':
            field_mapping = self.client_field_mapping
        else:
            logger.error(f"Type de questionnaire non reconnu: {questionnaire_type}")
            return {}
        
        # Traiter chaque champ du formulaire
        for field_name, field_value in form_data.items():
            # Normaliser les booléens
            if field_value == 'yes':
                field_value = True
            elif field_value == 'no':
                field_value = False
            
            # Traiter les champs spéciaux
            if questionnaire_type == 'candidate':
                # Traitement spécial pour les temps de trajet
                if field_name in self.commute_time_fields:
                    transport_method = self.commute_time_fields[field_name]
                    if 'mobility' not in parsed_data:
                        parsed_data['mobility'] = {'transport_methods': [], 'commute_times': {}}
                    
                    try:
                        parsed_data['mobility']['commute_times'][transport_method] = int(field_value)
                    except (ValueError, TypeError):
                        logger.warning(f"Temps de trajet invalide pour {field_name}: {field_value}")
                    
                    continue
                
                # Traitement pour la méthode de transport
                elif field_name == 'transport-method':
                    if isinstance(field_value, str):
                        field_value = [field_value]
                    
                    if 'mobility' not in parsed_data:
                        parsed_data['mobility'] = {'transport_methods': [], 'commute_times': {}}
                    
                    parsed_data['mobility']['transport_methods'] = field_value
                    continue
                
                # Traitement pour l'adresse et les coordonnées
                elif field_name == 'address':
                    parsed_data['exact_address'] = field_value
                    continue
                elif field_name == 'address-lat' and field_name == 'address-lng':
                    if 'address-lat' in form_data and 'address-lng' in form_data:
                        try:
                            lat = float(form_data['address-lat'])
                            lng = float(form_data['address-lng'])
                            parsed_data['location'] = f"{lat},{lng}"
                        except (ValueError, TypeError):
                            logger.warning("Coordonnées invalides")
                    continue
                
                # Traitement pour les motivations
                elif field_name == 'motivation-order':
                    if isinstance(field_value, str):
                        field_value = field_value.split(',')
                    parsed_data['motivations'] = field_value
                    continue
                
                # Traitement pour le type de structure
                elif field_name == 'structure-type':
                    if isinstance(field_value, str):
                        field_value = [field_value]
                    parsed_data['preferred_structure_types'] = field_value
                    continue
                
                # Traitement pour les préférences sectorielles
                elif field_name == 'sector-preference':
                    if isinstance(field_value, str):
                        field_value = [field_value]
                    parsed_data['preferred_sectors'] = field_value
                    continue
                elif field_name == 'prohibited-sector':
                    if isinstance(field_value, str):
                        field_value = [field_value]
                    parsed_data['prohibited_sectors'] = field_value
                    continue
                
                # Traitement pour la disponibilité
                elif field_name == 'availability':
                    days = self.availability_days_mapping.get(field_value, 30)
                    parsed_data['availability_days'] = days
                    continue
                
                # Traitement pour le préavis
                elif field_name == 'notice-period':
                    days = self.notice_period_days_mapping.get(field_value, 30)
                    parsed_data['notice_period_days'] = days
                    continue
            
            elif questionnaire_type == 'client':
                # Traitement pour le délai de recrutement
                if field_name == 'recruitment-delay':
                    if isinstance(field_value, str):
                        field_value = [field_value]
                    
                    # Prendre le délai le plus court
                    min_delay = min(self.recruitment_delay_mapping.get(delay, 90) for delay in field_value)
                    parsed_data['recruitment_delay_days'] = min_delay
                    continue
                
                # Traitement pour la durée de préavis acceptable
                elif field_name == 'notice-duration':
                    days = self.recruitment_delay_mapping.get(field_value, 30)
                    parsed_data['max_notice_period_days'] = days
                    continue
                
                # Traitement pour l'expérience requise
                elif field_name == 'experience-required':
                    years = self.experience_years_mapping.get(field_value, 3)
                    parsed_data['min_years_of_experience'] = years
                    parsed_data['max_years_of_experience'] = years + 3  # Estimation pour la fourchette
                    continue
                
                # Traitement pour les avantages
                elif field_name == 'benefits':
                    if field_value:
                        benefits_list = [b.strip() for b in field_value.split(',')]
                        parsed_data['benefits'] = benefits_list
                    continue
            
            # Appliquer le mapping standard pour les autres champs
            target_field = field_mapping.get(field_name)
            if target_field:
                # Gérer les champs avec des noms à niveaux multiples (ex: 'mobility.transport_methods')
                if '.' in target_field:
                    parts = target_field.split('.')
                    if len(parts) == 2:
                        parent, child = parts
                        if parent not in parsed_data:
                            parsed_data[parent] = {}
                        parsed_data[parent][child] = field_value
                else:
                    parsed_data[target_field] = field_value
        
        logger.info(f"Données du questionnaire {questionnaire_type} parsées avec succès")
        return parsed_data
    
    def parse_questionnaire_json(self, json_data: str, questionnaire_type: str) -> Dict[str, Any]:
        """
        Parse les données JSON d'un questionnaire
        
        Args:
            json_data (str): Données JSON du questionnaire
            questionnaire_type (str): Type de questionnaire ('candidate' ou 'client')
            
        Returns:
            Dict: Données structurées du questionnaire
        """
        try:
            data = json.loads(json_data)
            return self.parse_questionnaire_form_data(data, questionnaire_type)
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de décodage JSON: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Erreur lors du parsing du questionnaire: {str(e)}")
            return {}
    
    def extract_questionnaire_from_html(self, html_content: str, questionnaire_type: str) -> Dict[str, Any]:
        """
        Extrait les données d'un questionnaire à partir d'une page HTML complète
        
        Args:
            html_content (str): Contenu HTML du questionnaire
            questionnaire_type (str): Type de questionnaire ('candidate' ou 'client')
            
        Returns:
            Dict: Données structurées du questionnaire
        """
        form_data = {}
        
        # Extraire les champs à partir du HTML
        # Note: Dans une implémentation réelle, il serait préférable d'utiliser 
        # une bibliothèque comme BeautifulSoup pour parser le HTML correctement
        
        # Rechercher les éléments input
        input_pattern = r'<input[^>]*name=["\']([^"\']+)["\'][^>]*value=["\']([^"\']*)["\'][^>]*>'
        input_matches = re.finditer(input_pattern, html_content)
        
        for match in input_matches:
            field_name = match.group(1)
            field_value = match.group(2)
            
            # Vérifier si c'est un input radio/checkbox sélectionné
            input_element = match.group(0)
            if ('type="radio"' in input_element or 'type="checkbox"' in input_element) and 'checked' not in input_element:
                continue
            
            # Ajouter le champ aux données du formulaire
            form_data[field_name] = field_value
        
        # Rechercher les éléments select
        select_pattern = r'<select[^>]*name=["\']([^"\']+)["\'][^>]*>.*?</select>'
        select_matches = re.finditer(select_pattern, html_content, re.DOTALL)
        
        for match in select_matches:
            field_name = match.group(1)
            select_element = match.group(0)
            
            # Rechercher l'option sélectionnée
            option_pattern = r'<option[^>]*value=["\']([^"\']+)["\'][^>]*selected[^>]*>'
            option_match = re.search(option_pattern, select_element)
            
            if option_match:
                field_value = option_match.group(1)
                form_data[field_name] = field_value
        
        # Rechercher les éléments textarea
        textarea_pattern = r'<textarea[^>]*name=["\']([^"\']+)["\'][^>]*>(.*?)</textarea>'
        textarea_matches = re.finditer(textarea_pattern, html_content, re.DOTALL)
        
        for match in textarea_matches:
            field_name = match.group(1)
            field_value = match.group(2).strip()
            form_data[field_name] = field_value
        
        # Parser les données extraites
        return self.parse_questionnaire_form_data(form_data, questionnaire_type)
    
    def enrich_data_with_questionnaire(self, data: Dict[str, Any], questionnaire_data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        Enrichit les données avec les informations du questionnaire
        
        Args:
            data (Dict): Données originales (CV ou Job)
            questionnaire_data (Dict): Données du questionnaire
            data_type (str): Type de données ('candidate' ou 'client')
            
        Returns:
            Dict: Données enrichies
        """
        if not self.smartmatch_adapter:
            logger.warning("SmartMatchDataAdapter non disponible pour l'enrichissement")
            return data
        
        if data_type == 'candidate':
            return self.smartmatch_adapter.enrich_cv_data_with_questionnaire(data, questionnaire_data)
        elif data_type == 'client':
            return self.smartmatch_adapter.enrich_job_data_with_questionnaire(data, questionnaire_data)
        else:
            logger.error(f"Type de données non reconnu: {data_type}")
            return data
    
    def create_smartmatch_data(self, data: Dict[str, Any], questionnaire_data: Dict[str, Any], data_type: str, item_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Crée des données complètes au format SmartMatch en combinant les données originales et le questionnaire
        
        Args:
            data (Dict): Données originales (CV ou Job)
            questionnaire_data (Dict): Données du questionnaire
            data_type (str): Type de données ('candidate' ou 'client')
            item_id (str, optional): Identifiant de l'élément
            
        Returns:
            Dict: Données au format SmartMatch
        """
        if not self.smartmatch_adapter:
            logger.error("SmartMatchDataAdapter requis pour créer des données SmartMatch")
            return {}
        
        # Convertir d'abord les données originales au format SmartMatch
        if data_type == 'candidate':
            smartmatch_data = self.smartmatch_adapter.cv_to_smartmatch_format(data, item_id)
        elif data_type == 'client':
            smartmatch_data = self.smartmatch_adapter.job_to_smartmatch_format(data, item_id)
        else:
            logger.error(f"Type de données non reconnu: {data_type}")
            return {}
        
        # Enrichir avec les données du questionnaire
        return self.enrich_data_with_questionnaire(smartmatch_data, questionnaire_data, data_type)
    
    def process_html_forms(self, cv_html: str, job_html: str, cv_data: Dict[str, Any], job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite les formulaires HTML pour générer un résultat de matching complet
        
        Args:
            cv_html (str): Contenu HTML du questionnaire candidat
            job_html (str): Contenu HTML du questionnaire client
            cv_data (Dict): Données du CV
            job_data (Dict): Données de l'offre d'emploi
            
        Returns:
            Dict: Résultat du matching
        """
        if not self.smartmatch_adapter:
            logger.error("SmartMatchDataAdapter requis pour effectuer le matching")
            return {"error": "SmartMatchDataAdapter non disponible"}
        
        # Extraire les données des questionnaires
        cv_questionnaire = self.extract_questionnaire_from_html(cv_html, 'candidate')
        job_questionnaire = self.extract_questionnaire_from_html(job_html, 'client')
        
        # Générer les IDs
        cv_id = f"cv_{int(datetime.now().timestamp())}"
        job_id = f"job_{int(datetime.now().timestamp())}"
        
        # Créer les données SmartMatch
        cv_smartmatch = self.create_smartmatch_data(cv_data, cv_questionnaire, 'candidate', cv_id)
        job_smartmatch = self.create_smartmatch_data(job_data, job_questionnaire, 'client', job_id)
        
        # Effectuer le matching avancé
        if hasattr(self.smartmatch_adapter, 'enhanced_match'):
            result = self.smartmatch_adapter.enhanced_match(cv_smartmatch, job_smartmatch)
        else:
            logger.warning("La méthode enhanced_match n'est pas disponible, utilisation d'un résultat de base")
            result = {
                "candidate_id": cv_id,
                "job_id": job_id,
                "overall_score": 0.5,
                "category_scores": {},
                "insights": []
            }
        
        return result


class SmartMatchIntegration:
    """
    Système d'intégration de SmartMatch avec les questionnaires
    
    Cette classe assure l'intégration complète de SmartMatch dans l'application,
    en prenant en charge la gestion des questionnaires, la conversion des données
    et la génération des résultats de matching.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialisation du système d'intégration
        
        Args:
            api_key (str, optional): Clé API pour les services externes (ex: Google Maps)
        """
        # Importer et initialiser SmartMatchDataAdapter
        from smartmatch_data_adapter import SmartMatchDataAdapter
        self.data_adapter = SmartMatchDataAdapter(use_location_lookup=True)
        
        # Initialiser le connecteur de questionnaires
        self.questionnaire_connector = QuestionnaireConnector(self.data_adapter)
        
        # Importer SmartMatcher si disponible
        try:
            from smartmatch import SmartMatcher
            self.matcher = SmartMatcher(api_key=api_key)
        except ImportError:
            logger.warning("Module SmartMatcher non disponible")
            self.matcher = None
        
        logger.info("SmartMatchIntegration initialisé avec succès")
    
    def process_candidate_submission(self, cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une soumission de candidat (CV + questionnaire)
        
        Args:
            cv_data (Dict): Données du CV
            questionnaire_data (Dict): Données du questionnaire candidat
            
        Returns:
            Dict: Données candidat au format SmartMatch
        """
        # Générer un ID unique
        cv_id = f"cv_{int(datetime.now().timestamp())}"
        
        # Convertir les données CV au format SmartMatch
        cv_smartmatch = self.data_adapter.cv_to_smartmatch_format(cv_data, cv_id)
        
        # Enrichir avec les données du questionnaire
        if questionnaire_data:
            processed_questionnaire = self.questionnaire_connector.parse_questionnaire_form_data(
                questionnaire_data, 'candidate')
            cv_smartmatch = self.data_adapter.enrich_cv_data_with_questionnaire(
                cv_smartmatch, processed_questionnaire, cv_id)
        
        logger.info(f"Soumission candidat traitée avec succès, ID: {cv_id}")
        return cv_smartmatch
    
    def process_job_submission(self, job_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traite une soumission d'offre d'emploi (fiche de poste + questionnaire)
        
        Args:
            job_data (Dict): Données de l'offre d'emploi
            questionnaire_data (Dict): Données du questionnaire client
            
        Returns:
            Dict: Données offre d'emploi au format SmartMatch
        """
        # Générer un ID unique
        job_id = f"job_{int(datetime.now().timestamp())}"
        
        # Convertir les données d'offre au format SmartMatch
        job_smartmatch = self.data_adapter.job_to_smartmatch_format(job_data, job_id)
        
        # Enrichir avec les données du questionnaire
        if questionnaire_data:
            processed_questionnaire = self.questionnaire_connector.parse_questionnaire_form_data(
                questionnaire_data, 'client')
            job_smartmatch = self.data_adapter.enrich_job_data_with_questionnaire(
                job_smartmatch, processed_questionnaire, job_id)
        
        logger.info(f"Soumission offre d'emploi traitée avec succès, ID: {job_id}")
        return job_smartmatch
    
    def find_matches_for_candidate(self, candidate_data: Dict[str, Any], jobs: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recherche les meilleures offres d'emploi pour un candidat
        
        Args:
            candidate_data (Dict): Données du candidat au format SmartMatch
            jobs (List[Dict]): Liste des offres d'emploi au format SmartMatch
            limit (int): Nombre maximum de résultats à retourner
            
        Returns:
            List[Dict]: Résultats de matching triés par score
        """
        if not self.matcher:
            logger.error("SmartMatcher non disponible pour la recherche de matching")
            return []
        
        # Effectuer les matchings
        matches = []
        for job in jobs:
            try:
                # Utiliser enhanced_match si disponible
                if hasattr(self.data_adapter, 'enhanced_match'):
                    match_result = self.data_adapter.enhanced_match(candidate_data, job)
                else:
                    # Sinon, utiliser le matcher standard
                    match_result = self.matcher.calculate_match(candidate_data, job)
                
                matches.append(match_result)
            except Exception as e:
                logger.error(f"Erreur lors du matching: {str(e)}")
        
        # Trier par score global
        matches.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        
        # Limiter le nombre de résultats
        return matches[:limit]
    
    def find_matches_for_job(self, job_data: Dict[str, Any], candidates: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recherche les meilleurs candidats pour une offre d'emploi
        
        Args:
            job_data (Dict): Données de l'offre au format SmartMatch
            candidates (List[Dict]): Liste des candidats au format SmartMatch
            limit (int): Nombre maximum de résultats à retourner
            
        Returns:
            List[Dict]: Résultats de matching triés par score
        """
        if not self.matcher:
            logger.error("SmartMatcher non disponible pour la recherche de matching")
            return []
        
        # Effectuer les matchings
        matches = []
        for candidate in candidates:
            try:
                # Utiliser enhanced_match si disponible
                if hasattr(self.data_adapter, 'enhanced_match'):
                    match_result = self.data_adapter.enhanced_match(candidate, job_data)
                else:
                    # Sinon, utiliser le matcher standard
                    match_result = self.matcher.calculate_match(candidate, job_data)
                
                matches.append(match_result)
            except Exception as e:
                logger.error(f"Erreur lors du matching: {str(e)}")
        
        # Trier par score global
        matches.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        
        # Limiter le nombre de résultats
        return matches[:limit]
    
    def save_to_database(self, data: Dict[str, Any], data_type: str) -> str:
        """
        Sauvegarde les données dans la base de données
        
        Args:
            data (Dict): Données à sauvegarder
            data_type (str): Type de données ('candidate' ou 'job')
            
        Returns:
            str: ID de l'enregistrement
        """
        # Simuler une sauvegarde en base de données
        # Dans une implémentation réelle, cette méthode interagirait avec une base de données
        
        # Générer un ID si non présent
        if 'id' not in data:
            data['id'] = f"{data_type}_{int(datetime.now().timestamp())}"
        
        # Simuler la sauvegarde
        logger.info(f"Sauvegarde des données {data_type} avec ID: {data['id']}")
        
        # Dans une implémentation réelle :
        # - Connecter à la base de données
        # - Insérer ou mettre à jour les données
        # - Gérer les erreurs et les transactions
        
        return data['id']
    
    def load_from_database(self, item_id: str, data_type: str) -> Dict[str, Any]:
        """
        Charge des données depuis la base de données
        
        Args:
            item_id (str): ID de l'élément à charger
            data_type (str): Type de données ('candidate' ou 'job')
            
        Returns:
            Dict: Données chargées
        """
        # Simuler un chargement depuis la base de données
        # Dans une implémentation réelle, cette méthode interagirait avec une base de données
        
        logger.info(f"Chargement des données {data_type} avec ID: {item_id}")
        
        # Dans une implémentation réelle :
        # - Connecter à la base de données
        # - Requêter les données
        # - Gérer les erreurs
        
        # Retourner des données fictives pour la démonstration
        if data_type == 'candidate':
            return {
                "id": item_id,
                "name": "Exemple Candidat",
                "skills": ["Python", "JavaScript", "HTML/CSS"],
                "location": "48.8566,2.3522"
            }
        elif data_type == 'job':
            return {
                "id": item_id,
                "title": "Exemple Poste",
                "required_skills": ["Python", "Django"],
                "location": "48.8566,2.3522"
            }
        else:
            return {}


# Exemple d'utilisation dans un contexte Flask
def create_flask_routes(app, integration):
    """
    Crée les routes Flask pour l'API SmartMatch
    
    Args:
        app: Application Flask
        integration: Instance de SmartMatchIntegration
    """
    from flask import request, jsonify
    
    @app.route('/api/process-candidate', methods=['POST'])
    def process_candidate():
        """Traite une soumission de candidat (CV + questionnaire)"""
        try:
            data = request.json
            cv_data = data.get('cv', {})
            questionnaire_data = data.get('questionnaire', {})
            
            result = integration.process_candidate_submission(cv_data, questionnaire_data)
            
            # Sauvegarder en base de données
            candidate_id = integration.save_to_database(result, 'candidate')
            
            return jsonify({
                "status": "success",
                "message": "Candidat traité avec succès",
                "candidate_id": candidate_id,
                "data": result
            })
        
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Erreur lors du traitement: {str(e)}"
            }), 500
    
    @app.route('/api/process-job', methods=['POST'])
    def process_job():
        """Traite une soumission d'offre d'emploi (fiche de poste + questionnaire)"""
        try:
            data = request.json
            job_data = data.get('job', {})
            questionnaire_data = data.get('questionnaire', {})
            
            result = integration.process_job_submission(job_data, questionnaire_data)
            
            # Sauvegarder en base de données
            job_id = integration.save_to_database(result, 'job')
            
            return jsonify({
                "status": "success",
                "message": "Offre d'emploi traitée avec succès",
                "job_id": job_id,
                "data": result
            })
        
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Erreur lors du traitement: {str(e)}"
            }), 500
    
    @app.route('/api/match', methods=['POST'])
    def match():
        """Effectue un matching entre un candidat et une offre d'emploi"""
        try:
            data = request.json
            candidate_id = data.get('candidate_id')
            job_id = data.get('job_id')
            
            # Charger les données depuis la base de données
            candidate_data = integration.load_from_database(candidate_id, 'candidate')
            job_data = integration.load_from_database(job_id, 'job')
            
            # Utiliser enhanced_match si disponible
            if hasattr(integration.data_adapter, 'enhanced_match'):
                match_result = integration.data_adapter.enhanced_match(candidate_data, job_data)
            else:
                # Sinon, utiliser le matcher standard
                match_result = integration.matcher.calculate_match(candidate_data, job_data)
            
            return jsonify({
                "status": "success",
                "message": "Matching effectué avec succès",
                "match_result": match_result
            })
        
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Erreur lors du matching: {str(e)}"
            }), 500


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser le système d'intégration
    integration = SmartMatchIntegration(api_key="GOOGLE_MAPS_API_KEY")
    
    # Exemple de données pour un test
    cv_data = {
        "nom": "Dupont",
        "prenom": "Jean",
        "poste": "Développeur Python Senior",
        "competences": ["Python", "Django", "Flask", "REST API"],
        "logiciels": ["Git", "Docker", "VS Code", "PyCharm"],
        "email": "jean.dupont@example.com",
        "telephone": "06 12 34 56 78",
        "adresse": "123 rue de Paris, 75001 Paris"
    }
    
    questionnaire_candidat = {
        "transport-method": ["public-transport", "vehicle"],
        "commute-time-public-transport": "45",
        "commute-time-vehicle": "30",
        "address": "123 rue de Paris, 75001 Paris",
        "office-preference": "open-space",
        "motivation-order": "remuneration,evolution,flexibility",
        "structure-type": ["pme", "startup"],
        "has-sector-preference": "yes",
        "sector-preference": ["tech", "finance"],
        "salary-range": "45K - 55K",
        "availability": "1month",
        "currently-employed": "yes",
        "notice-period": "1month",
        "notice-negotiable": "yes"
    }
    
    # Traiter la soumission candidat
    candidate_smartmatch = integration.process_candidate_submission(cv_data, questionnaire_candidat)
    
    # Afficher le résultat
    print("Données candidat au format SmartMatch:")
    print(json.dumps(candidate_smartmatch, indent=2, ensure_ascii=False))
