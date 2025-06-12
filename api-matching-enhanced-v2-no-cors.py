#!/usr/bin/env python3
"""
🚀 SuperSmartMatch V2.1 Enhanced - Version Sans CORS (pour test rapide)
API améliorée temporaire sans dépendance flask_cors
"""

from flask import Flask, request, jsonify, send_file
import requests
import json
import logging
import time
from datetime import datetime
import os
import tempfile
from werkzeug.utils import secure_filename
import re
from typing import Dict, List, Tuple, Optional
from difflib import SequenceMatcher

app = Flask(__name__)

# Configuration
CV_PARSER_URL = "http://localhost:5051"
JOB_PARSER_URL = "http://localhost:5053"
UPLOAD_FOLDER = tempfile.gettempdir()

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ====================================
# CONFIGURATION DU SYSTÈME DE DOMAINES
# ====================================

DOMAIN_KEYWORDS = {
    'commercial': [
        'vente', 'client', 'business', 'développement commercial', 'négociation', 
        'prospection', 'ingénieur d\'affaires', 'business development', 'commercial',
        'vente b2b', 'vente b2c', 'relation client', 'responsable commercial'
    ],
    'facturation': [
        'facture', 'facturation', 'billing', 'devis', 'tarification', 
        'assistant facturation', 'gestionnaire facturation', 'agent facturation',
        'facturation client', 'suivi factures'
    ],
    'comptabilité': [
        'comptable', 'bilan', 'compte', 'écriture comptable', 'TVA', 
        'assistant comptable', 'comptabilité générale', 'grand livre',
        'balance comptable', 'clôture comptable', 'immobilisations'
    ],
    'RH': [
        'ressources humaines', 'recrutement', 'formation', 'paie', 'personnel',
        'assistant RH', 'gestionnaire RH', 'responsable RH', 'DRH',
        'gestion personnel', 'administration personnel'
    ],
    'gestion': [
        'gestion', 'management', 'organisation', 'pilotage', 'coordination',
        'gestionnaire', 'responsable', 'chef de projet', 'supervision',
        'administration', 'organisation'
    ],
    'reporting': [
        'rapport', 'analyse', 'dashboard', 'KPI', 'indicateur', 'analyste',
        'reporting', 'tableau de bord', 'suivi performance', 'contrôle de gestion'
    ],
    'saisie': [
        'saisie', 'data entry', 'encodage', 'input', 'saisie de données',
        'opérateur saisie', 'agent saisie', 'encodeur'
    ],
    'contrôle': [
        'contrôle', 'audit', 'vérification', 'validation', 'contrôleur',
        'auditeur', 'vérificateur', 'contrôle qualité', 'contrôle interne'
    ]
}

DOMAIN_COMPATIBILITY = {
    'commercial': {
        'compatible': ['commercial', 'gestion', 'RH'],
        'incompatible': ['facturation', 'saisie', 'contrôle', 'comptabilité'],
        'weight': 0.8
    },
    'facturation': {
        'compatible': ['facturation', 'saisie', 'contrôle', 'comptabilité', 'reporting'],
        'incompatible': ['commercial', 'RH'],
        'weight': 0.9
    },
    'comptabilité': {
        'compatible': ['facturation', 'saisie', 'contrôle', 'comptabilité', 'reporting'],
        'incompatible': ['commercial'],
        'weight': 0.85
    },
    'RH': {
        'compatible': ['RH', 'gestion', 'commercial'],
        'incompatible': ['facturation', 'saisie', 'contrôle', 'comptabilité'],
        'weight': 0.8
    },
    'gestion': {
        'compatible': ['gestion', 'commercial', 'RH', 'reporting'],
        'incompatible': [],
        'weight': 0.7
    },
    'reporting': {
        'compatible': ['reporting', 'gestion', 'comptabilité', 'facturation'],
        'incompatible': [],
        'weight': 0.6
    },
    'saisie': {
        'compatible': ['saisie', 'facturation', 'comptabilité', 'contrôle'],
        'incompatible': ['commercial', 'RH'],
        'weight': 0.7
    },
    'contrôle': {
        'compatible': ['contrôle', 'facturation', 'comptabilité', 'reporting'],
        'incompatible': ['commercial', 'RH'],
        'weight': 0.8
    }
}

# ====================================
# CLASSE MOTEUR DE MATCHING AMÉLIORÉ
# ====================================

class EnhancedMatchingEngine:
    
    def __init__(self):
        self.domain_keywords = DOMAIN_KEYWORDS
        self.domain_compatibility = DOMAIN_COMPATIBILITY
        
        # Nouvelles pondérations
        self.weights = {
            'domain_compatibility': 0.25,
            'missions': 0.30,
            'skills': 0.25,
            'experience': 0.10,
            'quality': 0.10
        }
    
    def detect_primary_domain(self, missions: List[str], job_title: str = '') -> Tuple[str, Dict]:
        """Détecte le domaine principal d'un profil/poste avec détails"""
        domain_scores = {domain: 0 for domain in self.domain_keywords.keys()}
        
        # Analyser le titre du poste (poids fort)
        title_lower = job_title.lower()
        title_matches = {}
        
        for domain, keywords in self.domain_keywords.items():
            title_matches[domain] = []
            for keyword in keywords:
                if keyword in title_lower:
                    domain_scores[domain] += 3
                    title_matches[domain].append(keyword)
        
        # Analyser les missions
        mission_matches = {}
        for domain in self.domain_keywords.keys():
            mission_matches[domain] = []
        
        for mission in missions:
            if isinstance(mission, dict):
                mission_text = mission.get('description', '') + ' ' + mission.get('category', '')
            else:
                mission_text = str(mission)
            
            mission_lower = mission_text.lower()
            
            for domain, keywords in self.domain_keywords.items():
                for keyword in keywords:
                    if keyword in mission_lower:
                        domain_scores[domain] += 1
                        if keyword not in mission_matches[domain]:
                            mission_matches[domain].append(keyword)
        
        # Retourner le domaine avec le score le plus élevé
        primary_domain = max(domain_scores, key=domain_scores.get)
        
        return primary_domain, {
            'scores': domain_scores,
            'title_matches': title_matches,
            'mission_matches': mission_matches,
            'confidence': domain_scores[primary_domain] / max(sum(domain_scores.values()), 1)
        }
    
    def calculate_domain_compatibility(self, cv_domain: str, job_domain: str) -> Dict:
        """Calcule la compatibilité entre deux domaines avec détails"""
        if cv_domain == job_domain:
            return {
                'score': 1.0,
                'level': 'identical',
                'message': f'Domaines identiques: {cv_domain}'
            }
        
        domain_config = self.domain_compatibility.get(cv_domain, {})
        
        if job_domain in domain_config.get('incompatible', []):
            return {
                'score': 0.1,
                'level': 'incompatible',
                'message': f'Incompatibilité majeure: {cv_domain} vs {job_domain}'
            }
        
        if job_domain in domain_config.get('compatible', []):
            return {
                'score': 0.7,
                'level': 'compatible',
                'message': f'Domaines compatibles: {cv_domain} et {job_domain}'
            }
        
        return {
            'score': 0.3,
            'level': 'neutral',
            'message': f'Domaines neutres: {cv_domain} et {job_domain}'
        }
    
    def calculate_enhanced_mission_score(self, cv_data: Dict, job_data: Dict) -> Dict:
        """Calcul amélioré du score des missions avec filtrage sémantique"""
        try:
            # Extraction des missions
            cv_missions = []
            professional_exp = cv_data.get('professional_experience', [])
            if professional_exp:
                cv_missions = professional_exp[0].get('missions', [])
            
            job_missions = job_data.get('missions', [])
            cv_job_title = cv_data.get('candidate_name', '') + ' ' + cv_data.get('current_position', '')
            job_title = job_data.get('title', '')
            
            if not cv_missions or not job_missions:
                return {
                    'score': 0,
                    'cv_domain': 'unknown',
                    'job_domain': 'unknown',
                    'compatibility': {'score': 0, 'level': 'unknown', 'message': 'Missions manquantes'},
                    'explanation': 'Aucune mission trouvée pour l\'analyse'
                }
            
            # Détecter les domaines
            cv_domain, cv_details = self.detect_primary_domain(cv_missions, cv_job_title)
            job_domain, job_details = self.detect_primary_domain(job_missions, job_title)
            
            # Calculer la compatibilité des domaines
            domain_compatibility = self.calculate_domain_compatibility(cv_domain, job_domain)
            
            logger.info(f"Domaines détectés: CV={cv_domain}, Job={job_domain}, Compatibilité={domain_compatibility['score']}")
            
            # Si incompatibilité forte, pénaliser drastiquement
            if domain_compatibility['score'] < 0.2:
                return {
                    'score': domain_compatibility['score'] * 10,  # Score max 2%
                    'cv_domain': cv_domain,
                    'job_domain': job_domain,
                    'compatibility': domain_compatibility,
                    'explanation': f'Incompatibilité majeure détectée: {cv_domain} vs {job_domain}',
                    'warning': True
                }
            
            # Calcul basique pour domaines compatibles
            score = 70 * domain_compatibility['score']
            
            return {
                'score': score,
                'cv_domain': cv_domain,
                'job_domain': job_domain,
                'compatibility': domain_compatibility,
                'explanation': f'Score missions: {score:.1f}% basé sur compatibilité domaines'
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul mission score amélioré: {e}")
            return {
                'score': 0,
                'cv_domain': 'error',
                'job_domain': 'error',
                'compatibility': {'score': 0, 'level': 'error', 'message': str(e)},
                'explanation': f'Erreur lors du calcul: {str(e)}'
            }
    
    def calculate_global_enhanced_score(self, cv_data: Dict, job_data: Dict) -> Dict:
        """Calcul du score global amélioré (version simplifiée)"""
        try:
            # Calcul du score des missions (principal)
            mission_result = self.calculate_enhanced_mission_score(cv_data, job_data)
            mission_score = mission_result['score']
            
            # Scores simplifiés pour les autres composants
            skills_score = 60  # Score neutre
            experience_score = 70  # Score neutre
            quality_score = 75  # Score neutre
            
            # Score de compatibilité des domaines
            domain_compatibility_score = mission_result.get('compatibility', {}).get('score', 0) * 100
            
            # Score global pondéré
            global_score = (
                domain_compatibility_score * self.weights['domain_compatibility'] +
                mission_score * self.weights['missions'] +
                skills_score * self.weights['skills'] +
                experience_score * self.weights['experience'] +
                quality_score * self.weights['quality']
            )
            
            # Seuil de cohérence
            if domain_compatibility_score < 20:
                global_score = min(global_score, 25)
                logger.warning(f"Score plafonné à 25% due à incompatibilité des domaines")
            
            # Génération de la recommandation
            if global_score >= 85:
                recommendation = "Candidat fortement recommandé"
            elif global_score >= 70:
                recommendation = "Candidat recommandé avec réserves"
            elif global_score >= 50:
                recommendation = "Candidat à considérer selon contexte"
            else:
                recommendation = "Candidat non recommandé pour ce poste"
            
            # Génération des alertes
            alerts = []
            compatibility = mission_result.get('compatibility', {}).get('score', 0)
            
            if compatibility < 0.2 and global_score > 30:
                alerts.append({
                    'type': 'domain_incompatibility',
                    'message': f"🚨 Incompatibilité majeure: {mission_result.get('cv_domain')} vs {mission_result.get('job_domain')}",
                    'severity': 'critical'
                })
            
            return {
                'total_score': round(global_score),
                'recommendation': recommendation,
                'version': 'Enhanced V2.1 (No-CORS)',
                'alerts': alerts,
                'detailed_breakdown': {
                    'domain_compatibility': {
                        'score': round(domain_compatibility_score * self.weights['domain_compatibility']),
                        'weight': int(self.weights['domain_compatibility'] * 100),
                        'raw_score': round(domain_compatibility_score)
                    },
                    'missions': {
                        'score': round(mission_score * self.weights['missions']),
                        'weight': int(self.weights['missions'] * 100),
                        'raw_score': round(mission_score)
                    }
                },
                'domain_analysis': {
                    'cv_domain': mission_result.get('cv_domain'),
                    'job_domain': mission_result.get('job_domain'),
                    'compatibility_level': mission_result.get('compatibility', {}).get('level'),
                    'compatibility_message': mission_result.get('compatibility', {}).get('message')
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul score global amélioré: {e}")
            return {
                'total_score': 0,
                'recommendation': 'Erreur lors du calcul',
                'error': str(e),
                'alerts': [{
                    'type': 'calculation_error',
                    'message': f'Erreur lors du calcul: {str(e)}',
                    'severity': 'critical'
                }]
            }

# ====================================
# ROUTES API
# ====================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check de l'API"""
    return jsonify({
        'service': 'SuperSmartMatch V2.1 Enhanced (No-CORS)',
        'status': 'healthy',
        'version': '2.1-no-cors',
        'features': ['domain_compatibility', 'false_positive_prevention'],
        'timestamp': datetime.now().isoformat(),
        'note': 'Version temporaire sans CORS - installer flask-cors pour version complète'
    })

@app.route('/api/matching/enhanced', methods=['POST'])
def matching_enhanced():
    """Endpoint pour matching amélioré"""
    try:
        data = request.json
        if not data or 'cv_data' not in data or 'job_data' not in data:
            return jsonify({'error': 'cv_data et job_data requis'}), 400
        
        cv_data = data['cv_data']
        job_data = data['job_data']
        
        # Calcul du matching avec moteur amélioré
        start_time = time.time()
        engine = EnhancedMatchingEngine()
        matching_result = engine.calculate_global_enhanced_score(cv_data, job_data)
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'processing_time_ms': processing_time,
            'matching_analysis': matching_result,
            'api_version': '2.1-no-cors'
        })
        
    except Exception as e:
        logger.error(f"Erreur matching amélioré: {e}")
        return jsonify({'error': f'Erreur lors du calcul: {str(e)}'}), 500

@app.route('/api/test/hugo-salvat', methods=['GET'])
def test_hugo_salvat():
    """Test du cas problématique Hugo Salvat"""
    test_cv = {
        'candidate_name': 'Hugo Salvat',
        'current_position': 'Ingénieur d\'affaires IT',
        'professional_experience': [{
            'missions': [
                {'description': 'Développement commercial B2B', 'category': 'commercial'},
                {'description': 'Prospection clients entreprises', 'category': 'commercial'},
                {'description': 'Négociation contrats IT', 'category': 'commercial'},
                {'description': 'Suivi business development', 'category': 'commercial'}
            ]
        }],
        'technical_skills': ['commercial', 'IT', 'négociation', 'CRM'],
        'experience_years': 5
    }
    
    test_job = {
        'title': 'Assistant Facturation',
        'missions': [
            {'description': 'Facturation clients', 'category': 'facturation'},
            {'description': 'Contrôle des comptes', 'category': 'contrôle'},
            {'description': 'Saisie comptable', 'category': 'comptabilité'},
            {'description': 'Reporting financier', 'category': 'reporting'}
        ]
    }
    
    # Test avec le nouveau système
    engine = EnhancedMatchingEngine()
    enhanced_result = engine.calculate_global_enhanced_score(test_cv, test_job)
    
    return jsonify({
        'test_case': 'Hugo Salvat - Ingénieur d\'affaires IT vs Assistant Facturation',
        'expected_result': 'Score faible (< 30%) due à incompatibilité des domaines',
        'enhanced_result': enhanced_result,
        'algorithm_version': '2.1-no-cors',
        'test_status': 'success' if enhanced_result['total_score'] < 30 else 'warning',
        'validation': {
            'score_under_30': enhanced_result['total_score'] < 30,
            'alerts_present': len(enhanced_result.get('alerts', [])) > 0,
            'domain_incompatibility_detected': any(
                alert['type'] == 'domain_incompatibility' 
                for alert in enhanced_result.get('alerts', [])
            )
        }
    })

if __name__ == '__main__':
    print("🚀 SuperSmartMatch V2.1 Enhanced (Version sans CORS)")
    print("="*55)
    print("⚠️  Version temporaire sans CORS pour test rapide")
    print("📋 Pour version complète: pip install flask-cors")
    print("")
    print("📡 Endpoints disponibles:")
    print("   GET  /health                    - Health check")
    print("   POST /api/matching/enhanced     - Matching amélioré")
    print("   GET  /api/test/hugo-salvat      - Test cas problématique")
    print("")
    print("🌐 Serveur démarré sur: http://localhost:5055")
    
    app.run(host='0.0.0.0', port=5055, debug=True)
