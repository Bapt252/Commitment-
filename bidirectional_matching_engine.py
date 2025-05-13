#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moteur de matching bidirectionnel

Ce module analyse les données du côté candidat et du côté entreprise 
pour calculer des scores de matching dans les deux sens :
- Candidat → Offres d'emploi (classique)
- Offre d'emploi → Candidats (inverse)

Ce format permet une mise en relation optimale des deux parties.
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

class BidirectionalMatchingEngine:
    """
    Moteur de matching bidirectionnel entre candidats et offres d'emploi
    """
    
    def __init__(self):
        self.candidates_data = {}  # Stockage des données de tous les candidats
        self.jobs_data = {}        # Stockage des données de toutes les offres
        self.company_preferences = {}  # Préférences de l'entreprise
    
    def load_candidates_data(self, candidates_data: List[Dict[str, Any]]) -> None:
        """
        Charge les données de tous les candidats dans le moteur
        
        Args:
            candidates_data: Liste des données de candidats (CV + questionnaire)
        """
        for candidate in candidates_data:
            if 'email' in candidate and candidate['email']:
                self.candidates_data[candidate['email']] = candidate
        
        logger.info(f"Données candidats chargées: {len(self.candidates_data)} candidats")
    
    def load_jobs_data(self, jobs_data: List[Dict[str, Any]]) -> None:
        """
        Charge les données de toutes les offres d'emploi dans le moteur
        
        Args:
            jobs_data: Liste des données d'offres d'emploi
        """
        for job in jobs_data:
            if 'id' in job and job['id']:
                self.jobs_data[job['id']] = job
        
        logger.info(f"Données emploi chargées: {len(self.jobs_data)} offres")
    
    def load_company_preferences(self, company_preferences: Dict[str, Any]) -> None:
        """
        Charge les préférences de l'entreprise dans le moteur (issues du questionnaire entreprise)
        
        Args:
            company_preferences: Données de préférences de l'entreprise
        """
        self.company_preferences = company_preferences
        logger.info(f"Préférences entreprise chargées: {len(self.company_preferences)} éléments")
    
    def get_candidates_for_job(self, job_id: Union[str, int], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retourne les candidats les plus adaptés à une offre d'emploi spécifique
        
        Args:
            job_id: ID de l'offre d'emploi
            limit: Nombre maximum de candidats à retourner
            
        Returns:
            Liste des candidats les plus adaptés avec leurs scores
        """
        if not self.candidates_data:
            logger.error("Aucun candidat chargé dans le système")
            return []
        
        job_id = str(job_id)  # Conversion en string pour uniformité
        
        if job_id not in self.jobs_data:
            logger.error(f"L'offre d'emploi avec l'ID {job_id} n'existe pas")
            return []
        
        job_data = self.jobs_data[job_id]
        results = []
        
        # Récupérer les poids des critères basés sur les préférences de l'entreprise
        weights = self._extract_company_weights()
        
        # Pour chaque candidat, calculer le score de matching avec l'offre
        for email, candidate in self.candidates_data.items():
            # Extraire les données du CV et du questionnaire
            cv_data = candidate.get('cv_data', {})
            questionnaire_data = candidate.get('questionnaire_data', {})
            
            # Calcul des différents critères de matching
            skills_score = self._calculate_candidate_skills_score(cv_data, job_data)
            contract_score = self._calculate_candidate_contract_score(questionnaire_data, job_data)
            location_score = self._calculate_candidate_location_score(questionnaire_data, job_data)
            date_score = self._calculate_candidate_availability_score(questionnaire_data, job_data)
            salary_score = self._calculate_candidate_salary_score(questionnaire_data, job_data)
            experience_score = self._calculate_candidate_experience_score(cv_data, job_data)
            soft_skills_score = self._calculate_candidate_soft_skills_score(cv_data, job_data)
            culture_score = self._calculate_candidate_culture_score(questionnaire_data, job_data)
            
            # Calcul du score global pondéré
            total_score = (
                skills_score * weights.get('skills', 0.30) +
                contract_score * weights.get('contract', 0.10) +
                location_score * weights.get('location', 0.10) +
                date_score * weights.get('date', 0.05) +
                salary_score * weights.get('salary', 0.15) +
                experience_score * weights.get('experience', 0.15) +
                soft_skills_score * weights.get('soft_skills', 0.10) +
                culture_score * weights.get('culture', 0.05)
            )
            
            # Critères non-négociables (deal breakers)
            deal_breakers = self._check_deal_breakers(cv_data, questionnaire_data, job_data)
            
            # Formatage du résultat
            result = {
                'email': email,
                'name': f"{cv_data.get('nom', '')} {cv_data.get('prenom', '')}".strip(),
                'matching_score': round(total_score * 100),
                'matching_details': {
                    'skills': round(skills_score * 100),
                    'contract': round(contract_score * 100),
                    'location': round(location_score * 100),
                    'date': round(date_score * 100),
                    'salary': round(salary_score * 100),
                    'experience': round(experience_score * 100),
                    'soft_skills': round(soft_skills_score * 100),
                    'culture': round(culture_score * 100)
                },
                'deal_breakers': deal_breakers
            }
            
            # Ajouter des explications pour l'entreprise
            result['matching_explanations'] = self._generate_company_explanations(
                result['matching_details'], 
                deal_breakers
            )
            
            results.append(result)
        
        # Filtrer les candidats avec des deal breakers si l'entreprise le demande
        if self.company_preferences.get('ignore_deal_breakers', False) == False:
            results = [r for r in results if len(r['deal_breakers']) == 0]
        
        # Trier les résultats par score décroissant
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        
        # Limiter le nombre de résultats
        return results[:limit]
    
    def _extract_company_weights(self) -> Dict[str, float]:
        """
        Extrait les poids des critères basés sur les préférences de l'entreprise
        
        Returns:
            Dictionnaire des poids par critère
        """
        # Poids par défaut
        default_weights = {
            'skills': 0.30,
            'contract': 0.10,
            'location': 0.10,
            'date': 0.05,
            'salary': 0.15,
            'experience': 0.15,
            'soft_skills': 0.10,
            'culture': 0.05
        }
        
        # Si pas de préférences spécifiées, retourner les poids par défaut
        if not self.company_preferences:
            return default_weights
        
        # Récupérer les priorités de l'entreprise
        priorities = self.company_preferences.get('priorites', {})
        
        if not priorities:
            return default_weights
        
        # Conversion du questionnaire client vers les critères du matching engine
        priority_mapping = {
            'competences_techniques': 'skills',
            'experience': 'experience',
            'formation': 'experience',  # On combine formation et expérience
            'soft_skills': 'soft_skills',
            'disponibilite': 'date'
        }
        
        # Calculer la somme totale des priorités
        total_priority = sum(priorities.values())
        
        if total_priority == 0:
            return default_weights
        
        # Convertir les priorités en poids normalisés
        weights = {}
        remaining_weight = 1.0
        
        # Traiter les critères spécifiés
        for criterion, priority in priorities.items():
            mapped_criterion = priority_mapping.get(criterion)
            if mapped_criterion:
                weights[mapped_criterion] = priority / total_priority
                remaining_weight -= weights[mapped_criterion]
        
        # Répartir le poids restant sur les critères non spécifiés
        unspecified_criteria = [k for k in default_weights.keys() if k not in weights]
        for criterion in unspecified_criteria:
            weights[criterion] = remaining_weight / len(unspecified_criteria)
        
        return weights
    
    def _check_deal_breakers(self, 
                            cv_data: Dict[str, Any], 
                            questionnaire_data: Dict[str, Any], 
                            job_data: Dict[str, Any]) -> List[str]:
        """
        Vérifie les critères non-négociables pour l'entreprise
        
        Args:
            cv_data: Données du CV du candidat
            questionnaire_data: Données du questionnaire du candidat
            job_data: Données de l'offre d'emploi
            
        Returns:
            Liste des deal breakers identifiés (vide si aucun)
        """
        deal_breakers = []
        
        # Si pas de préférences entreprise, pas de deal breakers
        if not self.company_preferences:
            return deal_breakers
        
        company_deal_breakers = self.company_preferences.get('deal_breakers', [])
        
        # Si l'entreprise n'a pas spécifié de deal breakers, retourner liste vide
        if not company_deal_breakers:
            return deal_breakers
        
        # Vérifier les compétences requises
        if "Pas de maîtrise de React" in company_deal_breakers:
            cv_skills = set(skill.lower() for skill in cv_data.get('competences', []))
            if "react" not in cv_skills and "reactjs" not in cv_skills:
                deal_breakers.append("Compétence React manquante")
        
        # Vérifier l'expérience minimum
        if "Moins de 2 ans d'expérience" in company_deal_breakers:
            experience_years = cv_data.get('annees_experience', 0)
            if experience_years < 2:
                deal_breakers.append("Expérience insuffisante (< 2 ans)")
        
        # Vérifier les soft skills
        if "Pas de travail d'équipe" in company_deal_breakers:
            cv_soft_skills = set(skill.lower() for skill in cv_data.get('soft_skills', []))
            if "travail d'équipe" not in cv_soft_skills and "teamwork" not in cv_soft_skills:
                deal_breakers.append("Absence de soft skill: travail d'équipe")
        
        # Ajouter d'autres vérifications selon les besoins de l'entreprise
        
        return deal_breakers
    
    def _generate_company_explanations(self, 
                                    scores: Dict[str, int], 
                                    deal_breakers: List[str]) -> Dict[str, str]:
        """
        Génère des explications textuelles pour l'entreprise sur le matching avec un candidat
        
        Args:
            scores: Scores détaillés par critère
            deal_breakers: Liste des critères bloquants identifiés
            
        Returns:
            Dictionnaire d'explications par critère
        """
        explanations = {}
        
        # Explications liées aux deal breakers
        if deal_breakers:
            explanations['deal_breakers'] = "Ce candidat ne remplit pas tous les critères essentiels : " + ", ".join(deal_breakers)
        else:
            explanations['deal_breakers'] = "Ce candidat remplit tous les critères essentiels."
        
        # Explications pour les compétences
        if scores['skills'] >= 90:
            explanations['skills'] = "Le candidat maîtrise toutes les compétences techniques requises pour le poste."
        elif scores['skills'] >= 70:
            explanations['skills'] = "Le candidat possède la plupart des compétences techniques nécessaires."
        elif scores['skills'] >= 50:
            explanations['skills'] = "Le candidat a des lacunes sur certaines compétences techniques importantes."
        else:
            explanations['skills'] = "Le candidat ne possède que peu des compétences techniques demandées."
        
        # Explications pour l'expérience
        if scores['experience'] >= 90:
            explanations['experience'] = "Le candidat a l'expérience idéale pour ce poste."
        elif scores['experience'] >= 70:
            explanations['experience'] = "L'expérience du candidat correspond bien aux besoins du poste."
        elif scores['experience'] >= 50:
            explanations['experience'] = "Le candidat a une expérience légèrement inférieure à celle recherchée."
        else:
            explanations['experience'] = "Le candidat manque d'expérience pour ce poste."
        
        # Explications pour le salaire
        if scores['salary'] >= 90:
            explanations['salary'] = "Les attentes salariales du candidat sont alignées avec votre budget."
        elif scores['salary'] >= 70:
            explanations['salary'] = "Les attentes salariales du candidat sont proches de votre budget."
        elif scores['salary'] >= 50:
            explanations['salary'] = "Les attentes salariales du candidat sont légèrement supérieures à votre budget."
        else:
            explanations['salary'] = "Les attentes salariales du candidat sont significativement au-dessus de votre budget."
        
        # Explications pour la disponibilité
        if scores['date'] >= 90:
            explanations['date'] = "Le candidat est disponible immédiatement ou dans le délai souhaité."
        elif scores['date'] >= 70:
            explanations['date'] = "Le candidat sera disponible avec un léger délai par rapport à vos attentes."
        else:
            explanations['date'] = "Le candidat n'est pas disponible dans les délais souhaités."
        
        # Explications pour les soft skills
        if scores['soft_skills'] >= 80:
            explanations['soft_skills'] = "Le candidat possède les compétences comportementales recherchées."
        elif scores['soft_skills'] >= 50:
            explanations['soft_skills'] = "Le candidat a certaines des compétences comportementales recherchées."
        else:
            explanations['soft_skills'] = "Le candidat ne démontre pas les compétences comportementales prioritaires."
        
        return explanations
    
    def _calculate_candidate_skills_score(self, 
                                        cv_data: Dict[str, Any], 
                                        job_data: Dict[str, Any]) -> float:
        """
        Calcule le score de matching des compétences techniques du candidat avec l'offre
        
        Args:
            cv_data: Données du CV du candidat
            job_data: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Extraire les compétences
        cv_skills = set(skill.lower() for skill in cv_data.get('competences', []))
        job_skills = set(skill.lower() for skill in job_data.get('competences', []))
        
        # Extraire les compétences par niveau d'importance (si disponible)
        job_skills_details = job_data.get('competences_techniques_details', {})
        essential_skills = set(skill.lower() for skill in job_skills_details.get('indispensables', []))
        important_skills = set(skill.lower() for skill in job_skills_details.get('importantes', []))
        nice_to_have_skills = set(skill.lower() for skill in job_skills_details.get('souhaitables', []))
        
        # Si pas de compétences détaillées, utiliser les compétences générales
        if not essential_skills and not important_skills and not nice_to_have_skills:
            # Si pas de compétences listées dans l'offre, score neutre
            if not job_skills:
                return 0.5
            
            # Calculer l'intersection des compétences
            matching_skills = cv_skills.intersection(job_skills)
            
            # Calculer le score basé sur le pourcentage de compétences requises que le candidat possède
            return len(matching_skills) / len(job_skills)
        
        # Score pondéré par niveau d'importance
        score = 0.0
        
        # Compétences indispensables (60% du score)
        if essential_skills:
            essential_match = cv_skills.intersection(essential_skills)
            score += 0.6 * (len(essential_match) / len(essential_skills))
        
        # Compétences importantes (30% du score)
        if important_skills:
            important_match = cv_skills.intersection(important_skills)
            score += 0.3 * (len(important_match) / len(important_skills))
        
        # Compétences souhaitables (10% du score)
        if nice_to_have_skills:
            nice_to_have_match = cv_skills.intersection(nice_to_have_skills)
            score += 0.1 * (len(nice_to_have_match) / len(nice_to_have_skills))
        
        return score
    
    def _calculate_candidate_contract_score(self, 
                                         questionnaire_data: Dict[str, Any], 
                                         job_data: Dict[str, Any]) -> float:
        """
        Calcule le score de matching du type de contrat
        
        Args:
            questionnaire_data: Données du questionnaire du candidat
            job_data: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Récupérer les types de contrat recherchés par le candidat
        preferred_contracts = questionnaire_data.get('contrats_recherches', [])
        
        # Récupérer le type de contrat proposé
        job_contract = job_data.get('type_contrat', '').lower()
        
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
        
        # Calcul du score (correspondance exacte = 1.0)
        if normalized_job_contract in normalized_preferences:
            return 1.0
        
        # Si le candidat veut un CDI mais on propose un CDD ou interim, score moyen
        if 'cdi' in normalized_preferences:
            if normalized_job_contract in ['cdd', 'interim']:
                return 0.5
        
        # Si le candidat veut un stage/alternance mais on propose un emploi, score bas
        if any(c in normalized_preferences for c in ['stage', 'alternance']):
            if normalized_job_contract in ['cdi', 'cdd', 'interim', 'freelance']:
                return 0.3
        
        # Pas de correspondance
        return 0.0
    
    def _calculate_candidate_location_score(self, 
                                         questionnaire_data: Dict[str, Any], 
                                         job_data: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de la localisation
        
        Args:
            questionnaire_data: Données du questionnaire du candidat
            job_data: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Pour l'implémentation actuelle, on réutilise le code existant
        candidate_address = questionnaire_data.get('adresse', '')
        job_address = job_data.get('localisation', '')
        max_commute_time = questionnaire_data.get('temps_trajet_max', 60)  # Minutes
        
        # Si les données sont manquantes, retourner un score moyen
        if not candidate_address or not job_address:
            return 0.5
        
        try:
            # Calculer le temps de trajet
            commute_time = self._get_commute_time(candidate_address, job_address)
            
            # Si on n'a pas pu calculer le temps de trajet, retourner un score moyen
            if commute_time is None:
                return 0.5
            
            # Calcul du score basé sur le temps de trajet maximum acceptable
            if commute_time <= max_commute_time:
                return 1.0 - (commute_time / max_commute_time)
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Erreur lors du calcul du temps de trajet: {str(e)}")
            return 0.5
    
    def _get_commute_time(self, origin: str, destination: str) -> Optional[int]:
        """
        Calcule le temps de trajet entre deux adresses (simulation)
        
        Args:
            origin: Adresse de départ
            destination: Adresse d'arrivée
            
        Returns:
            Temps de trajet en minutes ou None si erreur
        """
        # Code adapté de l'existant
        # Simulation pour le MVP:
        import random
        
        # Simuler une distance aléatoire entre 1 et 50 km
        distance = random.uniform(1, 50)
        
        # Vitesse moyenne en km/h (en ville)
        avg_speed = 30
        
        # Temps en minutes (formule simple)
        time_minutes = (distance / avg_speed) * 60
        
        return round(time_minutes)
    
    def _calculate_candidate_availability_score(self, 
                                              questionnaire_data: Dict[str, Any], 
                                              job_data: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de la disponibilité
        
        Args:
            questionnaire_data: Données du questionnaire du candidat
            job_data: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Code adapté de l'existant
        try:
            availability_date_str = questionnaire_data.get('date_disponibilite', '')
            job_start_date_str = job_data.get('date_debut', '')
            
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
    
    def _calculate_candidate_salary_score(self, 
                                       questionnaire_data: Dict[str, Any], 
                                       job_data: Dict[str, Any]) -> float:
        """
        Calcule le score de matching du salaire
        
        Args:
            questionnaire_data: Données du questionnaire du candidat
            job_data: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Code adapté de l'existant avec des améliorations
        min_salary = questionnaire_data.get('salaire_min', 0)
        job_salary_str = job_data.get('salaire', '')
        
        # Si les données sont manquantes, retourner un score moyen
        if not min_salary or not job_salary_str:
            return 0.5
        
        try:
            # Extraire la fourchette de salaire
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
            # Si le salaire maximum proposé est inférieur au minimum demandé
            if job_max_salary < min_salary:
                # Calculer l'écart en pourcentage
                gap_percentage = (min_salary - job_max_salary) / min_salary
                if gap_percentage > 0.2:  # Écart supérieur à 20%
                    return 0.0
                else:
                    # Score dégressif selon l'écart
                    return max(0.0, 0.5 - gap_percentage * 2.5)
            
            # Si le salaire minimum proposé est supérieur au minimum demandé
            elif job_min_salary >= min_salary:
                # Bonus si le salaire proposé est bien supérieur
                if job_min_salary >= min_salary * 1.2:
                    return 1.0
                else:
                    return 0.8 + (job_min_salary - min_salary) / (min_salary * 2)  # Max 1.0
            
            # Si l'intervalle de salaire proposé chevauche le minimum demandé
            else:
                # Plus le minimum proposé est proche du minimum demandé, meilleur est le score
                return job_min_salary / min_salary
        
        except Exception as e:
            logger.error(f"Erreur lors du calcul du score de salaire: {str(e)}")
            return 0.5
    
    def _calculate_candidate_experience_score(self, 
                                           cv_data: Dict[str, Any], 
                                           job_data: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de l'expérience
        
        Args:
            cv_data: Données du CV du candidat
            job_data: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Extrait du questionnaire client
        experience_mapping = {
            'junior': (0, 2),
            '2-3': (2, 4),
            '5-10': (5, 10),
            '10plus': (10, 20)
        }
        
        # Récupérer l'expérience requise depuis le questionnaire client
        exp_required = job_data.get('experience_required', '')
        if exp_required in experience_mapping:
            job_min_exp, job_max_exp = experience_mapping[exp_required]
        else:
            # Fallback vers l'analyse du champ expérience de l'offre
            job_experience_str = job_data.get('experience', '')
            
            # Si pas d'information sur l'expérience, score neutre
            if not job_experience_str:
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
            except:
                return 0.5
        
        # Récupérer l'expérience du candidat
        candidate_experience = cv_data.get('annees_experience', 0)
        
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
            # Expérience dans la fourchette ou légèrement supérieure - score optimal
            if candidate_experience <= job_max_exp:
                # Dans la fourchette exacte - score parfait
                return 1.0
            else:
                # Légèrement au-dessus, mais pas trop - score très bon
                return max(0.8, 1.0 - (candidate_experience - job_max_exp) / job_max_exp)
    
    def _calculate_candidate_soft_skills_score(self, 
                                            cv_data: Dict[str, Any], 
                                            job_data: Dict[str, Any]) -> float:
        """
        Calcule le score de matching des soft skills
        
        Args:
            cv_data: Données du CV
            job_data: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Extraire les soft skills du CV et du job
        cv_soft_skills = set(skill.lower() for skill in cv_data.get('soft_skills', []))
        
        # Vérifier si le job a des soft skills spécifiés
        if 'soft_skills' not in job_data:
            return 0.5  # Score neutre si pas d'information
        
        job_soft_skills = set(skill.lower() for skill in job_data.get('soft_skills', []))
        
        # Si pas de soft skills listés dans l'offre, retourner un score par défaut
        if not job_soft_skills:
            return 0.5
        
        # Calculer l'intersection des soft skills
        matching_skills = cv_soft_skills.intersection(job_soft_skills)
        
        # Calculer le score basé sur le pourcentage de soft skills requis que le candidat possède
        if len(job_soft_skills) == 0:
            return 0.5
        
        # Si le candidat n'a pas déclaré de soft skills mais que l'offre en demande
        if not cv_soft_skills:
            return 0.3  # Score par défaut plutôt bas mais pas nul
        
        # Calculer un score basé sur la correspondance
        match_ratio = len(matching_skills) / len(job_soft_skills)
        
        # Ajouter un bonus si le candidat a des soft skills supplémentaires valorisables
        additional_skills = cv_soft_skills - job_soft_skills
        if additional_skills:
            bonus = min(0.2, len(additional_skills) * 0.05)  # Max 20% de bonus
            match_ratio = min(1.0, match_ratio + bonus)
        
        return match_ratio
    
    def _calculate_candidate_culture_score(self, 
                                        questionnaire_data: Dict[str, Any], 
                                        job_data: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de la culture d'entreprise
        
        Args:
            questionnaire_data: Données du questionnaire du candidat
            job_data: Données de l'offre d'emploi
            
        Returns:
            Score entre 0 et 1
        """
        # Récupérer les données de culture d'entreprise
        job_culture = job_data.get('culture_entreprise', {})
        candidate_preferences = questionnaire_data.get('preferences_culture', {})
        
        # Si les données sont manquantes, retourner un score neutre
        if not job_culture or not candidate_preferences:
            return 0.5
        
        # Calculer le score sur plusieurs dimensions
        scores = []
        
        # Valeurs d'entreprise
        if 'valeurs' in job_culture and 'valeurs_importantes' in candidate_preferences:
            job_values = set(v.lower() for v in job_culture['valeurs'])
            candidate_values = set(v.lower() for v in candidate_preferences['valeurs_importantes'])
            
            if job_values and candidate_values:
                matching_values = job_values.intersection(candidate_values)
                values_score = len(matching_values) / max(len(job_values), len(candidate_values))
                scores.append(values_score)
        
        # Taille d'équipe
        if 'taille_equipe' in job_culture and 'taille_equipe_preferee' in candidate_preferences:
            job_size = job_culture['taille_equipe']
            preferred_size = candidate_preferences['taille_equipe_preferee']
            
            # Mappings pour la comparaison
            size_categories = {
                'petite': range(1, 10),
                'moyenne': range(10, 30),
                'grande': range(30, 100),
                'très grande': range(100, 1000)
            }
            
            # Convertir la taille numérique en catégorie
            job_size_category = None
            for category, size_range in size_categories.items():
                if job_size in size_range:
                    job_size_category = category
                    break
            
            if job_size_category and preferred_size:
                if job_size_category == preferred_size:
                    scores.append(1.0)
                elif (job_size_category == 'moyenne' and preferred_size == 'petite') or \
                     (job_size_category == 'petite' and preferred_size == 'moyenne') or \
                     (job_size_category == 'grande' and preferred_size == 'moyenne') or \
                     (job_size_category == 'moyenne' and preferred_size == 'grande'):
                    scores.append(0.7)  # Catégories adjacentes
                else:
                    scores.append(0.3)  # Catégories éloignées
        
        # Méthodologie de travail
        if 'methodologie' in job_culture and 'methodologie_preferee' in candidate_preferences:
            job_methodology = job_culture['methodologie'].lower()
            preferred_methodology = candidate_preferences['methodologie_preferee'].lower()
            
            if job_methodology and preferred_methodology:
                # Correspondance exacte
                if job_methodology == preferred_methodology:
                    scores.append(1.0)
                # Correspondances partielles (ex: Agile et Scrum)
                elif ('agile' in job_methodology and 'agile' in preferred_methodology) or \
                     ('scrum' in job_methodology and 'scrum' in preferred_methodology) or \
                     ('kanban' in job_methodology and 'kanban' in preferred_methodology):
                    scores.append(0.8)
                # Autres cas
                else:
                    scores.append(0.4)
        
        # Environnement de travail
        if 'environnement' in job_culture and 'environnement_prefere' in candidate_preferences:
            job_env = job_culture['environnement'].lower()
            preferred_env = candidate_preferences['environnement_prefere'].lower()
            
            if job_env and preferred_env:
                # Correspondance par mots-clés
                keywords_job = set(job_env.split())
                keywords_pref = set(preferred_env.split())
                
                matching_keywords = keywords_job.intersection(keywords_pref)
                if matching_keywords:
                    keyword_score = len(matching_keywords) / max(len(keywords_job), len(keywords_pref))
                    scores.append(keyword_score)
                else:
                    scores.append(0.3)
        
        # Si aucun critère n'a pu être comparé, retourner un score neutre
        if not scores:
            return 0.5
        
        # Moyenne des scores
        return sum(scores) / len(scores)

# Fonction pour obtenir les candidats les plus adaptés à une offre
def get_candidates_for_job(job_data: Dict[str, Any], 
                          candidates_data: List[Dict[str, Any]], 
                          company_preferences: Dict[str, Any] = None, 
                          limit: int = 10) -> List[Dict[str, Any]]:
    """
    Fonction pour obtenir les candidats les plus adaptés à une offre d'emploi
    
    Args:
        job_data: Données de l'offre d'emploi
        candidates_data: Liste des données des candidats
        company_preferences: Préférences de l'entreprise (optionnel)
        limit: Nombre maximum de candidats à retourner
        
    Returns:
        Liste des candidats les plus adaptés avec leurs scores
    """
    engine = BidirectionalMatchingEngine()
    engine.load_jobs_data({job_data['id']: job_data})
    engine.load_candidates_data(candidates_data)
    
    if company_preferences:
        engine.load_company_preferences(company_preferences)
    
    return engine.get_candidates_for_job(job_data['id'], limit)