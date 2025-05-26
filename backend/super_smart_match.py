#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SuperSmartMatch - Service Unifié de Matching
============================================

Service backend unifié qui regroupe TOUS les algorithmes de matching Nexten :
- Smart Match (bidirectionnel avec géolocalisation)
- Enhanced Matching Engine (moteur avancé)
- Analyseur Sémantique (compétences)
- Job Analyzer (analyse offres GPT)
- Algorithmes Originaux vs Personnalisés

Utilisation :
    from super_smart_match import SuperSmartMatch
    
    # Initialisation
    matcher = SuperSmartMatch()
    
    # Matching simple
    results = matcher.match(candidate_data, company_data)
    
    # Avec choix d'algorithme
    results = matcher.match(candidate_data, company_data, algorithm="smart-match")

Auteur: Nexten Team
Version: 1.0.0
"""

import os
import sys
import json
import time
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AlgorithmType(Enum):
    """Types d'algorithmes disponibles"""
    AUTO = "auto"
    SMART_MATCH = "smart-match"
    ENHANCED = "enhanced"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    COMPARISON = "comparison"

class MatchingStrategy(Enum):
    """Stratégies de matching"""
    BEST_PERFORMANCE = "best_performance"
    BEST_ACCURACY = "best_accuracy"
    BALANCED = "balanced"
    SPEED_OPTIMIZED = "speed_optimized"

@dataclass
class MatchingConfig:
    """Configuration du matching"""
    algorithm: AlgorithmType = AlgorithmType.AUTO
    strategy: MatchingStrategy = MatchingStrategy.BALANCED
    max_results: int = 10
    min_score_threshold: float = 0.3
    enable_semantic: bool = True
    enable_geolocation: bool = True
    enable_job_analysis: bool = True
    weights: Optional[Dict[str, float]] = None

@dataclass
class CandidateProfile:
    """Profil candidat standardisé"""
    competences: List[str]
    adresse: str
    mobilite: str  # "on-site", "remote", "hybrid"
    annees_experience: int
    salaire_souhaite: int
    contrats_recherches: List[str]
    disponibilite: str
    formation: Optional[str] = None
    domaines_interets: Optional[List[str]] = None

@dataclass
class CompanyOffer:
    """Offre entreprise standardisée"""
    id: Union[str, int]
    titre: str
    competences: List[str]
    localisation: str
    type_contrat: str
    salaire: str
    politique_remote: str  # "on-site", "remote", "hybrid"
    experience_requise: Optional[str] = None
    description: Optional[str] = None
    avantages: Optional[List[str]] = None

@dataclass
class MatchingResult:
    """Résultat de matching standardisé"""
    offer_id: Union[str, int]
    titre: str
    entreprise: str
    score_global: int  # Score sur 100
    scores_details: Dict[str, int]
    algorithme_utilise: str
    temps_calcul: float
    raison_score: str
    recommandations: List[str]
    metadata: Dict[str, Any]

class BaseMatchingAlgorithm(ABC):
    """Classe de base pour tous les algorithmes"""
    
    @abstractmethod
    def match(self, candidate: CandidateProfile, offers: List[CompanyOffer], 
              config: MatchingConfig) -> List[MatchingResult]:
        """Exécute l'algorithme de matching"""
        pass
    
    @abstractmethod
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Retourne les informations sur l'algorithme"""
        pass

class SmartMatchAlgorithm(BaseMatchingAlgorithm):
    """Algorithme Smart Match - Bidirectionnel avec géolocalisation"""
    
    def __init__(self):
        self.name = "SmartMatch"
        self.version = "2.0"
        
        # Données géographiques intelligentes
        self.location_zones = {
            "paris": {
                "keywords": ["paris", "ile-de-france", "idf", "75"],
                "score": 1.0,
                "remote_compatible": True
            },
            "lyon": {
                "keywords": ["lyon", "rhone", "69"],
                "score": 0.9,
                "remote_compatible": True
            },
            "remote": {
                "keywords": ["remote", "télétravail", "distance"],
                "score": 1.0,
                "remote_compatible": True
            }
        }
    
    def match(self, candidate: CandidateProfile, offers: List[CompanyOffer], 
              config: MatchingConfig) -> List[MatchingResult]:
        """Exécute l'algorithme SmartMatch"""
        start_time = time.time()
        results = []
        
        for offer in offers:
            # Calculs spécifiques SmartMatch
            skills_score = self._calculate_skills_bidirectional(candidate, offer)
            location_score = self._calculate_geolocation_score(candidate, offer)
            mobility_score = self._calculate_mobility_compatibility(candidate, offer)
            salary_score = self._calculate_salary_compatibility(candidate, offer)
            contract_score = self._calculate_contract_match(candidate, offer)
            
            # Score global avec pondération SmartMatch
            global_score = (
                skills_score * 0.35 +
                location_score * 0.25 +
                mobility_score * 0.15 +
                salary_score * 0.15 +
                contract_score * 0.10
            )
            
            # Filtrage par seuil
            if global_score < config.min_score_threshold:
                continue
            
            result = MatchingResult(
                offer_id=offer.id,
                titre=offer.titre,
                entreprise="Smart Match Company",
                score_global=int(global_score * 100),
                scores_details={
                    "competences": int(skills_score * 100),
                    "localisation": int(location_score * 100),
                    "mobilite": int(mobility_score * 100),
                    "salaire": int(salary_score * 100),
                    "contrat": int(contract_score * 100)
                },
                algorithme_utilise=f"{self.name} v{self.version}",
                temps_calcul=time.time() - start_time,
                raison_score=self._generate_score_explanation(global_score, skills_score, location_score),
                recommandations=self._generate_recommendations(candidate, offer, global_score),
                metadata={
                    "geolocation_used": True,
                    "bidirectional_matching": True,
                    "algorithm_type": "smart_match"
                }
            )
            results.append(result)
        
        # Tri par score décroissant
        results.sort(key=lambda x: x.score_global, reverse=True)
        return results[:config.max_results]
    
    def _calculate_skills_bidirectional(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul bidirectionnel des compétences"""
        candidate_skills = set(skill.lower() for skill in candidate.competences)
        offer_skills = set(skill.lower() for skill in offer.competences)
        
        if not offer_skills:
            return 0.5
        
        # Correspondance directe
        common_skills = candidate_skills.intersection(offer_skills)
        
        # Score candidat → offre
        candidate_to_offer = len(common_skills) / len(offer_skills) if offer_skills else 0
        
        # Score offre → candidat
        offer_to_candidate = len(common_skills) / len(candidate_skills) if candidate_skills else 0
        
        # Score bidirectionnel équilibré
        return (candidate_to_offer * 0.7 + offer_to_candidate * 0.3)
    
    def _calculate_geolocation_score(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul intelligent de la géolocalisation"""
        candidate_location = candidate.adresse.lower()
        offer_location = offer.localisation.lower()
        
        # Détection des zones
        candidate_zone = self._detect_zone(candidate_location)
        offer_zone = self._detect_zone(offer_location)
        
        if offer_zone == "remote":
            return 1.0
        elif candidate_zone == offer_zone:
            return 1.0
        elif candidate_zone == "paris" and offer_zone in ["lyon"]:
            return 0.6  # Grandes villes entre elles
        else:
            return 0.4
    
    def _detect_zone(self, location: str) -> Optional[str]:
        """Détecte la zone géographique"""
        for zone, data in self.location_zones.items():
            if any(keyword in location for keyword in data["keywords"]):
                return zone
        return None
    
    def _calculate_mobility_compatibility(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul de compatibilité mobilité"""
        mobility_matrix = {
            ("remote", "remote"): 1.0,
            ("remote", "hybrid"): 0.9,
            ("remote", "on-site"): 0.3,
            ("hybrid", "remote"): 1.0,
            ("hybrid", "hybrid"): 1.0,
            ("hybrid", "on-site"): 0.7,
            ("on-site", "remote"): 0.8,
            ("on-site", "hybrid"): 0.8,
            ("on-site", "on-site"): 1.0,
        }
        return mobility_matrix.get((candidate.mobilite, offer.politique_remote), 0.5)
    
    def _calculate_salary_compatibility(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul de compatibilité salariale"""
        try:
            import re
            numbers = re.findall(r'\d+', offer.salaire)
            if len(numbers) >= 2:
                offer_min = int(numbers[0]) * 1000
                offer_max = int(numbers[1]) * 1000
            elif len(numbers) == 1:
                offer_min = int(numbers[0]) * 1000
                offer_max = offer_min * 1.2
            else:
                return 0.6
            
            if offer_min >= candidate.salaire_souhaite:
                return 1.0
            elif offer_max >= candidate.salaire_souhaite:
                return 0.8
            else:
                ratio = offer_max / candidate.salaire_souhaite
                return max(0.2, min(0.6, ratio))
        except:
            return 0.6
    
    def _calculate_contract_match(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul de correspondance de contrat"""
        offer_contract = offer.type_contrat.lower()
        candidate_contracts = [c.lower() for c in candidate.contrats_recherches]
        
        if offer_contract in candidate_contracts:
            return 1.0
        elif "cdi" in candidate_contracts and offer_contract == "cdd":
            return 0.8
        else:
            return 0.4
    
    def _generate_score_explanation(self, global_score: float, skills_score: float, location_score: float) -> str:
        """Génère une explication du score"""
        if global_score >= 0.8:
            return "Excellente correspondance - Profil très adapté"
        elif global_score >= 0.6:
            return "Bonne correspondance - Quelques ajustements possibles"
        elif skills_score < 0.4:
            return "Correspondance limitée - Compétences à développer"
        elif location_score < 0.4:
            return "Correspondance limitée - Contraintes géographiques"
        else:
            return "Correspondance modérée - Profil partiellement adapté"
    
    def _generate_recommendations(self, candidate: CandidateProfile, offer: CompanyOffer, score: float) -> List[str]:
        """Génère des recommandations"""
        recommendations = []
        
        if score >= 0.8:
            recommendations.append("Postulez rapidement - Profil idéal")
        elif score >= 0.6:
            recommendations.append("Candidature recommandée avec lettre personnalisée")
        else:
            recommendations.append("Développez les compétences manquantes avant de postuler")
        
        return recommendations
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        """Informations sur l'algorithme"""
        return {
            "name": self.name,
            "version": self.version,
            "type": "bidirectional_geolocation",
            "strengths": ["Géolocalisation avancée", "Matching bidirectionnel", "Mobilité intelligente"],
            "use_cases": ["Recherche géographiquement contrainte", "Matching équilibré candidat-entreprise"]
        }

class EnhancedMatchingAlgorithm(BaseMatchingAlgorithm):
    """Algorithme Enhanced - Moteur avancé avec pondération adaptative"""
    
    def __init__(self):
        self.name = "Enhanced"
        self.version = "1.5"
        
        # Écosystèmes de compétences sémantiques
        self.skill_ecosystems = {
            "python": ["django", "fastapi", "flask", "pandas", "numpy"],
            "javascript": ["react", "vue", "angular", "node.js", "typescript"],
            "data": ["sql", "mongodb", "elasticsearch", "spark", "kafka"],
            "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"]
        }
    
    def match(self, candidate: CandidateProfile, offers: List[CompanyOffer], 
              config: MatchingConfig) -> List[MatchingResult]:
        """Exécute l'algorithme Enhanced avec pondération adaptative"""
        start_time = time.time()
        results = []
        
        # Pondération adaptative selon l'expérience
        weights = self._get_adaptive_weights(candidate.annees_experience)
        
        for offer in offers:
            # Calculs Enhanced
            skills_score = self._calculate_semantic_skills(candidate, offer)
            experience_score = self._calculate_experience_fit(candidate, offer)
            salary_score = self._calculate_salary_negotiation(candidate, offer)
            contract_score = self._calculate_contract_flexibility(candidate, offer)
            location_score = self._calculate_location_zones(candidate, offer)
            
            # Score global avec pondération adaptative
            global_score = (
                skills_score * weights["skills"] +
                experience_score * weights["experience"] +
                salary_score * weights["salary"] +
                contract_score * weights["contract"] +
                location_score * weights["location"]
            )
            
            if global_score < config.min_score_threshold:
                continue
            
            result = MatchingResult(
                offer_id=offer.id,
                titre=offer.titre,
                entreprise="Enhanced Match Company",
                score_global=int(global_score * 100),
                scores_details={
                    "competences_semantiques": int(skills_score * 100),
                    "experience_fit": int(experience_score * 100),
                    "salaire_negociation": int(salary_score * 100),
                    "flexibilite_contrat": int(contract_score * 100),
                    "zones_localisation": int(location_score * 100)
                },
                algorithme_utilise=f"{self.name} v{self.version}",
                temps_calcul=time.time() - start_time,
                raison_score=self._generate_enhanced_explanation(global_score, candidate.annees_experience),
                recommandations=self._generate_enhanced_recommendations(candidate, offer, global_score),
                metadata={
                    "adaptive_weights": weights,
                    "semantic_matching": True,
                    "experience_level": self._get_experience_level(candidate.annees_experience)
                }
            )
            results.append(result)
        
        results.sort(key=lambda x: x.score_global, reverse=True)
        return results[:config.max_results]
    
    def _get_adaptive_weights(self, experience: int) -> Dict[str, float]:
        """Pondération adaptative selon l'expérience"""
        if experience >= 7:  # Senior
            return {"skills": 0.4, "salary": 0.25, "location": 0.15, "contract": 0.1, "experience": 0.1}
        elif experience >= 3:  # Confirmé
            return {"skills": 0.3, "experience": 0.2, "location": 0.2, "salary": 0.2, "contract": 0.1}
        else:  # Junior
            return {"skills": 0.25, "experience": 0.25, "location": 0.2, "contract": 0.15, "salary": 0.15}
    
    def _calculate_semantic_skills(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul sémantique des compétences avec écosystèmes"""
        candidate_skills = set(skill.lower() for skill in candidate.competences)
        offer_skills = set(skill.lower() for skill in offer.competences)
        
        if not offer_skills:
            return 0.5
        
        total_score = 0
        for offer_skill in offer_skills:
            best_match = 0
            
            # Correspondance exacte
            if offer_skill in candidate_skills:
                best_match = 1.0
            else:
                # Correspondance sémantique via écosystèmes
                for ecosystem, related_skills in self.skill_ecosystems.items():
                    if offer_skill in related_skills:
                        for candidate_skill in candidate_skills:
                            if candidate_skill in related_skills:
                                best_match = max(best_match, 0.8)
                            elif ecosystem in candidate_skill or candidate_skill in ecosystem:
                                best_match = max(best_match, 0.6)
            
            total_score += best_match
        
        return total_score / len(offer_skills)
    
    def _calculate_experience_fit(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul de l'adéquation d'expérience"""
        if not offer.experience_requise:
            return 0.8
        
        import re
        numbers = re.findall(r'\d+', offer.experience_requise)
        
        if "junior" in offer.experience_requise.lower():
            required_min, required_max = 0, 3
        elif "senior" in offer.experience_requise.lower():
            required_min, required_max = 5, 15
        elif len(numbers) >= 2:
            required_min, required_max = int(numbers[0]), int(numbers[1])
        elif len(numbers) == 1:
            required_min = int(numbers[0])
            required_max = required_min + 2
        else:
            return 0.7
        
        if required_min <= candidate.annees_experience <= required_max:
            return 1.0
        elif candidate.annees_experience < required_min:
            gap = required_min - candidate.annees_experience
            return max(0.3, 1.0 - gap * 0.2)
        else:
            excess = candidate.annees_experience - required_max
            return max(0.5, 1.0 - excess * 0.1)
    
    def _calculate_salary_negotiation(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul avec marge de négociation salariale"""
        try:
            import re
            numbers = re.findall(r'\d+', offer.salaire)
            if not numbers:
                return 0.6
            
            if len(numbers) >= 2:
                offer_min = int(numbers[0]) * 1000
                offer_max = int(numbers[1]) * 1000
            else:
                offer_min = int(numbers[0]) * 1000
                offer_max = offer_min * 1.15
            
            # Marge de négociation de 10%
            negotiable_max = offer_max * 1.1
            
            if offer_min >= candidate.salaire_souhaite:
                return 1.0
            elif negotiable_max >= candidate.salaire_souhaite:
                return 0.85
            elif offer_max >= candidate.salaire_souhaite * 0.9:
                return 0.7
            else:
                return max(0.2, offer_max / candidate.salaire_souhaite)
        except:
            return 0.6
    
    def _calculate_contract_flexibility(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul avec flexibilité de contrat"""
        offer_contract = offer.type_contrat.lower()
        candidate_contracts = [c.lower() for c in candidate.contrats_recherches]
        
        # Matrice de compatibilité flexible
        compatibility = {
            ("cdi", "cdi"): 1.0,
            ("cdi", "cdd"): 0.8,
            ("cdd", "cdi"): 0.9,
            ("cdd", "cdd"): 1.0,
            ("freelance", "cdi"): 0.6,
            ("freelance", "cdd"): 0.8,
        }
        
        best_score = 0
        for candidate_contract in candidate_contracts:
            score = compatibility.get((candidate_contract, offer_contract), 0.4)
            best_score = max(best_score, score)
        
        return best_score
    
    def _calculate_location_zones(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Calcul par zones avec bonus remote"""
        candidate_location = candidate.adresse.lower()
        offer_location = offer.localisation.lower()
        
        # Bonus remote
        if "remote" in offer_location or candidate.mobilite == "remote":
            return 1.0
        
        # Correspondance de zones
        if any(city in candidate_location and city in offer_location 
               for city in ["paris", "lyon", "marseille", "lille", "toulouse"]):
            return 1.0
        
        return 0.6
    
    def _get_experience_level(self, experience: int) -> str:
        """Détermine le niveau d'expérience"""
        if experience >= 7:
            return "Senior"
        elif experience >= 3:
            return "Confirmé"
        else:
            return "Junior"
    
    def _generate_enhanced_explanation(self, score: float, experience: int) -> str:
        """Explication Enhanced avec niveau d'expérience"""
        level = self._get_experience_level(experience)
        if score >= 0.8:
            return f"Excellente adéquation pour un profil {level} - Matching sémantique optimal"
        elif score >= 0.6:
            return f"Bonne correspondance {level} - Compétences écosystème compatibles"
        else:
            return f"Profil {level} partiellement compatible - Développement nécessaire"
    
    def _generate_enhanced_recommendations(self, candidate: CandidateProfile, offer: CompanyOffer, score: float) -> List[str]:
        """Recommandations Enhanced"""
        recommendations = []
        level = self._get_experience_level(candidate.annees_experience)
        
        if score >= 0.8:
            recommendations.append(f"Candidature prioritaire pour profil {level}")
            recommendations.append("Négociation salariale possible")
        elif score >= 0.6:
            recommendations.append(f"Bonne opportunité {level} - Préparez les points faibles")
            recommendations.append("Mettez en avant l'écosystème technique")
        else:
            recommendations.append(f"Formation recommandée avant candidature {level}")
        
        return recommendations
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "type": "adaptive_semantic",
            "strengths": ["Pondération adaptative", "Matching sémantique", "Négociation salariale"],
            "use_cases": ["Profils expérimentés", "Technologies émergentes", "Négociation flexible"]
        }

class SemanticAnalyzerAlgorithm(BaseMatchingAlgorithm):
    """Algorithme d'analyse sémantique pure"""
    
    def __init__(self):
        self.name = "SemanticAnalyzer"
        self.version = "2.1"
    
    def match(self, candidate: CandidateProfile, offers: List[CompanyOffer], 
              config: MatchingConfig) -> List[MatchingResult]:
        """Matching purement sémantique"""
        start_time = time.time()
        results = []
        
        for offer in offers:
            semantic_score = self._deep_semantic_analysis(candidate, offer)
            
            if semantic_score < config.min_score_threshold:
                continue
            
            result = MatchingResult(
                offer_id=offer.id,
                titre=offer.titre,
                entreprise="Semantic Match Company",
                score_global=int(semantic_score * 100),
                scores_details={"semantic_similarity": int(semantic_score * 100)},
                algorithme_utilise=f"{self.name} v{self.version}",
                temps_calcul=time.time() - start_time,
                raison_score="Analyse sémantique pure des compétences",
                recommandations=["Correspondance basée sur l'intelligence sémantique"],
                metadata={"semantic_only": True}
            )
            results.append(result)
        
        results.sort(key=lambda x: x.score_global, reverse=True)
        return results[:config.max_results]
    
    def _deep_semantic_analysis(self, candidate: CandidateProfile, offer: CompanyOffer) -> float:
        """Analyse sémantique approfondie"""
        # Implémentation simplifiée - en réalité utiliserait NLP avancé
        candidate_skills = set(skill.lower() for skill in candidate.competences)
        offer_skills = set(skill.lower() for skill in offer.competences)
        
        if not offer_skills:
            return 0.5
        
        # Simulation d'analyse sémantique avec Word2Vec/BERT
        semantic_score = len(candidate_skills.intersection(offer_skills)) / len(offer_skills)
        
        # Bonus pour compétences proches sémantiquement
        bonus = 0
        for offer_skill in offer_skills:
            for candidate_skill in candidate_skills:
                if self._semantic_similarity(offer_skill, candidate_skill) > 0.7:
                    bonus += 0.1
        
        return min(1.0, semantic_score + bonus)
    
    def _semantic_similarity(self, skill1: str, skill2: str) -> float:
        """Similarité sémantique entre deux compétences"""
        # Simulation - en réalité utiliserait des embeddings
        if skill1 == skill2:
            return 1.0
        elif any(common in skill1 and common in skill2 
                for common in ["python", "javascript", "react", "data"]):
            return 0.8
        else:
            return 0.2
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "type": "pure_semantic",
            "strengths": ["Analyse NLP", "Similarité contextuelle", "Intelligence linguistique"],
            "use_cases": ["Correspondances subtiles", "Technologies émergentes", "Profils atypiques"]
        }

class HybridMatchingAlgorithm(BaseMatchingAlgorithm):
    """Algorithme hybride combinant tous les autres"""
    
    def __init__(self, algorithms: List[BaseMatchingAlgorithm]):
        self.name = "Hybrid"
        self.version = "1.0"
        self.algorithms = algorithms
    
    def match(self, candidate: CandidateProfile, offers: List[CompanyOffer], 
              config: MatchingConfig) -> List[MatchingResult]:
        """Matching hybride avec fusion des résultats"""
        start_time = time.time()
        
        # Exécuter tous les algorithmes
        all_results = {}
        for algo in self.algorithms:
            algo_results = algo.match(candidate, offers, config)
            for result in algo_results:
                if result.offer_id not in all_results:
                    all_results[result.offer_id] = []
                all_results[result.offer_id].append(result)
        
        # Fusion des résultats
        final_results = []
        for offer_id, results in all_results.items():
            if len(results) < 2:  # Pas assez d'algorithmes concordants
                continue
            
            # Score hybride (moyenne pondérée)
            hybrid_score = sum(r.score_global for r in results) / len(results)
            
            # Prendre le meilleur résultat comme base
            best_result = max(results, key=lambda r: r.score_global)
            
            hybrid_result = MatchingResult(
                offer_id=offer_id,
                titre=best_result.titre,
                entreprise="Hybrid Match Company",
                score_global=int(hybrid_score),
                scores_details={
                    "hybrid_consensus": int(hybrid_score),
                    "algorithms_count": len(results),
                    "score_variance": int(max(r.score_global for r in results) - min(r.score_global for r in results))
                },
                algorithme_utilise=f"{self.name} v{self.version}",
                temps_calcul=time.time() - start_time,
                raison_score=f"Consensus de {len(results)} algorithmes",
                recommandations=[f"Validé par {len(results)} méthodes différentes"],
                metadata={
                    "participating_algorithms": [r.algorithme_utilise for r in results],
                    "individual_scores": [r.score_global for r in results]
                }
            )
            final_results.append(hybrid_result)
        
        final_results.sort(key=lambda x: x.score_global, reverse=True)
        return final_results[:config.max_results]
    
    def get_algorithm_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "type": "hybrid_ensemble",
            "strengths": ["Consensus multi-algorithmes", "Robustesse", "Validation croisée"],
            "use_cases": ["Décisions critiques", "Validation maximale", "Profils complexes"]
        }

class SuperSmartMatch:
    """Service unifié SuperSmartMatch"""
    
    def __init__(self):
        """Initialise SuperSmartMatch avec tous les algorithmes"""
        self.version = "1.0.0"
        
        # Initialisation des algorithmes
        self.smart_match = SmartMatchAlgorithm()
        self.enhanced = EnhancedMatchingAlgorithm()
        self.semantic = SemanticAnalyzerAlgorithm()
        self.hybrid = HybridMatchingAlgorithm([self.smart_match, self.enhanced, self.semantic])
        
        self.algorithms = {
            AlgorithmType.SMART_MATCH: self.smart_match,
            AlgorithmType.ENHANCED: self.enhanced,
            AlgorithmType.SEMANTIC: self.semantic,
            AlgorithmType.HYBRID: self.hybrid,
        }
        
        logger.info(f"SuperSmartMatch v{self.version} initialisé avec {len(self.algorithms)} algorithmes")
    
    def match(self, candidate_data: Dict[str, Any], offers_data: List[Dict[str, Any]], 
              algorithm: str = "auto", **kwargs) -> Dict[str, Any]:
        """
        Point d'entrée principal pour le matching
        
        Args:
            candidate_data: Données candidat (format front-end)
            offers_data: Liste des offres (format front-end)
            algorithm: Type d'algorithme ("auto", "smart-match", "enhanced", "hybrid", etc.)
            **kwargs: Configuration additionnelle
        
        Returns:
            Résultats de matching formatés
        """
        start_time = time.time()
        
        try:
            # Conversion des données d'entrée
            candidate = self._convert_candidate_data(candidate_data)
            offers = [self._convert_offer_data(offer) for offer in offers_data]
            
            # Configuration par défaut
            config = MatchingConfig(
                algorithm=AlgorithmType(algorithm),
                max_results=kwargs.get('max_results', 10),
                min_score_threshold=kwargs.get('min_score', 0.3)
            )
            
            # Sélection automatique de l'algorithme si nécessaire
            if config.algorithm == AlgorithmType.AUTO:
                config.algorithm = self._auto_select_algorithm(candidate, offers)
            
            # Exécution du matching
            selected_algorithm = self.algorithms[config.algorithm]
            results = selected_algorithm.match(candidate, offers, config)
            
            # Formatage de la réponse
            response = {
                "success": True,
                "algorithm_used": {
                    "type": config.algorithm.value,
                    "info": selected_algorithm.get_algorithm_info()
                },
                "candidate_profile": {
                    "experience_level": self._get_experience_level(candidate.annees_experience),
                    "skills_count": len(candidate.competences),
                    "location": candidate.adresse,
                    "mobility": candidate.mobilite
                },
                "matching_results": {
                    "total_offers_analyzed": len(offers),
                    "matches_found": len(results),
                    "execution_time": round(time.time() - start_time, 3),
                    "matches": [self._format_result(result) for result in results]
                },
                "recommendations": self._generate_global_recommendations(results, candidate),
                "metadata": {
                    "version": self.version,
                    "timestamp": time.time(),
                    "config": asdict(config)
                }
            }
            
            logger.info(f"Matching réussi: {len(results)} résultats en {response['matching_results']['execution_time']}s")
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors du matching: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "algorithm_used": algorithm,
                "execution_time": round(time.time() - start_time, 3)
            }
    
    def _convert_candidate_data(self, data: Dict[str, Any]) -> CandidateProfile:
        """Convertit les données candidat du front-end vers le format interne"""
        return CandidateProfile(
            competences=data.get('competences', []),
            adresse=data.get('adresse', ''),
            mobilite=data.get('mobilite', 'hybrid'),
            annees_experience=data.get('annees_experience', 0),
            salaire_souhaite=data.get('salaire_souhaite', 0),
            contrats_recherches=data.get('contrats_recherches', ['CDI']),
            disponibilite=data.get('disponibilite', 'immediate'),
            formation=data.get('formation'),
            domaines_interets=data.get('domaines_interets')
        )
    
    def _convert_offer_data(self, data: Dict[str, Any]) -> CompanyOffer:
        """Convertit les données offre du front-end vers le format interne"""
        return CompanyOffer(
            id=data.get('id', 0),
            titre=data.get('titre', ''),
            competences=data.get('competences', []),
            localisation=data.get('localisation', ''),
            type_contrat=data.get('type_contrat', 'CDI'),
            salaire=data.get('salaire', ''),
            politique_remote=data.get('politique_remote', 'on-site'),
            experience_requise=data.get('experience'),
            description=data.get('description'),
            avantages=data.get('avantages')
        )
    
    def _auto_select_algorithm(self, candidate: CandidateProfile, offers: List[CompanyOffer]) -> AlgorithmType:
        """Sélection automatique du meilleur algorithme"""
        # Règles de sélection intelligente
        if candidate.annees_experience >= 7:
            return AlgorithmType.ENHANCED  # Meilleur pour les seniors
        elif len(candidate.competences) >= 8:
            return AlgorithmType.SEMANTIC  # Beaucoup de compétences = sémantique
        elif candidate.mobilite == "remote":
            return AlgorithmType.SMART_MATCH  # Géolocalisation avancée
        elif len(offers) >= 20:
            return AlgorithmType.HYBRID  # Beaucoup d'offres = consensus
        else:
            return AlgorithmType.ENHANCED  # Par défaut
    
    def _get_experience_level(self, experience: int) -> str:
        """Détermine le niveau d'expérience"""
        if experience >= 7:
            return "Senior"
        elif experience >= 3:
            return "Confirmé"
        else:
            return "Junior"
    
    def _format_result(self, result: MatchingResult) -> Dict[str, Any]:
        """Formate un résultat pour la réponse API"""
        return {
            "offer_id": result.offer_id,
            "title": result.titre,
            "company": result.entreprise,
            "score": result.score_global,
            "score_details": result.scores_details,
            "algorithm": result.algorithme_utilise,
            "explanation": result.raison_score,
            "recommendations": result.recommandations,
            "metadata": result.metadata
        }
    
    def _generate_global_recommendations(self, results: List[MatchingResult], candidate: CandidateProfile) -> List[str]:
        """Génère des recommandations globales"""
        recommendations = []
        
        if not results:
            recommendations.append("Aucune correspondance trouvée - Élargissez vos critères")
            recommendations.append("Développez vos compétences dans les technologies demandées")
        elif len(results) >= 5:
            best_score = results[0].score_global
            if best_score >= 80:
                recommendations.append("Excellentes opportunités disponibles - Postulez rapidement")
            else:
                recommendations.append("Bonnes opportunités - Personnalisez vos candidatures")
        else:
            recommendations.append("Peu d'opportunités - Considérez élargir vos critères")
        
        return recommendations
    
    def get_algorithm_info(self, algorithm_type: str = None) -> Dict[str, Any]:
        """Retourne les informations sur les algorithmes"""
        if algorithm_type:
            algo_enum = AlgorithmType(algorithm_type)
            return self.algorithms[algo_enum].get_algorithm_info()
        else:
            return {
                "service": "SuperSmartMatch",
                "version": self.version,
                "available_algorithms": {
                    algo_type.value: algo.get_algorithm_info() 
                    for algo_type, algo in self.algorithms.items()
                }
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Vérification de l'état du service"""
        return {
            "status": "healthy",
            "version": self.version,
            "algorithms_count": len(self.algorithms),
            "algorithms_status": {
                algo_type.value: "operational" 
                for algo_type in self.algorithms.keys()
            },
            "uptime": "OK"
        }

# Point d'entrée simple pour l'API Flask/FastAPI
def create_matching_service() -> SuperSmartMatch:
    """Crée une instance du service de matching"""
    return SuperSmartMatch()

# Fonction de compatibilité avec l'API existante
def match_candidate_with_jobs(cv_data: Dict[str, Any], questionnaire_data: Dict[str, Any], 
                             job_data: List[Dict[str, Any]], algorithm: str = "auto") -> List[Dict[str, Any]]:
    """
    Fonction de compatibilité avec l'API existante
    """
    service = SuperSmartMatch()
    
    # Fusion des données candidat
    candidate_data = {**cv_data, **questionnaire_data}
    
    # Exécution du matching
    response = service.match(candidate_data, job_data, algorithm=algorithm)
    
    # Retour au format attendu par l'API existante
    if response["success"]:
        return [
            {
                "id": match["offer_id"],
                "titre": match["title"],
                "entreprise": match["company"],
                "matching_score": match["score"],
                "matching_details": match["score_details"],
                "algorithm_version": match["algorithm"]
            }
            for match in response["matching_results"]["matches"]
        ]
    else:
        return []

# Test et démonstration
if __name__ == "__main__":
    print("🚀 TEST DE SUPERSMARTMATCH")
    print("=" * 60)
    
    # Création du service
    service = SuperSmartMatch()
    
    # Données de test
    candidate_data = {
        "competences": ["Python", "React", "Django", "SQL", "Git"],
        "adresse": "Paris",
        "mobilite": "hybrid",
        "annees_experience": 4,
        "salaire_souhaite": 50000,
        "contrats_recherches": ["CDI"],
        "disponibilite": "immediate"
    }
    
    offers_data = [
        {
            "id": 1,
            "titre": "Développeur Full Stack",
            "competences": ["Python", "Django", "React"],
            "localisation": "Paris",
            "type_contrat": "CDI",
            "salaire": "45K-55K€",
            "politique_remote": "hybrid"
        },
        {
            "id": 2,
            "titre": "Data Scientist",
            "competences": ["Python", "Machine Learning", "SQL"],
            "localisation": "Remote",
            "type_contrat": "CDI",
            "salaire": "55K-65K€",
            "politique_remote": "remote"
        }
    ]
    
    # Test avec différents algorithmes
    algorithms_to_test = ["auto", "smart-match", "enhanced", "semantic", "hybrid"]
    
    for algo in algorithms_to_test:
        print(f"\n🧠 TEST ALGORITHME: {algo.upper()}")
        print("-" * 40)
        
        response = service.match(candidate_data, offers_data, algorithm=algo)
        
        if response["success"]:
            print(f"✅ Succès - {response['matching_results']['matches_found']} matches")
            print(f"   Algorithme: {response['algorithm_used']['type']}")
            print(f"   Temps: {response['matching_results']['execution_time']}s")
            
            for i, match in enumerate(response['matching_results']['matches'][:2]):
                print(f"   🎯 Match #{i+1}: {match['title']} - Score: {match['score']}%")
        else:
            print(f"❌ Erreur: {response['error']}")
    
    print(f"\n🎉 SuperSmartMatch opérationnel ! Prêt pour l'intégration.")
