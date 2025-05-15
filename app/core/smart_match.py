#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Moteur de matching SmartMatch pour comparer candidats et entreprises."""

import logging
from typing import Dict, List, Any, Tuple

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartMatch")

class SmartMatcher:
    """
    Moteur de matching qui évalue la correspondance entre candidats et entreprises
    en fonction de différents critères.
    """
    
    def __init__(self):
        """Initialise le moteur de matching."""
        logger.info("Initialisation du moteur SmartMatch")
        
        # Poids des différents critères (à ajuster selon les besoins)
        self.weights = {
            "skills": 0.5,        # Compétences
            "experience": 0.2,    # Expérience professionnelle
            "location": 0.15,     # Emplacement géographique
            "remote": 0.1,        # Politique de travail à distance
            "salary": 0.05        # Attentes salariales
        }
    
    def calculate_match(self, candidate: Dict[str, Any], 
                        company: Dict[str, Any]) -> Tuple[float, Dict[str, Any]]:
        """
        Calcule le score de matching entre un candidat et une entreprise.
        
        Args:
            candidate (Dict): Profil du candidat
            company (Dict): Profil de l'entreprise/poste
            
        Returns:
            Tuple[float, Dict]: Score de matching (0-100) et détails
        """
        logger.debug(f"Calcul du matching entre candidat {candidate.get('id')} et entreprise {company.get('id')}")
        
        # Calcul des scores par critère
        skills_score = self._calculate_skills_match(candidate, company)
        experience_score = self._calculate_experience_match(candidate, company)
        location_score = self._calculate_location_match(candidate, company)
        remote_score = self._calculate_remote_match(candidate, company)
        salary_score = self._calculate_salary_match(candidate, company)
        
        # Calcul du score global
        total_score = (
            skills_score * self.weights["skills"] +
            experience_score * self.weights["experience"] +
            location_score * self.weights["location"] +
            remote_score * self.weights["remote"] +
            salary_score * self.weights["salary"]
        ) * 100  # Conversion en pourcentage
        
        # Arrondir à 2 décimales
        total_score = round(total_score, 2)
        
        # Détails du matching
        details = {
            "skills": {
                "score": skills_score,
                "weight": self.weights["skills"],
                "details": self._get_skills_details(candidate, company)
            },
            "experience": {
                "score": experience_score,
                "weight": self.weights["experience"]
            },
            "location": {
                "score": location_score,
                "weight": self.weights["location"]
            },
            "remote": {
                "score": remote_score,
                "weight": self.weights["remote"]
            },
            "salary": {
                "score": salary_score,
                "weight": self.weights["salary"]
            }
        }
        
        logger.debug(f"Score de matching: {total_score}%")
        return total_score, details
    
    def match(self, candidates: List[Dict[str, Any]], 
              companies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Effectue le matching entre plusieurs candidats et entreprises.
        
        Args:
            candidates (List[Dict]): Liste de profils de candidats
            companies (List[Dict]): Liste de profils d'entreprises/postes
            
        Returns:
            List[Dict]: Résultats de matching triés par score
        """
        logger.info(f"Matching de {len(candidates)} candidats avec {len(companies)} entreprises")
        
        results = []
        
        for candidate in candidates:
            for company in companies:
                score, details = self.calculate_match(candidate, company)
                
                # Créer l'objet de résultat
                result = {
                    "candidate_id": candidate["id"],
                    "candidate_name": candidate.get("name", ""),
                    "company_id": company["id"],
                    "company_name": company.get("name", ""),
                    "score": score,
                    "details": details
                }
                
                results.append(result)
        
        # Trier les résultats par score décroissant
        results.sort(key=lambda x: x["score"], reverse=True)
        
        logger.info(f"{len(results)} matchings calculés")
        return results
    
    def _calculate_skills_match(self, candidate: Dict[str, Any], 
                               company: Dict[str, Any]) -> float:
        """
        Calcule le score de matching des compétences.
        
        Args:
            candidate (Dict): Profil du candidat
            company (Dict): Profil de l'entreprise/poste
            
        Returns:
            float: Score de matching des compétences (0-1)
        """
        candidate_skills = set(s.lower() for s in candidate.get("skills", []))
        required_skills = set(s.lower() for s in company.get("required_skills", []))
        
        if not required_skills:  # Aucune compétence requise
            return 1.0
        
        # Nombre de compétences requises que le candidat possède
        matching_skills = candidate_skills.intersection(required_skills)
        
        # Calcul du score (nombre de compétences correspondantes / nombre de compétences requises)
        score = len(matching_skills) / len(required_skills)
        
        return score
    
    def _get_skills_details(self, candidate: Dict[str, Any], 
                           company: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fournit des détails sur le matching des compétences.
        
        Args:
            candidate (Dict): Profil du candidat
            company (Dict): Profil de l'entreprise/poste
            
        Returns:
            Dict: Détails du matching des compétences
        """
        candidate_skills = set(s.lower() for s in candidate.get("skills", []))
        required_skills = set(s.lower() for s in company.get("required_skills", []))
        
        matching_skills = candidate_skills.intersection(required_skills)
        missing_skills = required_skills - candidate_skills
        
        return {
            "matching_skills": list(matching_skills),
            "missing_skills": list(missing_skills),
            "total_required": len(required_skills),
            "total_matching": len(matching_skills)
        }
    
    def _calculate_experience_match(self, candidate: Dict[str, Any], 
                                   company: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de l'expérience.
        
        Args:
            candidate (Dict): Profil du candidat
            company (Dict): Profil de l'entreprise/poste
            
        Returns:
            float: Score de matching de l'expérience (0-1)
        """
        candidate_experience = candidate.get("experience", 0)
        required_experience = company.get("required_experience", 0)
        
        if required_experience == 0:  # Aucune expérience requise
            return 1.0
        
        # Si le candidat a plus d'expérience que nécessaire
        if candidate_experience >= required_experience:
            return 1.0
        
        # Sinon, calcul du ratio (avec un minimum de 0)
        return max(0, candidate_experience / required_experience)
    
    def _calculate_location_match(self, candidate: Dict[str, Any], 
                                 company: Dict[str, Any]) -> float:
        """
        Calcule le score de matching de la localisation.
        Version simplifiée basée sur la correspondance exacte des villes.
        
        Args:
            candidate (Dict): Profil du candidat
            company (Dict): Profil de l'entreprise/poste
            
        Returns:
            float: Score de matching de la localisation (0-1)
        """
        # Version simplifiée - à remplacer par un calcul de distance réel
        candidate_location = candidate.get("location", "").lower()
        company_location = company.get("location", "").lower()
        
        # Si l'un des deux emplacements n'est pas spécifié
        if not candidate_location or not company_location:
            return 0.5  # Score neutre
        
        # Si les emplacements correspondent exactement
        if candidate_location == company_location:
            return 1.0
        
        # Vérifier si la ville correspond (première partie de l'emplacement)
        candidate_city = candidate_location.split(",")[0].strip()
        company_city = company_location.split(",")[0].strip()
        
        if candidate_city == company_city:
            return 0.9  # Même ville, peut-être un quartier différent
        
        # Score par défaut pour des emplacements différents
        return 0.3
    
    def _calculate_remote_match(self, candidate: Dict[str, Any], 
                               company: Dict[str, Any]) -> float:
        """
        Calcule le score de matching des préférences de travail à distance.
        
        Args:
            candidate (Dict): Profil du candidat
            company (Dict): Profil de l'entreprise/poste
            
        Returns:
            float: Score de matching du travail à distance (0-1)
        """
        candidate_remote = candidate.get("remote_preference", "hybrid")
        company_remote = company.get("remote_policy", "hybrid")
        
        # Correspondance parfaite
        if candidate_remote == company_remote:
            return 1.0
        
        # Matrice de compatibilité
        compatibility = {
            # candidat: {politique entreprise: score}
            "full": {"hybrid": 0.7, "office_only": 0.2},
            "hybrid": {"full": 0.8, "office_only": 0.6},
            "office": {"full": 0.3, "hybrid": 0.7}
        }
        
        # Obtenir le score de compatibilité ou 0.5 par défaut
        return compatibility.get(candidate_remote, {}).get(company_remote, 0.5)
    
    def _calculate_salary_match(self, candidate: Dict[str, Any], 
                               company: Dict[str, Any]) -> float:
        """
        Calcule le score de matching des attentes salariales.
        
        Args:
            candidate (Dict): Profil du candidat
            company (Dict): Profil de l'entreprise/poste
            
        Returns:
            float: Score de matching du salaire (0-1)
        """
        candidate_salary = candidate.get("salary_expectation", 0)
        company_salary_range = company.get("salary_range", {"min": 0, "max": 0})
        
        min_salary = company_salary_range.get("min", 0)
        max_salary = company_salary_range.get("max", 0)
        
        # Si l'une des parties n'a pas spécifié de salaire
        if candidate_salary == 0 or (min_salary == 0 and max_salary == 0):
            return 0.5  # Score neutre
        
        # Si le salaire attendu est dans la fourchette
        if min_salary <= candidate_salary <= max_salary:
            return 1.0
        
        # Si le salaire attendu est inférieur au minimum
        if candidate_salary < min_salary:
            # Calculer le ratio (avec un minimum de 0.5 pour ne pas trop pénaliser)
            return max(0.5, candidate_salary / min_salary)
        
        # Si le salaire attendu est supérieur au maximum
        return max(0.2, max_salary / candidate_salary)
