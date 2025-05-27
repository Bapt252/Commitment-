#!/usr/bin/env python3

import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ajouter le répertoire parent
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SuperSmartMatch:
    def __init__(self):
        self.algorithms = {}
        self.load_algorithms()
    
    def load_algorithms(self):
        # Algorithme simple de fallback
        self.algorithms['fallback'] = self.simple_matching
        
        # Essayer de charger les autres algorithmes
        try:
            from matching_engine import match_candidate_with_jobs
            self.algorithms['original'] = match_candidate_with_jobs
            logger.info("✅ Algorithme ORIGINAL chargé")
        except ImportError:
            logger.warning("⚠️ Algorithme original non disponible")
        
        try:
            from matching_engine_enhanced import enhanced_match_candidate_with_jobs
            self.algorithms['enhanced'] = enhanced_match_candidate_with_jobs
            logger.info("✅ Algorithme ENHANCED chargé")
        except ImportError:
            logger.warning("⚠️ Algorithme enhanced non disponible")
        
        logger.info(f"📊 {len(self.algorithms)} algorithmes chargés")
    
    def simple_matching(self, cv_data, questionnaire_data, job_data):
        """Algorithme simple qui fonctionne toujours"""
        results = []
        candidate_skills = set(cv_data.get('competences', []))
        
        for job in job_data:
            job_skills = set(job.get('competences', []))
            
            if candidate_skills and job_skills:
                common_skills = candidate_skills.intersection(job_skills)
                score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 50
            else:
                score = 50
            
            job_copy = job.copy()
            job_copy['matching_score'] = min(100, max(0, int(score)))
            results.append(job_copy)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def match(self, cv_data, questionnaire_data, job_data, algorithm="auto", limit=10):
        """Méthode principale"""
        try:
            # Sélection de l'algorithme
            if algorithm == "auto":
                if 'enhanced' in self.algorithms:
                    algorithm = 'enhanced'
                elif 'original' in self.algorithms:
                    algorithm = 'original'
                else:
                    algorithm = 'fallback'
            
            if algorithm not in self.algorithms:
                algorithm = 'fallback'
            
            # Exécution
            results = self.algorithms[algorithm](cv_data, questionnaire_data, job_data)
            
            if limit > 0:
                results = results[:limit]
            
            return {
                'success': True,
                'algorithm_used': algorithm,
                'total_results': len(results),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Erreur: {e}")
            # Fallback vers l'algorithme simple
            results = self.simple_matching(cv_data, questionnaire_data, job_data)
            return {
                'success': True,
                'algorithm_used': 'fallback',
                'total_results': len(results),
                'results': results[:limit] if limit > 0 else results,
                'fallback_used': True
            }

# Instance globale
service = SuperSmartMatch()

@app.route('/')
def index():
    return jsonify({
        'service': 'SuperSmartMatch',
        'status': 'running',
        'algorithms': list(service.algorithms.keys())
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'algorithms_loaded': len(service.algorithms),
        'available_algorithms': list(service.algorithms.keys())
    })

@app.route('/api/algorithms')
def algorithms():
    return jsonify({
        'algorithms': {name: {'status': 'available'} for name in service.algorithms.keys()},
        'total_count': len(service.algorithms)
    })

@app.route('/api/match', methods=['POST'])
def match():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON required'}), 400
        
        cv_data = data.get('cv_data', {})
        questionnaire_data = data.get('questionnaire_data', {})
        job_data = data.get('job_data', [])
        algorithm = data.get('algorithm', 'auto')
        limit = data.get('limit', 10)
        
        if not job_data:
            return jsonify({'error': 'job_data required'}), 400
        
        result = service.match(cv_data, questionnaire_data, job_data, algorithm, limit)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = 5060
    logger.info(f"🚀 Démarrage sur le port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
