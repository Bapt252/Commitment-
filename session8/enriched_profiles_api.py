"""
API de profils enrichis.

Ce module fournit une API pour accéder aux profils utilisateurs enrichis avec des
données comportementales et des préférences calculées.
"""

from flask import Flask, jsonify, request, abort
import logging
from typing import Dict, Any, Optional, List
import json
import jwt
import datetime
import os
from functools import wraps

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class EnrichedProfilesAPI:
    """
    API pour accéder aux profils utilisateurs enrichis.
    """
    
    def __init__(self, profile_manager=None, preference_calculator=None, user_clustering=None, 
                 pattern_detector=None, config=None):
        """
        Initialise l'API de profils enrichis.
        
        Args:
            profile_manager: Gestionnaire de profils utilisateurs
            preference_calculator: Calculateur de préférences
            user_clustering: Module de clustering d'utilisateurs
            pattern_detector: Détecteur de patterns comportementaux
            config: Configuration de l'API
        """
        self.profile_manager = profile_manager
        self.preference_calculator = preference_calculator
        self.user_clustering = user_clustering
        self.pattern_detector = pattern_detector
        
        # Configuration par défaut
        self.config = {
            "port": 5000,
            "host": "0.0.0.0",
            "debug": False,
            "secret_key": "your-secret-key-here",
            "auth_enabled": True,
            "cors_origins": ["*"],
            "rate_limit": {
                "enabled": True,
                "limit": 100,
                "period": 60
            }
        }
        
        # Mise à jour de la configuration si fournie
        if config:
            self.config.update(config)
        
        # Initialisation de l'application Flask
        self.app = Flask(__name__)
        self.app.secret_key = self.config["secret_key"]
        
        # Configuration CORS
        if self.config["cors_origins"]:
            try:
                from flask_cors import CORS
                CORS(self.app, resources={r"/api/*": {"origins": self.config["cors_origins"]}})
                logger.info(f"CORS enabled for origins: {self.config['cors_origins']}")
            except ImportError:
                logger.warning("flask_cors not installed, CORS not enabled")
        
        # Configuration rate limiting
        if self.config["rate_limit"]["enabled"]:
            try:
                from flask_limiter import Limiter
                from flask_limiter.util import get_remote_address
                
                self.limiter = Limiter(
                    app=self.app,
                    key_func=get_remote_address,
                    default_limits=[f"{self.config['rate_limit']['limit']} per {self.config['rate_limit']['period']} second"]
                )
                logger.info(f"Rate limiting enabled: {self.config['rate_limit']['limit']} per {self.config['rate_limit']['period']} second")
            except ImportError:
                logger.warning("flask_limiter not installed, rate limiting not enabled")
        
        # Définition des routes
        self._setup_routes()
        
        logger.info("EnrichedProfilesAPI initialized")
    
    def _setup_routes(self):
        """Configure les routes de l'API."""
        
        # Décorateur pour l'authentification
        def token_required(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                if not self.config["auth_enabled"]:
                    return f(*args, **kwargs)
                
                token = None
                auth_header = request.headers.get("Authorization")
                
                if auth_header:
                    if auth_header.startswith("Bearer "):
                        token = auth_header.split(" ")[1]
                
                if not token:
                    return jsonify({"message": "Authentication token is missing"}), 401
                
                try:
                    data = jwt.decode(token, self.app.secret_key, algorithms=["HS256"])
                    if "user_id" not in data:
                        return jsonify({"message": "Invalid token"}), 401
                except Exception as e:
                    return jsonify({"message": f"Invalid token: {str(e)}"}), 401
                
                return f(*args, **kwargs)
            
            return decorated
        
        # Route pour vérifier la santé de l'API
        @self.app.route("/api/profile/health", methods=["GET"])
        def health_check():
            return jsonify({"status": "ok", "message": "EnrichedProfilesAPI is running"})
        
        # Route pour l'authentification (simulation)
        @self.app.route("/api/profile/auth", methods=["POST"])
        def auth():
            auth_data = request.json
            
            if not auth_data or "username" not in auth_data or "password" not in auth_data:
                return jsonify({"message": "Missing username or password"}), 400
            
            # Simuler l'authentification (dans un environnement réel, vérifier avec une base de données)
            # Pour les tests, n'importe quel utilisateur/mot de passe est accepté
            user_id = f"user_{hash(auth_data['username'])}"
            
            # Générer un token JWT
            token = jwt.encode(
                {
                    "user_id": user_id,
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                },
                self.app.secret_key,
                algorithm="HS256"
            )
            
            return jsonify({"token": token, "user_id": user_id})
        
        # Route pour obtenir un profil enrichi
        @self.app.route("/api/profile/<user_id>", methods=["GET"])
        @token_required
        def get_profile(user_id):
            if not self.profile_manager:
                return jsonify({"message": "Profile manager not configured"}), 500
            
            profile = self.profile_manager.get_profile(user_id)
            if not profile:
                return jsonify({"message": f"Profile for user {user_id} not found"}), 404
            
            return jsonify(profile)
        
        # Route pour obtenir les préférences calculées
        @self.app.route("/api/profile/<user_id>/preferences", methods=["GET"])
        @token_required
        def get_preferences(user_id):
            if not self.preference_calculator:
                return jsonify({"message": "Preference calculator not configured"}), 500
            
            preferences = self.preference_calculator.get_preferences(user_id)
            if not preferences:
                return jsonify({"message": f"Preferences for user {user_id} not found"}), 404
            
            return jsonify(preferences)
        
        # Route pour obtenir les patterns comportementaux
        @self.app.route("/api/profile/<user_id>/patterns", methods=["GET"])
        @token_required
        def get_patterns(user_id):
            if not self.pattern_detector:
                return jsonify({"message": "Pattern detector not configured"}), 500
            
            patterns = self.pattern_detector.get_user_patterns(user_id)
            if not patterns:
                return jsonify({"message": f"Patterns for user {user_id} not found"}), 404
            
            return jsonify(patterns)
        
        # Route pour obtenir les informations de clustering
        @self.app.route("/api/profile/<user_id>/cluster", methods=["GET"])
        @token_required
        def get_cluster_info(user_id):
            if not self.user_clustering:
                return jsonify({"message": "User clustering not configured"}), 500
            
            cluster_info = self.user_clustering.get_user_cluster(user_id)
            if not cluster_info:
                return jsonify({"message": f"Cluster info for user {user_id} not found"}), 404
            
            return jsonify(cluster_info)
        
        # Route pour obtenir toutes les informations enrichies en une seule requête
        @self.app.route("/api/profile/<user_id>/enriched", methods=["GET"])
        @token_required
        def get_enriched_profile(user_id):
            enriched_profile = {"user_id": user_id}
            
            # Récupérer le profil de base
            if self.profile_manager:
                profile = self.profile_manager.get_profile(user_id)
                if profile:
                    enriched_profile["profile"] = profile
            
            # Récupérer les préférences
            if self.preference_calculator:
                preferences = self.preference_calculator.get_preferences(user_id)
                if preferences:
                    enriched_profile["preferences"] = preferences
            
            # Récupérer les patterns
            if self.pattern_detector:
                patterns = self.pattern_detector.get_user_patterns(user_id)
                if patterns:
                    enriched_profile["patterns"] = patterns
            
            # Récupérer les informations de clustering
            if self.user_clustering:
                cluster_info = self.user_clustering.get_user_cluster(user_id)
                if cluster_info:
                    enriched_profile["cluster"] = cluster_info
            
            if len(enriched_profile) == 1:  # Seulement user_id
                return jsonify({"message": f"No enriched data found for user {user_id}"}), 404
            
            return jsonify(enriched_profile)
        
        # Route pour les recommandations basées sur les préférences
        @self.app.route("/api/profile/<user_id>/recommendations", methods=["GET"])
        @token_required
        def get_recommendations(user_id):
            if not self.preference_calculator:
                return jsonify({"message": "Preference calculator not configured"}), 500
            
            item_type = request.args.get("type", "job")
            limit = int(request.args.get("limit", 10))
            
            # Simuler des recommandations basées sur les préférences
            items = self._generate_mock_recommendations(user_id, item_type, limit)
            
            return jsonify({"recommendations": items})
        
        # Route pour mettre à jour un profil (données de base uniquement)
        @self.app.route("/api/profile/<user_id>", methods=["PUT"])
        @token_required
        def update_profile(user_id):
            if not self.profile_manager:
                return jsonify({"message": "Profile manager not configured"}), 500
            
            profile_data = request.json
            if not profile_data:
                return jsonify({"message": "No profile data provided"}), 400
            
            try:
                updated = self.profile_manager.update_profile(user_id, profile_data)
                if updated:
                    return jsonify({"message": f"Profile for user {user_id} updated successfully"})
                else:
                    return jsonify({"message": f"Failed to update profile for user {user_id}"}), 500
            except Exception as e:
                return jsonify({"message": f"Error updating profile: {str(e)}"}), 500
        
        # Route pour déclencher un recalcul des données enrichies
        @self.app.route("/api/profile/<user_id>/recalculate", methods=["POST"])
        @token_required
        def recalculate_enriched_data(user_id):
            results = {}
            
            # Recalculer les préférences
            if self.preference_calculator:
                try:
                    preferences = self.preference_calculator.calculate_preferences(user_id)
                    results["preferences"] = "recalculated"
                except Exception as e:
                    results["preferences"] = f"error: {str(e)}"
            
            # Recalculer les patterns
            if self.pattern_detector:
                try:
                    patterns = self.pattern_detector.analyze_user_patterns(user_id)
                    results["patterns"] = "recalculated"
                except Exception as e:
                    results["patterns"] = f"error: {str(e)}"
            
            # Mettre à jour le clustering
            if self.user_clustering:
                try:
                    self.user_clustering.update_clusters()
                    results["clustering"] = "recalculated"
                except Exception as e:
                    results["clustering"] = f"error: {str(e)}"
            
            if not results:
                return jsonify({"message": "No recalculation performed, components not configured"}), 500
            
            return jsonify({"results": results})
        
        logger.info("API routes configured")
    
    def _generate_mock_recommendations(self, user_id: str, item_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Génère des recommandations simulées pour les tests.
        
        Args:
            user_id: Identifiant de l'utilisateur
            item_type: Type d'élément à recommander
            limit: Nombre de recommandations à générer
            
        Returns:
            Liste des recommandations simulées
        """
        import random
        
        recommendations = []
        
        if item_type == "job":
            categories = ["engineering", "marketing", "sales", "design", "finance"]
            locations = ["paris", "lyon", "marseille", "bordeaux", "toulouse"]
            companies = ["TechCorp", "DataSystems", "AI Solutions", "Web Experts", "Digital Agency"]
            
            # Récupérer les préférences de l'utilisateur si disponibles
            user_preferences = None
            if self.preference_calculator:
                user_prefs = self.preference_calculator.get_preferences(user_id)
                if user_prefs and "content_preferences" in user_prefs:
                    user_preferences = user_prefs["content_preferences"]
            
            for i in range(limit):
                # Favoriser les préférences de l'utilisateur si elles sont disponibles
                if user_preferences and random.random() < 0.7:
                    top_categories = user_preferences.get("top_preferences", {}).get("categories", {})
                    category = random.choice(list(top_categories.keys())) if top_categories else random.choice(categories)
                    
                    top_locations = user_preferences.get("top_preferences", {}).get("locations", {})
                    location = random.choice(list(top_locations.keys())) if top_locations else random.choice(locations)
                else:
                    category = random.choice(categories)
                    location = random.choice(locations)
                
                job = {
                    "id": f"job_{i+1}",
                    "title": f"{category.capitalize()} Specialist",
                    "company": random.choice(companies),
                    "location": location.capitalize(),
                    "category": category,
                    "match_score": random.uniform(0.7, 0.99),
                    "salary_range": f"{random.randint(30, 120)}k-{random.randint(45, 150)}k",
                    "description": f"This is a {category} position based in {location}."
                }
                
                recommendations.append(job)
        
        elif item_type == "candidate":
            skills = ["Python", "JavaScript", "React", "Data Analysis", "Product Management", "UX Design"]
            experience_levels = ["Entry", "Mid", "Senior", "Lead", "Director"]
            
            for i in range(limit):
                candidate_skills = random.sample(skills, random.randint(2, 5))
                candidate = {
                    "id": f"candidate_{i+1}",
                    "name": f"Candidate {i+1}",
                    "experience_level": random.choice(experience_levels),
                    "skills": candidate_skills,
                    "match_score": random.uniform(0.7, 0.99),
                    "summary": f"Experienced professional with skills in {', '.join(candidate_skills[:-1])} and {candidate_skills[-1]}."
                }
                
                recommendations.append(candidate)
        
        return recommendations
    
    def start(self):
        """Démarre le serveur d'API."""
        host = self.config["host"]
        port = self.config["port"]
        debug = self.config["debug"]
        
        logger.info(f"Starting EnrichedProfilesAPI server on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)
    
    def get_app(self):
        """
        Récupère l'application Flask pour l'intégration avec d'autres serveurs.
        
        Returns:
            Application Flask
        """
        return self.app
