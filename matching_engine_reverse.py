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

class ReverseMatchingEngine:
    """
    Moteur de matching INVERSÉ : 1 offre d'emploi → N candidats
    Pondération intelligente selon caractéristiques du poste
    """
    
    def __init__(self):
        self.job_data = {}
        self.candidates_data = []
        self.job_preferences = {}
        
    def load_job_data(self, job_data: Dict[str, Any]) -> None:
        """Charge l'offre d'emploi à analyser"""
        self.job_data = job_data
        self.job_preferences = self._extract_job_preferences()
        logger.info(f"Offre d'emploi chargée: {job_data.get('titre', 'Sans titre')}")
    
    def load_candidates_data(self, candidates_data: List[Dict[str, Any]]) -> None:
        """Charge la liste des candidats à évaluer"""
        self.candidates_data = candidates_data
        logger.info(f"Candidats chargés: {len(candidates_data)} profils")
    
    def _extract_job_preferences(self) -> Dict[str, float]:
        """
        Analyse les caractéristiques du poste pour déterminer la pondération intelligente
        """
        titre = self.job_data.get('titre', '').lower()
        description = self.job_data.get('description', '').lower()
        entreprise_type = self.job_data.get('type_entreprise', '').lower()
        niveau_poste = self.job_data.get('niveau_poste', '').lower()
        
        # Poids par défaut
        weights = {
            'skills': 0.25,
            'experience': 0.20,
            'location': 0.15,
            'travel_time': 0.15,
            'salary': 0.15,
            'career_goals': 0.05,  # Objectifs carrière candidat
            'adaptability': 0.05   # Flexibilité candidat
        }
        
        # LOGIQUE INTELLIGENTE CÔTÉ ENTREPRISE
        
        # 1. Poste avec perspectives d'évolution
        if any(keyword in titre + description for keyword in ['senior', 'lead', 'manager', 'évolution', 'carrière']):
            weights['career_goals'] = 0.20  # Prioriser candidats ambitieux
            weights['experience'] = 0.25
            weights['skills'] = 0.20
            logger.info("🎯 Pondération ÉVOLUTION privilégiée (poste senior/évolution)")
        
        # 2. Startup ou environnement dynamique
        elif any(keyword in entreprise_type + description for keyword in ['startup', 'agile', 'innovation', 'dynamique']):
            weights['adaptability'] = 0.20  # Prioriser flexibilité
            weights['skills'] = 0.30  # Compétences techniques importantes
            weights['experience'] = 0.15  # Moins critique
            logger.info("🎯 Pondération STARTUP privilégiée (flexibilité + technique)")
        
        # 3. Poste très technique/spécialisé
        elif any(keyword in titre + description for keyword in ['développeur', 'ingénieur', 'architecte', 'technique']):
            weights['skills'] = 0.35  # Compétences primordiales
            weights['experience'] = 0.25
            weights['salary'] = 0.10  # Moins important
            logger.info("🎯 Pondération TECHNIQUE privilégiée (compétences cruciales)")
        
        # 4. Poste avec contraintes géographiques fortes
        if self.job_data.get('teletravail_possible', False) == False and \
           'sur site' in description or 'présentiel' in description:
            weights['location'] = 0.25
            weights['travel_time'] = 0.20
            weights['adaptability'] = 0.15  # Mobilité importante
            logger.info("🎯 Pondération LOCALISATION privilégiée (contraintes géographiques)")
        
        # 5. Poste management/leadership
        if any(keyword in titre for keyword in ['manager', 'directeur', 'responsable', 'chef']):
            weights['experience'] = 0.30  # Expérience cruciale
            weights['career_goals'] = 0.15  # Leadership
            weights['skills'] = 0.20
            logger.info("🎯 Pondération MANAGEMENT privilégiée (expérience + leadership)")
        
        return weights
    
    def calculate_candidates_scores(self) -> List[Dict[str, Any]]:
        """Calcule les scores de correspondance pour tous les candidats"""
        if not self.job_data or not self.candidates_data:
            logger.error("Données manquantes pour le calcul des scores")
            return []
        
        results = []
        
        for candidate in self.candidates_data:
            cv_data = candidate.get('cv_data', {})
            questionnaire_data = candidate.get('questionnaire_data', {})
            candidate_id = candidate.get('candidate_id', 'unknown')
            
            # Calcul des différents critères
            skills_score = self._calculate_candidate_skills_score(cv_data)
            experience_score = self._calculate_candidate_experience_score(cv_data)
            location_score = self._calculate_candidate_location_score(questionnaire_data)
            travel_time_score = self._calculate_candidate_travel_time_score(questionnaire_data)
            salary_score = self._calculate_candidate_salary_score(questionnaire_data)
            career_goals_score = self._calculate_candidate_career_goals_score(questionnaire_data)
            adaptability_score = self._calculate_candidate_adaptability_score(questionnaire_data)
            
            # Utiliser les poids intelligents selon le poste
            weights = self.job_preferences
            
            # Score global pondéré
            total_score = (
                skills_score * weights.get('skills', 0.25) +
                experience_score * weights.get('experience', 0.20) +
                location_score * weights.get('location', 0.15) +
                travel_time_score * weights.get('travel_time', 0.15) +
                salary_score * weights.get('salary', 0.15) +
                career_goals_score * weights.get('career_goals', 0.05) +
                adaptability_score * weights.get('adaptability', 0.05)
            )
            
            # Formatage résultat enrichi
            candidate_result = {
                'candidate_id': candidate_id,
                'candidate_name': cv_data.get('nom', f'Candidat {candidate_id}'),
                'matching_score': round(total_score * 100),
                'matching_details': {
                    'skills': round(skills_score * 100),
                    'experience': round(experience_score * 100),
                    'location': round(location_score * 100),
                    'travel_time': round(travel_time_score * 100),
                    'salary': round(salary_score * 100),
                    'career_goals': round(career_goals_score * 100),
                    'adaptability': round(adaptability_score * 100)
                },
                'matching_explanations': self._generate_candidate_explanations(
                    cv_data, questionnaire_data, {
                        'skills': round(skills_score * 100),
                        'experience': round(experience_score * 100),
                        'location': round(location_score * 100),
                        'travel_time': round(travel_time_score * 100),
                        'salary': round(salary_score * 100),
                        'career_goals': round(career_goals_score * 100),
                        'adaptability': round(adaptability_score * 100)
                    }
                ),
                'candidate_info': self._get_candidate_summary(cv_data, questionnaire_data),
                'cv_data': cv_data,
                'questionnaire_data': questionnaire_data
            }
            
            results.append(candidate_result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def _calculate_candidate_skills_score(self, cv_data: Dict[str, Any]) -> float:
        """Score des compétences du candidat vs poste"""
        candidate_skills = set(skill.lower().strip() for skill in cv_data.get('competences', []))
        job_skills = set(skill.lower().strip() for skill in self.job_data.get('competences', []))
        
        if not job_skills:
            return 0.7  # Score neutre si pas de compétences spécifiées
        
        if not candidate_skills:
            return 0.0
        
        # Compétences communes
        common_skills = candidate_skills.intersection(job_skills)
        
        # Score basé sur couverture + bonus si plus de compétences
        coverage_score = len(common_skills) / len(job_skills)
        bonus = min(0.3, (len(candidate_skills) - len(job_skills)) * 0.05) if len(candidate_skills) > len(job_skills) else 0
        
        return min(1.0, coverage_score + bonus)
    
    def _calculate_candidate_experience_score(self, cv_data: Dict[str, Any]) -> float:
        """Score de l'expérience du candidat vs requirements"""
        candidate_exp = cv_data.get('annees_experience', 0)
        job_exp_required = self.job_data.get('experience_requise', 0)
        
        if not job_exp_required:
            return 0.8  # Score par défaut
        
        if candidate_exp >= job_exp_required:
            # Candidat a l'expérience requise ou plus
            excess = candidate_exp - job_exp_required
            if excess <= 3:
                return 1.0  # Parfait
            elif excess <= 7:
                return 0.9  # Très bien
            else:
                return 0.7  # Sur-qualifié mais acceptable
        else:
            # Candidat manque d'expérience
            deficit = job_exp_required - candidate_exp
            if deficit <= 1:
                return 0.8  # Léger manque, acceptable
            elif deficit <= 3:
                return 0.5  # Manque significatif
            else:
                return 0.2  # Très insuffisant
    
    def _calculate_candidate_location_score(self, questionnaire_data: Dict[str, Any]) -> float:
        """Score de localisation candidat vs poste"""
        candidate_location = questionnaire_data.get('adresse', '').lower()
        job_location = self.job_data.get('localisation', '').lower()
        
        if not candidate_location or not job_location:
            return 0.5
        
        # Correspondance exacte
        if candidate_location in job_location or job_location in candidate_location:
            return 1.0
        
        # Correspondances régionales (Paris, Lyon, etc.)
        paris_region = ['paris', 'boulogne', 'neuilly', 'levallois', 'issy']
        lyon_region = ['lyon', 'villeurbanne', 'vaulx']
        
        candidate_in_paris = any(city in candidate_location for city in paris_region)
        job_in_paris = any(city in job_location for city in paris_region)
        candidate_in_lyon = any(city in candidate_location for city in lyon_region)
        job_in_lyon = any(city in job_location for city in lyon_region)
        
        if (candidate_in_paris and job_in_paris) or (candidate_in_lyon and job_in_lyon):
            return 0.8
        
        # Télétravail possible
        if self.job_data.get('teletravail_possible', False):
            return 0.9
        
        return 0.3  # Trop éloigné
    
    def _calculate_candidate_travel_time_score(self, questionnaire_data: Dict[str, Any]) -> float:
        """Score temps de trajet candidat vers poste"""
        candidate_address = questionnaire_data.get('adresse', '')
        job_address = self.job_data.get('localisation', '')
        transport_mode = questionnaire_data.get('mode_transport', 'voiture').lower()
        
        if not candidate_address or not job_address:
            return 0.5
        
        # Télétravail = score parfait
        if self.job_data.get('teletravail_possible', False):
            return 1.0
        
        try:
            # Réutiliser la logique de calcul temps trajet
            travel_time_minutes = self._calculate_real_travel_time(
                candidate_address, job_address, transport_mode
            )
            
            candidate_max_time = questionnaire_data.get('temps_trajet_max', 60)
            
            if travel_time_minutes <= candidate_max_time * 0.5:
                return 1.0
            elif travel_time_minutes <= candidate_max_time * 0.75:
                return 0.8
            elif travel_time_minutes <= candidate_max_time:
                return 0.6
            elif travel_time_minutes <= candidate_max_time * 1.25:
                return 0.4
            else:
                return 0.1
                
        except Exception:
            return 0.5
    
    def _calculate_candidate_salary_score(self, questionnaire_data: Dict[str, Any]) -> float:
        """Score correspondance salaire candidat vs poste"""
        candidate_salary = questionnaire_data.get('salaire_souhaite', 0)
        job_salary_min = self.job_data.get('salaire_min', 0)
        job_salary_max = self.job_data.get('salaire_max', 0)
        
        if not candidate_salary:
            return 0.7  # Neutre si pas d'attente
        
        if not job_salary_min and not job_salary_max:
            return 0.5  # Neutre si salaire poste non spécifié
        
        # Prendre la moyenne du poste
        if job_salary_min and job_salary_max:
            job_salary = (job_salary_min + job_salary_max) / 2
        else:
            job_salary = job_salary_min or job_salary_max
        
        # Ratio attentes candidat vs offre poste
        ratio = job_salary / candidate_salary
        
        if ratio >= 1.1:
            return 1.0  # Poste paye plus que demandé
        elif ratio >= 0.95:
            return 0.9  # Très proche
        elif ratio >= 0.8:
            return 0.7  # Acceptable
        elif ratio >= 0.6:
            return 0.4  # Faible
        else:
            return 0.1  # Très faible
    
    def _calculate_candidate_career_goals_score(self, questionnaire_data: Dict[str, Any]) -> float:
        """Score objectifs carrière candidat vs opportunités poste"""
        candidate_goals = questionnaire_data.get('objectif', '').lower()
        candidate_ambition = questionnaire_data.get('niveau_ambition', 'moyen').lower()
        
        job_title = self.job_data.get('titre', '').lower()
        job_description = self.job_data.get('description', '').lower()
        
        # Si poste avec perspectives d'évolution
        job_has_evolution = any(keyword in job_title + job_description 
                               for keyword in ['senior', 'lead', 'manager', 'évolution', 'progression'])
        
        # Si candidat cherche évolution
        candidate_wants_evolution = any(keyword in candidate_goals 
                                      for keyword in ['evolution', 'carriere', 'progression', 'management'])
        
        if job_has_evolution and candidate_wants_evolution:
            return 1.0  # Match parfait
        elif job_has_evolution and candidate_ambition in ['élevé', 'high']:
            return 0.8  # Candidat ambitieux pour poste évolutif
        elif not job_has_evolution and candidate_goals in ['stabilite', 'equilibre']:
            return 0.8  # Candidat stable pour poste stable
        else:
            return 0.6  # Score neutre
    
    def _calculate_candidate_adaptability_score(self, questionnaire_data: Dict[str, Any]) -> float:
        """Score flexibilité/adaptabilité candidat"""
        # Flexibilité contrat
        candidate_contracts = questionnaire_data.get('types_contrat', [])
        contract_flexibility = len(candidate_contracts) / 4.0  # Max 4 types (CDI,CDD,INTERIM,FREELANCE)
        
        # Flexibilité géographique
        mobility = questionnaire_data.get('mobilite', 'faible').lower()
        if mobility in ['élevé', 'high', 'internationale']:
            geo_flexibility = 1.0
        elif mobility in ['moyen', 'medium', 'nationale']:
            geo_flexibility = 0.7
        else:
            geo_flexibility = 0.4
        
        # Flexibilité télétravail
        remote_ok = questionnaire_data.get('accepte_teletravail', True)
        remote_flexibility = 1.0 if remote_ok else 0.6
        
        # Score global adaptabilité
        adaptability = (contract_flexibility + geo_flexibility + remote_flexibility) / 3.0
        return min(1.0, adaptability)
    
    def _calculate_real_travel_time(self, origin: str, destination: str, mode: str) -> int:
        """Calcul temps trajet (réutilise logique existante)"""
        # Simulation basée sur correspondances ville
        paris_suburbs = ['paris', 'boulogne', 'neuilly', 'levallois', 'issy']
        lyon_suburbs = ['lyon', 'villeurbanne', 'vaulx']
        
        origin_lower = origin.lower()
        dest_lower = destination.lower()
        
        # Même ville
        if any(city in origin_lower and city in dest_lower for city in paris_suburbs + lyon_suburbs):
            if mode == 'pied':
                return 25
            elif mode in ['metro', 'transport']:
                return 20
            elif mode == 'velo':
                return 15
            else:  # voiture
                return 15
        
        # Même région
        elif (any(city in origin_lower for city in paris_suburbs) and 
              any(city in dest_lower for city in paris_suburbs)):
            if mode == 'pied':
                return 90
            elif mode in ['metro', 'transport']:
                return 45
            elif mode == 'velo':
                return 40
            else:  # voiture
                return 30
        
        # Régions différentes
        else:
            if mode == 'pied':
                return 180
            elif mode in ['metro', 'transport']:
                return 120
            elif mode == 'velo':
                return 150
            else:  # voiture
                return 90
    
    def _generate_candidate_explanations(self, cv_data: Dict[str, Any], 
                                       questionnaire_data: Dict[str, Any], 
                                       scores: Dict[str, int]) -> Dict[str, str]:
        """Génère explications détaillées pour chaque candidat"""
        explanations = {}
        
        # Compétences
        if scores['skills'] >= 80:
            explanations['skills'] = "Profil technique excellent - maîtrise la plupart des compétences requises"
        elif scores['skills'] >= 60:
            explanations['skills'] = "Profil technique correct - quelques compétences à développer"
        else:
            explanations['skills'] = "Profil technique limité - formation nécessaire"
        
        # Expérience
        candidate_exp = cv_data.get('annees_experience', 0)
        job_exp = self.job_data.get('experience_requise', 0)
        if candidate_exp >= job_exp:
            explanations['experience'] = f"Expérience suffisante ({candidate_exp} ans vs {job_exp} requis)"
        else:
            explanations['experience'] = f"Manque d'expérience ({candidate_exp} ans vs {job_exp} requis)"
        
        # Localisation
        if scores['location'] >= 80:
            explanations['location'] = "Localisation excellente - proximité géographique"
        elif scores['location'] >= 60:
            explanations['location'] = "Localisation acceptable - même région"
        else:
            explanations['location'] = "Localisation éloignée - nécessite mobilité"
        
        # Objectifs carrière
        candidate_goals = questionnaire_data.get('objectif', '')
        if scores['career_goals'] >= 80:
            explanations['career_goals'] = f"Objectifs alignés - candidat motivé pour évoluer"
        else:
            explanations['career_goals'] = f"Objectifs partiellement alignés"
        
        return explanations
    
    def _get_candidate_summary(self, cv_data: Dict[str, Any], 
                             questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """Résumé candidat pour entreprise"""
        return {
            'experience_years': cv_data.get('annees_experience', 0),
            'main_skills': cv_data.get('competences', [])[:5],  # Top 5
            'education': cv_data.get('niveau_etudes', ''),
            'current_salary': questionnaire_data.get('salaire_actuel', 0),
            'expected_salary': questionnaire_data.get('salaire_souhaite', 0),
            'availability': questionnaire_data.get('date_disponibilite', ''),
            'location': questionnaire_data.get('adresse', ''),
            'transport_mode': questionnaire_data.get('mode_transport', ''),
            'career_goals': questionnaire_data.get('objectif', ''),
            'contract_preferences': questionnaire_data.get('types_contrat', [])
        }
    
    def get_top_candidates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retourne les N meilleurs candidats pour le poste"""
        all_matches = self.calculate_candidates_scores()
        return all_matches[:limit]

# Fonction d'entrée pour matching inverse (entreprise → candidats)
def reverse_match_job_with_candidates(job_data: Dict[str, Any], 
                                    candidates_data: List[Dict[str, Any]], 
                                    limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fonction de matching inversé : 1 poste → N candidats
    """
    engine = ReverseMatchingEngine()
    engine.load_job_data(job_data)
    engine.load_candidates_data(candidates_data)
    
    return engine.get_top_candidates(limit)
