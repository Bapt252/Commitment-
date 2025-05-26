#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Interface de base pour tous les algorithmes de SuperSmartMatch
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseAlgorithm(ABC):
    """
    Interface de base que tous les algorithmes doivent implémenter
    """
    
    def __init__(self):
        self.name = "base"
        self.description = "Algorithme de base"
        self.version = "1.0"
        self.initialized = False
    
    @abstractmethod
    def supports(self, candidat: Dict[str, Any], offres: List[Dict[str, Any]]) -> bool:
        """
        Vérifie si l'algorithme peut traiter ces données
        
        Args:
            candidat: Données du candidat
            offres: Liste des offres d'emploi
            
        Returns:
            True si l'algorithme peut traiter les données
        """
        pass
    
    @abstractmethod
    def match_candidate_with_jobs(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Exécute le matching entre un candidat et des offres
        
        Args:
            candidat: Données du candidat
            offres: Liste des offres d'emploi
            limit: Nombre maximum de résultats à retourner
            
        Returns:
            Liste des offres avec leurs scores de matching
        """
        pass
    
    @abstractmethod
    def get_algorithm_info(self) -> Dict[str, Any]:
        """
        Retourne les informations sur l'algorithme
        
        Returns:
            Dictionnaire contenant les informations de l'algorithme
        """
        pass
    
    def validate_input(self, candidat: Dict[str, Any], offres: List[Dict[str, Any]]) -> bool:
        """
        Valide les données d'entrée
        
        Args:
            candidat: Données candidat
            offres: Liste des offres
            
        Returns:
            True si les données sont valides
        """
        # Validation basique
        if not isinstance(candidat, dict):
            return False
        
        if not isinstance(offres, list) or len(offres) == 0:
            return False
        
        return True
    
    def preprocess_data(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]]
    ) -> tuple:
        """
        Prétraite les données avant le matching
        
        Args:
            candidat: Données candidat
            offres: Liste des offres
            
        Returns:
            Tuple (candidat_traité, offres_traitées)
        """
        # Prétraitement par défaut (peut être overridé)
        return candidat, offres
    
    def postprocess_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Post-traite les résultats
        
        Args:
            results: Résultats bruts
            
        Returns:
            Résultats traités
        """
        # Post-traitement par défaut
        for result in results:
            # Assurer que le score est entre 0 et 100
            if 'matching_score' in result:
                result['matching_score'] = max(0, min(100, result['matching_score']))
        
        return results
    
    def calculate_confidence_score(self, result: Dict[str, Any]) -> float:
        """
        Calcule un score de confiance pour un résultat
        
        Args:
            result: Résultat de matching
            
        Returns:
            Score de confiance entre 0 et 1
        """
        # Score de confiance basique basé sur le score de matching
        base_score = result.get('matching_score', 0) / 100.0
        
        # Bonus si des détails sont disponibles
        details_bonus = 0.1 if result.get('matching_details') else 0
        
        # Bonus si des explications sont disponibles
        explanations_bonus = 0.05 if result.get('matching_explanations') else 0
        
        return min(1.0, base_score + details_bonus + explanations_bonus)
