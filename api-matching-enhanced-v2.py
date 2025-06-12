#!/usr/bin/env python3
"""
🚀 SuperSmartMatch V2 - Enhanced API with Domain Compatibility
API améliorée avec système de compatibilité des domaines métiers
Version: 2.1 - Correction des faux positifs
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
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
CORS(app)

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
            'domain_compatibility': 0.25,  # NOUVEAU
            'missions': 0.30,              # Réduit de 40%
            'skills': 0.25,                # Réduit de 30%
            'experience': 0.10,            # Réduit de 15%
            'quality': 0.10               # Réduit de 15%
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
    
    def extract_missions_with_filtering(self, raw_missions: List, job_title: str = '') -> List[str]:
        """Extrait et filtre les missions pertinentes"""
        filtered_missions = []
        
        # Convertir les missions en texte
        mission_texts = []
        for mission in raw_missions:
            if isinstance(mission, dict):
                text = mission.get('description', '') + ' ' + mission.get('category', '')
                mission_texts.append(text.strip())
            else:
                mission_texts.append(str(mission))
        
        # Déterminer le domaine principal
        primary_domain, _ = self.detect_primary_domain(mission_texts, job_title)
        relevant_keywords = self.domain_keywords.get(primary_domain, [])
        
        for mission_text in mission_texts:
            if not mission_text.strip():
                continue
                
            mission_lower = mission_text.lower()
            
            # Vérifier si la mission est pertinente au domaine
            is_relevant = any(keyword in mission_lower for keyword in relevant_keywords)
            
            # Filtrer les missions trop génériques
            generic_terms = ['gestion', 'organisation', 'coordination', 'suivi', 'administration']
            is_too_generic = (len(mission_text.split()) < 3 and 
                            any(term in mission_lower for term in generic_terms))
            
            if is_relevant and not is_too_generic:
                filtered_missions.append(mission_text)
        
        return filtered_missions
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calcule la similarité entre deux textes"""
        if not text1 or not text2:
            return 0.0
        
        # Utilise SequenceMatcher pour une meilleure précision
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
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
                    'filtered_cv_missions': [],
                    'filtered_job_missions': [],
                    'explanation': 'Aucune mission trouvée pour l\'analyse'
                }
            
            # Filtrer les missions
            filtered_cv_missions = self.extract_missions_with_filtering(cv_missions, cv_job_title)
            filtered_job_missions = self.extract_missions_with_filtering(job_missions, job_title)
            
            # Détecter les domaines
            cv_domain, cv_details = self.detect_primary_domain(filtered_cv_missions, cv_job_title)
            job_domain, job_details = self.detect_primary_domain(filtered_job_missions, job_title)
            
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
                    'filtered_cv_missions': filtered_cv_missions,
                    'filtered_job_missions': filtered_job_missions,
                    'cv_domain_details': cv_details,
                    'job_domain_details': job_details,
                    'explanation': f'Incompatibilité majeure détectée: {cv_domain} vs {job_domain}',
                    'warning': True
                }
            
            # Calcul traditionnel pour domaines compatibles
            if not filtered_cv_missions or not filtered_job_missions:
                return {
                    'score': 20,  # Score bas mais pas zéro
                    'cv_domain': cv_domain,
                    'job_domain': job_domain,
                    'compatibility': domain_compatibility,
                    'explanation': 'Missions filtrées insuffisantes'
                }
            
            total_score = 0
            match_details = []
            
            for job_mission in filtered_job_missions:
                best_match = 0
                best_cv_mission = ""
                
                for cv_mission in filtered_cv_missions:
                    similarity = self.calculate_text_similarity(cv_mission, job_mission)
                    if similarity > best_match:
                        best_match = similarity
                        best_cv_mission = cv_mission
                
                total_score += best_match
                match_details.append({
                    'job_mission': job_mission,
                    'best_cv_match': best_cv_mission,
                    'similarity': best_match
                })
            
            raw_score = (total_score / len(filtered_job_missions)) * 100 if filtered_job_missions else 0
            final_score = raw_score * domain_compatibility['score']
            
            return {
                'score': final_score,
                'cv_domain': cv_domain,
                'job_domain': job_domain,
                'compatibility': domain_compatibility,
                'raw_score': raw_score,
                'filtered_cv_missions': filtered_cv_missions,
                'filtered_job_missions': filtered_job_missions,
                'cv_domain_details': cv_details,
                'job_domain_details': job_details,
                'match_details': match_details,
                'explanation': f'Score missions: {raw_score:.1f}% × compatibilité {domain_compatibility["score"]:.1f} = {final_score:.1f}%'
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
    
    def calculate_skills_score(self, cv_data: Dict, job_data: Dict) -> Dict:
        """Calcul du score des compétences (repris de l'original)"""
        try:
            cv_skills = []
            cv_skills.extend(cv_data.get('technical_skills', []))
            cv_skills.extend(cv_data.get('soft_skills', []))
            
            job_skills = []
            job_requirements = job_data.get('requirements', {})
            job_skills.extend(job_requirements.get('technical_skills', []))
            job_skills.extend(job_requirements.get('soft_skills', []))
            
            if not job_skills:
                return {
                    'score': 50,
                    'cv_skills': cv_skills,
                    'job_skills': job_skills,
                    'exact_matches': [],
                    'partial_matches': [],
                    'explanation': 'Aucune compétence spécifiée dans l\'offre'
                }
            
            # Normalisation pour comparaison
            cv_skills_lower = [skill.lower() for skill in cv_skills]
            job_skills_lower = [skill.lower() for skill in job_skills]
            
            # Correspondances exactes
            exact_matches = [skill for skill in job_skills_lower if skill in cv_skills_lower]
            
            # Correspondances partielles
            partial_matches = []
            for job_skill in job_skills_lower:
                if job_skill not in exact_matches:
                    for cv_skill in cv_skills_lower:
                        if job_skill in cv_skill or cv_skill in job_skill:
                            partial_matches.append(job_skill)
                            break
            
            # Calcul du score
            score = ((len(exact_matches) * 1.0 + len(partial_matches) * 0.5) / len(job_skills)) * 100
            
            return {
                'score': min(score, 100),
                'cv_skills': cv_skills,
                'job_skills': job_skills,
                'exact_matches': exact_matches,
                'partial_matches': partial_matches,
                'explanation': f'{len(exact_matches)} compétences parfaitement alignées et {len(partial_matches)} partiellement compatibles'
            }
        except Exception as e:
            logger.error(f"Erreur calcul skills score: {e}")
            return {
                'score': 0,
                'cv_skills': [],
                'job_skills': [],
                'exact_matches': [],
                'partial_matches': [],
                'explanation': f'Erreur lors du calcul: {str(e)}'
            }
    
    def calculate_experience_score(self, cv_data: Dict, job_data: Dict) -> Dict:
        """Calcul du score d'expérience (repris de l'original)"""
        try:
            cv_experience = cv_data.get('experience_years', 0)
            required_experience = job_data.get('requirements', {}).get('experience_level', '0-2 ans')
            
            # Extraction de la fourchette d'expérience
            matches = re.findall(r'(\d+)', required_experience)
            if len(matches) >= 2:
                min_exp, max_exp = int(matches[0]), int(matches[1])
            elif len(matches) == 1:
                min_exp, max_exp = int(matches[0]), int(matches[0]) + 2
            else:
                min_exp, max_exp = 0, 2
            
            # Calcul du score
            if min_exp <= cv_experience <= max_exp + 2:
                score = 100  # Expérience parfaitement alignée
            elif cv_experience >= min_exp:
                score = 85   # Surqualifié mais acceptable
            else:
                score = max(30, (cv_experience / min_exp) * 70) if min_exp > 0 else 30
            
            return {
                'score': score,
                'cv_experience': cv_experience,
                'required_experience': required_experience,
                'explanation': f'{cv_experience} ans d\'expérience vs {required_experience} requis'
            }
        except Exception as e:
            logger.error(f"Erreur calcul experience score: {e}")
            return {
                'score': 50,
                'cv_experience': 0,
                'required_experience': 'Non spécifié',
                'explanation': f'Erreur lors du calcul: {str(e)}'
            }
    
    def calculate_quality_score(self, cv_data: Dict, job_data: Dict) -> Dict:
        """Calcul du score de qualité (repris de l'original)"""
        try:
            score = 0
            factors = []
            
            # Vérification de la complétude du CV
            if cv_data.get('candidate_name'):
                score += 20
                factors.append('Nom du candidat')
            
            if cv_data.get('professional_experience') and len(cv_data['professional_experience']) > 0:
                score += 25
                factors.append('Expérience professionnelle')
            
            if cv_data.get('technical_skills') and len(cv_data['technical_skills']) > 0:
                score += 20
                factors.append('Compétences techniques')
            
            mission_summary = cv_data.get('mission_summary', {})
            if mission_summary.get('confidence_avg', 0) > 0.8:
                score += 20
                factors.append('Missions bien détaillées')
            
            if cv_data.get('professional_experience', [{}])[0].get('missions') and \
               len(cv_data['professional_experience'][0]['missions']) >= 3:
                score += 15
                factors.append('Missions détaillées')
            
            return {
                'score': min(score, 100),
                'quality_factors': factors,
                'explanation': f'Qualité évaluée sur {len(factors)} critères de complétude'
            }
        except Exception as e:
            logger.error(f"Erreur calcul quality score: {e}")
            return {
                'score': 50,
                'quality_factors': [],
                'explanation': f'Erreur lors du calcul: {str(e)}'
            }
    
    def generate_alerts(self, mission_details: Dict, global_score: float) -> List[Dict]:
        """Génère des alertes de cohérence"""
        alerts = []
        compatibility = mission_details.get('compatibility', {}).get('score', 0)
        
        if compatibility < 0.2 and global_score > 30:
            alerts.append({
                'type': 'domain_incompatibility',
                'message': f"🚨 Incompatibilité majeure: {mission_details.get('cv_domain')} vs {mission_details.get('job_domain')}",
                'severity': 'critical',
                'recommendation': 'Ce profil ne convient pas pour ce poste'
            })
        
        if compatibility < 0.5 and global_score > 60:
            alerts.append({
                'type': 'domain_mismatch',
                'message': f"⚠️ Domaines différents: vérifier la pertinence du match",
                'severity': 'warning',
                'recommendation': 'Analyser en détail les compétences transversales'
            })
        
        if mission_details.get('warning'):
            alerts.append({
                'type': 'false_positive_risk',
                'message': f"⚠️ Risque de faux positif détecté",
                'severity': 'warning',
                'recommendation': 'Vérifier manuellement la pertinence du profil'
            })
        
        return alerts
    
    def calculate_global_enhanced_score(self, cv_data: Dict, job_data: Dict) -> Dict:
        """Calcul du score global amélioré"""
        try:
            # Calcul des scores individuels
            mission_result = self.calculate_enhanced_mission_score(cv_data, job_data)
            skills_result = self.calculate_skills_score(cv_data, job_data)
            experience_result = self.calculate_experience_score(cv_data, job_data)
            quality_result = self.calculate_quality_score(cv_data, job_data)
            
            # Extraction des scores
            mission_score = mission_result['score']
            skills_score = skills_result['score']
            experience_score = experience_result['score']
            quality_score = quality_result['score']
            
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
            
            # Seuil de cohérence : si incompatibilité forte, plafonner le score
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
            alerts = self.generate_alerts(mission_result, global_score)
            
            return {
                'total_score': round(global_score),
                'recommendation': recommendation,
                'version': 'Enhanced V2.1',
                'alerts': alerts,
                'detailed_breakdown': {
                    'domain_compatibility': {
                        'score': round(domain_compatibility_score * self.weights['domain_compatibility']),
                        'weight': int(self.weights['domain_compatibility'] * 100),
                        'raw_score': round(domain_compatibility_score),
                        'details': mission_result.get('compatibility', {})
                    },
                    'missions': {
                        'score': round(mission_score * self.weights['missions']),
                        'weight': int(self.weights['missions'] * 100),
                        'raw_score': round(mission_score),
                        'details': mission_result
                    },
                    'skills': {
                        'score': round(skills_score * self.weights['skills']),
                        'weight': int(self.weights['skills'] * 100),
                        'raw_score': round(skills_score),
                        'details': skills_result
                    },
                    'experience': {
                        'score': round(experience_score * self.weights['experience']),
                        'weight': int(self.weights['experience'] * 100),
                        'raw_score': round(experience_score),
                        'details': experience_result
                    },
                    'quality': {
                        'score': round(quality_score * self.weights['quality']),
                        'weight': int(self.weights['quality'] * 100),
                        'raw_score': round(quality_score),
                        'details': quality_result
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
# FONCTIONS LEGACY COMPATIBLES
# ====================================

def calculate_advanced_score(cv_data, job_data):
    """Fonction compatible avec l'ancien système"""
    engine = EnhancedMatchingEngine()
    return engine.calculate_global_enhanced_score(cv_data, job_data)

# ====================================
# GESTION DES ERREURS
# ====================================

class MatchingAPIError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

@app.errorhandler(MatchingAPIError)
def handle_matching_error(error):
    response = jsonify({
        'error': error.message,
        'status': 'error',
        'timestamp': datetime.now().isoformat()
    })
    response.status_code = error.status_code
    return response

# ====================================
# ROUTES API
# ====================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check de l'API"""
    return jsonify({
        'service': 'SuperSmartMatch V2.1 Enhanced',
        'status': 'healthy',
        'version': '2.1',
        'features': ['domain_compatibility', 'semantic_filtering', 'false_positive_prevention'],
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            'matching_complete': '/api/matching/complete',
            'matching_enhanced': '/api/matching/enhanced',
            'matching_files': '/api/matching/files',
            'test_endpoint': '/api/test/hugo-salvat'
        }
    })

@app.route('/api/matching/enhanced', methods=['POST'])
def matching_enhanced():
    """
    Endpoint pour matching amélioré avec nouveau système de domaines
    
    Body JSON attendu:
    {
        "cv_data": { ... },
        "job_data": { ... }
    }
    """
    try:
        data = request.json
        if not data or 'cv_data' not in data or 'job_data' not in data:
            raise MatchingAPIError('cv_data et job_data requis dans le body JSON')
        
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
            'api_version': '2.1-enhanced',
            'algorithm': 'domain_compatibility_v2'
        })
        
    except MatchingAPIError:
        raise
    except Exception as e:
        logger.error(f"Erreur matching amélioré: {e}")
        raise MatchingAPIError(f'Erreur lors du calcul de matching: {str(e)}', 500)

@app.route('/api/matching/complete', methods=['POST'])
def matching_complete():
    """Endpoint legacy compatible avec l'ancien système"""
    try:
        data = request.json
        if not data or 'cv_data' not in data or 'job_data' not in data:
            raise MatchingAPIError('cv_data et job_data requis dans le body JSON')
        
        cv_data = data['cv_data']
        job_data = data['job_data']
        
        # Utilise le nouveau moteur mais avec format de réponse legacy
        start_time = time.time()
        matching_result = calculate_advanced_score(cv_data, job_data)
        processing_time = round((time.time() - start_time) * 1000, 2)
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'processing_time_ms': processing_time,
            'matching_analysis': matching_result,
            'api_version': '2.1-legacy-compatible'
        })
        
    except MatchingAPIError:
        raise
    except Exception as e:
        logger.error(f"Erreur matching complet: {e}")
        raise MatchingAPIError(f'Erreur lors du calcul de matching: {str(e)}', 500)

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
        'soft_skills': ['communication', 'persuasion'],
        'experience_years': 5
    }
    
    test_job = {
        'title': 'Assistant Facturation',
        'missions': [
            {'description': 'Facturation clients', 'category': 'facturation'},
            {'description': 'Contrôle des comptes', 'category': 'contrôle'},
            {'description': 'Saisie comptable', 'category': 'comptabilité'},
            {'description': 'Reporting financier', 'category': 'reporting'}
        ],
        'requirements': {
            'technical_skills': ['facturation', 'comptabilité', 'excel'],
            'soft_skills': ['rigueur', 'organisation'],
            'experience_level': '1-3 ans'
        }
    }
    
    # Test avec ancien et nouveau système
    engine = EnhancedMatchingEngine()
    
    enhanced_result = engine.calculate_global_enhanced_score(test_cv, test_job)
    
    return jsonify({
        'test_case': 'Hugo Salvat - Ingénieur d\'affaires IT vs Assistant Facturation',
        'expected_result': 'Score faible (< 30%) due à incompatibilité des domaines',
        'enhanced_result': enhanced_result,
        'algorithm_version': '2.1-enhanced',
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

@app.route('/api/matching/files', methods=['POST'])
def matching_files():
    """
    Endpoint pour matching avec upload de fichiers PDF
    Utilise le nouveau moteur amélioré
    """
    try:
        if 'cv_file' not in request.files or 'job_file' not in request.files:
            raise MatchingAPIError('cv_file et job_file requis')
        
        cv_file = request.files['cv_file']
        job_file = request.files['job_file']
        
        if cv_file.filename == '' or job_file.filename == '':
            raise MatchingAPIError('Fichiers vides non autorisés')
        
        # Sauvegarde temporaire des fichiers
        cv_filename = secure_filename(cv_file.filename)
        job_filename = secure_filename(job_file.filename)
        
        cv_path = os.path.join(UPLOAD_FOLDER, f"cv_{int(time.time())}_{cv_filename}")
        job_path = os.path.join(UPLOAD_FOLDER, f"job_{int(time.time())}_{job_filename}")
        
        cv_file.save(cv_path)
        job_file.save(job_path)
        
        try:
            # Parsing du CV
            with open(cv_path, 'rb') as f:
                cv_response = requests.post(
                    f"{CV_PARSER_URL}/api/parse-cv/",
                    files={'file': f},
                    data={'force_refresh': 'false'},
                    timeout=30
                )
            
            if not cv_response.ok:
                raise MatchingAPIError(f'Erreur parsing CV: {cv_response.status_code}')
            
            cv_data = cv_response.json()
            
            # Parsing du Job
            with open(job_path, 'rb') as f:
                job_response = requests.post(
                    f"{JOB_PARSER_URL}/api/parse-job",
                    files={'file': f},
                    data={'force_refresh': 'false'},
                    timeout=30
                )
            
            if not job_response.ok:
                raise MatchingAPIError(f'Erreur parsing Job: {job_response.status_code}')
            
            job_data = job_response.json()
            
            # Calcul du matching avec moteur amélioré
            start_time = time.time()
            engine = EnhancedMatchingEngine()
            matching_result = engine.calculate_global_enhanced_score(cv_data, job_data)
            processing_time = round((time.time() - start_time) * 1000, 2)
            
            return jsonify({
                'status': 'success',
                'timestamp': datetime.now().isoformat(),
                'processing_time_ms': processing_time,
                'files_processed': {
                    'cv_file': cv_filename,
                    'job_file': job_filename
                },
                'cv_data': cv_data,
                'job_data': job_data,
                'matching_analysis': matching_result,
                'api_version': '2.1-enhanced'
            })
            
        finally:
            # Nettoyage des fichiers temporaires
            try:
                os.remove(cv_path)
                os.remove(job_path)
            except:
                pass
        
    except MatchingAPIError:
        raise
    except Exception as e:
        logger.error(f"Erreur matching fichiers: {e}")
        raise MatchingAPIError(f'Erreur lors du traitement des fichiers: {str(e)}', 500)

if __name__ == '__main__':
    print("🚀 SuperSmartMatch V2.1 - API Améliorée avec Compatibilité Domaines")
    print("="*70)
    print("🆕 NOUVELLES FONCTIONNALITÉS:")
    print("   ✅ Détection automatique des domaines métiers")
    print("   ✅ Matrice de compatibilité des domaines")
    print("   ✅ Filtrage sémantique des missions")
    print("   ✅ Prévention des faux positifs")
    print("   ✅ Système d'alertes intelligent")
    print("")
    print("📊 NOUVELLES PONDÉRATIONS:")
    print("   • Compatibilité métier: 25% (NOUVEAU)")
    print("   • Missions: 30% (↓ de 40%)")
    print("   • Compétences: 25% (↓ de 30%)")
    print("   • Expérience: 10% (↓ de 15%)")
    print("   • Qualité: 10% (↓ de 15%)")
    print("")
    print("📡 ENDPOINTS DISPONIBLES:")
    print("   GET  /health                     - Health check + info version")
    print("   POST /api/matching/enhanced      - Nouveau matching amélioré")
    print("   POST /api/matching/complete      - Matching legacy compatible")
    print("   POST /api/matching/files         - Matching avec upload fichiers")
    print("   GET  /api/test/hugo-salvat       - Test cas problématique")
    print("")
    print("🧪 TESTS DISPONIBLES:")
    print("   curl http://localhost:5055/api/test/hugo-salvat")
    print("")
    print("🌐 Serveur démarré sur: http://localhost:5055")
    
    app.run(host='0.0.0.0', port=5055, debug=True)
