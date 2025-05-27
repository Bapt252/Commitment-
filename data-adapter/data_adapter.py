#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Data Adapter optimisé pour ImprovedMatchingEngine
================================================
Ce module adapte les données du parsing CV/Job vers le format exact attendu 
par votre moteur de matching ImprovedMatchingEngine.

Auteur: Claude
Date: 26/05/2025
Version: 1.0.0
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CommitmentDataAdapter:
    """
    Adaptateur de données pour le système Commitment-
    
    Convertit les données des parsers CV/Job vers le format exact attendu
    par ImprovedMatchingEngine
    """
    
    def __init__(self):
        """Initialisation de l'adaptateur"""
        
        # Mapping des compétences synonymes pour normalisation
        self.skills_normalization = {
            'javascript': ['js', 'ecmascript', 'node.js', 'nodejs', 'reactjs', 'vue.js', 'angularjs'],
            'python': ['py', 'django', 'flask', 'fastapi'],
            'sql': ['mysql', 'postgresql', 'postgres', 'sqlite', 'oracle'],
            'nosql': ['mongodb', 'cassandra', 'couchdb', 'redis'],
            'docker': ['containerization', 'kubernetes', 'k8s'],
            'aws': ['amazon web services', 'ec2', 's3', 'lambda'],
            'git': ['github', 'gitlab', 'version control'],
            'api': ['rest', 'restful', 'graphql', 'soap'],
            'machine learning': ['ml', 'ai', 'artificial intelligence', 'deep learning'],
            'react': ['reactjs', 'react.js'],
            'vue': ['vuejs', 'vue.js'],
            'angular': ['angularjs', 'angular.js']
        }
        
        # Mapping des types de contrats
        self.contract_mapping = {
            'cdi': ['cdi', 'permanent', 'full-time', 'temps plein'],
            'cdd': ['cdd', 'temporary', 'contract', 'temporaire'],
            'stage': ['stage', 'internship', 'intern'],
            'alternance': ['alternance', 'apprenticeship', 'apprentice'],
            'freelance': ['freelance', 'indépendant', 'consultant'],
            'interim': ['interim', 'intérim', 'temporary work']
        }
        
        logger.info("CommitmentDataAdapter initialisé avec succès")
    
    def normalize_skills(self, skills: List[str]) -> List[str]:
        """
        Normalise et déduplique les compétences
        
        Args:
            skills (List[str]): Liste des compétences brutes
            
        Returns:
            List[str]: Liste des compétences normalisées
        """
        if not skills:
            return []
        
        normalized = set()
        skills_lower = [skill.lower().strip() for skill in skills if skill]
        
        for skill in skills_lower:
            # Trouver le nom canonique
            canonical_name = skill
            for canonical, variants in self.skills_normalization.items():
                if skill == canonical or skill in variants:
                    canonical_name = canonical
                    break
            normalized.add(canonical_name)
        
        return list(normalized)
    
    def extract_experience_years(self, experience_text: str) -> int:
        """
        Extrait le nombre d'années d'expérience depuis un texte
        
        Args:
            experience_text (str): Texte décrivant l'expérience
            
        Returns:
            int: Nombre d'années d'expérience
        """
        if not experience_text:
            return 0
        
        text_lower = experience_text.lower()
        
        # Patterns pour extraire les années
        patterns = [
            r'(\d+)\s*(?:ans?|années?|years?)',
            r'(\d+)\s*(?:an|année|year)',
            r'(\d+)[+]\s*(?:ans?|années?|years?)',
            r'(\d+)\s*(?:à|-)?\s*\d*\s*(?:ans?|années?|years?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                return int(match.group(1))
        
        # Mots-clés descriptifs
        if any(word in text_lower for word in ['débutant', 'junior', 'entry']):
            return 1
        elif any(word in text_lower for word in ['confirmé', 'intermédiaire', 'mid']):
            return 3
        elif any(word in text_lower for word in ['senior', 'expérimenté', 'expert']):
            return 5
        
        return 0
    
    def normalize_contract_type(self, contract_text: str) -> str:
        """
        Normalise le type de contrat
        
        Args:
            contract_text (str): Texte décrivant le type de contrat
            
        Returns:
            str: Type de contrat normalisé
        """
        if not contract_text:
            return 'cdi'
        
        text_lower = contract_text.lower().strip()
        
        for canonical, variants in self.contract_mapping.items():
            if text_lower in variants:
                return canonical
        
        return 'cdi'  # Par défaut
    
    def parse_salary_range(self, salary_text: str) -> Dict[str, Any]:
        """
        Parse une fourchette de salaire depuis un texte
        
        Args:
            salary_text (str): Texte décrivant le salaire
            
        Returns:
            Dict: {'min': int, 'max': int, 'currency': str}
        """
        if not salary_text:
            return {'min': 0, 'max': 0, 'currency': 'EUR'}
        
        # Nettoyer le texte
        text = salary_text.replace(' ', '').replace(',', '.')
        
        # Patterns pour extraire les salaires
        # Pattern pour fourchette (ex: "40k-50k", "40000-50000")
        range_pattern = r'(\d+(?:\.\d+)?)[kK€$]?\s*(?:[-–à])\s*(\d+(?:\.\d+)?)[kK€$]?'
        range_match = re.search(range_pattern, text)
        
        if range_match:
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            
            # Conversion en milliers si 'k' ou 'K'
            if 'k' in salary_text.lower():
                min_val *= 1000
                max_val *= 1000
            
            return {
                'min': int(min_val),
                'max': int(max_val),
                'currency': 'EUR'
            }
        
        # Pattern pour valeur unique
        single_pattern = r'(\d+(?:\.\d+)?)[kK€$]?'
        single_match = re.search(single_pattern, text)
        
        if single_match:
            value = float(single_match.group(1))
            
            if 'k' in salary_text.lower():
                value *= 1000
            
            # Créer une fourchette ±10%
            return {
                'min': int(value * 0.9),
                'max': int(value * 1.1),
                'currency': 'EUR'
            }
        
        return {'min': 0, 'max': 0, 'currency': 'EUR'}
    
    def parse_date(self, date_text: str) -> str:
        """
        Parse une date depuis différents formats vers DD/MM/YYYY
        
        Args:
            date_text (str): Date au format texte
            
        Returns:
            str: Date au format DD/MM/YYYY
        """
        if not date_text:
            return ""
        
        # Essayer différents formats
        formats = [
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d-%m-%Y',
            '%d.%m.%Y'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_text.strip(), fmt)
                return dt.strftime('%d/%m/%Y')
            except ValueError:
                continue
        
        return date_text  # Retourner tel quel si parsing échoue
    
    def adapt_cv_data(self, parsed_cv: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapte les données du CV Parser vers le format ImprovedMatchingEngine
        
        Args:
            parsed_cv (Dict): Données du CV Parser
            
        Returns:
            Dict: Données au format attendu par ImprovedMatchingEngine
        """
        # Normaliser les compétences
        competences_brutes = parsed_cv.get('competences', [])
        if isinstance(competences_brutes, str):
            competences_brutes = [comp.strip() for comp in competences_brutes.split(',')]
        
        logiciels = parsed_cv.get('logiciels', [])
        if isinstance(logiciels, str):
            logiciels = [log.strip() for log in logiciels.split(',')]
        
        # Combiner et normaliser toutes les compétences
        all_skills = competences_brutes + logiciels
        normalized_skills = self.normalize_skills(all_skills)
        
        # Extraire les années d'expérience
        experience_text = parsed_cv.get('experience', '') or parsed_cv.get('poste', '')
        years_exp = self.extract_experience_years(experience_text)
        
        # Adapter au format exact attendu par ImprovedMatchingEngine
        adapted_cv = {
            'nom': parsed_cv.get('nom', ''),
            'prenom': parsed_cv.get('prenom', ''),
            'email': parsed_cv.get('email', ''),
            'telephone': parsed_cv.get('telephone', ''),
            'adresse': parsed_cv.get('adresse', ''),
            'poste': parsed_cv.get('poste', ''),
            'competences': normalized_skills,
            'annees_experience': years_exp,
            'formation': parsed_cv.get('formation', ''),
            'langues': parsed_cv.get('langues', []),
            'soft_skills': parsed_cv.get('soft_skills', [])
        }
        
        logger.info(f"CV adapté pour {adapted_cv.get('prenom', '')} {adapted_cv.get('nom', '')}")
        return adapted_cv
    
    def adapt_questionnaire_data(self, parsed_questionnaire: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapte les données du questionnaire vers le format ImprovedMatchingEngine
        
        Args:
            parsed_questionnaire (Dict): Données du questionnaire
            
        Returns:
            Dict: Données au format attendu par ImprovedMatchingEngine
        """
        # Adapter la fourchette de salaire
        salary_range = self.parse_salary_range(parsed_questionnaire.get('fourchette_salaire', ''))
        
        # Adapter les types de contrats recherchés
        contrats_raw = parsed_questionnaire.get('types_contrat', [])
        if isinstance(contrats_raw, str):
            contrats_raw = [c.strip() for c in contrats_raw.split(',')]
        
        contrats_normalises = [self.normalize_contract_type(c) for c in contrats_raw]
        
        # Adapter la date de disponibilité
        date_dispo = self.parse_date(parsed_questionnaire.get('disponibilite', ''))
        
        adapted_questionnaire = {
            'adresse': parsed_questionnaire.get('adresse', ''),
            'temps_trajet_max': parsed_questionnaire.get('temps_trajet_max', 60),
            'contrats_recherches': contrats_normalises,
            'salaire_min': salary_range.get('min', 0),
            'date_disponibilite': date_dispo,
            'domaines_interets': parsed_questionnaire.get('secteurs_interesse', []),
            'preference_teletravail': parsed_questionnaire.get('teletravail', False),
            'mobilite_geo': parsed_questionnaire.get('mobilite', True)
        }
        
        logger.info("Questionnaire adapté avec succès")
        return adapted_questionnaire
    
    def adapt_job_data(self, parsed_job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapte les données du Job Parser vers le format ImprovedMatchingEngine
        
        Args:
            parsed_job (Dict): Données du Job Parser
            
        Returns:
            Dict: Données au format attendu par ImprovedMatchingEngine
        """
        # Normaliser les compétences requises
        competences_raw = parsed_job.get('competences', [])
        if isinstance(competences_raw, str):
            competences_raw = [comp.strip() for comp in competences_raw.split(',')]
        
        normalized_skills = self.normalize_skills(competences_raw)
        
        # Parse le salaire
        salary_range = self.parse_salary_range(parsed_job.get('salaire', ''))
        salary_formatted = f"{salary_range['min']}-{salary_range['max']}" if salary_range['min'] > 0 else ""
        
        # Normaliser le type de contrat
        contract_type = self.normalize_contract_type(parsed_job.get('type_contrat', ''))
        
        # Adapter la date de début
        date_debut = self.parse_date(parsed_job.get('date_debut', ''))
        
        adapted_job = {
            'id': parsed_job.get('id', f"job_{int(datetime.now().timestamp())}"),
            'titre': parsed_job.get('titre', ''),
            'entreprise': parsed_job.get('entreprise', ''),
            'localisation': parsed_job.get('localisation', ''),
            'description': parsed_job.get('description', ''),
            'competences': normalized_skills,
            'experience': parsed_job.get('experience', ''),
            'formation': parsed_job.get('formation', ''),
            'type_contrat': contract_type,
            'salaire': salary_formatted,
            'date_debut': date_debut,
            'avantages': parsed_job.get('avantages', []),
            'secteur': parsed_job.get('secteur', '')
        }
        
        logger.info(f"Offre d'emploi adaptée: {adapted_job.get('titre', '')}")
        return adapted_job
    
    def prepare_matching_data(self, cv_data: Dict[str, Any], 
                            questionnaire_data: Dict[str, Any], 
                            jobs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Prépare toutes les données pour le matching avec ImprovedMatchingEngine
        
        Args:
            cv_data (Dict): Données CV parsées
            questionnaire_data (Dict): Données questionnaire parsées
            jobs_data (List[Dict]): Liste des offres d'emploi parsées
            
        Returns:
            Dict: Données formatées pour ImprovedMatchingEngine
        """
        try:
            # Adapter chaque type de données
            adapted_cv = self.adapt_cv_data(cv_data)
            adapted_questionnaire = self.adapt_questionnaire_data(questionnaire_data)
            adapted_jobs = [self.adapt_job_data(job) for job in jobs_data]
            
            result = {
                'cv_data': adapted_cv,
                'questionnaire_data': adapted_questionnaire,
                'job_data': adapted_jobs,
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'cv_id': adapted_cv.get('email', ''),
                    'num_jobs': len(adapted_jobs)
                }
            }
            
            logger.info(f"Données préparées pour matching: {len(adapted_jobs)} offres")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de la préparation des données: {str(e)}")
            raise
    
    def run_matching(self, cv_data: Dict[str, Any], 
                    questionnaire_data: Dict[str, Any], 
                    jobs_data: List[Dict[str, Any]],
                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        Lance le matching complet avec votre ImprovedMatchingEngine
        
        Args:
            cv_data (Dict): Données CV parsées
            questionnaire_data (Dict): Données questionnaire parsées  
            jobs_data (List[Dict]): Liste des offres d'emploi parsées
            limit (int): Nombre max de résultats
            
        Returns:
            List[Dict]: Résultats du matching triés par score
        """
        try:
            # Importer votre moteur de matching
            from my_matching_engine import match_candidate_with_jobs
            
            # Préparer les données
            prepared_data = self.prepare_matching_data(cv_data, questionnaire_data, jobs_data)
            
            # Lancer le matching
            results = match_candidate_with_jobs(
                cv_data=prepared_data['cv_data'],
                questionnaire_data=prepared_data['questionnaire_data'],
                job_data=prepared_data['job_data'],
                limit=limit
            )
            
            logger.info(f"Matching terminé: {len(results)} résultats")
            return results
            
        except ImportError as e:
            logger.error(f"Impossible d'importer my_matching_engine: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du matching: {str(e)}")
            raise
    
    def validate_input_data(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        Valide et nettoie les données d'entrée
        
        Args:
            data (Dict): Données à valider
            data_type (str): Type de données ('cv', 'questionnaire', 'job')
            
        Returns:
            Dict: Données validées et nettoyées
        """
        if not isinstance(data, dict):
            raise ValueError(f"Les données {data_type} doivent être un dictionnaire")
        
        # Validation spécifique par type
        if data_type == 'cv':
            required_fields = ['competences']
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Champ manquant dans CV: {field}")
        
        elif data_type == 'questionnaire':
            # Valider les champs du questionnaire
            if 'temps_trajet_max' in data:
                try:
                    data['temps_trajet_max'] = int(data['temps_trajet_max'])
                except (ValueError, TypeError):
                    data['temps_trajet_max'] = 60
        
        elif data_type == 'job':
            required_fields = ['titre', 'competences']
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Champ manquant dans offre d'emploi: {field}")
        
        return data
    
    def get_matching_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcule des statistiques sur les résultats de matching
        
        Args:
            results (List[Dict]): Résultats du matching
            
        Returns:
            Dict: Statistiques détaillées
        """
        if not results:
            return {'total': 0, 'moyenne_score': 0}
        
        scores = [r.get('matching_score', 0) for r in results]
        
        stats = {
            'total': len(results),
            'moyenne_score': sum(scores) / len(scores),
            'score_max': max(scores),
            'score_min': min(scores),
            'scores_par_tranche': {
                'excellent': len([s for s in scores if s >= 80]),
                'bon': len([s for s in scores if 60 <= s < 80]),
                'moyen': len([s for s in scores if 40 <= s < 60]),
                'faible': len([s for s in scores if s < 40])
            }
        }
        
        return stats


# Utilitaires pour FastAPI
def create_matching_response(results: List[Dict[str, Any]], 
                           stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Crée une réponse formatée pour l'API
    
    Args:
        results (List[Dict]): Résultats du matching
        stats (Dict): Statistiques
        
    Returns:
        Dict: Réponse API formatée
    """
    return {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'statistics': stats,
        'results': results,
        'count': len(results)
    }


def create_error_response(error_message: str, 
                         error_code: str = 'PROCESSING_ERROR') -> Dict[str, Any]:
    """
    Crée une réponse d'erreur formatée pour l'API
    
    Args:
        error_message (str): Message d'erreur
        error_code (str): Code d'erreur
        
    Returns:
        Dict: Réponse d'erreur formatée
    """
    return {
        'success': False,
        'timestamp': datetime.now().isoformat(),
        'error': {
            'code': error_code,
            'message': error_message
        }
    }


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test basique
    adapter = CommitmentDataAdapter()
    
    # Exemple de données CV
    cv_example = {
        'nom': 'Dupont',
        'prenom': 'Jean',
        'email': 'jean.dupont@email.com',
        'competences': ['Python', 'Django', 'React', 'SQL'],
        'experience': '5 ans d\'expérience'
    }
    
    # Exemple de questionnaire
    questionnaire_example = {
        'fourchette_salaire': '45k-55k',
        'types_contrat': ['CDI'],
        'temps_trajet_max': 45
    }
    
    # Exemple d'offre d'emploi
    job_example = {
        'titre': 'Développeur Python Senior',
        'entreprise': 'Acme Corp',
        'competences': ['Python', 'Django', 'PostgreSQL'],
        'salaire': '50k'
    }
    
    # Test d'adaptation
    adapted_cv = adapter.adapt_cv_data(cv_example)
    adapted_questionnaire = adapter.adapt_questionnaire_data(questionnaire_example)
    adapted_job = adapter.adapt_job_data(job_example)
    
    print("CV adapté:", json.dumps(adapted_cv, indent=2, ensure_ascii=False))
    print("Questionnaire adapté:", json.dumps(adapted_questionnaire, indent=2, ensure_ascii=False))
    print("Offre adaptée:", json.dumps(adapted_job, indent=2, ensure_ascii=False))
