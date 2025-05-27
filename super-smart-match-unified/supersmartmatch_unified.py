"""
SuperSmartMatch Unifié - Pipeline d'intégration Frontend
Suit les 3 étapes : Parsing → Questionnaire → Matching
"""

from typing import Dict, List, Optional, Any
import asyncio
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
import redis
import requests
import logging
from flask import Flask, request, jsonify, g
from flask_cors import CORS

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ParsedData:
    """Structure des données parsées"""
    cv_data: Optional[Dict] = None
    job_data: Optional[Dict] = None
    questionnaire_data: Optional[Dict] = None
    parsing_confidence: float = 0.0
    timestamp: datetime = None
    
    def to_dict(self):
        return {
            'cv_data': self.cv_data,
            'job_data': self.job_data,
            'questionnaire_data': self.questionnaire_data,
            'parsing_confidence': self.parsing_confidence,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

@dataclass
class MatchingResult:
    """Résultat du matching unifié"""
    matching_score_entreprise: float
    matching_score_candidat: float
    detailed_analysis: Dict
    questionnaire_boost: float
    parsing_quality: Dict
    recommendations: List[str]
    match_id: str
    confidence: float = 0.0
    semantic_boost: float = 0.0

class SuperSmartMatchUnified:
    """
    Algorithme de matching unifié qui suit le pipeline frontend :
    1. Parsing (CV + Job) 
    2. Questionnaire
    3. Matching avec toutes les données
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client or self._get_redis_client()
        self.cv_parser_url = os.getenv('CV_PARSER_URL', 'http://cv-parser:5000')
        self.job_parser_url = os.getenv('JOB_PARSER_URL', 'http://job-parser:5000')
        
        # Modules ML intégrés (optionnels)
        self.semantic_analyzer = self._load_semantic_analyzer()
        self.ner_extractor = self._load_ner_extractor()
        self.learning_system = self._load_learning_system()
        
        logger.info("SuperSmartMatch Unifié initialisé")
        
    def _get_redis_client(self):
        """Initialisation du client Redis"""
        try:
            return redis.Redis(
                host=os.getenv('REDIS_HOST', 'redis'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                db=int(os.getenv('REDIS_DB', 0)),
                decode_responses=True
            )
        except Exception as e:
            logger.error(f"Erreur connexion Redis: {e}")
            return None
    
    def _load_semantic_analyzer(self):
        """Chargement optionnel de l'analyseur sémantique"""
        try:
            # Import conditionnel pour éviter les erreurs si ML indisponible
            from .ml_modules.semantic_analyzer import SemanticAnalyzer
            return SemanticAnalyzer()
        except ImportError:
            logger.warning("Module d'analyse sémantique non disponible")
            return None
    
    def _load_ner_extractor(self):
        """Chargement optionnel de l'extracteur NER"""
        try:
            from .ml_modules.ner_extractor import NERExtractor
            return NERExtractor()
        except ImportError:
            logger.warning("Module NER non disponible")
            return None
    
    def _load_learning_system(self):
        """Chargement optionnel du système d'apprentissage"""
        try:
            from .ml_modules.learning_system import LearningSystem
            return LearningSystem()
        except ImportError:
            logger.warning("Système d'apprentissage non disponible")
            return None
        
    async def process_complete_pipeline(self, 
                                      cv_file=None, 
                                      job_file=None,
                                      cv_id=None,
                                      job_id=None,
                                      questionnaire_data=None,
                                      session_id=None) -> Dict:
        """
        Pipeline complet suivant les 3 étapes frontend
        """
        session_id = session_id or f"session_{datetime.now().timestamp()}"
        
        try:
            # ÉTAPE 1: PARSING (récolte des informations)
            logger.info(f"🔍 ÉTAPE 1: Parsing des documents - Session {session_id}")
            parsed_data = await self._step1_parsing(cv_file, job_file, cv_id, job_id, session_id)
            
            # ÉTAPE 2: ATTENTE QUESTIONNAIRE (données stockées en cache)
            logger.info("📝 ÉTAPE 2: En attente du questionnaire...")
            if questionnaire_data:
                parsed_data.questionnaire_data = questionnaire_data
            else:
                # Stocker en cache pour attendre le questionnaire
                self._cache_parsed_data(session_id, parsed_data)
                return {
                    "status": "waiting_questionnaire", 
                    "session_id": session_id, 
                    "parsed_data": parsed_data.to_dict()
                }
            
            # ÉTAPE 3: MATCHING COMPLET
            logger.info("⚡ ÉTAPE 3: Matching avec toutes les données...")
            matching_result = await self._step3_unified_matching(parsed_data, session_id)
            
            return {
                "status": "completed",
                "session_id": session_id,
                "result": asdict(matching_result)
            }
            
        except Exception as e:
            logger.error(f"Erreur pipeline: {e}")
            return {
                "status": "error",
                "session_id": session_id,
                "error": str(e)
            }
    
    async def _step1_parsing(self, cv_file, job_file, cv_id, job_id, session_id) -> ParsedData:
        """
        ÉTAPE 1: Parsing CV + Job via les microservices existants
        """
        parsed_data = ParsedData(timestamp=datetime.now())
        
        # Parsing CV (via service existant)
        if cv_file or cv_id:
            try:
                cv_data = await self._parse_cv(cv_file, cv_id)
                parsed_data.cv_data = cv_data
                logger.info(f"✅ CV parsé: {len(cv_data.get('competences', []))} compétences détectées")
            except Exception as e:
                logger.error(f"❌ Erreur parsing CV: {e}")
                parsed_data.cv_data = {"error": str(e)}
        
        # Parsing Job (via service existant)  
        if job_file or job_id:
            try:
                job_data = await self._parse_job(job_file, job_id)
                parsed_data.job_data = job_data
                logger.info(f"✅ Job parsé: {len(job_data.get('competences_requises', []))} compétences requises")
            except Exception as e:
                logger.error(f"❌ Erreur parsing Job: {e}")
                parsed_data.job_data = {"error": str(e)}
        
        # Calcul de la confiance du parsing
        parsed_data.parsing_confidence = self._calculate_parsing_confidence(parsed_data)
        
        return parsed_data
    
    async def _parse_cv(self, cv_file, cv_id) -> Dict:
        """Appel au service de parsing CV existant"""
        if cv_id and self.redis_client:
            # Récupérer depuis cache
            cached_cv = self.redis_client.get(f"cv_parsed:{cv_id}")
            if cached_cv:
                return json.loads(cached_cv)
        
        if cv_file:
            # Appel au microservice de parsing CV
            files = {"file": cv_file}
            data = {"force_refresh": False}
            
            response = requests.post(f"{self.cv_parser_url}/api/parse-cv/", 
                                   files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                cv_data = response.json()
                
                # Enrichissement avec extraction NER si disponible
                if self.ner_extractor:
                    cv_data = self._enrich_cv_with_ner(cv_data)
                
                return cv_data
            else:
                raise Exception(f"Erreur parsing CV: {response.status_code}")
    
    async def _parse_job(self, job_file, job_id) -> Dict:
        """Appel au service de parsing Job existant"""
        if job_id and self.redis_client:
            # Récupérer depuis cache
            cached_job = self.redis_client.get(f"job_parsed:{job_id}")
            if cached_job:
                return json.loads(cached_job)
        
        if job_file:
            # Appel au microservice de parsing Job
            files = {"file": job_file}
            data = {"force_refresh": False}
            
            response = requests.post(f"{self.job_parser_url}/api/parse-job", 
                                   files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                job_data = response.json()
                
                # Enrichissement avec extraction NER si disponible
                if self.ner_extractor:
                    job_data = self._enrich_job_with_ner(job_data)
                
                return job_data
            else:
                raise Exception(f"Erreur parsing Job: {response.status_code}")
    
    def continue_with_questionnaire(self, session_id: str, questionnaire_data: Dict) -> Dict:
        """
        Continuer le pipeline après réception du questionnaire
        (appelé par le frontend après l'étape 2)
        """
        # Récupérer les données parsées du cache
        parsed_data = self._get_cached_parsed_data(session_id)
        if not parsed_data:
            raise Exception(f"Session {session_id} introuvable")
        
        # Ajouter les données du questionnaire
        parsed_data.questionnaire_data = questionnaire_data
        
        # ÉTAPE 3: Matching complet
        return asyncio.run(self._step3_unified_matching(parsed_data, session_id))
    
    async def _step3_unified_matching(self, parsed_data: ParsedData, session_id: str) -> MatchingResult:
        """
        ÉTAPE 3: Matching unifié avec toutes les données collectées
        """
        if not parsed_data.cv_data or not parsed_data.job_data:
            raise Exception("Données CV ou Job manquantes pour le matching")
        
        # 1. Matching de base (logique métier SuperSmartMatch)
        base_scores = self._calculate_base_matching(parsed_data.cv_data, parsed_data.job_data)
        
        # 2. Boost du questionnaire 
        questionnaire_boost = 0.0
        if parsed_data.questionnaire_data:
            questionnaire_boost = self._calculate_questionnaire_boost(
                parsed_data.cv_data, 
                parsed_data.job_data, 
                parsed_data.questionnaire_data
            )
        
        # 3. Analyse sémantique ML (si disponible)
        semantic_boost = 0.0
        if self.semantic_analyzer:
            semantic_boost = self._calculate_semantic_similarity(
                parsed_data.cv_data, parsed_data.job_data
            )
        
        # 4. Score final unifié
        final_score_entreprise = self._combine_scores(
            base_scores['entreprise'], questionnaire_boost, semantic_boost
        )
        
        final_score_candidat = self._combine_scores(
            base_scores['candidat'], questionnaire_boost, semantic_boost
        )
        
        # 5. Analyse détaillée et recommandations
        detailed_analysis = self._generate_detailed_analysis(parsed_data, base_scores)
        recommendations = self._generate_recommendations(parsed_data, final_score_entreprise)
        
        # 6. Enregistrement pour apprentissage
        match_id = f"match_{session_id}_{datetime.now().timestamp()}"
        if self.learning_system:
            self.learning_system.record_match(parsed_data, final_score_entreprise, match_id)
        
        return MatchingResult(
            matching_score_entreprise=final_score_entreprise,
            matching_score_candidat=final_score_candidat,
            detailed_analysis=detailed_analysis,
            questionnaire_boost=questionnaire_boost,
            parsing_quality={
                "cv_confidence": parsed_data.parsing_confidence,
                "job_confidence": parsed_data.parsing_confidence,
                "total_data_quality": self._assess_data_quality(parsed_data)
            },
            recommendations=recommendations,
            match_id=match_id,
            semantic_boost=semantic_boost,
            confidence=self._calculate_overall_confidence(parsed_data, final_score_entreprise)
        )
    
    def _calculate_base_matching(self, cv_data: Dict, job_data: Dict) -> Dict:
        """Calcul du matching de base (logique SuperSmartMatch)"""
        # Logique métier existante de SuperSmartMatch
        # Adaptée pour utiliser les données parsées
        
        competences_cv = set(cv_data.get('competences', []))
        competences_job = set(job_data.get('competences_requises', []))
        
        # Score de correspondance des compétences
        if competences_job:
            competences_match = len(competences_cv & competences_job) / len(competences_job)
        else:
            competences_match = 0.0
        
        # Score d'expérience
        experience_cv = cv_data.get('experience_totale', 0)
        experience_requise = job_data.get('experience_requise', 0)
        experience_match = min(experience_cv / max(experience_requise, 1), 1.0) if experience_requise > 0 else 0.5
        
        # Score de formation
        niveau_cv = cv_data.get('niveau_formation', 0)
        niveau_requis = job_data.get('niveau_formation_requis', 0)
        formation_match = min(niveau_cv / max(niveau_requis, 1), 1.0) if niveau_requis > 0 else 0.5
        
        # Score de localisation
        localisation_match = self._calculate_location_match(cv_data, job_data)
        
        # Scores combinés
        score_entreprise = (
            competences_match * 0.4 + 
            experience_match * 0.3 + 
            formation_match * 0.2 + 
            localisation_match * 0.1
        ) * 100
        
        score_candidat = score_entreprise  # Même logique pour l'instant
        
        return {
            'entreprise': score_entreprise,
            'candidat': score_candidat,
            'details': {
                'competences_match': competences_match,
                'experience_match': experience_match,
                'formation_match': formation_match,
                'localisation_match': localisation_match
            }
        }
    
    def _calculate_questionnaire_boost(self, cv_data: Dict, job_data: Dict, questionnaire: Dict) -> float:
        """Calcul du boost basé sur le questionnaire"""
        boost = 0.0
        
        # Motivation du candidat (1-10)
        motivation = questionnaire.get('motivation', 5) / 10.0
        boost += motivation * 0.1
        
        # Disponibilité (1-10)
        disponibilite = questionnaire.get('disponibilite', 5) / 10.0
        boost += disponibilite * 0.05
        
        # Mobilité géographique (1-10)
        mobilite = questionnaire.get('mobilite', 5) / 10.0
        boost += mobilite * 0.05
        
        # Prétentions salariales
        salaire_souhaite = questionnaire.get('salaire_souhaite', 0)
        salaire_propose = job_data.get('salaire_max', 0)
        if salaire_propose > 0 and salaire_souhaite > 0:
            if salaire_souhaite <= salaire_propose:
                boost += 0.1
            elif salaire_souhaite <= salaire_propose * 1.1:  # Marge de 10%
                boost += 0.05
        
        # Expérience spécifique mentionnée
        if questionnaire.get('experience_specifique'):
            boost += 0.05
        
        return min(boost, 0.3)  # Max 30% de boost
    
    def _calculate_semantic_similarity(self, cv_data: Dict, job_data: Dict) -> float:
        """Calcul de la similarité sémantique (ML)"""
        if not self.semantic_analyzer:
            return 0.0
        
        try:
            # Analyse sémantique des compétences
            competences_cv = cv_data.get('competences', [])
            competences_job = job_data.get('competences_requises', [])
            
            return self.semantic_analyzer.calculate_similarity(competences_cv, competences_job)
        except Exception as e:
            logger.error(f"Erreur analyse sémantique: {e}")
            return 0.0
    
    def _calculate_location_match(self, cv_data: Dict, job_data: Dict) -> float:
        """Calcul de la correspondance géographique"""
        cv_location = cv_data.get('localisation', '')
        job_location = job_data.get('localisation', '')
        
        if not cv_location or not job_location:
            return 0.5  # Score neutre si données manquantes
        
        # Correspondance exacte
        if cv_location.lower() == job_location.lower():
            return 1.0
        
        # Correspondance partielle (même ville/région)
        if any(word in job_location.lower() for word in cv_location.lower().split()):
            return 0.7
        
        return 0.3  # Score faible pour localisation différente
    
    def _combine_scores(self, base_score: float, questionnaire_boost: float, semantic_boost: float) -> float:
        """Combinaison intelligente des scores"""
        # Score de base + boosts
        final_score = base_score + (questionnaire_boost * 100) + (semantic_boost * 100)
        
        # Limitation à 100
        return min(final_score, 100.0)
    
    def _cache_parsed_data(self, session_id: str, parsed_data: ParsedData):
        """Mise en cache des données parsées"""
        if not self.redis_client:
            return
            
        try:
            cache_key = f"parsed_data:{session_id}"
            data_dict = parsed_data.to_dict()
            self.redis_client.setex(cache_key, 3600, json.dumps(data_dict, default=str))
        except Exception as e:
            logger.error(f"Erreur cache: {e}")
    
    def _get_cached_parsed_data(self, session_id: str) -> Optional[ParsedData]:
        """Récupération des données parsées du cache"""
        if not self.redis_client:
            return None
            
        try:
            cache_key = f"parsed_data:{session_id}"
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data_dict = json.loads(cached_data)
                return ParsedData(
                    cv_data=data_dict.get('cv_data'),
                    job_data=data_dict.get('job_data'),
                    questionnaire_data=data_dict.get('questionnaire_data'),
                    parsing_confidence=data_dict.get('parsing_confidence', 0.0),
                    timestamp=datetime.fromisoformat(data_dict['timestamp']) if data_dict.get('timestamp') else None
                )
        except Exception as e:
            logger.error(f"Erreur récupération cache: {e}")
        return None
    
    def _calculate_parsing_confidence(self, parsed_data: ParsedData) -> float:
        """Calcul de la confiance du parsing"""
        confidence = 0.0
        
        if parsed_data.cv_data and 'error' not in parsed_data.cv_data:
            confidence += 0.5
        if parsed_data.job_data and 'error' not in parsed_data.job_data:
            confidence += 0.5
            
        return confidence
    
    def _assess_data_quality(self, parsed_data: ParsedData) -> float:
        """Évaluation de la qualité globale des données"""
        quality = 0.0
        
        # Qualité des données CV
        if parsed_data.cv_data:
            cv_fields = ['competences', 'experience_totale', 'formation']
            cv_quality = sum(1 for field in cv_fields if parsed_data.cv_data.get(field)) / len(cv_fields)
            quality += cv_quality * 0.4
        
        # Qualité des données Job
        if parsed_data.job_data:
            job_fields = ['competences_requises', 'experience_requise', 'description']
            job_quality = sum(1 for field in job_fields if parsed_data.job_data.get(field)) / len(job_fields)
            quality += job_quality * 0.4
        
        # Qualité du questionnaire
        if parsed_data.questionnaire_data:
            quality += 0.2
        
        return quality
    
    def _calculate_overall_confidence(self, parsed_data: ParsedData, score: float) -> float:
        """Calcul de la confiance globale du matching"""
        confidence = parsed_data.parsing_confidence * 0.4
        confidence += self._assess_data_quality(parsed_data) * 0.4
        confidence += (score / 100.0) * 0.2
        return confidence
    
    def _generate_detailed_analysis(self, parsed_data: ParsedData, base_scores: Dict) -> Dict:
        """Génération d'une analyse détaillée"""
        return {
            "competences_analysis": base_scores['details'],
            "data_sources": {
                "cv_parsing": bool(parsed_data.cv_data),
                "job_parsing": bool(parsed_data.job_data),
                "questionnaire": bool(parsed_data.questionnaire_data)
            },
            "parsing_quality": parsed_data.parsing_confidence,
            "timestamp": parsed_data.timestamp.isoformat() if parsed_data.timestamp else None,
            "ml_features": {
                "semantic_analysis": bool(self.semantic_analyzer),
                "ner_extraction": bool(self.ner_extractor),
                "learning_system": bool(self.learning_system)
            }
        }
    
    def _generate_recommendations(self, parsed_data: ParsedData, score: float) -> List[str]:
        """Génération de recommandations"""
        recommendations = []
        
        if score < 50:
            recommendations.append("Score faible - Vérifier l'adéquation du profil")
            recommendations.append("Analyser les compétences manquantes")
        elif score < 70:
            recommendations.append("Score moyen - Formation complémentaire recommandée")
            recommendations.append("Identifier les axes d'amélioration")
        else:
            recommendations.append("Excellent profil - Candidat fortement recommandé")
            recommendations.append("Prioriser ce candidat dans le processus de recrutement")
        
        if parsed_data.questionnaire_data:
            recommendations.append("Données questionnaire intégrées - Matching optimisé")
        else:
            recommendations.append("Questionnaire manquant - Compléter pour un matching optimal")
        
        # Recommandations basées sur l'analyse des données
        if parsed_data.cv_data and parsed_data.job_data:
            cv_competences = set(parsed_data.cv_data.get('competences', []))
            job_competences = set(parsed_data.job_data.get('competences_requises', []))
            
            missing_skills = job_competences - cv_competences
            if missing_skills:
                recommendations.append(f"Compétences à développer: {', '.join(list(missing_skills)[:3])}")
        
        return recommendations
    
    def _enrich_cv_with_ner(self, cv_data: Dict) -> Dict:
        """Enrichissement CV avec NER (si module disponible)"""
        if not self.ner_extractor:
            return cv_data
            
        try:
            # Extraction automatique de compétences supplémentaires
            additional_skills = self.ner_extractor.extract_skills_from_text(
                cv_data.get('texte_complet', '')
            )
            
            existing_skills = cv_data.get('competences', [])
            cv_data['competences'] = list(set(existing_skills + additional_skills))
            cv_data['ner_enriched'] = True
            
        except Exception as e:
            logger.error(f"Erreur enrichissement NER CV: {e}")
            
        return cv_data
    
    def _enrich_job_with_ner(self, job_data: Dict) -> Dict:
        """Enrichissement Job avec NER (si module disponible)"""
        if not self.ner_extractor:
            return job_data
            
        try:
            # Extraction automatique de compétences supplémentaires
            additional_skills = self.ner_extractor.extract_skills_from_text(
                job_data.get('description', '')
            )
            
            existing_skills = job_data.get('competences_requises', [])
            job_data['competences_requises'] = list(set(existing_skills + additional_skills))
            job_data['ner_enriched'] = True
            
        except Exception as e:
            logger.error(f"Erreur enrichissement NER Job: {e}")
            
        return job_data


# ===== API FLASK POUR INTÉGRATION FRONTEND =====

app = Flask(__name__)
CORS(app, origins=["*"])  # Permettre les requêtes cross-origin

# Instance globale du matcher
matcher = SuperSmartMatchUnified()

@app.before_request
def before_request():
    g.start_time = datetime.now()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        duration = (datetime.now() - g.start_time).total_seconds()
        logger.info(f"Request {request.method} {request.path} completed in {duration:.3f}s")
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SuperSmartMatch Unifié",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "semantic_analysis": bool(matcher.semantic_analyzer),
            "ner_extraction": bool(matcher.ner_extractor),
            "learning_system": bool(matcher.learning_system),
            "redis_connected": bool(matcher.redis_client)
        }
    })

@app.route('/api/unified-match/start', methods=['POST'])
def start_matching_pipeline():
    """
    Démarrage du pipeline - ÉTAPE 1 + 2
    Appelé par le frontend après upload des fichiers
    """
    try:
        cv_file = request.files.get('cv_file')
        job_file = request.files.get('job_file')
        cv_id = request.form.get('cv_id')
        job_id = request.form.get('job_id')
        session_id = request.form.get('session_id')
        
        if not cv_file and not job_file and not cv_id and not job_id:
            return jsonify({"error": "Au moins un fichier CV ou Job requis"}), 400
        
        result = asyncio.run(matcher.process_complete_pipeline(
            cv_file=cv_file,
            job_file=job_file, 
            cv_id=cv_id,
            job_id=job_id,
            session_id=session_id
        ))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur start pipeline: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/unified-match/complete', methods=['POST'])
def complete_matching_with_questionnaire():
    """
    Finalisation du matching - ÉTAPE 3
    Appelé par le frontend après soumission du questionnaire
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        questionnaire_data = data.get('questionnaire_data')
        
        if not session_id or not questionnaire_data:
            return jsonify({"error": "session_id et questionnaire_data requis"}), 400
        
        result = matcher.continue_with_questionnaire(session_id, questionnaire_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur complete pipeline: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/unified-match/status/<session_id>', methods=['GET'])
def get_matching_status(session_id):
    """Vérification du statut d'une session de matching"""
    try:
        parsed_data = matcher._get_cached_parsed_data(session_id)
        if parsed_data:
            return jsonify({
                "status": "ready_for_questionnaire",
                "has_cv": bool(parsed_data.cv_data),
                "has_job": bool(parsed_data.job_data),
                "parsing_confidence": parsed_data.parsing_confidence,
                "data_quality": matcher._assess_data_quality(parsed_data)
            })
        else:
            return jsonify({"status": "not_found"}), 404
            
    except Exception as e:
        logger.error(f"Erreur status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/unified-match/sessions', methods=['GET'])
def list_active_sessions():
    """Liste des sessions actives"""
    try:
        if not matcher.redis_client:
            return jsonify({"error": "Redis non disponible"}), 503
            
        # Récupérer toutes les clés de session
        keys = matcher.redis_client.keys("parsed_data:*")
        sessions = []
        
        for key in keys:
            session_id = key.replace("parsed_data:", "")
            ttl = matcher.redis_client.ttl(key)
            sessions.append({
                "session_id": session_id,
                "ttl_seconds": ttl
            })
        
        return jsonify({
            "active_sessions": len(sessions),
            "sessions": sessions
        })
        
    except Exception as e:
        logger.error(f"Erreur list sessions: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint non trouvé"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Erreur interne du serveur"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5052))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🚀 Démarrage SuperSmartMatch Unifié sur le port {port}")
    logger.info(f"🔧 Mode debug: {debug}")
    logger.info(f"📊 Fonctionnalités ML: Sémantique={bool(matcher.semantic_analyzer)}, NER={bool(matcher.ner_extractor)}, Learning={bool(matcher.learning_system)}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
