#!/usr/bin/env python3
"""
SuperSmartMatch V1 - Legacy Matching Service
"""

from flask import Flask, request, jsonify
import random
import time
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "version": "v1", "service": "SuperSmartMatch Legacy"})

@app.route('/match', methods=['POST'])
@app.route('/api/match', methods=['POST'])
def match():
    data = request.get_json()
    
    # Simuler temps de traitement V1
    start_time = time.time()
    time.sleep(random.uniform(0.1, 0.15))  # 100-150ms
    processing_time = (time.time() - start_time) * 1000
    
    # Calculer score basique
    candidate = data.get('candidate', {})
    jobs = data.get('jobs', [{}])
    job = jobs[0] if jobs else {}
    
    # Score conservateur V1
    base_score = 75
    
    # Bonus compétences
    candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
    required_skills = set([s.lower() for s in job.get('required_skills', [])])
    
    if required_skills:
        skill_match = len(candidate_skills & required_skills) / len(required_skills)
        base_score += skill_match * 15
    
    # Malus expérience
    candidate_exp = candidate.get('experience', 0)
    required_exp = job.get('experience_required', 0)
    
    if candidate_exp < required_exp:
        base_score -= 10
    
    # Ajouter variabilité
    final_score = max(0, min(100, base_score + random.uniform(-5, 5)))
    
    return jsonify({
        "matches": [{
            "job_id": job.get('id', 1),
            "score": round(final_score, 1),
            "confidence": "medium"
        }],
        "processing_time_ms": round(processing_time, 0),
        "algorithm_used": "legacy",
        "version": "v1"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
