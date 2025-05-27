#!/bin/bash

# Fix SuperSmartMatch - Script FINAL corrigé
# Version ultra-robuste sans pollution de caractères

set -e

echo "🔧 Fix SuperSmartMatch - Version FINALE"
echo "========================================"

# 1. Vérifier et libérer le port 5060
fix_port_issue() {
    echo "ℹ️  Vérification du port 5060..."
    
    PORT_USERS=$(lsof -ti :5060 2>/dev/null || true)
    
    if [ -n "$PORT_USERS" ]; then
        echo "⚠️  Port 5060 occupé, libération..."
        
        for pid in $PORT_USERS; do
            if ps -p $pid > /dev/null 2>&1; then
                kill -TERM $pid 2>/dev/null || true
                sleep 1
                if ps -p $pid > /dev/null 2>&1; then
                    kill -9 $pid 2>/dev/null || true
                fi
            fi
        done
        
        sleep 2
        if lsof -ti :5060 > /dev/null 2>&1; then
            echo "❌ Port 5060 toujours occupé, utilisation du port 5061"
            echo "5061"
        else
            echo "✅ Port 5060 libéré"
            echo "5060"
        fi
    else
        echo "✅ Port 5060 disponible"
        echo "5060"
    fi
}

# 2. Créer le script de démarrage PROPRE
create_startup_script() {
    local PORT="$1"
    echo "📝 Création du script de démarrage pour port $PORT..."
    
    cat > "start-supersmartmatch.sh" << EOF
#!/bin/bash

echo "🚀 Démarrage SuperSmartMatch sur port $PORT"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 requis"
    exit 1
fi

if [ ! -d "super-smart-match" ]; then
    mkdir -p super-smart-match
fi

cd super-smart-match

if [ ! -d "venv" ]; then
    echo "📦 Installation dépendances..."
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-cors pandas numpy scikit-learn
else
    source venv/bin/activate
fi

export PYTHONPATH="\$(pwd)/..:$PYTHONPATH"
export PORT=$PORT
export FLASK_ENV=development

echo "🎯 Service sur:"
echo "   Health: http://localhost:$PORT/api/health"  
echo "   API: http://localhost:$PORT/api/match"

python3 app.py
EOF
    
    chmod +x "start-supersmartmatch.sh"
    echo "✅ Script de démarrage créé"
}

# 3. Créer le script de test PROPRE
create_test_script() {
    local PORT="$1"
    echo "🧪 Création du script de test pour port $PORT..."
    
    cat > "test-supersmartmatch.sh" << EOF
#!/bin/bash

PORT=$PORT
BASE_URL="http://localhost:\$PORT"

echo "🧪 Test SuperSmartMatch port \$PORT"

echo "1️⃣ Health check..."
curl -s "\$BASE_URL/api/health" | python3 -m json.tool 2>/dev/null || echo "❌ Health failed"

echo ""
echo "2️⃣ Test matching..."
curl -s -X POST "\$BASE_URL/api/match" \\
  -H "Content-Type: application/json" \\
  -d '{
    "cv_data": {
      "competences": ["Python", "React"],
      "annees_experience": 3
    },
    "questionnaire_data": {
      "adresse": "Paris",
      "salaire_souhaite": 45000
    },
    "job_data": [{
      "id": "job1",
      "titre": "Développeur",
      "competences": ["Python"],
      "localisation": "Paris"
    }],
    "algorithm": "auto"
  }' | python3 -m json.tool 2>/dev/null || echo "❌ Matching failed"

echo ""
echo "✅ Tests terminés"
EOF
    
    chmod +x "test-supersmartmatch.sh"
    echo "✅ Script de test créé"
}

# 4. Créer l'application Python PROPRE
create_clean_app() {
    echo "🐍 Création de l'application Python..."
    
    mkdir -p super-smart-match
    
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
            'enhanced': self.enhanced_matching,
            'simple': self.simple_matching,
            'auto': self.auto_matching
        }
        logger.info(f"✅ {len(self.algorithms)} algorithmes chargés")
    
    def simple_matching(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict]) -> List[Dict]:
        results = []
        candidate_skills = set(cv_data.get('competences', []))
        candidate_exp = cv_data.get('annees_experience', 0)
        
        for job in job_data:
            job_skills = set(job.get('competences', []))
            
            if candidate_skills and job_skills:
                common_skills = candidate_skills.intersection(job_skills)
                skill_score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 0
            else:
                skill_score = 50
            
            required_exp = job.get('experience_requise', 0)
            if candidate_exp >= required_exp:
                exp_bonus = min(10, candidate_exp - required_exp)
            else:
                exp_bonus = max(-20, (candidate_exp - required_exp) * 5)
            
            final_score = min(100, max(0, int(skill_score + exp_bonus)))
            
            job_copy = job.copy()
            job_copy['matching_score'] = final_score
            job_copy['matching_details'] = {
                'skill_score': int(skill_score),
                'experience_bonus': exp_bonus,
                'common_skills': list(common_skills) if candidate_skills and job_skills else []
            }
            results.append(job_copy)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        return results
    
    def enhanced_matching(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict]) -> List[Dict]:
        logger.info("🚀 Enhanced matching")
        
        results = []
        candidate_skills = set(cv_data.get('competences', []))
        candidate_exp = cv_data.get('annees_experience', 0)
        candidate_location = questionnaire_data.get('adresse', '')
        candidate_salary = questionnaire_data.get('salaire_souhaite', 0)
        
        for job in job_data:
            job_skills = set(job.get('competences', []))
            job_location = job.get('localisation', '')
            
            # Score compétences (40%)
            if candidate_skills and job_skills:
                common_skills = candidate_skills.intersection(job_skills)
                skill_score = (len(common_skills) / len(job_skills)) * 100 if job_skills else 0
            else:
                skill_score = 30
            
            # Score expérience (30%)
            required_exp = job.get('experience_requise', 0)
            if required_exp == 0:
                exp_score = 100
            elif candidate_exp >= required_exp:
                exp_score = min(100, 90 + (candidate_exp - required_exp) * 2)
            else:
                exp_score = max(20, (candidate_exp / required_exp) * 90)
            
            # Score localisation (20%)
            if candidate_location and job_location:
                if candidate_location.lower() in job_location.lower() or job_location.lower() in candidate_location.lower():
                    location_score = 100
                elif 'paris' in candidate_location.lower() and 'paris' in job_location.lower():
                    location_score = 90
                else:
                    location_score = 50
            else:
                location_score = 70
            
            # Score salaire (10%)
            salary_score = 70
            if candidate_salary > 0:
                job_salary_min = job.get('salaire_min', 0)
                job_salary_max = job.get('salaire_max', 0)
                
                if job_salary_max > 0:
                    if job_salary_min <= candidate_salary <= job_salary_max:
                        salary_score = 100
                    elif candidate_salary < job_salary_min:
                        salary_score = 90
                    else:
                        over_budget = ((candidate_salary - job_salary_max) / job_salary_max) * 100
                        salary_score = max(20, 100 - over_budget)
            
            final_score = (
                skill_score * 0.4 +
                exp_score * 0.3 +
                location_score * 0.2 +
                salary_score * 0.1
            )
            
            job_copy = job.copy()
            job_copy['matching_score'] = min(100, max(0, int(final_score)))
            job_copy['matching_details'] = {
                'skills': int(skill_score),
                'experience': int(exp_score),
                'location': int(location_score),
                'salary': int(salary_score),
                'common_skills': list(common_skills) if candidate_skills and job_skills else []
            }
            results.append(job_copy)
        
        results.sort(key=lambda x: x['matching_score'], reverse=True)
        logger.info(f"✅ Enhanced matching: {len(results)} résultats")
        return results
    
    def auto_matching(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict]) -> List[Dict]:
        skills_count = len(cv_data.get('competences', []))
        has_location = bool(questionnaire_data.get('adresse'))
        has_salary = bool(questionnaire_data.get('salaire_souhaite'))
        
        if skills_count >= 3 and (has_location or has_salary):
            return self.enhanced_matching(cv_data, questionnaire_data, job_data)
        else:
            return self.simple_matching(cv_data, questionnaire_data, job_data)
    
    def match(self, cv_data: Dict, questionnaire_data: Dict, job_data: List[Dict], 
              algorithm: str = "auto", limit: int = 10) -> Dict[str, Any]:
        
        if algorithm not in self.algorithms:
            algorithm = "auto"
        
        try:
            logger.info(f"🎯 Matching: {algorithm}")
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
            logger.error(f"❌ Erreur: {e}")
            return {
                'success': False,
                'error': str(e),
                'algorithm_used': algorithm
            }

smart_match_service = SuperSmartMatch()

@app.route('/')
def index():
    return jsonify({
        'service': 'SuperSmartMatch',
        'version': '1.0.0-clean',
        'status': 'active',
        'algorithms': list(smart_match_service.algorithms.keys())
    })

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'SuperSmartMatch',
        'algorithms_loaded': len(smart_match_service.algorithms),
        'available_algorithms': list(smart_match_service.algorithms.keys())
    })

@app.route('/api/algorithms')
def algorithms():
    return jsonify({
        'algorithms': {
            'simple': {'description': 'Matching basique par compétences'},
            'enhanced': {'description': 'Matching avancé multi-critères'},
            'auto': {'description': 'Sélection automatique du meilleur algorithme'}
        },
        'total_count': len(smart_match_service.algorithms)
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
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        cv_data = data['cv_data']
        questionnaire_data = data['questionnaire_data']
        job_data = data['job_data']
        algorithm = data.get('algorithm', 'auto')
        limit = data.get('limit', 10)
        
        if not isinstance(job_data, list) or len(job_data) == 0:
            return jsonify({'error': 'job_data must be a non-empty list'}), 400
        
        result = smart_match_service.match(cv_data, questionnaire_data, job_data, algorithm, limit)
        
        if not result.get('success'):
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Erreur endpoint: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Démarrage SuperSmartMatch")
    port = int(os.environ.get('PORT', 5061))
    app.run(host='0.0.0.0', port=port, debug=True)
EOF
    
    echo "✅ Application Python créée"
}

# Fonction principale
main() {
    echo "🚀 Début correction finale..."
    
    # Obtenir le port une seule fois
    NEW_PORT=$(fix_port_issue)
    echo "📌 Port sélectionné: $NEW_PORT"
    
    # Créer les composants
    create_clean_app
    create_startup_script "$NEW_PORT"
    create_test_script "$NEW_PORT"
    
    echo ""
    echo "✅ SuperSmartMatch FINAL prêt!"
    echo "🚀 Démarrer: ./start-supersmartmatch.sh"
    echo "🧪 Tester: ./test-supersmartmatch.sh"
    echo "🌐 API: http://localhost:$NEW_PORT"
    echo ""
    
    if [ -t 0 ]; then
        echo -n "Démarrer maintenant ? (y/N): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            echo "🚀 Démarrage..."
            ./start-supersmartmatch.sh
        fi
    fi
}

main "$@"
