#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sélecteur d'Algorithme Intelligent pour SuperSmartMatch
Analyse automatiquement les données et sélectionne l'algorithme optimal
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AlgorithmCapability:
    """Capacités d'un algorithme"""
    name: str
    handles_geolocation: bool = False
    handles_soft_skills: bool = False
    handles_semantic_matching: bool = False
    handles_remote_preferences: bool = False
    performance_score: float = 1.0
    complexity_level: int = 1  # 1=simple, 5=complexe

class AlgorithmSelector:
    """
    Sélecteur intelligent d'algorithme basé sur l'analyse des données
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le sélecteur d'algorithmes
        
        Args:
            config: Configuration du sélecteur
        """
        self.config = config or {}
        self._initialize_algorithms()
        self._load_selection_rules()
    
    def _initialize_algorithms(self):
        """Initialise les capacités des algorithmes disponibles"""
        self.algorithms = {
            "smart-match": AlgorithmCapability(
                name="smart-match",
                handles_geolocation=True,
                handles_remote_preferences=True,
                performance_score=0.9,
                complexity_level=3
            ),
            "enhanced": AlgorithmCapability(
                name="enhanced",
                handles_soft_skills=True,
                handles_remote_preferences=True,
                performance_score=0.95,
                complexity_level=4
            ),
            "semantic": AlgorithmCapability(
                name="semantic",
                handles_semantic_matching=True,
                performance_score=0.85,
                complexity_level=2
            ),
            "hybrid": AlgorithmCapability(
                name="hybrid",
                handles_geolocation=True,
                handles_soft_skills=True,
                handles_semantic_matching=True,
                handles_remote_preferences=True,
                performance_score=0.98,
                complexity_level=5
            )
        }
    
    def _load_selection_rules(self):
        """Charge les règles de sélection automatique"""
        self.selection_rules = [
            {
                "condition": self._has_complex_requirements,
                "algorithm": "hybrid",
                "priority": 1,
                "reason": "Données complexes nécessitant l'approche hybride"
            },
            {
                "condition": self._has_soft_skills_data,
                "algorithm": "enhanced",
                "priority": 2,
                "reason": "Présence de soft skills ou préférences culturelles"
            },
            {
                "condition": self._has_geolocation_needs,
                "algorithm": "smart-match",
                "priority": 3,
                "reason": "Besoins de géolocalisation identifiés"
            },
            {
                "condition": self._has_semantic_needs,
                "algorithm": "semantic",
                "priority": 4,
                "reason": "Matching sémantique des compétences nécessaire"
            },
            {
                "condition": self._is_simple_case,
                "algorithm": "enhanced",
                "priority": 5,
                "reason": "Cas standard, algorithme enhanced par défaut"
            }
        ]
    
    def select_best_algorithm(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> str:
        """
        Sélectionne automatiquement le meilleur algorithme
        
        Args:
            candidat: Données du candidat
            offres: Liste des offres d'emploi
            
        Returns:
            Nom de l'algorithme sélectionné
        """
        # Analyser les données
        analysis = self._analyze_data(candidat, offres)
        
        logger.info(f"Analyse des données: {analysis}")
        
        # Appliquer les règles de sélection
        selected_algorithm = self._apply_selection_rules(analysis, candidat, offres)
        
        logger.info(f"Algorithme sélectionné: {selected_algorithm}")
        
        return selected_algorithm
    
    def _analyze_data(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyse les données pour identifier les besoins
        
        Args:
            candidat: Données candidat
            offres: Offres d'emploi
            
        Returns:
            Analyse des besoins identifiés
        """
        analysis = {
            "has_geolocation": False,
            "has_soft_skills": False,
            "has_remote_preferences": False,
            "has_complex_skills": False,
            "has_cultural_preferences": False,
            "data_quality": "basic",
            "complexity_score": 0
        }
        
        # Analyse du candidat
        if candidat:
            # Géolocalisation
            if candidat.get('adresse') or candidat.get('localisation'):
                analysis['has_geolocation'] = True
                analysis['complexity_score'] += 1
            
            # Préférences remote
            if candidat.get('mobilite') or candidat.get('remote_preference'):
                analysis['has_remote_preferences'] = True
                analysis['complexity_score'] += 1
            
            # Soft skills
            if (candidat.get('soft_skills') or 
                candidat.get('competences_comportementales') or
                candidat.get('personnalite')):
                analysis['has_soft_skills'] = True
                analysis['complexity_score'] += 1
            
            # Préférences culturelles
            if (candidat.get('preferences_culture') or
                candidat.get('valeurs_importantes') or
                candidat.get('environnement_prefere')):
                analysis['has_cultural_preferences'] = True
                analysis['complexity_score'] += 1
            
            # Compétences complexes
            competences = candidat.get('competences', [])
            if len(competences) > 5:
                analysis['has_complex_skills'] = True
                analysis['complexity_score'] += 1
        
        # Analyse des offres
        if offres:
            for offre in offres:
                # Géolocalisation dans les offres
                if offre.get('localisation') or offre.get('lieu'):
                    analysis['has_geolocation'] = True
                
                # Politique remote
                if (offre.get('politique_remote') or 
                    offre.get('remote_policy') or
                    offre.get('teletravail')):
                    analysis['has_remote_preferences'] = True
                
                # Soft skills requis
                if (offre.get('soft_skills') or
                    offre.get('competences_comportementales')):
                    analysis['has_soft_skills'] = True
                
                # Culture d'entreprise
                if (offre.get('culture_entreprise') or
                    offre.get('valeurs')):
                    analysis['has_cultural_preferences'] = True
        
        # Déterminer la qualité des données
        if analysis['complexity_score'] >= 4:
            analysis['data_quality'] = "rich"
        elif analysis['complexity_score'] >= 2:
            analysis['data_quality'] = "medium"
        else:
            analysis['data_quality'] = "basic"
        
        return analysis
    
    def _apply_selection_rules(
        self, 
        analysis: Dict[str, Any], 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> str:
        """
        Applique les règles de sélection pour choisir l'algorithme
        
        Args:
            analysis: Analyse des données
            candidat: Données candidat
            offres: Offres d'emploi
            
        Returns:
            Algorithme sélectionné
        """
        # Trier les règles par priorité
        sorted_rules = sorted(self.selection_rules, key=lambda x: x['priority'])
        
        # Appliquer chaque règle
        for rule in sorted_rules:
            if rule['condition'](analysis, candidat, offres):
                logger.info(f"Règle appliquée: {rule['reason']}")
                return rule['algorithm']
        
        # Fallback (ne devrait jamais arriver)
        logger.warning("Aucune règle appliquée, utilisation de l'algorithme par défaut")
        return "enhanced"
    
    # Conditions de sélection
    def _has_complex_requirements(
        self, 
        analysis: Dict[str, Any], 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> bool:
        """Vérifie si les exigences sont complexes"""
        return (
            analysis['complexity_score'] >= 4 or
            analysis['data_quality'] == "rich" or
            (analysis['has_geolocation'] and 
             analysis['has_soft_skills'] and 
             analysis['has_remote_preferences'])
        )
    
    def _has_soft_skills_data(
        self, 
        analysis: Dict[str, Any], 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> bool:
        """Vérifie la présence de données soft skills"""
        return (
            analysis['has_soft_skills'] or 
            analysis['has_cultural_preferences']
        )
    
    def _has_geolocation_needs(
        self, 
        analysis: Dict[str, Any], 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> bool:
        """Vérifie les besoins de géolocalisation"""
        return (
            analysis['has_geolocation'] and 
            analysis['has_remote_preferences']
        )
    
    def _has_semantic_needs(
        self, 
        analysis: Dict[str, Any], 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> bool:
        """Vérifie les besoins de matching sémantique"""
        return (
            analysis['has_complex_skills'] and
            not analysis['has_geolocation'] and
            not analysis['has_soft_skills']
        )
    
    def _is_simple_case(
        self, 
        analysis: Dict[str, Any], 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> bool:
        """Cas simple par défaut"""
        return True  # Toujours vrai, c'est le fallback final
    
    def get_algorithm(self, algorithm_name: str):
        """
        Retourne une instance de l'algorithme demandé
        
        Args:
            algorithm_name: Nom de l'algorithme
            
        Returns:
            Instance de l'algorithme ou None
        """
        try:
            if algorithm_name == "smart-match":
                from ..algorithms.smart_match import SmartMatchAlgorithm
                return SmartMatchAlgorithm()
            elif algorithm_name == "enhanced":
                from ..algorithms.enhanced import EnhancedAlgorithm
                return EnhancedAlgorithm()
            elif algorithm_name == "semantic":
                from ..algorithms.semantic import SemanticAlgorithm
                return SemanticAlgorithm()
            elif algorithm_name == "hybrid":
                from ..algorithms.hybrid import HybridAlgorithm
                return HybridAlgorithm()
            else:
                logger.error(f"Algorithme inconnu: {algorithm_name}")
                return None
        except ImportError as e:
            logger.error(f"Erreur d'import pour l'algorithme {algorithm_name}: {e}")
            return None
    
    def get_algorithm_config(self, algorithm_name: str) -> Dict[str, Any]:
        """
        Retourne la configuration d'un algorithme
        
        Args:
            algorithm_name: Nom de l'algorithme
            
        Returns:
            Configuration de l'algorithme
        """
        if algorithm_name in self.algorithms:
            algo = self.algorithms[algorithm_name]
            return {
                "name": algo.name,
                "capabilities": {
                    "geolocation": algo.handles_geolocation,
                    "soft_skills": algo.handles_soft_skills,
                    "semantic": algo.handles_semantic_matching,
                    "remote": algo.handles_remote_preferences
                },
                "performance_score": algo.performance_score,
                "complexity_level": algo.complexity_level
            }
        return {}
    
    def get_available_algorithms(self) -> List[str]:
        """
        Retourne la liste des algorithmes disponibles
        
        Returns:
            Liste des noms d'algorithmes
        """
        return list(self.algorithms.keys())
    
    def explain_selection(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Explique pourquoi un algorithme a été sélectionné
        
        Args:
            candidat: Données candidat
            offres: Offres d'emploi
            
        Returns:
            Explication de la sélection
        """
        analysis = self._analyze_data(candidat, offres)
        selected = self.select_best_algorithm(candidat, offres)
        
        # Trouver la règle appliquée
        applied_rule = None
        for rule in sorted(self.selection_rules, key=lambda x: x['priority']):
            if rule['condition'](analysis, candidat, offres):
                applied_rule = rule
                break
        
        return {
            "algorithm_selected": selected,
            "reason": applied_rule['reason'] if applied_rule else "Algorithme par défaut",
            "data_analysis": analysis,
            "algorithm_capabilities": self.get_algorithm_config(selected),
            "alternatives": [
                {
                    "algorithm": name,
                    "would_work": self._algorithm_would_work(name, analysis),
                    "confidence": self._calculate_algorithm_confidence(name, analysis)
                }
                for name in self.get_available_algorithms()
                if name != selected
            ]
        }
    
    def _algorithm_would_work(self, algorithm_name: str, analysis: Dict[str, Any]) -> bool:
        """
        Vérifie si un algorithme pourrait fonctionner avec les données
        
        Args:
            algorithm_name: Nom de l'algorithme
            analysis: Analyse des données
            
        Returns:
            True si l'algorithme peut gérer les données
        """
        if algorithm_name not in self.algorithms:
            return False
        
        algo = self.algorithms[algorithm_name]
        
        # Vérifier les capacités requises
        if analysis['has_geolocation'] and not algo.handles_geolocation:
            return False
        
        if analysis['has_soft_skills'] and not algo.handles_soft_skills:
            return False
        
        if analysis['has_complex_skills'] and not algo.handles_semantic_matching:
            return False
        
        return True
    
    def _calculate_algorithm_confidence(
        self, 
        algorithm_name: str, 
        analysis: Dict[str, Any]
    ) -> float:
        """
        Calcule la confiance d'un algorithme pour les données
        
        Args:
            algorithm_name: Nom de l'algorithme
            analysis: Analyse des données
            
        Returns:
            Score de confiance entre 0 et 1
        """
        if algorithm_name not in self.algorithms:
            return 0.0
        
        algo = self.algorithms[algorithm_name]
        confidence = algo.performance_score
        
        # Ajuster selon les capacités
        if analysis['has_geolocation'] and algo.handles_geolocation:
            confidence += 0.1
        elif analysis['has_geolocation'] and not algo.handles_geolocation:
            confidence -= 0.2
        
        if analysis['has_soft_skills'] and algo.handles_soft_skills:
            confidence += 0.1
        elif analysis['has_soft_skills'] and not algo.handles_soft_skills:
            confidence -= 0.1
        
        if analysis['has_complex_skills'] and algo.handles_semantic_matching:
            confidence += 0.1
        elif analysis['has_complex_skills'] and not algo.handles_semantic_matching:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def benchmark_algorithms(
        self, 
        test_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Benchmarke tous les algorithmes sur des cas de test
        
        Args:
            test_cases: Liste de cas de test
            
        Returns:
            Résultats du benchmark
        """
        results = {}
        
        for algorithm_name in self.get_available_algorithms():
            algorithm = self.get_algorithm(algorithm_name)
            if not algorithm:
                continue
            
            algorithm_results = {
                "total_tests": len(test_cases),
                "successful_tests": 0,
                "avg_execution_time": 0,
                "avg_score": 0,
                "errors": []
            }
            
            total_time = 0
            total_score = 0
            
            for i, test_case in enumerate(test_cases):
                try:
                    import time
                    start_time = time.time()
                    
                    result = algorithm.match_candidate_with_jobs(
                        test_case['candidat'],
                        test_case['offres']
                    )
                    
                    execution_time = time.time() - start_time
                    total_time += execution_time
                    
                    if result:
                        score = sum(r.get('matching_score', 0) for r in result) / len(result)
                        total_score += score
                        algorithm_results["successful_tests"] += 1
                    
                except Exception as e:
                    algorithm_results["errors"].append(f"Test {i}: {str(e)}")
            
            if algorithm_results["successful_tests"] > 0:
                algorithm_results["avg_execution_time"] = total_time / algorithm_results["successful_tests"]
                algorithm_results["avg_score"] = total_score / algorithm_results["successful_tests"]
            
            results[algorithm_name] = algorithm_results
        
        return results
