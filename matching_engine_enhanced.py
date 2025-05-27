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

class EnhancedMatchingEngine:
    """
    Moteur de matching amélioré entre candidats et offres d'emploi
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
        self.preferences = self._extract_candidate_preferences()
        logger.info(f"Données candidat chargées: {len(self.cv_data)} éléments CV, {len(self.questionnaire_data)} éléments questionnaire")
    
    def load_job_data(self, job_data: List[Dict[str, Any]]) -> None:
        """Charge les données des offres d'emploi dans le moteur"""
        self.job_data = job_data
        logger.info(f"Données emploi chargées: {len(self.job_data)} offres")
    
    def _extract_candidate_preferences(self) -> Dict[str, float]:
        """Extrait les préférences du candidat pour ajuster la pondération des critères"""
        return {
            'skills': 0.35,        # 35% pour les compétences
            'contract': 0.15,      # 15% pour le type de contrat
            'location': 0.20,      # 20% pour la localisation
            'date': 0.10,          # 10% pour la disponibilité
            'salary': 0.15,        # 15% pour le salaire
            'experience': 0.05     # 5% pour l'expérience
        }
    
    def calculate_matching_scores(self) -> List[Dict[str, Any]]:
        """Calcule les scores de matching pour toutes les offres chargées"""
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
            
            # Utiliser les poids dynamiques basés sur les préférences du candidat
            weights = self.preferences
            
            # Calcul du score global (pondéré)
            total_score = (
                skills_score * weights.get('skills', 0.35) +
                contract_score * weights.get('contract', 0.15) +
                location_score * weights.get('location', 0.20) +
                date_score * weights.get('date', 0.10) +
                salary_score * weights.get('salary', 0.15) +
                experience_score * weights.get('experience', 0.05)
            )
            
            # Formatage du score final en pourcentage
            job_result = job.copy()
            job_result['matching_score'] = round(total_score * 100)
            
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
    
    def _calculate_skills_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance des compétences"""
        cv_skills = set(skill.lower().strip() for skill in self.cv_data.get('competences', []))
        job_skills = set(skill.lower().strip() for skill in job.get('competences', []))
        
        if not job_skills:
            return 0.5  # Score neutre si pas de compétences spécifiées
        
        if not cv_skills:
            return 0.0  # Aucune compétence du candidat
        
        # Compétences communes
        common_skills = cv_skills.intersection(job_skills)
        
        # Score basé sur le pourcentage de compétences requises couvertes
        coverage_score = len(common_skills) / len(job_skills)
        
        # Bonus si le candidat a plus de compétences que demandé
        bonus = min(0.2, (len(cv_skills) - len(job_skills)) * 0.05) if len(cv_skills) > len(job_skills) else 0
        
        return min(1.0, coverage_score + bonus)
    
    def _calculate_contract_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance du type de contrat"""
        candidate_contracts = self.questionnaire_data.get('types_contrat', [])
        job_contract = job.get('type_contrat', '').lower()
        
        if not candidate_contracts or not job_contract:
            return 0.7  # Score par défaut si informations manquantes
        
        # Normaliser les types de contrats
        candidate_contracts_lower = [c.lower() for c in candidate_contracts]
        
        if job_contract in candidate_contracts_lower:
            return 1.0
        
        # Correspondances partielles
        partial_matches = {
            'cdi': ['permanent', 'indefinite'],
            'cdd': ['temporary', 'fixed'],
            'freelance': ['consultant', 'independant', 'contractor'],
            'stage': ['internship', 'stagiaire'],
            'alternance': ['apprentissage', 'apprentice']
        }
        
        for candidate_contract in candidate_contracts_lower:
            if candidate_contract in partial_matches.get(job_contract, []):
                return 0.8
            if job_contract in partial_matches.get(candidate_contract, []):
                return 0.8
        
        return 0.3  # Pas de correspondance
    
    def _calculate_location_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance de la localisation"""
        candidate_location = self.questionnaire_data.get('adresse', '').lower()
        job_location = job.get('localisation', '').lower()
        
        if not candidate_location or not job_location:
            return 0.5  # Score par défaut
        
        # Correspondance exacte de ville
        if candidate_location in job_location or job_location in candidate_location:
            return 1.0
        
        # Correspondances par région (simplifiée)
        paris_region = ['paris', 'boulogne', 'neuilly', 'levallois', 'issy', 'courbevoie']
        lyon_region = ['lyon', 'villeurbanne', 'vaulx']
        
        candidate_in_paris = any(city in candidate_location for city in paris_region)
        job_in_paris = any(city in job_location for city in paris_region)
        
        candidate_in_lyon = any(city in candidate_location for city in lyon_region)
        job_in_lyon = any(city in job_location for city in lyon_region)
        
        if (candidate_in_paris and job_in_paris) or (candidate_in_lyon and job_in_lyon):
            return 0.8
        
        # Vérifier la politique de télétravail
        if 'remote' in job.get('politique_remote', '').lower() or \
           'télétravail' in job.get('description', '').lower():
            return 0.9
        
        return 0.3  # Localisation éloignée
    
    def _calculate_availability_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance de la disponibilité"""
        candidate_date = self.questionnaire_data.get('date_disponibilite')
        job_date = job.get('date_debut_souhaitee')
        
        if not candidate_date or not job_date:
            return 0.8  # Score par défaut élevé si dates non spécifiées
        
        try:
            # Conversion en dates si ce sont des strings
            if isinstance(candidate_date, str):
                candidate_date = datetime.datetime.strptime(candidate_date, '%Y-%m-%d').date()
            if isinstance(job_date, str):
                job_date = datetime.datetime.strptime(job_date, '%Y-%m-%d').date()
            
            # Différence en jours
            diff_days = abs((candidate_date - job_date).days)
            
            if diff_days <= 7:
                return 1.0  # Parfait
            elif diff_days <= 30:
                return 0.8  # Très bon
            elif diff_days <= 60:
                return 0.6  # Acceptable
            else:
                return 0.3  # Décalage important
        except:
            return 0.7  # Score par défaut en cas d'erreur de parsing
    
    def _calculate_salary_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance du salaire"""
        candidate_salary = self.questionnaire_data.get('salaire_souhaite', 0)
        job_salary_min = job.get('salaire_min', 0)
        job_salary_max = job.get('salaire_max', 0)
        
        if not candidate_salary:
            return 0.7  # Score par défaut si pas d'attente salariale
        
        if not job_salary_min and not job_salary_max:
            return 0.5  # Score neutre si salaire non spécifié
        
        # Prendre la moyenne si min et max sont disponibles
        if job_salary_min and job_salary_max:
            job_salary = (job_salary_min + job_salary_max) / 2
        else:
            job_salary = job_salary_min or job_salary_max
        
        # Ratio entre salaire proposé et salaire souhaité
        ratio = job_salary / candidate_salary
        
        if ratio >= 1.1:
            return 1.0  # Salaire supérieur aux attentes
        elif ratio >= 0.95:
            return 0.9  # Salaire proche des attentes
        elif ratio >= 0.8:
            return 0.7  # Salaire acceptable
        elif ratio >= 0.6:
            return 0.4  # Salaire faible
        else:
            return 0.1  # Salaire très faible
    
    def _calculate_experience_score(self, job: Dict[str, Any]) -> float:
        """Calcule le score de correspondance de l'expérience"""
        candidate_exp = self.cv_data.get('annees_experience', 0)
        job_exp_required = job.get('experience_requise', 0)
        
        if not job_exp_required:
            return 0.8  # Score par défaut si pas d'exigence
        
        if candidate_exp >= job_exp_required:
            # Le candidat a plus d'expérience que requis
            excess = candidate_exp - job_exp_required
            if excess <= 2:
                return 1.0  # Parfait
            elif excess <= 5:
                return 0.9  # Très bien (pas de sur-qualification excessive)
            else:
                return 0.7  # Sur-qualifié
        else:
            # Le candidat a moins d'expérience
            deficit = job_exp_required - candidate_exp
            if deficit <= 1:
                return 0.8  # Acceptable
            elif deficit <= 2:
                return 0.6  # Faible mais possible
            else:
                return 0.2  # Insuffisant
    
    def get_top_matches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les N meilleures offres correspondant au profil"""
        all_matches = self.calculate_matching_scores()
        return all_matches[:limit]

# Fonction d'entrée principale
def enhanced_match_candidate_with_jobs(cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any], 
                           job_data: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fonction principale améliorée qui calcule les matchings entre un candidat et des offres d'emploi
    """
    engine = EnhancedMatchingEngine()
    engine.load_candidate_data(cv_data, questionnaire_data)
    engine.load_job_data(job_data)
    
    return engine.get_top_matches(limit)
