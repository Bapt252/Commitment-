#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemple d'intégration du module de transport avec l'algorithme principal de matching
"""

import os
import logging
import json
from typing import Dict, List, Any
from dotenv import load_dotenv
from app.hybrid_maps_client import HybridGoogleMapsClient
from app.smartmatch_transport import CommuteMatchExtension

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedSmartMatcher:
    """
    Version améliorée du SmartMatcher avec intégration du transport
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialise le système de matching amélioré
        
        Args:
            config: Configuration du système (poids, seuils, etc.)
        """
        # Charger la configuration par défaut si non fournie
        self.config = config or {
            "weights": {
                "skills": 0.65,           # Poids des compétences dans le score final
                "transport": 0.25,        # Poids du transport dans le score final
                "cultural_fit": 0.10      # Poids de la compatibilité culturelle
            },
            "thresholds": {
                "max_commute_minutes": 60,  # Temps de trajet maximum acceptable par défaut
                "min_skills_score": 0.5,    # Score minimum de compétences
                "min_total_score": 0.6      # Score minimum total pour un match
            },
            "transport": {
                "preferred_mode": "transit",  # Mode de transport préféré par défaut
                "remote_bonus": 0.1,          # Bonus de score pour les emplois remote
                "hybrid_factor": 0.5          # Facteur pour les emplois hybrides
            }
        }
        
        # Initialiser le client Google Maps hybride adapté
        self.maps_client = HybridGoogleMapsClient()
        logger.info("Client Google Maps hybride adapté initialisé")
        
        # Initialiser l'extension de transport avec notre client
        self.transport_extension = CommuteMatchExtension(self.maps_client)
        logger.info("Extension de transport initialisée")
    
    def calculate_skills_score(self, candidate: Dict, job: Dict) -> float:
        """
        Calcule le score de compatibilité des compétences
        À remplacer par l'implémentation réelle du SmartMatcher
        
        Args:
            candidate: Informations sur le candidat
            job: Informations sur le poste
            
        Returns:
            Score de compatibilité des compétences (0-1)
        """
        # Exemple simple pour la démonstration
        # À remplacer par l'algorithme NLP réel
        
        # Récupérer les compétences
        candidate_skills = set(s.lower() for s in candidate.get("skills", []))
        job_skills = set(s.lower() for s in job.get("skills", []))
        
        # Si aucune compétence, score nul
        if not candidate_skills or not job_skills:
            return 0.0
        
        # Calculer les correspondances
        matched_skills = candidate_skills.intersection(job_skills)
        match_ratio = len(matched_skills) / len(job_skills) if job_skills else 0
        
        return min(match_ratio, 1.0)  # Cap à 1.0
    
    def calculate_match_score(self, candidate: Dict, job: Dict) -> Dict:
        """
        Calcule le score complet de matching entre un candidat et un poste
        
        Args:
            candidate: Informations sur le candidat
            job: Informations sur le poste
            
        Returns:
            Dictionnaire contenant le score final et les détails
        """
        # 1. Calcul du score de compétences
        skills_score = self.calculate_skills_score(candidate, job)
        
        # 2. Calcul du score de transport
        transport_score = self.transport_extension.calculate_commute_score(
            candidate_address=candidate.get("address", ""),
            job_address=job.get("address", ""),
            is_remote=job.get("is_remote", False),
            is_hybrid=job.get("is_hybrid", False),
            max_commute_minutes=candidate.get("max_commute_minutes", 
                                             self.config["thresholds"]["max_commute_minutes"]),
            preferred_mode=candidate.get("preferred_mode", 
                                        self.config["transport"]["preferred_mode"])
        )
        
        # 3. Analyse détaillée du transport
        transport_analysis = self.transport_extension.analyze_commute_compatibility(
            candidate_address=candidate.get("address", ""),
            job_address=job.get("address", ""),
            candidate_preferences={
                "max_commute_minutes": candidate.get("max_commute_minutes", 
                                                   self.config["thresholds"]["max_commute_minutes"]),
                "preferred_mode": candidate.get("preferred_mode", 
                                               self.config["transport"]["preferred_mode"]),
                "accepts_remote": candidate.get("accepts_remote", True)
            },
            job_requirements={
                "is_remote": job.get("is_remote", False),
                "is_hybrid": job.get("is_hybrid", False),
                "days_in_office": job.get("days_in_office", 5)
            }
        )
        
        # 4. Calcul du score culturel (exemple simple)
        cultural_score = 0.7  # À remplacer par un calcul réel
        
        # 5. Calcul du score final pondéré
        weights = self.config["weights"]
        final_score = (
            skills_score * weights["skills"] + 
            transport_score * weights["transport"] + 
            cultural_score * weights["cultural_fit"]
        )
        
        # 6. Préparer les résultats détaillés
        match_result = {
            "final_score": round(final_score, 2),
            "skills_score": round(skills_score, 2),
            "transport_score": round(transport_score, 2),
            "cultural_score": round(cultural_score, 2),
            "transport_details": transport_analysis,
            "is_match": final_score >= self.config["thresholds"]["min_total_score"],
            "explanation": self._generate_explanation(skills_score, transport_score, 
                                                     cultural_score, transport_analysis)
        }
        
        return match_result
    
    def _generate_explanation(self, skills_score: float, transport_score: float, 
                             cultural_score: float, transport_analysis: Dict) -> str:
        """Génère une explication textuelle du score de matching"""
        
        # Évaluation des compétences
        if skills_score > 0.8:
            skills_text = "correspondance excellente des compétences"
        elif skills_score > 0.6:
            skills_text = "bonne correspondance des compétences"
        elif skills_score > 0.4:
            skills_text = "correspondance moyenne des compétences"
        else:
            skills_text = "correspondance faible des compétences"
        
        # Évaluation du transport
        if "explanation" in transport_analysis:
            transport_text = transport_analysis["explanation"]
        else:
            if transport_score > 0.8:
                transport_text = "situation géographique idéale"
            elif transport_score > 0.6:
                transport_text = "bon temps de trajet"
            elif transport_score > 0.4:
                transport_text = "temps de trajet acceptable"
            else:
                transport_text = "temps de trajet problématique"
        
        # Explication globale
        return f"Ce matching présente une {skills_text} et une {transport_text}."
    
    def find_matches(self, candidates: List[Dict], jobs: List[Dict], 
                    top_n: int = 10) -> Dict[str, List[Dict]]:
        """
        Trouve les meilleurs matchings entre candidats et emplois
        
        Args:
            candidates: Liste des candidats
            jobs: Liste des emplois
            top_n: Nombre de meilleurs matchings à retourner par candidat/emploi
            
        Returns:
            Dictionnaire contenant les matchings par candidat et par emploi
        """
        # Initialiser les résultats
        results = {
            "by_candidate": {},  # candidat -> liste d'emplois
            "by_job": {}         # emploi -> liste de candidats
        }
        
        # Pour chaque candidat, trouver les meilleurs emplois
        for candidate in candidates:
            candidate_id = candidate.get("id", "unknown")
            candidate_matches = []
            
            for job in jobs:
                job_id = job.get("id", "unknown")
                
                # Calculer le score de matching
                match_result = self.calculate_match_score(candidate, job)
                match_result["candidate_id"] = candidate_id
                match_result["job_id"] = job_id
                
                # Ajouter aux résultats si c'est un match
                if match_result["is_match"]:
                    candidate_matches.append(match_result)
            
            # Trier par score décroissant et garder les top_n
            candidate_matches.sort(key=lambda x: x["final_score"], reverse=True)
            results["by_candidate"][candidate_id] = candidate_matches[:top_n]
        
        # Pour chaque emploi, trouver les meilleurs candidats
        for job in jobs:
            job_id = job.get("id", "unknown")
            job_matches = []
            
            for candidate in candidates:
                candidate_id = candidate.get("id", "unknown")
                
                # Calculer le score de matching
                match_result = self.calculate_match_score(candidate, job)
                match_result["candidate_id"] = candidate_id
                match_result["job_id"] = job_id
                
                # Ajouter aux résultats si c'est un match
                if match_result["is_match"]:
                    job_matches.append(match_result)
            
            # Trier par score décroissant et garder les top_n
            job_matches.sort(key=lambda x: x["final_score"], reverse=True)
            results["by_job"][job_id] = job_matches[:top_n]
        
        return results

# Exemple d'utilisation
def run_example():
    """Exécute un exemple de matching avec des données de test"""
    
    # Charger les variables d'environnement
    load_dotenv()
    
    logger.info("=== EXEMPLE D'INTÉGRATION DU MODULE DE TRANSPORT AVEC LE SMARTMATCHER ===")
    
    # Initialiser le matcher
    matcher = EnhancedSmartMatcher()
    
    # Données de test
    candidates = [
        {
            "id": "c1",
            "name": "Jean Dupont",
            "address": "20 Rue de la Paix, 75002 Paris, France",
            "skills": ["Python", "Django", "React", "SQL"],
            "max_commute_minutes": 45,
            "preferred_mode": "transit",
            "accepts_remote": True
        },
        {
            "id": "c2",
            "name": "Marie Martin",
            "address": "10 Place Bellecour, 69002 Lyon, France",
            "skills": ["Java", "Spring", "Angular", "PostgreSQL"],
            "max_commute_minutes": 30,
            "preferred_mode": "bicycling",
            "accepts_remote": False
        }
    ]
    
    jobs = [
        {
            "id": "j1",
            "title": "Développeur Full Stack",
            "company": "TechCorp",
            "address": "Tour Montparnasse, 75015 Paris, France",
            "skills": ["Python", "Django", "React", "MongoDB"],
            "is_remote": False,
            "is_hybrid": True,
            "days_in_office": 3
        },
        {
            "id": "j2",
            "title": "Ingénieur Backend",
            "company": "DataSoft",
            "address": "15 Quai des Bateliers, 67000 Strasbourg, France",
            "skills": ["Java", "Spring", "SQL", "Kafka"],
            "is_remote": True,
            "is_hybrid": False,
            "days_in_office": 0
        }
    ]
    
    # Calculer un match spécifique
    logger.info("Calcul d'un matching spécifique:")
    match = matcher.calculate_match_score(candidates[0], jobs[0])
    logger.info(f"Score final: {match['final_score']}")
    logger.info(f"Score de compétences: {match['skills_score']}")
    logger.info(f"Score de transport: {match['transport_score']}")
    logger.info(f"Explication: {match['explanation']}")
    
    # Trouver tous les matchings
    logger.info("\nCalcul de tous les matchings:")
    all_matches = matcher.find_matches(candidates, jobs)
    
    # Afficher les matchings par candidat
    logger.info("\nMatchings par candidat:")
    for candidate_id, matches in all_matches["by_candidate"].items():
        logger.info(f"Candidat {candidate_id}:")
        for i, match in enumerate(matches, 1):
            logger.info(f"  {i}. Job {match['job_id']} - Score: {match['final_score']} - {match['explanation']}")
    
    # Afficher les matchings par emploi
    logger.info("\nMatchings par emploi:")
    for job_id, matches in all_matches["by_job"].items():
        logger.info(f"Emploi {job_id}:")
        for i, match in enumerate(matches, 1):
            logger.info(f"  {i}. Candidat {match['candidate_id']} - Score: {match['final_score']} - {match['explanation']}")
    
    # Afficher les statistiques d'utilisation de l'API
    logger.info("\nStatistiques d'utilisation de l'API:")
    if hasattr(matcher.maps_client, 'stats'):
        stats = matcher.maps_client.stats
        for key, value in stats.items():
            logger.info(f"  - {key}: {value}")
    
    logger.info("=== EXEMPLE TERMINÉ ===")

if __name__ == "__main__":
    run_example()
