"""
Optimiseur Optuna pour le système de matching intelligent.

Utilise l'optimisation Bayésienne d'Optuna pour auto-tuner les poids
du système de matching et améliorer continuellement les performances.
"""

import logging
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime

try:
    import optuna
    from optuna.samplers import TPESampler
    from optuna.pruners import MedianPruner
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

from ..core.models import Candidate, Job, MatchResult
from ..matchers.enhanced_skills_matcher import EnhancedSkillsMatcher, MatchingMode

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Résultat d'une session d'optimisation."""
    best_params: Dict[str, Any]
    best_value: float
    n_trials: int
    optimization_time: float
    convergence_reached: bool
    improvement_percentage: float


@dataclass
class ValidationData:
    """Données de validation pour l'optimisation."""
    candidates: List[Candidate]
    jobs: List[Job]
    ground_truth: List[Dict[str, Any]]  # Expected matching scores/outcomes
    user_feedback: List[Dict[str, Any]]  # Historical user feedback


class OptunaMatchingOptimizer:
    """
    Optimiseur Optuna pour le système de matching intelligent.
    
    Utilise l'optimisation Bayésienne pour trouver automatiquement
    les meilleurs poids et hyperparamètres du système de matching.
    
    Fonctionnalités:
    - Optimisation multi-objectif (précision + diversité + performance)
    - Support de plusieurs algorithmes de sampling
    - Pruning automatique des essais non prometteurs
    - Sauvegarde et chargement d'études persistantes
    - Intégration avec le feedback utilisateur temps réel
    """
    
    def __init__(self, 
                 enhanced_matcher: EnhancedSkillsMatcher,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialise l'optimiseur Optuna.
        
        Args:
            enhanced_matcher: Le matcher principal à optimiser
            config: Configuration spécifique de l'optimiseur
        """
        if not OPTUNA_AVAILABLE:
            raise ImportError("optuna is required for optimization features")
        
        self.enhanced_matcher = enhanced_matcher
        self.config = config or self._get_default_config()
        
        # Configuration Optuna
        self.study_name = self.config.get('study_name', 'matching_optimization')
        self.storage_url = self.config.get('storage_url')  # For persistent studies
        self.n_trials = self.config.get('n_trials', 100)
        self.timeout = self.config.get('timeout_seconds', 3600)  # 1 hour default
        
        # Paramètres d'optimisation
        self.param_space = self.config.get('param_space', self._get_default_param_space())
        self.objective_weights = self.config.get('objective_weights', {
            'accuracy': 0.5,
            'diversity': 0.3,
            'performance': 0.2
        })
        
        # État interne
        self.study: Optional[optuna.Study] = None
        self.best_result: Optional[OptimizationResult] = None
        self.optimization_history: List[OptimizationResult] = []
        self.baseline_metrics: Optional[Dict[str, float]] = None
        
        # Callbacks pour monitoring
        self.callbacks: List[Callable] = []
        
        logger.info(f"OptunaMatchingOptimizer initialized for study: {self.study_name}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Configuration par défaut de l'optimiseur."""
        return {
            'study_name': 'matching_optimization',
            'storage_url': None,  # In-memory by default
            'n_trials': 100,
            'timeout_seconds': 3600,
            'sampler': 'TPE',  # Tree-structured Parzen Estimator
            'pruner': 'MedianPruner',
            'direction': 'maximize',
            'n_startup_trials': 10,
            'n_warmup_steps': 5,
            'pruning_percentile': 25.0,
            'enable_parallel': True,
            'n_jobs': 1,
            'seed': 42
        }
    
    def _get_default_param_space(self) -> Dict[str, Dict[str, Any]]:
        """Espace de recherche par défaut des hyperparamètres."""
        return {
            # Poids des modes de matching
            'embeddings_weight': {'type': 'float', 'low': 0.3, 'high': 0.9},
            'tfidf_weight': {'type': 'float', 'low': 0.1, 'high': 0.7},
            
            # Seuils sémantiques
            'semantic_threshold': {'type': 'float', 'low': 0.6, 'high': 0.9},
            'synonym_threshold': {'type': 'float', 'low': 0.7, 'high': 0.95},
            
            # Paramètres d'expansion
            'max_expanded_skills': {'type': 'int', 'low': 3, 'high': 10},
            
            # Bonus et facteurs
            'essential_skill_bonus': {'type': 'float', 'low': 1.1, 'high': 2.0},
            'nice_to_have_factor': {'type': 'float', 'low': 0.5, 'high': 0.9},
            
            # Mode de matching
            'matching_mode': {
                'type': 'categorical',
                'choices': [mode.value for mode in MatchingMode if mode != MatchingMode.AB_TESTING]
            }
        }
    
    def create_study(self, 
                    study_name: Optional[str] = None,
                    direction: str = 'maximize',
                    load_if_exists: bool = True) -> optuna.Study:
        """
        Crée ou charge une étude d'optimisation.
        
        Args:
            study_name: Nom de l'étude (utilise self.study_name si None)
            direction: Direction d'optimisation ('maximize' ou 'minimize')
            load_if_exists: Charge l'étude si elle existe déjà
            
        Returns:
            L'étude Optuna créée ou chargée
        """
        study_name = study_name or self.study_name
        
        # Configuration du sampler
        sampler_name = self.config.get('sampler', 'TPE')
        if sampler_name == 'TPE':
            sampler = TPESampler(
                n_startup_trials=self.config.get('n_startup_trials', 10),
                n_ei_candidates=self.config.get('n_ei_candidates', 24),
                seed=self.config.get('seed', 42)
            )
        else:
            sampler = None  # Use default
        
        # Configuration du pruner
        pruner_name = self.config.get('pruner', 'MedianPruner')
        if pruner_name == 'MedianPruner':
            pruner = MedianPruner(
                n_startup_trials=self.config.get('n_startup_trials', 10),
                n_warmup_steps=self.config.get('n_warmup_steps', 5),
                interval_steps=1
            )
        else:
            pruner = None  # Use default
        
        # Création de l'étude
        self.study = optuna.create_study(
            study_name=study_name,
            direction=direction,
            sampler=sampler,
            pruner=pruner,
            storage=self.storage_url,
            load_if_exists=load_if_exists
        )
        
        logger.info(f"Study '{study_name}' created/loaded with {len(self.study.trials)} existing trials")
        return self.study
    
    def suggest_hyperparameters(self, trial: optuna.Trial) -> Dict[str, Any]:
        """
        Suggère des hyperparamètres pour un essai donné.
        
        Args:
            trial: Essai Optuna en cours
            
        Returns:
            Dictionnaire des hyperparamètres suggérés
        """
        params = {}
        
        for param_name, param_config in self.param_space.items():
            param_type = param_config['type']
            
            if param_type == 'float':
                params[param_name] = trial.suggest_float(
                    param_name,
                    param_config['low'],
                    param_config['high']
                )
            elif param_type == 'int':
                params[param_name] = trial.suggest_int(
                    param_name,
                    param_config['low'],
                    param_config['high']
                )
            elif param_type == 'categorical':
                params[param_name] = trial.suggest_categorical(
                    param_name,
                    param_config['choices']
                )
            elif param_type == 'discrete_uniform':
                params[param_name] = trial.suggest_discrete_uniform(
                    param_name,
                    param_config['low'],
                    param_config['high'],
                    param_config['q']
                )
        
        # Contrainte : embeddings_weight + tfidf_weight = 1.0
        if 'embeddings_weight' in params and 'tfidf_weight' in params:
            total_weight = params['embeddings_weight'] + params['tfidf_weight']
            params['embeddings_weight'] = params['embeddings_weight'] / total_weight
            params['tfidf_weight'] = params['tfidf_weight'] / total_weight
        
        return params
    
    async def objective_function(self, 
                                trial: optuna.Trial,
                                validation_data: ValidationData) -> float:
        """
        Fonction objectif pour Optuna.
        
        Évalue la performance du système de matching avec des paramètres donnés.
        
        Args:
            trial: Essai Optuna en cours
            validation_data: Données de validation
            
        Returns:
            Score à maximiser/minimiser
        """
        from .objective_functions import MultiObjectiveFunction
        
        # Suggérer les hyperparamètres
        params = self.suggest_hyperparameters(trial)
        
        # Appliquer les paramètres au matcher
        self._apply_parameters_to_matcher(params)
        
        # Calculer les matchings avec les nouveaux paramètres
        start_time = time.time()
        matching_results = []
        execution_times = []
        
        for candidate, job in zip(validation_data.candidates, validation_data.jobs):
            match_start = time.time()
            
            try:
                result = await self.enhanced_matcher.calculate_match(candidate, job)
                matching_results.append(result)
                execution_times.append(time.time() - match_start)
                
                # Pruning: arrêter si l'essai ne semble pas prometteur
                if len(matching_results) % 10 == 0:  # Check every 10 matches
                    intermediate_score = self._calculate_intermediate_score(
                        matching_results[-10:], execution_times[-10:]
                    )
                    trial.report(intermediate_score, len(matching_results))
                    
                    if trial.should_prune():
                        logger.debug(f"Trial {trial.number} pruned at step {len(matching_results)}")
                        raise optuna.TrialPruned()
                        
            except Exception as e:
                logger.warning(f"Error in matching during optimization: {e}")
                # Pénaliser les configurations qui causent des erreurs
                return 0.0
        
        total_time = time.time() - start_time
        
        # Calculer le score avec la fonction objectif multi-critères
        objective_func = MultiObjectiveFunction(weights=self.objective_weights)
        final_score = await objective_func.evaluate(
            matching_results,
            validation_data.ground_truth,
            execution_times,
            validation_data.user_feedback
        )
        
        # Log des métriques pour monitoring
        logger.debug(f"Trial {trial.number}: score={final_score:.4f}, params={params}")
        
        # Store additional metrics in trial
        trial.set_user_attr('total_time', total_time)
        trial.set_user_attr('avg_execution_time', sum(execution_times) / len(execution_times))
        trial.set_user_attr('n_matches', len(matching_results))
        
        return final_score
    
    def _apply_parameters_to_matcher(self, params: Dict[str, Any]) -> None:
        """Applique les paramètres suggérés au matcher."""
        config_updates = {}
        
        # Map parameters to matcher configuration
        if 'embeddings_weight' in params:
            config_updates['embeddings_weight'] = params['embeddings_weight']
        if 'tfidf_weight' in params:
            config_updates['tfidf_weight'] = params['tfidf_weight']
        if 'semantic_threshold' in params:
            config_updates['semantic_threshold'] = params['semantic_threshold']
        if 'synonym_threshold' in params:
            config_updates['synonym_threshold'] = params['synonym_threshold']
        if 'max_expanded_skills' in params:
            config_updates['max_expanded_skills'] = params['max_expanded_skills']
        if 'essential_skill_bonus' in params:
            config_updates['essential_skill_bonus'] = params['essential_skill_bonus']
        if 'nice_to_have_factor' in params:
            config_updates['nice_to_have_factor'] = params['nice_to_have_factor']
        if 'matching_mode' in params:
            config_updates['matching_mode'] = params['matching_mode']
        
        # Update matcher configuration
        for key, value in config_updates.items():
            setattr(self.enhanced_matcher, key, value)
        
        # Update internal config
        self.enhanced_matcher.config.update(config_updates)
    
    def _calculate_intermediate_score(self, 
                                    recent_results: List[MatchResult],
                                    recent_times: List[float]) -> float:
        """Calcule un score intermédiaire pour le pruning."""
        if not recent_results:
            return 0.0
        
        # Simple scoring basé sur les scores moyens et temps de réponse
        avg_score = sum(result.overall_score for result in recent_results) / len(recent_results)
        avg_time = sum(recent_times) / len(recent_times)
        
        # Pénaliser les temps de réponse trop longs
        time_penalty = max(0, (avg_time - 1.0) * 0.1)  # Pénalité si >1sec
        
        return avg_score - time_penalty
    
    async def optimize(self, 
                      validation_data: ValidationData,
                      n_trials: Optional[int] = None,
                      timeout: Optional[int] = None) -> OptimizationResult:
        """
        Lance l'optimisation Bayésienne.
        
        Args:
            validation_data: Données pour valider les hyperparamètres
            n_trials: Nombre d'essais (utilise self.n_trials si None)
            timeout: Timeout en secondes (utilise self.timeout si None)
            
        Returns:
            Résultat de l'optimisation
        """
        n_trials = n_trials or self.n_trials
        timeout = timeout or self.timeout
        
        if self.study is None:
            self.create_study()
        
        # Mesurer les performances de base
        if self.baseline_metrics is None:
            self.baseline_metrics = await self._measure_baseline_performance(validation_data)
        
        start_time = time.time()
        initial_best_value = self.study.best_value if self.study.trials else None
        
        logger.info(f"Starting optimization with {n_trials} trials, timeout {timeout}s")
        
        # Wrapper pour la fonction objectif asynchrone
        def objective_wrapper(trial):
            return asyncio.run(self.objective_function(trial, validation_data))
        
        try:
            # Lancer l'optimisation
            if self.config.get('enable_parallel', False):
                # Optimisation parallèle
                self.study.optimize(
                    objective_wrapper,
                    n_trials=n_trials,
                    timeout=timeout,
                    n_jobs=self.config.get('n_jobs', 1),
                    callbacks=self.callbacks
                )
            else:
                # Optimisation séquentielle
                self.study.optimize(
                    objective_wrapper,
                    n_trials=n_trials,
                    timeout=timeout,
                    callbacks=self.callbacks
                )
        
        except KeyboardInterrupt:
            logger.info("Optimization interrupted by user")
        except Exception as e:
            logger.error(f"Error during optimization: {e}")
            raise
        
        # Calculer les résultats
        optimization_time = time.time() - start_time
        best_value = self.study.best_value
        best_params = self.study.best_params
        
        # Calculer l'amélioration
        if initial_best_value is not None:
            improvement = ((best_value - initial_best_value) / initial_best_value) * 100
        else:
            baseline_score = self.baseline_metrics.get('overall_score', 0.5)
            improvement = ((best_value - baseline_score) / baseline_score) * 100
        
        # Vérifier la convergence
        convergence_reached = self._check_convergence()
        
        # Créer le résultat
        result = OptimizationResult(
            best_params=best_params,
            best_value=best_value,
            n_trials=len(self.study.trials),
            optimization_time=optimization_time,
            convergence_reached=convergence_reached,
            improvement_percentage=improvement
        )
        
        self.best_result = result
        self.optimization_history.append(result)
        
        logger.info(f"Optimization completed: best_value={best_value:.4f}, "
                   f"improvement={improvement:.2f}%, trials={len(self.study.trials)}")
        
        return result
    
    async def _measure_baseline_performance(self, 
                                          validation_data: ValidationData) -> Dict[str, float]:
        """Mesure les performances de base avant optimisation."""
        logger.info("Measuring baseline performance...")
        
        baseline_results = []
        execution_times = []
        
        for candidate, job in zip(validation_data.candidates[:10], validation_data.jobs[:10]):
            start_time = time.time()
            result = await self.enhanced_matcher.calculate_match(candidate, job)
            execution_times.append(time.time() - start_time)
            baseline_results.append(result)
        
        avg_score = sum(r.overall_score for r in baseline_results) / len(baseline_results)
        avg_time = sum(execution_times) / len(execution_times)
        
        baseline = {
            'overall_score': avg_score,
            'avg_execution_time': avg_time,
            'n_samples': len(baseline_results)
        }
        
        logger.info(f"Baseline measured: score={avg_score:.4f}, time={avg_time:.3f}s")
        return baseline
    
    def _check_convergence(self, patience: int = 20, tolerance: float = 0.001) -> bool:
        """Vérifie si l'optimisation a convergé."""
        if len(self.study.trials) < patience * 2:
            return False
        
        # Vérifier si les derniers essais n'améliorent plus significativement
        recent_values = [t.value for t in self.study.trials[-patience:] if t.value is not None]
        
        if len(recent_values) < patience:
            return False
        
        best_recent = max(recent_values)
        previous_best = max(t.value for t in self.study.trials[:-patience] if t.value is not None)
        
        improvement = (best_recent - previous_best) / previous_best if previous_best > 0 else 0
        
        return improvement < tolerance
    
    def get_best_configuration(self) -> Dict[str, Any]:
        """
        Retourne la meilleure configuration trouvée.
        
        Returns:
            Configuration optimale des hyperparamètres
        """
        if self.study is None or not self.study.trials:
            logger.warning("No optimization study found or no trials completed")
            return {}
        
        best_params = self.study.best_params.copy()
        
        # Ajouter des métadonnées
        best_trial = self.study.best_trial
        best_params['_metadata'] = {
            'best_value': self.study.best_value,
            'trial_number': best_trial.number,
            'optimization_date': datetime.now().isoformat(),
            'n_total_trials': len(self.study.trials),
            'user_attrs': best_trial.user_attrs
        }
        
        return best_params
    
    def apply_best_configuration(self) -> None:
        """Applique la meilleure configuration trouvée au matcher."""
        if self.best_result is None:
            logger.warning("No optimization result available")
            return
        
        self._apply_parameters_to_matcher(self.best_result.best_params)
        logger.info(f"Applied best configuration with score {self.best_result.best_value:.4f}")
    
    def add_callback(self, callback: Callable) -> None:
        """Ajoute un callback de monitoring."""
        self.callbacks.append(callback)
    
    def get_optimization_history(self) -> List[OptimizationResult]:
        """Retourne l'historique des optimisations."""
        return self.optimization_history.copy()
    
    def save_study(self, file_path: str) -> None:
        """Sauvegarde l'étude dans un fichier."""
        if self.study is None:
            logger.warning("No study to save")
            return
        
        import pickle
        with open(file_path, 'wb') as f:
            pickle.dump(self.study, f)
        
        logger.info(f"Study saved to {file_path}")
    
    def load_study(self, file_path: str) -> None:
        """Charge une étude depuis un fichier."""
        import pickle
        with open(file_path, 'rb') as f:
            self.study = pickle.load(f)
        
        logger.info(f"Study loaded from {file_path} with {len(self.study.trials)} trials")
    
    def get_parameter_importance(self) -> Dict[str, float]:
        """Calcule l'importance de chaque paramètre."""
        if self.study is None or len(self.study.trials) < 10:
            logger.warning("Not enough trials to calculate parameter importance")
            return {}
        
        try:
            importance = optuna.importance.get_param_importances(self.study)
            return importance
        except Exception as e:
            logger.warning(f"Error calculating parameter importance: {e}")
            return {}
    
    def get_optimization_insights(self) -> Dict[str, Any]:
        """Génère des insights sur l'optimisation."""
        if self.study is None:
            return {}
        
        trials = self.study.trials
        completed_trials = [t for t in trials if t.state == optuna.trial.TrialState.COMPLETE]
        
        if not completed_trials:
            return {}
        
        values = [t.value for t in completed_trials]
        
        insights = {
            'total_trials': len(trials),
            'completed_trials': len(completed_trials),
            'best_value': max(values),
            'worst_value': min(values),
            'mean_value': sum(values) / len(values),
            'std_value': (sum((v - sum(values) / len(values))**2 for v in values) / len(values))**0.5,
            'improvement_over_trials': (max(values) - values[0]) / values[0] * 100 if values[0] > 0 else 0,
            'parameter_importance': self.get_parameter_importance(),
            'convergence_reached': self._check_convergence(),
            'pruned_trials': len([t for t in trials if t.state == optuna.trial.TrialState.PRUNED])
        }
        
        return insights
