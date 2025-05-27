#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

class AdvancedMatchingEngine:
    """
    Moteur de matching avancé avec calculs de trajets et pondération intelligente
    """
    
    def __init__(self):
        self.cv_data = {}
        self.questionnaire_data = {}
        self.job_data = {}
        self.preferences = {}
        
    def load_candidate_data(self, cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any]) -> None:
        """Charge les données du candidat dans le moteur"""
        self.cv_data = cv_data
        self.questionnaire_data = questionnaire_data
        self.preferences = self._extract_intelligent_preferences()
        logger.info(f"Données candidat chargées avec pondération intelligente")
    
    def load_job_data(self, job_data: List[Dict[str, Any]]) -> None:
        """Charge les données des offres d'emploi dans le moteur"""
        self.job_data = job_data
        logger.info(f"Données emploi chargées: {len(self.job_data)} offres")
    
    def _extract_intelligent_preferences(self) -> Dict[str, float]:
        """
        Extrait les préférences intelligentes basées sur le questionnaire
        Adapte les poids selon les réponses du candidat
        """
        # Poids par défaut
        weights = {
            'skills': 0.25,
            'contract': 0.15, 
            'location': 0.20,
            'travel_time': 0.15,  # NOUVEAU : temps de trajet
            'date': 0.05,
            'salary': 0.15,
            'experience': 0.05
        }
        
        # LOGIQUE INTELLIGENTE : Adaptation selon questionnaire
        
        # 1. Si candidat a quitté précédent poste pour salaire
        if self.questionnaire_data.get('raison_changement') in ['salaire', 'rémunération', 'argent']:
            weights['salary'] = 0.35  # Prioriser salaire
            weights['skills'] = 0.20
            weights['location'] = 0.15
            logger.info("🎯 Pondération SALAIRE privilégiée (raison de changement)")
        
        # 2. Si candidat privilégie équilibre vie pro/perso
        elif self.questionnaire_data.get('priorite') in ['equilibre', 'famille', 'personnel']:
            weights['travel_time'] = 0.25  # Prioriser temps de trajet
            weights['location'] = 0.25
            weights['skills'] = 0.20
            logger.info("🎯 Pondération LOCALISATION privilégiée (équilibre vie)")
        
        # 3. Si candidat cherche évolution de carrière
        elif self.questionnaire_data.get('objectif') in ['evolution', 'carriere', 'competences']:
            weights['skills'] = 0.35  # Prioriser compétences
            weights['experience'] = 0.15
            weights['salary'] = 0.10
            logger.info("🎯 Pondération COMPÉTENCES privilégiée (évolution)")
        
        # 4. Si candidat disponible immédiatement
        if self.questionnaire_data.get('disponibilite') == 'immediate':
            weights['date'] = 0.20  # Prioriser dates compatibles
            
        # 5. Si candidat a contraintes de transport
        mode_transport = self.questionnaire_data.get('mode_transport', '').lower()
        if mode_transport in ['transport', 'bus', 'metro', 'train']:
            weights['travel_time'] = 0.25  # Très important pour transports en commun
        elif mode_transport == 'pied':
            weights['travel_time'] = 0.30  # Critique pour marche
        
        return weights
    
    def calculate_matching_scores(self) -> List[Dict[str, Any]]:
        """Calcule les scores de matching avec logique avancée"""
        if not self.cv_data or not self.questionnaire_data or not self.job_data:
            logger.error("Données manquantes pour le calcul des scores")
            return []
        
        results = []
        
        for job in self.job_data:
            # Calcul des critères existants
            skills_score = self._calculate_skills_score(job)
            contract_score = self._calculate_contract_score(job)
            location_score = self._calculate_location_score(job)
            date_score = self._calculate_availability_score(job)
            salary_score = self._calculate_salary_score(job)
            experience_score = self._calculate_experience_score(job)
            
            # NOUVEAU : Calcul temps de trajet
            travel_time_score = self._calculate_travel_time_score(job)
            
            # Utiliser les poids intelligents
            weights = self.preferences
            
            # Score global pondéré
            total_score = (
                skills_score * weights.get('skills', 0.25) +
                contract_score * weights.get('contract', 0.15) +
                location_score * weights.get('location', 0.20) +
                travel_time_score * weights.get('travel_time', 0.15) +
                date_score * weights.get('date', 0.05) +
                salary_score * weights.get('salary', 0.15) +
                experience_score * weights.get('experience', 0.05)
            )
            
            # Formatage résultat enrichi
            job_result = job.copy()
            job_result['matching_score'] = round(total_score * 100)
            
            # Détails enrichis avec nouvelles métriques
            job_result['matching_details'] = {
                'skills': round(skills_score * 100),
                'contract': round(contract_score * 100), 
                'location': round(location_score * 100),
                'travel_time': round(travel_time_score * 100),  # NOUVEAU
                'date': round(date_score * 100),
                'salary': round(salary_score * 100),
                'experience': round(experience_score * 100)
            }
            
            # NOUVEAU : Explications détaillées
            job_result['matching_explanations'] = self._generate_explanations(job, job_result['matching_details'])
            
            # NOUVEAU : Informations de trajet
            job_result['travel_info'] = self._get_travel_info(job)
            
            results.append(job_result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _calculate_travel_time_score(self, job: Dict[str, Any]) -> float:
        """
        NOUVEAU : Calcule le score basé sur le temps de trajet réel
        selon le mode de transport préféré du candidat
        """
        candidate_address = self.questionnaire_data.get('adresse', '')
        job_address = job.get('localisation', '')
        transport_mode = self.questionnaire_data.get('mode_transport', 'voiture').lower()
        
        if not candidate_address or not job_address:
            return 0.5  # Score neutre
        
        # Vérifier si télétravail possible
        if 'remote' in job.get('politique_remote', '').lower() or \
           job.get('teletravail_possible', False):
            return 1.0  # Score parfait pour télétravail
        
        try:
            # Calcul du temps de trajet (simulation pour l'instant)
            travel_time_minutes = self._calculate_real_travel_time(
                candidate_address, job_address, transport_mode
            )
            
            # Barèmes selon mode de transport et préférences candidat
            max_acceptable = self.questionnaire_data.get('temps_trajet_max', 60)  # minutes
            
            if travel_time_minutes <= max_acceptable * 0.5:
                return 1.0  # Très proche
            elif travel_time_minutes <= max_acceptable * 0.75:
                return 0.8  # Acceptable
            elif travel_time_minutes <= max_acceptable:
                return 0.6  # Limite acceptable
            elif travel_time_minutes <= max_acceptable * 1.25:
                return 0.4  # Un peu long
            else:
                return 0.1  # Trop long
                
        except Exception as e:
            logger.warning(f"Erreur calcul trajet: {e}")
            return 0.5
    
    def _calculate_real_travel_time(self, origin: str, destination: str, mode: str) -> int:
        """
        Calcule le temps de trajet réel via API (Google Maps, etc.)
        Pour l'instant : simulation basée sur distance estimée
        """
        # TODO: Intégrer vraie API de géolocalisation
        
        # Simulation basée sur correspondances ville connues
        paris_suburbs = ['paris', 'boulogne', 'neuilly', 'levallois', 'issy']
        lyon_suburbs = ['lyon', 'villeurbanne', 'vaulx']
        
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        # Même ville
        if any(city in origin_lower and city in dest_lower for city in paris_suburbs + lyon_suburbs):
            if mode == 'pied':
                return 25  # 25 min à pied en ville
            elif mode in ['metro', 'transport']:
                return 20  # 20 min en transport
            elif mode == 'velo':
                return 15  # 15 min en vélo
            else:  # voiture
                return 15  # 15 min en voiture
        
        # Villes différentes mais même région
        elif (any(city in origin_lower for city in paris_suburbs) and 
              any(city in dest_lower for city in paris_suburbs)):
            if mode == 'pied':
                return 90  # Trop long à pied
            elif mode in ['metro', 'transport']:
                return 45  # 45 min en transport
            elif mode == 'velo':
                return 40  # 40 min en vélo
            else:  # voiture
                return 30  # 30 min en voiture
        
        # Régions différentes
        else:
            if mode == 'pied':
                return 180  # Impossible à pied
            elif mode in ['metro', 'transport']:
                return 120  # 2h en transport
            elif mode == 'velo':
                return 150  # Très long en vélo
            else:  # voiture
                return 90  # 1h30 en voiture
    
    def _get_travel_info(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Génère les informations détaillées de trajet"""
        candidate_address = self.questionnaire_data.get('adresse', '')
        job_address = job.get('localisation', '')
        transport_mode = self.questionnaire_data.get('mode_transport', 'voiture')
        
        travel_time = self._calculate_real_travel_time(candidate_address, job_address, transport_mode)
        
        return {
            'origin': candidate_address,
            'destination': job_address,
            'transport_mode': transport_mode,
            'estimated_time_minutes': travel_time,
            'estimated_time_display': f"{travel_time // 60}h{travel_time % 60:02d}min" if travel_time >= 60 else f"{travel_time}min",
            'is_reasonable': travel_time <= self.questionnaire_data.get('temps_trajet_max', 60)
        }
    
    def _generate_explanations(self, job: Dict[str, Any], scores: Dict[str, int]) -> Dict[str, str]:
        """Génère des explications détaillées pour chaque score"""
        explanations = {}
        
        # Compétences
        if scores['skills'] >= 80:
            explanations['skills'] = "Excellente correspondance - vous maîtrisez la plupart des compétences requises"
        elif scores['skills'] >= 60:
            explanations['skills'] = "Bonne correspondance - quelques compétences complémentaires à développer"
        else:
            explanations['skills'] = "Correspondance partielle - formation recommandée sur certaines compétences"
        
        # Contrat
        job_contract = job.get('type_contrat', '').upper()
        candidate_contracts = [c.upper() for c in self.questionnaire_data.get('types_contrat', [])]
        if job_contract in candidate_contracts:
            explanations['contract'] = f"Type de contrat {job_contract} correspond à vos préférences"
        else:
            explanations['contract'] = f"Type de contrat {job_contract} différent de vos préférences ({', '.join(candidate_contracts)})"
        
        # Temps de trajet
        travel_info = self._get_travel_info(job)
        if scores['travel_time'] >= 80:
            explanations['travel_time'] = f"Trajet court ({travel_info['estimated_time_display']}) en {travel_info['transport_mode']}"
        elif scores['travel_time'] >= 60:
            explanations['travel_time'] = f"Trajet acceptable ({travel_info['estimated_time_display']}) en {travel_info['transport_mode']}"
        else:
            explanations['travel_time'] = f"Trajet long ({travel_info['estimated_time_display']}) en {travel_info['transport_mode']}"
        
        # Salaire
        candidate_salary = self.questionnaire_data.get('salaire_souhaite', 0)
        job_salary_min = job.get('salaire_min', 0)
        job_salary_max = job.get('salaire_max', 0)
        
        if job_salary_min and job_salary_max:
            if candidate_salary <= job_salary_max:
                explanations['salary'] = f"Fourchette salariale {job_salary_min}-{job_salary_max}€ compatible avec vos attentes ({candidate_salary}€)"
            else:
                explanations['salary'] = f"Fourchette salariale {job_salary_min}-{job_salary_max}€ inférieure à vos attentes ({candidate_salary}€)"
        
        return explanations
    
    # Réutilisation des méthodes existantes (skills, contract, location, etc.)
    def _calculate_skills_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance des compétences"""
        cv_skills = set(skill.lower().strip() for skill in self.cv_data.get('competences', []))
        job_skills = set(skill.lower().strip() for skill in job.get('competences', []))
        
        if not job_skills:
            return 0.5
        if not cv_skills:
            return 0.0
        
        common_skills = cv_skills.intersection(job_skills)
        coverage_score = len(common_skills) / len(job_skills)
        bonus = min(0.2, (len(cv_skills) - len(job_skills)) * 0.05) if len(cv_skills) > len(job_skills) else 0
        
        return min(1.0, coverage_score + bonus)
    
    def _calculate_contract_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance du type de contrat"""
        candidate_contracts = self.questionnaire_data.get('types_contrat', [])
        job_contract = job.get('type_contrat', '').lower()
        
        if not candidate_contracts or not job_contract:
            return 0.7
        
        candidate_contracts_lower = [c.lower() for c in candidate_contracts]
        
        if job_contract in candidate_contracts_lower:
            return 1.0
        
        # Correspondances partielles
        partial_matches = {
            'cdi': ['permanent', 'indefinite'],
            'cdd': ['temporary', 'fixed', 'interim'],
            'freelance': ['consultant', 'independant', 'contractor'],
            'stage': ['internship', 'stagiaire'],
            'alternance': ['apprentissage', 'apprentice']
        }
        
        for candidate_contract in candidate_contracts_lower:
            if candidate_contract in partial_matches.get(job_contract, []):
                return 0.8
            if job_contract in partial_matches.get(candidate_contract, []):
                return 0.8
        
        return 0.3
    
    def _calculate_location_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance de la localisation"""
        candidate_location = self.questionnaire_data.get('adresse', '').lower()
        job_location = job.get('localisation', '').lower()
        
        if not candidate_location or not job_location:
            return 0.5
        
        if candidate_location in job_location or job_location in candidate_location:
            return 1.0
        
        # Correspondances par région
        paris_region = ['paris', 'boulogne', 'neuilly', 'levallois', 'issy', 'courbevoie']
        lyon_region = ['lyon', 'villeurbanne', 'vaulx']
        
        candidate_in_paris = any(city in candidate_location for city in paris_region)
        job_in_paris = any(city in job_location for city in paris_region)
        candidate_in_lyon = any(city in candidate_location for city in lyon_region)
        job_in_lyon = any(city in job_location for city in lyon_region)
        
        if (candidate_in_paris and job_in_paris) or (candidate_in_lyon and job_in_lyon):
            return 0.8
        
        if 'remote' in job.get('politique_remote', '').lower():
            return 0.9
        
        return 0.3
    
    def _calculate_availability_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance de la disponibilité"""
        candidate_date = self.questionnaire_data.get('date_disponibilite')
        job_date = job.get('date_debut_souhaitee')
        
        if not candidate_date or not job_date:
            return 0.8
        
        try:
            if isinstance(candidate_date, str):
                candidate_date = datetime.datetime.strptime(candidate_date, '%Y-%m-%d').date()
            if isinstance(job_date, str):
                job_date = datetime.datetime.strptime(job_date, '%Y-%m-%d').date()
            
            diff_days = abs((candidate_date - job_date).days)
            
            if diff_days <= 7:
                return 1.0
            elif diff_days <= 30:
                return 0.8
            elif diff_days <= 60:
                return 0.6
            else:
                return 0.3
        except:
            return 0.7
    
    def _calculate_salary_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance du salaire"""
        candidate_salary = self.questionnaire_data.get('salaire_souhaite', 0)
        job_salary_min = job.get('salaire_min', 0)
        job_salary_max = job.get('salaire_max', 0)
        
        if not candidate_salary:
            return 0.7
        
        if not job_salary_min and not job_salary_max:
            return 0.5
        
        if job_salary_min and job_salary_max:
            job_salary = (job_salary_min + job_salary_max) / 2
        else:
            job_salary = job_salary_min or job_salary_max
        
        ratio = job_salary / candidate_salary
        
        if ratio >= 1.1:
            return 1.0
        elif ratio >= 0.95:
            return 0.9
        elif ratio >= 0.8:
            return 0.7
        elif ratio >= 0.6:
            return 0.4
        else:
            return 0.1
    
    def _calculate_experience_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance de l'expérience"""
        candidate_exp = self.cv_data.get('annees_experience', 0)
        job_exp_required = job.get('experience_requise', 0)
        
        if not job_exp_required:
            return 0.8
        
        if candidate_exp >= job_exp_required:
            excess = candidate_exp - job_exp_required
            if excess <= 2:
                return 1.0
            elif excess <= 5:
                return 0.9
            else:
                return 0.7
        else:
            deficit = job_exp_required - candidate_exp
            if deficit <= 1:
                return 0.8
            elif deficit <= 2:
                return 0.6
            else:
                return 0.2
    
    def get_top_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les N meilleures offres avec explications détaillées"""
        all_matches = self.calculate_matching_scores()
        return all_matches[:limit]

# Fonction d'entrée pour SuperSmartMatch
def advanced_match_candidate_with_jobs(cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any], 
                           job_data: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fonction de matching avancée avec calculs de trajets et pondération intelligente
    """
    engine = AdvancedMatchingEngine()
    engine.load_candidate_data(cv_data, questionnaire_data)
    engine.load_job_data(job_data)
    
    return engine.get_top_matches(limit)
