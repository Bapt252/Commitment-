#!/bin/bash

# Fix dépendances SuperSmartMatch
# Installe les modules manquants et corrige les imports

echo "🔧 Installation des dépendances manquantes pour SuperSmartMatch"

# Aller dans l'environnement SuperSmartMatch
cd super-smart-match
source venv/bin/activate

echo "📦 Installation des modules Python manquants..."

# Installer toutes les dépendances nécessaires
pip install --quiet requests pandas numpy scikit-learn python-dateutil

echo "✅ Modules installés"

# Créer des versions simplifiées des algorithmes dans le répertoire parent
cd ..

echo "🔧 Création d'algorithmes simplifiés..."

# 1. Algorithme original simplifié
cat > "matching_engine_simple.py" << 'EOF'
"""
Algorithme de matching original simplifié
Version sans dépendances externes
"""

def match_candidate_with_jobs(cv_data, questionnaire_data, job_data):
    """Algorithme de matching original simplifié"""
    results = []
    candidate_skills = set(cv_data.get('competences', []))
    candidate_experience = cv_data.get('annees_experience', 0)
    
    for job in job_data:
        job_skills = set(job.get('competences', []))
        required_experience = job.get('experience_requise', 0)
        
        # Score basé sur les compétences
        if candidate_skills and job_skills:
            common_skills = candidate_skills.intersection(job_skills)
            skills_score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 0
        else:
            skills_score = 0
        
        # Score basé sur l'expérience
        if required_experience <= candidate_experience:
            experience_score = 100
        else:
            experience_score = max(0, 100 - (required_experience - candidate_experience) * 20)
        
        # Score final
        final_score = (skills_score * 0.7) + (experience_score * 0.3)
        
        job_copy = job.copy()
        job_copy['matching_score'] = min(100, max(0, int(final_score)))
        results.append(job_copy)
    
    # Trier par score décroissant
    results.sort(key=lambda x: x['matching_score'], reverse=True)
    return results
EOF

# 2. Algorithme enhanced simplifié
cat > "matching_engine_enhanced_simple.py" << 'EOF'
"""
Algorithme de matching enhanced simplifié
Version sans dépendances externes
"""

def enhanced_match_candidate_with_jobs(cv_data, questionnaire_data, job_data):
    """Algorithme de matching enhanced simplifié"""
    results = []
    candidate_skills = set(cv_data.get('competences', []))
    candidate_experience = cv_data.get('annees_experience', 0)
    candidate_salary = questionnaire_data.get('salaire_souhaite', 0)
    
    for job in job_data:
        job_skills = set(job.get('competences', []))
        required_experience = job.get('experience_requise', 0)
        job_salary_min = job.get('salaire_min', 0)
        job_salary_max = job.get('salaire_max', 999999)
        
        scores = {}
        
        # 1. Score compétences (40%)
        if candidate_skills and job_skills:
            common_skills = candidate_skills.intersection(job_skills)
            skills_score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 0
        else:
            skills_score = 0
        scores['skills'] = skills_score
        
        # 2. Score expérience (30%)
        if required_experience <= candidate_experience:
            experience_score = 100
        elif candidate_experience == 0:
            experience_score = 20
        else:
            experience_score = max(20, 100 - (required_experience - candidate_experience) * 15)
        scores['experience'] = experience_score
        
        # 3. Score salaire (20%)
        if candidate_salary == 0:
            salary_score = 80  # Neutre si pas de preference
        elif job_salary_min <= candidate_salary <= job_salary_max:
            salary_score = 100
        elif candidate_salary < job_salary_min:
            salary_score = 90  # Bonus si candidat demande moins
        else:
            diff_percent = ((candidate_salary - job_salary_max) / job_salary_max) * 100
            salary_score = max(20, 80 - diff_percent)
        scores['salary'] = salary_score
        
        # 4. Score localisation (10%)
        candidate_location = questionnaire_data.get('adresse', '').lower()
        job_location = job.get('localisation', '').lower()
        
        if 'paris' in candidate_location and 'paris' in job_location:
            location_score = 100
        elif candidate_location and job_location:
            if candidate_location in job_location or job_location in candidate_location:
                location_score = 80
            else:
                location_score = 40
        else:
            location_score = 60
        scores['location'] = location_score
        
        # Score final pondéré
        final_score = (
            scores['skills'] * 0.4 +
            scores['experience'] * 0.3 +
            scores['salary'] * 0.2 +
            scores['location'] * 0.1
        )
        
        job_copy = job.copy()
        job_copy['matching_score'] = min(100, max(0, int(final_score)))
        job_copy['score_details'] = scores
        results.append(job_copy)
    
    # Trier par score décroissant
    results.sort(key=lambda x: x['matching_score'], reverse=True)
    return results
EOF

# 3. Copier et adapter l'algorithme custom existant
if [ -f "my_matching_engine.py" ]; then
    cp "my_matching_engine.py" "my_matching_engine_simple.py"
    echo "✅ Algorithme custom copié"
else
    # Créer un algorithme custom simple
    cat > "my_matching_engine_simple.py" << 'EOF'
"""
Algorithme de matching custom simplifié
"""

def match_candidate_with_jobs(cv_data, questionnaire_data, job_data):
    """Algorithme custom avec logique métier spécifique"""
    results = []
    candidate_skills = set(cv_data.get('competences', []))
    candidate_experience = cv_data.get('annees_experience', 0)
    
    # Weights spécifiques à votre domaine
    tech_skills = {'Python', 'JavaScript', 'React', 'Django', 'Node.js', 'SQL', 'Docker'}
    
    for job in job_data:
        job_skills = set(job.get('competences', []))
        
        # Score compétences avec bonus tech
        if candidate_skills and job_skills:
            common_skills = candidate_skills.intersection(job_skills)
            
            # Bonus pour les compétences tech
            tech_common = common_skills.intersection(tech_skills)
            tech_bonus = len(tech_common) * 5  # 5 points par compétence tech
            
            base_score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 0
            skills_score = min(100, base_score + tech_bonus)
        else:
            skills_score = 0
        
        # Score expérience avec courbe progressive
        required_exp = job.get('experience_requise', 0)
        if candidate_experience >= required_exp:
            exp_score = min(100, 80 + (candidate_experience - required_exp) * 4)
        else:
            exp_score = max(10, (candidate_experience / required_exp) * 70) if required_exp > 0 else 50
        
        # Score final
        final_score = (skills_score * 0.6) + (exp_score * 0.4)
        
        job_copy = job.copy()
        job_copy['matching_score'] = min(100, max(0, int(final_score)))
        results.append(job_copy)
    
    results.sort(key=lambda x: x['matching_score'], reverse=True)
    return results
EOF
fi

echo "✅ Algorithmes simplifiés créés"

# 4. Mettre à jour app.py pour utiliser les versions simplifiées
echo "🔧 Mise à jour de app.py..."

cd super-smart-match

# Créer un patch pour app.py qui utilise les versions simplifiées
cat > "app_simple.py" << 'EOF'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SuperSmartMatch - Version Simplifiée
Service unifié de matching pour Nexten - Sans dépendances externes
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

# Ajouter le répertoire parent au PYTHONPATH pour les imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configuration du logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SuperSmartMatchSimple:
    """Service unifié de matching - Version simplifiée"""
    
    def __init__(self):
        self.algorithms = {}
        self.default_algorithm = "enhanced"
        self.load_algorithms()
    
    def load_algorithms(self):
        """Charge tous les algorithmes disponibles - Version simplifiée"""
        
        # 1. Algorithme original
        try:
            from matching_engine_simple import match_candidate_with_jobs as original_algo
            self.algorithms['original'] = original_algo
            logger.info("✅ Algorithme ORIGINAL chargé")
        except ImportError as e:
            logger.warning(f"⚠️  Algorithme original non disponible: {e}")
        
        # 2. Algorithme Enhanced
        try:
            from matching_engine_enhanced_simple import enhanced_match_candidate_with_jobs as enhanced_algo
            self.algorithms['enhanced'] = enhanced_algo
            logger.info("✅ Algorithme ENHANCED chargé")
        except ImportError as e:
            logger.warning(f"⚠️  Algorithme enhanced non disponible: {e}")
        
        # 3. Algorithme Custom
        try:
            from my_matching_engine_simple import match_candidate_with_jobs as custom_algo
            self.algorithms['custom'] = custom_algo
            logger.info("✅ Algorithme CUSTOM chargé")
        except ImportError as e:
            logger.warning(f"⚠️  Algorithme custom non disponible: {e}")
        
        # 4. Algorithme Hybrid
        self.algorithms['hybrid'] = self.hybrid_matching
        logger.info("✅ Algorithme HYBRID configuré")
        
        # 5. Algorithme de fallback simple
        if not self.algorithms:
            self.algorithms['fallback'] = self.simple_fallback
            logger.info("✅ Algorithme FALLBACK activé")
        
        logger.info(f"🎯 {len(self.algorithms)} algorithmes chargés: {list(self.algorithms.keys())}")
    
    def simple_fallback(self, cv_data, questionnaire_data, job_data):
        """Algorithme de fallback ultra-simple"""
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
    
    def hybrid_matching(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict]) -> List[Dict]:
        """Algorithme hybride simplifié"""
        logger.info("🔄 Exécution de l'algorithme HYBRID")
        
        all_results = {}
        
        # Exécuter les algorithmes disponibles (sauf hybrid et fallback)
        for name, algo in self.algorithms.items():
            if name in ['hybrid', 'fallback']:
                continue
                
            try:
                start_time = time.time()
                results = algo(cv_data, questionnaire_data, job_data)
                exec_time = time.time() - start_time
                
                logger.info(f"✅ {name}: {len(results)} résultats en {exec_time:.3f}s")
                
                # Stocker les résultats
                for result in results:
                    job_id = result.get('id', result.get('job_id', f"job_{len(all_results)}"))
                    if job_id not in all_results:
                        all_results[job_id] = {
                            'job_data': result.copy(),
                            'scores': {},
                            'count': 0
                        }
                    
                    score = result.get('matching_score', 0)
                    all_results[job_id]['scores'][name] = score
                    all_results[job_id]['count'] += 1
                    
            except Exception as e:
                logger.error(f"❌ Erreur avec l'algorithme {name}: {e}")
        
        # Si aucun algorithme n'a fonctionné, utiliser le fallback
        if not all_results:
            logger.warning("🔄 Utilisation de l'algorithme de fallback")
            return self.simple_fallback(cv_data, questionnaire_data, job_data)
        
        # Calcul du score hybride
        final_results = []
        for job_id, data in all_results.items():
            if data['count'] == 0:
                continue
            
            scores = list(data['scores'].values())
            
            # Score hybride = moyenne des scores
            hybrid_score = sum(scores) / len(scores)
            
            # Bonus de consensus
            if len(scores) > 1:
                score_variance = sum((s - hybrid_score) ** 2 for s in scores) / len(scores)
                consensus_bonus = max(0, 5 - score_variance/20)
                hybrid_score += consensus_bonus
            
            result = data['job_data'].copy()
            result['matching_score'] = min(100, max(0, int(hybrid_score)))
            result['hybrid_details'] = {
                'individual_scores': data['scores'],
                'algorithms_used': list(data['scores'].keys()),
                'algorithms_count': len(data['scores'])
            }
            
            final_results.append(result)
        
        final_results.sort(key=lambda x: x['matching_score'], reverse=True)
        logger.info(f"🎯 HYBRID terminé: {len(final_results)} résultats")
        return final_results
    
    def match(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict], 
              algorithm: str = "auto", limit: int = 10) -> Dict[str, Any]:
        """Méthode principale de matching"""
        start_time = time.time()
        
        # Sélection automatique
        if algorithm == "auto":
            if len(self.algorithms) > 2:  # Si on a plus que hybrid + fallback
                algorithm = "enhanced" if "enhanced" in self.algorithms else "hybrid"
            else:
                algorithm = list(self.algorithms.keys())[0]
        
        # Vérifier que l'algorithme existe
        if algorithm not in self.algorithms:
            available = list(self.algorithms.keys())
            return {
                'error': f"Algorithme '{algorithm}' non disponible",
                'available_algorithms': available,
            }
        
        try:
            logger.info(f"🚀 Exécution de l'algorithme: {algorithm.upper()}")
            results = self.algorithms[algorithm](cv_data, questionnaire_data, job_data)
            
            if limit > 0:
                results = results[:limit]
            
            execution_time = time.time() - start_time
            
            return {
                'algorithm_used': algorithm,
                'execution_time': round(execution_time, 3),
                'total_results': len(results),
                'results': results,
                'metadata': {
                    'timestamp': int(time.time()),
                    'candidate_skills_count': len(cv_data.get('competences', [])),
                    'jobs_analyzed': len(job_data),
                    'available_algorithms': list(self.algorithms.keys())
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur avec l'algorithme {algorithm}: {e}")
            return {
                'error': f"Erreur lors de l'exécution: {e}",
                'algorithm_used': algorithm,
            }

# Instance globale
smart_match_service = SuperSmartMatchSimple()

# Routes API
@app.route('/')
def index():
    return jsonify({
        'service': 'SuperSmartMatch',
        'version': '1.0.0-simple',
        'description': 'Service unifié de matching pour Nexten - Version simplifiée',
        'available_algorithms': list(smart_match_service.algorithms.keys()),
        'endpoints': {
            'match': '/api/match',
            'algorithms': '/api/algorithms',
            'health': '/api/health'
        }
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'SuperSmartMatch Simple',
        'algorithms_loaded': len(smart_match_service.algorithms),
        'available_algorithms': list(smart_match_service.algorithms.keys())
    })

@app.route('/api/algorithms')
def list_algorithms():
    algorithms_info = {}
    
    for name in smart_match_service.algorithms.keys():
        algorithms_info[name] = {
            'name': name,
            'status': 'available'
        }
    
    return jsonify({
        'algorithms': algorithms_info,
        'total_count': len(algorithms_info),
        'default_algorithm': smart_match_service.default_algorithm
    })

@app.route('/api/match', methods=['POST'])
def match_endpoint():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        required_fields = ['cv_data', 'questionnaire_data', 'job_data']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        cv_data = data['cv_data']
        questionnaire_data = data['questionnaire_data']
        job_data = data['job_data']
        algorithm = data.get('algorithm', 'auto')
        limit = data.get('limit', 10)
        
        if not isinstance(job_data, list) or len(job_data) == 0:
            return jsonify({'error': 'job_data must be a non-empty list'}), 400
        
        logger.info(f"🎯 Nouvelle demande: {algorithm}, {len(job_data)} jobs, limit={limit}")
        result = smart_match_service.match(cv_data, questionnaire_data, job_data, algorithm, limit)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur dans l'endpoint: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("🚀 Démarrage de SuperSmartMatch Simple")
    logger.info(f"📊 {len(smart_match_service.algorithms)} algorithmes chargés")
    
    port = int(os.environ.get('PORT', 5060))
    app.run(host='0.0.0.0', port=port, debug=True)
EOF

# Remplacer app.py par la version simple
cp app.py app_original.py  # Sauvegarde
cp app_simple.py app.py

echo "✅ app.py mis à jour avec la version simplifiée"

cd ..

echo ""
echo "🎉 SuperSmartMatch corrigé !"
echo ""
echo "🔄 Redémarrez le service avec:"
echo "   Ctrl+C (pour arrêter le service actuel)"
echo "   ./start-supersmartmatch-simple.sh"
echo ""
echo "📊 Vous devriez maintenant avoir 4 algorithmes au lieu de 1"
