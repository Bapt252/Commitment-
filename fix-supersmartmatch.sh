#!/bin/bash

# SuperSmartMatch Fix - Version Ultra-Minimaliste
# Absolument AUCUN caractère spécial qui peut polluer

set -e

echo "Fix SuperSmartMatch - Version Ultra-Clean"
echo "========================================"

# Fonction pour obtenir un port libre (SANS émojis)
get_free_port() {
    if lsof -ti :5060 > /dev/null 2>&1; then
        echo "Port 5060 occupé, libération..."
        for pid in $(lsof -ti :5060 2>/dev/null || true); do
            if ps -p $pid > /dev/null 2>&1; then
                kill -TERM $pid 2>/dev/null || true
                sleep 1
            fi
        done
        sleep 2
        if lsof -ti :5060 > /dev/null 2>&1; then
            echo "5061"  # Retourne juste le numéro
        else
            echo "5060"
        fi
    else
        echo "5060"
    fi
}

# Obtenir le port UNE SEULE fois
PORT=$(get_free_port)
echo "Port sélectionné: $PORT"

# Créer le dossier
mkdir -p super-smart-match

# Créer l'app Python ultra-simple
echo "Création de l'application Python..."
cat > "super-smart-match/app.py" << 'EOF'
#!/usr/bin/env python3

import os
import logging
from typing import Dict, List, Any
from flask import Flask, request, jsonify
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SuperSmartMatch:
    def __init__(self):
        self.algorithms = {
            'simple': self.simple_matching,
            'enhanced': self.enhanced_matching,
            'auto': self.auto_matching
        }
        logger.info(f"Algorithmes chargés: {len(self.algorithms)}")
    
    def simple_matching(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict]) -> List[Dict]:
        results = []
        candidate_skills = set(cv_data.get('competences', []))
        
        for job in job_data:
            job_skills = set(job.get('competences', []))
            
            if candidate_skills and job_skills:
                common = candidate_skills.intersection(job_skills)
                score = (len(common) / len(job_skills)) * 100 if job_skills else 50
            else:
                score = 50
            
            job_copy = job.copy()
            job_copy['matching_score'] = int(score)
            results.append(job_copy)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def enhanced_matching(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict]) -> List[Dict]:
        results = []
        candidate_skills = set(cv_data.get('competences', []))
        candidate_exp = cv_data.get('annees_experience', 0)
        
        for job in job_data:
            job_skills = set(job.get('competences', []))
            required_exp = job.get('experience_requise', 0)
            
            # Score compétences
            if candidate_skills and job_skills:
                common = candidate_skills.intersection(job_skills)
                skill_score = (len(common) / len(job_skills)) * 100 if job_skills else 30
            else:
                skill_score = 30
            
            # Score expérience
            if required_exp == 0:
                exp_score = 100
            elif candidate_exp >= required_exp:
                exp_score = min(100, 90 + (candidate_exp - required_exp) * 2)
            else:
                exp_score = max(20, (candidate_exp / required_exp) * 90)
            
            # Score final pondéré
            final_score = int(skill_score * 0.7 + exp_score * 0.3)
            
            job_copy = job.copy()
            job_copy['matching_score'] = min(100, max(0, final_score))
            results.append(job_copy)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def auto_matching(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict]) -> List[Dict]:
        skills_count = len(cv_data.get('competences', []))
        if skills_count >= 3:
            return self.enhanced_matching(cv_data, questionnaire_data, job_data)
        else:
            return self.simple_matching(cv_data, questionnaire_data, job_data)
    
    def match(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict], 
              algorithm: str = "auto", limit: int = 10) -> Dict[str, Any]:
        
        if algorithm not in self.algorithms:
            algorithm = "auto"
        
        try:
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
            return {'success': False, 'error': str(e)}

service = SuperSmartMatch()

@app.route('/')
def index():
    return jsonify({
        'service': 'SuperSmartMatch',
        'version': '1.0.0-ultraclean',
        'algorithms': list(service.algorithms.keys())
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'algorithms': list(service.algorithms.keys())
    })

@app.route('/api/match', methods=['POST'])
def match():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'JSON required'}), 400
        
        required = ['cv_data', 'questionnaire_data', 'job_data']
        for field in required:
            if field not in data:
                return jsonify({'error': f'Missing {field}'}), 400
        
        result = service.match(
            data['cv_data'],
            data['questionnaire_data'], 
            data['job_data'],
            data.get('algorithm', 'auto'),
            data.get('limit', 10)
        )
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("Démarrage SuperSmartMatch")
    port = int(os.environ.get('PORT', 5061))
    app.run(host='0.0.0.0', port=port, debug=True)
EOF

# Créer le script de démarrage ultra-simple
echo "Création du script de démarrage..."
cat > "start-supersmartmatch.sh" << EOF
#!/bin/bash

echo "Démarrage SuperSmartMatch sur port $PORT"

if ! command -v python3 &> /dev/null; then
    echo "Python 3 requis"
    exit 1
fi

cd super-smart-match

if [ ! -d "venv" ]; then
    echo "Installation dépendances..."
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-cors
else
    source venv/bin/activate
fi

export PORT=$PORT
export FLASK_ENV=development

echo "Service sur: http://localhost:$PORT"
python3 app.py
EOF

chmod +x "start-supersmartmatch.sh"

# Créer le script de test ultra-simple
echo "Création du script de test..."
cat > "test-supersmartmatch.sh" << EOF
#!/bin/bash

echo "Test SuperSmartMatch port $PORT"

# Health check
echo "Test health..."
curl -s "http://localhost:$PORT/api/health" | python3 -m json.tool 2>/dev/null || echo "Health failed"

# Test matching
echo "Test matching..."
curl -s -X POST "http://localhost:$PORT/api/match" \\
  -H "Content-Type: application/json" \\
  -d '{
    "cv_data": {"competences": ["Python"], "annees_experience": 3},
    "questionnaire_data": {"adresse": "Paris"},
    "job_data": [{"id": "1", "titre": "Dev", "competences": ["Python"]}],
    "algorithm": "auto"
  }' | python3 -m json.tool 2>/dev/null || echo "Matching failed"

echo "Tests terminés"
EOF

chmod +x "test-supersmartmatch.sh"

echo ""
echo "SuperSmartMatch prêt!"
echo "Démarrer: ./start-supersmartmatch.sh"
echo "Tester: ./test-supersmartmatch.sh"
echo "API: http://localhost:$PORT"
echo ""

if [ -t 0 ]; then
    echo -n "Démarrer maintenant ? (y/N): "
    read response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        ./start-supersmartmatch.sh
    fi
fi
