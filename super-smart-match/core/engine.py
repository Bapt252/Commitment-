#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SuperSmartMatch - Moteur Principal Unifié
Regroupe tous les algorithmes de matching sous une seule interface
"""

import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .selector import AlgorithmSelector
from .unified_api import UnifiedAPI
from ..utils.data_adapter import DataAdapter
from ..utils.performance import PerformanceMonitor
from ..utils.fallback import FallbackManager

logger = logging.getLogger(__name__)

class AlgorithmType(Enum):
    AUTO = "auto"
    SMART_MATCH = "smart-match"
    ENHANCED = "enhanced"
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    COMPARISON = "comparison"

@dataclass
class MatchOptions:
    """Options de configuration pour le matching"""
    algorithme: AlgorithmType = AlgorithmType.AUTO
    limite: int = 10
    seuil_minimum: float = 0.6
    details: bool = True
    explications: bool = True
    performance_tracking: bool = True
    fallback_enabled: bool = True

@dataclass
class MatchResult:
    """Résultat d'un matching"""
    id: str
    titre: str
    score_global: float
    scores_details: Dict[str, float]
    explications: Dict[str, str]
    confiance: float
    donnees_originales: Dict[str, Any]

@dataclass
class SuperMatchResponse:
    """Réponse complète du SuperSmartMatch"""
    status: str
    algorithme_utilise: str
    temps_execution: float
    resultats: List[MatchResult]
    meta: Dict[str, Any]
    erreurs: List[str] = None

class SuperSmartMatchEngine:
    """
    Moteur principal du service SuperSmartMatch
    Unifie tous les algorithmes de matching sous une seule interface
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialise le moteur SuperSmartMatch
        
        Args:
            config: Configuration du moteur
        """
        self.config = config or {}
        self.selector = AlgorithmSelector(self.config)
        self.api = UnifiedAPI()
        self.data_adapter = DataAdapter()
        self.performance = PerformanceMonitor()
        self.fallback = FallbackManager()
        
        # Configuration par défaut
        self.default_options = MatchOptions()
        
        logger.info("SuperSmartMatch Engine initialisé")
    
    def match(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        options: MatchOptions = None
    ) -> SuperMatchResponse:
        """
        Effectue le matching principal entre un candidat et des offres
        
        Args:
            candidat: Données du candidat
            offres: Liste des offres d'emploi
            options: Options de matching
            
        Returns:
            Réponse complète avec les résultats
        """
        start_time = time.time()
        options = options or self.default_options
        erreurs = []
        
        try:
            # 1. Validation et adaptation des données
            candidat_adapte = self.data_adapter.adapt_candidate(candidat)
            offres_adaptees = self.data_adapter.adapt_jobs(offres)
            
            # 2. Sélection de l'algorithme
            if options.algorithme == AlgorithmType.AUTO:
                algorithme_choisi = self.selector.select_best_algorithm(
                    candidat_adapte, offres_adaptees
                )
            else:
                algorithme_choisi = options.algorithme.value
            
            logger.info(f"Algorithme sélectionné: {algorithme_choisi}")
            
            # 3. Exécution du matching
            resultats_bruts = []
            
            if options.algorithme == AlgorithmType.COMPARISON:
                # Mode comparaison : teste tous les algorithmes
                resultats_bruts = self._execute_comparison_mode(
                    candidat_adapte, offres_adaptees, options
                )
            else:
                # Mode standard : utilise l'algorithme sélectionné
                resultats_bruts = self._execute_single_algorithm(
                    algorithme_choisi, candidat_adapte, offres_adaptees, options
                )
            
            # 4. Post-traitement des résultats
            resultats_traites = self._process_results(
                resultats_bruts, options
            )
            
            # 5. Application des filtres
            resultats_filtres = self._apply_filters(
                resultats_traites, options
            )
            
            # 6. Tri et limitation
            resultats_finaux = self._sort_and_limit(
                resultats_filtres, options
            )
            
            # 7. Calcul des métriques
            execution_time = time.time() - start_time
            meta = self._generate_meta(
                algorithme_choisi, resultats_finaux, execution_time, 
                len(offres), options
            )
            
            # 8. Tracking des performances
            if options.performance_tracking:
                self.performance.track_execution(
                    algorithme_choisi, execution_time, len(resultats_finaux)
                )
            
            return SuperMatchResponse(
                status="success",
                algorithme_utilise=algorithme_choisi,
                temps_execution=execution_time,
                resultats=resultats_finaux,
                meta=meta,
                erreurs=erreurs if erreurs else None
            )
            
        except Exception as e:
            logger.error(f"Erreur dans SuperSmartMatch: {e}")
            
            # Gestion du fallback
            if options.fallback_enabled:
                return self._execute_fallback(candidat, offres, options, str(e))
            
            return SuperMatchResponse(
                status="error",
                algorithme_utilise="none",
                temps_execution=time.time() - start_time,
                resultats=[],
                meta={},
                erreurs=[str(e)]
            )
    
    def _execute_single_algorithm(
        self, 
        algorithme: str, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        options: MatchOptions
    ) -> List[Dict[str, Any]]:
        """
        Exécute un seul algorithme de matching
        
        Args:
            algorithme: Nom de l'algorithme à utiliser
            candidat: Données candidat adaptées
            offres: Offres adaptées
            options: Options de matching
            
        Returns:
            Résultats bruts de l'algorithme
        """
        # Charger l'algorithme approprié
        algorithm_instance = self.selector.get_algorithm(algorithme)
        
        if not algorithm_instance:
            raise ValueError(f"Algorithme '{algorithme}' non trouvé")
        
        # Exécuter le matching
        return algorithm_instance.match_candidate_with_jobs(
            candidat, offres, limit=options.limite
        )
    
    def _execute_comparison_mode(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        options: MatchOptions
    ) -> List[Dict[str, Any]]:
        """
        Exécute le mode comparaison (teste tous les algorithmes)
        
        Args:
            candidat: Données candidat adaptées
            offres: Offres adaptées
            options: Options de matching
            
        Returns:
            Résultats agrégés de tous les algorithmes
        """
        algorithms_to_test = [
            AlgorithmType.SMART_MATCH.value,
            AlgorithmType.ENHANCED.value,
            AlgorithmType.SEMANTIC.value
        ]
        
        all_results = {}
        
        for algo_name in algorithms_to_test:
            try:
                results = self._execute_single_algorithm(
                    algo_name, candidat, offres, options
                )
                all_results[algo_name] = results
            except Exception as e:
                logger.warning(f"Erreur avec l'algorithme {algo_name}: {e}")
                all_results[algo_name] = []
        
        # Agrégation des résultats (moyenne pondérée)
        return self._aggregate_comparison_results(all_results, options)
    
    def _aggregate_comparison_results(
        self, 
        all_results: Dict[str, List[Dict[str, Any]]], 
        options: MatchOptions
    ) -> List[Dict[str, Any]]:
        """
        Agrège les résultats de plusieurs algorithmes
        
        Args:
            all_results: Résultats de tous les algorithmes
            options: Options de matching
            
        Returns:
            Résultats agrégés
        """
        # Poids pour l'agrégation
        weights = {
            "smart-match": 0.3,
            "enhanced": 0.4,
            "semantic": 0.3
        }
        
        # Map des offres par ID
        job_scores = {}
        
        for algo_name, results in all_results.items():
            weight = weights.get(algo_name, 0.1)
            
            for result in results:
                job_id = result.get('id', str(result.get('titre', '')))
                
                if job_id not in job_scores:
                    job_scores[job_id] = {
                        'job_data': result,
                        'scores': [],
                        'weights': []
                    }
                
                score = result.get('matching_score', 0)
                job_scores[job_id]['scores'].append(score)
                job_scores[job_id]['weights'].append(weight)
        
        # Calcul des scores moyens pondérés
        aggregated_results = []
        
        for job_id, data in job_scores.items():
            if data['scores']:
                # Score moyen pondéré
                weighted_score = sum(
                    score * weight 
                    for score, weight in zip(data['scores'], data['weights'])
                ) / sum(data['weights'])
                
                result = data['job_data'].copy()
                result['matching_score'] = round(weighted_score)
                result['algorithm_scores'] = {
                    algo: score for algo, score in zip(all_results.keys(), data['scores'])
                }
                
                aggregated_results.append(result)
        
        return aggregated_results
    
    def _process_results(
        self, 
        resultats_bruts: List[Dict[str, Any]], 
        options: MatchOptions
    ) -> List[MatchResult]:
        """
        Traite et structure les résultats bruts
        
        Args:
            resultats_bruts: Résultats bruts des algorithmes
            options: Options de matching
            
        Returns:
            Résultats structurés
        """
        resultats_traites = []
        
        for i, resultat in enumerate(resultats_bruts):
            # Extraction des données principales
            job_id = resultat.get('id', f"job_{i}")
            titre = resultat.get('titre', 'Poste sans titre')
            score_global = resultat.get('matching_score', 0)
            
            # Extraction des détails si disponibles
            details = resultat.get('matching_details', {})
            explications = resultat.get('matching_explanations', {})
            
            # Calcul de la confiance (basé sur la cohérence des scores)
            confiance = self._calculate_confidence(resultat)
            
            match_result = MatchResult(
                id=job_id,
                titre=titre,
                score_global=score_global,
                scores_details=details,
                explications=explications,
                confiance=confiance,
                donnees_originales=resultat
            )
            
            resultats_traites.append(match_result)
        
        return resultats_traites
    
    def _calculate_confidence(self, resultat: Dict[str, Any]) -> float:
        """
        Calcule un score de confiance pour un résultat
        
        Args:
            resultat: Résultat d'un matching
            
        Returns:
            Score de confiance entre 0 et 1
        """
        # Score de base
        score = resultat.get('matching_score', 0) / 100.0
        
        # Bonus si des détails sont disponibles
        if resultat.get('matching_details'):
            details = resultat['matching_details']
            # Vérifier la cohérence des scores
            scores = list(details.values())
            if scores:
                variance = sum((s - score*100)**2 for s in scores) / len(scores)
                consistency_bonus = max(0, (100 - variance) / 100 * 0.2)
                score += consistency_bonus
        
        # Bonus si des explications sont disponibles
        if resultat.get('matching_explanations'):
            score += 0.1
        
        # Bonus si provient d'un algorithme multiple
        if resultat.get('algorithm_scores'):
            score += 0.05
        
        return min(1.0, score)
    
    def _apply_filters(
        self, 
        resultats: List[MatchResult], 
        options: MatchOptions
    ) -> List[MatchResult]:
        """
        Applique les filtres aux résultats
        
        Args:
            resultats: Résultats à filtrer
            options: Options de matching
            
        Returns:
            Résultats filtrés
        """
        # Filtre par seuil minimum
        filtered = [
            r for r in resultats 
            if r.score_global >= (options.seuil_minimum * 100)
        ]
        
        return filtered
    
    def _sort_and_limit(
        self, 
        resultats: List[MatchResult], 
        options: MatchOptions
    ) -> List[MatchResult]:
        """
        Trie et limite les résultats
        
        Args:
            resultats: Résultats à trier
            options: Options de matching
            
        Returns:
            Résultats triés et limités
        """
        # Tri par score global décroissant, puis par confiance
        sorted_results = sorted(
            resultats, 
            key=lambda x: (x.score_global, x.confiance), 
            reverse=True
        )
        
        # Limitation
        return sorted_results[:options.limite]
    
    def _generate_meta(
        self, 
        algorithme: str, 
        resultats: List[MatchResult], 
        execution_time: float,
        total_offres: int,
        options: MatchOptions
    ) -> Dict[str, Any]:
        """
        Génère les métadonnées de la réponse
        
        Args:
            algorithme: Algorithme utilisé
            resultats: Résultats finaux
            execution_time: Temps d'exécution
            total_offres: Nombre total d'offres
            options: Options utilisées
            
        Returns:
            Métadonnées
        """
        # Calcul des métriques de performance
        if resultats:
            avg_score = sum(r.score_global for r in resultats) / len(resultats)
            avg_confidence = sum(r.confiance for r in resultats) / len(resultats)
        else:
            avg_score = 0
            avg_confidence = 0
        
        return {
            "total_offres": total_offres,
            "offres_retournees": len(resultats),
            "score_moyen": round(avg_score, 1),
            "confiance_moyenne": round(avg_confidence, 3),
            "algorithme_details": {
                "nom": algorithme,
                "version": "1.0",
                "config": self.selector.get_algorithm_config(algorithme)
            },
            "performance": {
                "temps_execution": round(execution_time, 3),
                "offres_par_seconde": round(total_offres / execution_time, 1) if execution_time > 0 else 0
            },
            "options_utilisees": {
                "seuil_minimum": options.seuil_minimum,
                "limite": options.limite,
                "details": options.details
            }
        }
    
    def _execute_fallback(
        self, 
        candidat: Dict[str, Any], 
        offres: List[Dict[str, Any]], 
        options: MatchOptions,
        error_message: str
    ) -> SuperMatchResponse:
        """
        Exécute le mode fallback en cas d'erreur
        
        Args:
            candidat: Données candidat
            offres: Offres
            options: Options
            error_message: Message d'erreur original
            
        Returns:
            Réponse en mode fallback
        """
        try:
            # Utiliser l'algorithme de fallback (le plus simple)
            fallback_results = self.fallback.execute_simple_matching(
                candidat, offres, options.limite
            )
            
            return SuperMatchResponse(
                status="fallback",
                algorithme_utilise="simple_fallback",
                temps_execution=0.1,
                resultats=fallback_results,
                meta={"fallback_reason": error_message},
                erreurs=[f"Erreur originale: {error_message}"]
            )
            
        except Exception as fallback_error:
            return SuperMatchResponse(
                status="error",
                algorithme_utilise="none",
                temps_execution=0.0,
                resultats=[],
                meta={},
                erreurs=[error_message, str(fallback_error)]
            )
    
    def get_algorithm_performance(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de performance des algorithmes
        
        Returns:
            Statistiques de performance
        """
        return self.performance.get_statistics()
    
    def get_available_algorithms(self) -> List[str]:
        """
        Retourne la liste des algorithmes disponibles
        
        Returns:
            Liste des noms d'algorithmes
        """
        return self.selector.get_available_algorithms()
