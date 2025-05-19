"""
Configuration Management for SmartMatcher
-----------------------------------------
Gère la configuration centralisée du système de matching.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field
from .exceptions import ConfigurationError


@dataclass
class WeightsConfig:
    """Configuration des poids des différents critères"""
    skills: float = 0.40
    location: float = 0.25
    experience: float = 0.15
    education: float = 0.10
    preferences: float = 0.10
    
    def validate(self) -> None:
        """Valide que la somme des poids fait 1.0"""
        total = self.skills + self.location + self.experience + self.education + self.preferences
        if abs(total - 1.0) > 0.001:  # Tolérance pour les erreurs d'arrondi
            raise ConfigurationError(f"La somme des poids doit faire 1.0, trouvé: {total}")
        
        # Vérifier que tous les poids sont positifs
        for name, weight in [
            ("skills", self.skills),
            ("location", self.location), 
            ("experience", self.experience),
            ("education", self.education),
            ("preferences", self.preferences)
        ]:
            if weight < 0:
                raise ConfigurationError(f"Le poids '{name}' doit être positif, trouvé: {weight}")


@dataclass
class ThresholdsConfig:
    """Configuration des seuils de qualification"""
    minimum_score: float = 0.30
    excellent_match: float = 0.85
    good_match: float = 0.70
    moderate_match: float = 0.50
    
    def validate(self) -> None:
        """Valide la cohérence des seuils"""
        thresholds = [
            ("minimum_score", self.minimum_score),
            ("moderate_match", self.moderate_match),
            ("good_match", self.good_match),
            ("excellent_match", self.excellent_match)
        ]
        
        # Vérifier que tous les seuils sont entre 0 et 1
        for name, threshold in thresholds:
            if not (0 <= threshold <= 1):
                raise ConfigurationError(
                    f"Le seuil '{name}' doit être entre 0 et 1, trouvé: {threshold}"
                )
        
        # Vérifier l'ordre croissant
        if not (self.minimum_score <= self.moderate_match <= 
                self.good_match <= self.excellent_match):
            raise ConfigurationError(
                "Les seuils doivent être en ordre croissant: "
                f"minimum({self.minimum_score}) <= moderate({self.moderate_match}) <= "
                f"good({self.good_match}) <= excellent({self.excellent_match})"
            )


@dataclass
class PerformanceConfig:
    """Configuration des paramètres de performance"""
    cache_ttl_seconds: int = 86400  # 24 heures
    max_concurrent_matches: int = 100
    batch_size: int = 50
    timeout_seconds: int = 30
    max_memory_mb: int = 512
    enable_parallel_processing: bool = True
    
    def validate(self) -> None:
        """Valide les paramètres de performance"""
        if self.cache_ttl_seconds <= 0:
            raise ConfigurationError(f"cache_ttl_seconds doit être positif: {self.cache_ttl_seconds}")
        
        if self.max_concurrent_matches <= 0:
            raise ConfigurationError(f"max_concurrent_matches doit être positif: {self.max_concurrent_matches}")
        
        if self.batch_size <= 0:
            raise ConfigurationError(f"batch_size doit être positif: {self.batch_size}")
        
        if self.timeout_seconds <= 0:
            raise ConfigurationError(f"timeout_seconds doit être positif: {self.timeout_seconds}")
        
        if self.max_memory_mb <= 0:
            raise ConfigurationError(f"max_memory_mb doit être positif: {self.max_memory_mb}")


@dataclass
class NLPConfig:
    """Configuration du service NLP"""
    vectorizer_type: str = "tfidf"  # "tfidf", "word2vec", "bert"
    enable_synonyms: bool = True
    synonym_similarity_threshold: float = 0.85
    stop_words_language: str = "english"
    max_features: int = 10000
    ngram_range: tuple = (1, 2)
    
    def validate(self) -> None:
        """Valide la configuration NLP"""
        valid_vectorizers = ["tfidf", "word2vec", "bert"]
        if self.vectorizer_type not in valid_vectorizers:
            raise ConfigurationError(
                f"vectorizer_type doit être dans {valid_vectorizers}, trouvé: {self.vectorizer_type}"
            )
        
        if not (0 <= self.synonym_similarity_threshold <= 1):
            raise ConfigurationError(
                f"synonym_similarity_threshold doit être entre 0 et 1: {self.synonym_similarity_threshold}"
            )
        
        if self.max_features <= 0:
            raise ConfigurationError(f"max_features doit être positif: {self.max_features}")


@dataclass
class LocationConfig:
    """Configuration du service de géolocalisation"""
    google_maps_api_key: Optional[str] = None
    default_transport_mode: str = "driving"  # driving, walking, transit, bicycling
    cache_travel_times: bool = True
    max_travel_time_minutes: int = 180
    fallback_to_coordinates: bool = True
    
    def validate(self) -> None:
        """Valide la configuration de géolocalisation"""
        valid_modes = ["driving", "walking", "transit", "bicycling"]
        if self.default_transport_mode not in valid_modes:
            raise ConfigurationError(
                f"default_transport_mode doit être dans {valid_modes}, trouvé: {self.default_transport_mode}"
            )
        
        if self.max_travel_time_minutes <= 0:
            raise ConfigurationError(
                f"max_travel_time_minutes doit être positif: {self.max_travel_time_minutes}"
            )


@dataclass
class CacheConfig:
    """Configuration du système de cache"""
    enabled: bool = True
    backend: str = "memory"  # memory, redis, file
    redis_url: Optional[str] = None
    file_cache_dir: Optional[str] = None
    max_memory_items: int = 10000
    compression: bool = False
    
    def validate(self) -> None:
        """Valide la configuration du cache"""
        valid_backends = ["memory", "redis", "file"]
        if self.backend not in valid_backends:
            raise ConfigurationError(
                f"Cache backend doit être dans {valid_backends}, trouvé: {self.backend}"
            )
        
        if self.backend == "redis" and not self.redis_url:
            raise ConfigurationError("redis_url requis pour le backend Redis")
        
        if self.backend == "file" and not self.file_cache_dir:
            raise ConfigurationError("file_cache_dir requis pour le backend File")
        
        if self.max_memory_items <= 0:
            raise ConfigurationError(f"max_memory_items doit être positif: {self.max_memory_items}")


@dataclass
class SmartMatchConfig:
    """Configuration globale du SmartMatcher"""
    weights: WeightsConfig = field(default_factory=WeightsConfig)
    thresholds: ThresholdsConfig = field(default_factory=ThresholdsConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    nlp: NLPConfig = field(default_factory=NLPConfig)
    location: LocationConfig = field(default_factory=LocationConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    
    # Configuration générale
    debug: bool = False
    log_level: str = "INFO"
    metrics_enabled: bool = True
    version: str = "2.0.0"
    
    def validate(self) -> None:
        """Valide toute la configuration"""
        self.weights.validate()
        self.thresholds.validate()
        self.performance.validate()
        self.nlp.validate()
        self.location.validate()
        self.cache.validate()
        
        # Valider le niveau de log
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ConfigurationError(
                f"log_level doit être dans {valid_log_levels}, trouvé: {self.log_level}"
            )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SmartMatchConfig':
        """Crée une configuration à partir d'un dictionnaire"""
        try:
            return cls(
                weights=WeightsConfig(**config_dict.get('weights', {})),
                thresholds=ThresholdsConfig(**config_dict.get('thresholds', {})),
                performance=PerformanceConfig(**config_dict.get('performance', {})),
                nlp=NLPConfig(**config_dict.get('nlp', {})),
                location=LocationConfig(**config_dict.get('location', {})),
                cache=CacheConfig(**config_dict.get('cache', {})),
                debug=config_dict.get('debug', False),
                log_level=config_dict.get('log_level', 'INFO'),
                metrics_enabled=config_dict.get('metrics_enabled', True),
                version=config_dict.get('version', '2.0.0')
            )
        except Exception as e:
            raise ConfigurationError(f"Erreur lors de la création de la configuration: {str(e)}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire"""
        return {
            'weights': {
                'skills': self.weights.skills,
                'location': self.weights.location,
                'experience': self.weights.experience,
                'education': self.weights.education,
                'preferences': self.weights.preferences
            },
            'thresholds': {
                'minimum_score': self.thresholds.minimum_score,
                'excellent_match': self.thresholds.excellent_match,
                'good_match': self.thresholds.good_match,
                'moderate_match': self.thresholds.moderate_match
            },
            'performance': {
                'cache_ttl_seconds': self.performance.cache_ttl_seconds,
                'max_concurrent_matches': self.performance.max_concurrent_matches,
                'batch_size': self.performance.batch_size,
                'timeout_seconds': self.performance.timeout_seconds,
                'max_memory_mb': self.performance.max_memory_mb,
                'enable_parallel_processing': self.performance.enable_parallel_processing
            },
            'nlp': {
                'vectorizer_type': self.nlp.vectorizer_type,
                'enable_synonyms': self.nlp.enable_synonyms,
                'synonym_similarity_threshold': self.nlp.synonym_similarity_threshold,
                'stop_words_language': self.nlp.stop_words_language,
                'max_features': self.nlp.max_features,
                'ngram_range': self.nlp.ngram_range
            },
            'location': {
                'google_maps_api_key': self.location.google_maps_api_key,
                'default_transport_mode': self.location.default_transport_mode,
                'cache_travel_times': self.location.cache_travel_times,
                'max_travel_time_minutes': self.location.max_travel_time_minutes,
                'fallback_to_coordinates': self.location.fallback_to_coordinates
            },
            'cache': {
                'enabled': self.cache.enabled,
                'backend': self.cache.backend,
                'redis_url': self.cache.redis_url,
                'file_cache_dir': self.cache.file_cache_dir,
                'max_memory_items': self.cache.max_memory_items,
                'compression': self.cache.compression
            },
            'debug': self.debug,
            'log_level': self.log_level,
            'metrics_enabled': self.metrics_enabled,
            'version': self.version
        }


class ConfigurationManager:
    """Gestionnaire de configuration pour le SmartMatcher"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le gestionnaire de configuration
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config_path = config_path
        self._config: Optional[SmartMatchConfig] = None
    
    def load_config(self, config_path: Optional[str] = None) -> SmartMatchConfig:
        """
        Charge la configuration depuis un fichier ou les variables d'environnement
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Configuration chargée et validée
        """
        config_path = config_path or self.config_path
        
        # Commencer avec la configuration par défaut
        config_dict = {}
        
        # 1. Charger depuis un fichier si fourni
        if config_path:
            config_dict = self._load_from_file(config_path)
        
        # 2. Surcharger avec les variables d'environnement
        env_config = self._load_from_environment()
        self._deep_update(config_dict, env_config)
        
        # 3. Créer et valider la configuration
        self._config = SmartMatchConfig.from_dict(config_dict)
        self._config.validate()
        
        return self._config
    
    def get_config(self) -> SmartMatchConfig:
        """
        Retourne la configuration courante
        
        Returns:
            Configuration courante ou configuration par défaut si non chargée
        """
        if self._config is None:
            return self.load_config()
        return self._config
    
    def reload_config(self) -> SmartMatchConfig:
        """
        Recharge la configuration
        
        Returns:
            Configuration rechargée
        """
        self._config = None
        return self.load_config()
    
    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Charge la configuration depuis un fichier (JSON ou YAML)"""
        path = Path(file_path)
        
        if not path.exists():
            raise ConfigurationError(f"Fichier de configuration non trouvé: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yml', '.yaml']:
                    return yaml.safe_load(f) or {}
                elif path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    raise ConfigurationError(
                        f"Format de fichier non supporté: {path.suffix}. "
                        "Utilisez .json, .yml ou .yaml"
                    )
        except Exception as e:
            raise ConfigurationError(f"Erreur lors du chargement du fichier {file_path}: {str(e)}")
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Charge la configuration depuis les variables d'environnement"""
        env_config = {}
        
        # Variables d'environnement avec préfixe SMARTMATCH_
        prefix = "SMARTMATCH_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convertir SMARTMATCH_WEIGHTS_SKILLS en ['weights', 'skills']
                config_key = key[len(prefix):].lower().split('_')
                
                # Convertir la valeur en type approprié
                converted_value = self._convert_env_value(value)
                
                # Créer la structure imbriquée
                self._set_nested_value(env_config, config_key, converted_value)
        
        # Variables spéciales
        if 'GOOGLE_MAPS_API_KEY' in os.environ:
            env_config.setdefault('location', {})['google_maps_api_key'] = os.environ['GOOGLE_MAPS_API_KEY']
        
        if 'REDIS_URL' in os.environ:
            env_config.setdefault('cache', {})['redis_url'] = os.environ['REDIS_URL']
        
        return env_config
    
    def _convert_env_value(self, value: str) -> Any:
        """Convertit une valeur de variable d'environnement en type approprié"""
        # Booléens
        if value.lower() in ['true', '1', 'yes', 'on']:
            return True
        if value.lower() in ['false', '0', 'no', 'off']:
            return False
        
        # Nombres
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # String par défaut
        return value
    
    def _set_nested_value(self, config_dict: Dict[str, Any], keys: List[str], value: Any) -> None:
        """Définit une valeur dans un dictionnaire imbriqué"""
        current = config_dict
        for key in keys[:-1]:
            current = current.setdefault(key, {})
        current[keys[-1]] = value
    
    def _deep_update(self, base_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> None:
        """Met à jour récursivement un dictionnaire"""
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                self._deep_update(base_dict[key], value)
            else:
                base_dict[key] = value
    
    def save_config(self, file_path: str) -> None:
        """
        Sauvegarde la configuration courante dans un fichier
        
        Args:
            file_path: Chemin où sauvegarder la configuration
        """
        if self._config is None:
            raise ConfigurationError("Aucune configuration à sauvegarder")
        
        config_dict = self._config.to_dict()
        path = Path(file_path)
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                if path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                elif path.suffix.lower() == '.json':
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)
                else:
                    raise ConfigurationError(
                        f"Format de fichier non supporté: {path.suffix}. "
                        "Utilisez .json, .yml ou .yaml"
                    )
        except Exception as e:
            raise ConfigurationError(f"Erreur lors de la sauvegarde: {str(e)}")


# Instance globale du gestionnaire de configuration
config_manager = ConfigurationManager()


def get_config() -> SmartMatchConfig:
    """Raccourci pour obtenir la configuration courante"""
    return config_manager.get_config()


def load_config(config_path: str) -> SmartMatchConfig:
    """Raccourci pour charger une configuration"""
    return config_manager.load_config(config_path)
