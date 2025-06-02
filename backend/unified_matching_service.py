#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Super Smart Match Service - Point d'entrée unifié avec Nexten V3
================================================================

Service de production qui expose SuperSmartMatch V3 avec vraie intégration Nexten
via une API Flask standardisée pour compatibilité avec l'écosystème existant.

Fonctionnalités:
- ✅ API Flask avec SuperSmartMatch V3 
- ✅ Vraie intégration HTTP vers Nexten (port 5052)
- ✅ Sélection intelligente d'algorithme
- ✅ Circuit breaker et monitoring
- ✅ Compatibilité backward complète
- ✅ Health checks et métriques

Auteur: Claude/Anthropic pour Nexten Team
Version: 3.0.0  
Date: 2025-06-02
"""

import os
import sys
import json
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, List, Any, Optional

# Import de SuperSmartMatch V3 avec vraie intégration Nexten
try:
    from super_smart_match_v3 import (
        SuperSmartMatchV3, 
        MatchingConfigV3, 
        NextenServiceConfig,
        create_matching_service_v3
    )
    V3_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ SuperSmartMatch V3 with real Nexten integration loaded")
except ImportError as e:
    # Fallback vers V2 si V3 indisponible
    from super_smart_match_v2 import SuperSmartMatchV2, MatchingConfigV2
    V3_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ V3 unavailable, fallback to V2: {str(e)}")

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
CORS(app)

# Configuration globale du service
SERVICE_VERSION = "3.0.0"
SERVICE_NAME = "super-smart-match-unified"

# Variables d'environnement
NEXTEN_SERVICE_URL = os.getenv('NEXTEN_SERVICE_URL', 'http://matching-api:5000')
SUPERSMARTMATCH_VERSION = os.getenv('SUPERSMARTMATCH_VERSION', 'v3')
DEBUG_MODE = os.getenv('DEBUG', 'false').lower() == 'true'
PORT = int(os.getenv('PORT', 5062))

class UnifiedMatchingService:
    """Service unifié qui orchestre SuperSmartMatch avec Nexten"""
    
    def __init__(self):
        self.service_version = SERVICE_VERSION
        self.nexten_url = NEXTEN_SERVICE_URL
        
        # Initialisation du service selon la version disponible
        if V3_AVAILABLE and SUPERSMARTMATCH_VERSION == 'v3':
            self._init_v3_service()
        else:
            self._init_fallback_service()
    
    def _init_v3_service(self):
        """Initialise le service V3 avec vraie intégration Nexten"""
        try:
            logger.info(f"🚀 Initializing SuperSmartMatch V3 with Nexten: {self.nexten_url}")
            
            # Configuration Nexten optimisée pour production
            nexten_config = NextenServiceConfig(
                base_url=self.nexten_url,
                timeout=8.0,
                max_retries=3,
                circuit_breaker_threshold=5,
                circuit_breaker_timeout=60.0,
                connection_pool_size=10,
                request_timeout=5.0
            )
            
            # Configuration V3
            config_v3 = MatchingConfigV3(
                enable_nexten=True,
                nexten_service_config=nexten_config,
                min_data_quality_for_nexten=0.8,
                enable_benchmarking=True,
                enable_fallback=True,
                fallback_cascade=["intelligent-hybrid", "enhanced", "smart-match"]
            )
            
            self.matching_service = SuperSmartMatchV3(config_v3)
            self.service_type = "V3_REAL_NEXTEN"
            
            # Test de connectivité Nexten
            nexten_health = self.matching_service.real_nexten.http_client.health_check()
            if nexten_health:
                logger.info("✅ Nexten service connectivity confirmed")
            else:
                logger.warning("⚠️ Nexten service not accessible, fallback will be used")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize V3: {str(e)}")
            self._init_fallback_service()
    
    def _init_fallback_service(self):
        """Initialise le service de fallback (V2 ou V1)"""
        try:
            if not V3_AVAILABLE:
                logger.info("🔄 Initializing SuperSmartMatch V2 (fallback)")
                config_v2 = MatchingConfigV2(enable_nexten=False)  # Désactiver simulation
                self.matching_service = SuperSmartMatchV2(config_v2)
                self.service_type = "V2_FALLBACK"
            else:
                logger.info("🔄 V3 failed, using V2 fallback")
                config_v2 = MatchingConfigV2(enable_nexten=False)
                self.matching_service = SuperSmartMatchV2(config_v2)
                self.service_type = "V2_FALLBACK"
        except Exception as e:
            logger.error(f"❌ Critical error: Could not initialize any service version: {str(e)}")
            raise RuntimeError("No matching service could be initialized")
    
    def perform_matching(self, candidate_data: Dict[str, Any], offers_data: List[Dict[str, Any]], 
                        algorithm: str = "auto", **kwargs) -> Dict[str, Any]:
        """Effectue le matching avec le service approprié"""
        start_time = time.time()
        
        try:
            # Appel au service de matching
            response = self.matching_service.match(
                candidate_data=candidate_data,
                offers_data=offers_data,
                algorithm=algorithm,
                **kwargs
            )
            
            # Enrichissement de la réponse avec informations du service unifié
            if response.get("success", False):
                response["unified_service"] = {
                    "version": self.service_version,
                    "service_type": self.service_type,
                    "nexten_url": self.nexten_url,
                    "processing_time": round(time.time() - start_time, 3)
                }
            
            return response
            
        except Exception as e:
            logger.error(f"Matching error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "unified_service": {
                    "version": self.service_version,
                    "service_type": self.service_type,
                    "error_occurred": True
                }
            }
    
    def get_service_info(self) -> Dict[str, Any]:
        """Retourne les informations complètes du service"""
        base_info = {
            "service_name": SERVICE_NAME,
            "service_version": self.service_version,
            "service_type": self.service_type,
            "nexten_integration": {
                "url": self.nexten_url,
                "v3_available": V3_AVAILABLE
            }
        }
        
        # Ajout d'informations spécifiques selon le service
        if hasattr(self.matching_service, 'health_check'):
            try:
                health_info = self.matching_service.health_check()
                base_info["matching_service_health"] = health_info
            except Exception as e:
                base_info["matching_service_health"] = {"error": str(e)}
        
        return base_info
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques de performance"""
        if hasattr(self.matching_service, 'get_performance_metrics'):
            try:
                return self.matching_service.get_performance_metrics()
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"message": "Performance metrics not available for this service version"}

# Instance globale du service unifié
try:
    unified_service = UnifiedMatchingService()
    logger.info(f"✅ Unified Matching Service initialized: {unified_service.service_type}")
except Exception as e:
    logger.error(f"❌ Critical: Failed to initialize unified service: {str(e)}")
    sys.exit(1)

# Routes API Flask

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint complet"""
    try:
        service_info = unified_service.get_service_info()
        return jsonify({
            "status": "healthy",
            "timestamp": time.time(),
            **service_info
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/api/v1/health', methods=['GET'])
def health_check_v1():
    """Health check endpoint V1 pour compatibilité"""
    return health_check()

@app.route('/api/v1/match', methods=['POST'])
def api_match():
    """Endpoint principal de matching"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        # Extraction des données
        candidate_data = data.get('candidate', {})
        offers_data = data.get('offers', data.get('jobs', []))
        algorithm = data.get('algorithm', 'auto')
        options = data.get('options', {})
        
        # Validation des données
        if not candidate_data:
            return jsonify({
                "success": False,
                "error": "Candidate data is required"
            }), 400
        
        if not offers_data:
            return jsonify({
                "success": False,
                "error": "Offers data is required"
            }), 400
        
        # Exécution du matching
        result = unified_service.perform_matching(
            candidate_data=candidate_data,
            offers_data=offers_data,
            algorithm=algorithm,
            **options
        )
        
        status_code = 200 if result.get("success", False) else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e),
            "api_version": "v1"
        }), 500

@app.route('/api/v1/info', methods=['GET'])
def api_info():
    """Informations sur le service et les algorithmes disponibles"""
    try:
        service_info = unified_service.get_service_info()
        return jsonify(service_info), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "service": SERVICE_NAME
        }), 500

@app.route('/api/v1/metrics', methods=['GET'])
def api_metrics():
    """Métriques de performance du service"""
    try:
        metrics = unified_service.get_performance_metrics()
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({
            "error": str(e),
            "service": SERVICE_NAME
        }), 500

# Routes de compatibilité avec l'API existante

@app.route('/match', methods=['POST'])
def legacy_match():
    """Endpoint de compatibilité avec l'ancienne API"""
    try:
        data = request.get_json()
        
        # Transformation format ancien vers nouveau
        cv_data = data.get('cv_data', {})
        questionnaire_data = data.get('questionnaire_data', {})
        job_data = data.get('job_data', [])
        
        # Fusion des données candidat
        candidate_data = {**cv_data, **questionnaire_data}
        
        # Matching avec format unifié
        result = unified_service.perform_matching(
            candidate_data=candidate_data,
            offers_data=job_data,
            algorithm=data.get('algorithm', 'auto')
        )
        
        # Transformation du résultat vers format ancien si nécessaire
        if result.get("success", False):
            legacy_format = []
            for match in result.get("matching_results", {}).get("matches", []):
                legacy_match = {
                    "id": match.get("offer_id"),
                    "titre": match.get("title"),
                    "entreprise": match.get("company", "Unknown"),
                    "matching_score": match.get("score", 0),
                    "matching_details": match.get("score_details", {}),
                    "algorithm_version": match.get("algorithm", "unknown"),
                    "nexten_powered": match.get("quality_indicators", {}).get("powered_by_nexten", False)
                }
                legacy_format.append(legacy_match)
            
            return jsonify(legacy_format), 200
        else:
            return jsonify([]), 200
            
    except Exception as e:
        logger.error(f"Legacy API error: {str(e)}")
        return jsonify([]), 500

@app.route('/', methods=['GET'])
def index():
    """Page d'accueil du service"""
    return jsonify({
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "description": "Unified SuperSmartMatch service with real Nexten integration",
        "endpoints": {
            "health": "/health",
            "match": "/api/v1/match",
            "info": "/api/v1/info", 
            "metrics": "/api/v1/metrics",
            "legacy_match": "/match"
        },
        "nexten_integration": {
            "enabled": V3_AVAILABLE,
            "service_url": NEXTEN_SERVICE_URL
        }
    }), 200

# Gestion des erreurs

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "service": SERVICE_NAME,
        "available_endpoints": ["/health", "/api/v1/match", "/api/v1/info", "/match"]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "service": SERVICE_NAME,
        "message": "Please check service logs for details"
    }), 500

# Point d'entrée principal
if __name__ == '__main__':
    logger.info(f"🚀 Starting {SERVICE_NAME} v{SERVICE_VERSION}")
    logger.info(f"   Service type: {unified_service.service_type}")
    logger.info(f"   Nexten URL: {NEXTEN_SERVICE_URL}")
    logger.info(f"   Port: {PORT}")
    logger.info(f"   Debug: {DEBUG_MODE}")
    
    # Test rapide au démarrage
    try:
        health = unified_service.get_service_info()
        logger.info(f"✅ Service startup health check passed")
    except Exception as e:
        logger.error(f"❌ Service startup health check failed: {str(e)}")
    
    # Démarrage du serveur Flask
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=DEBUG_MODE,
        threaded=True
    )
