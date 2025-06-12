#!/usr/bin/env python3
"""
SuperSmartMatch V2 - AI Enhanced Matching Service
"""

from flask import Flask, request, jsonify
import random
import time
import os
import requests

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "version": "v2", "service": "SuperSmartMatch AI Enhanced"})

@app.route('/match', methods=['POST'])
@app.route('/api/match', methods=['POST'])
def match():
    data = request.get_json()
    
    # Simuler temps de traitement V2 (plus rapide)
    start_time = time.time()
    time.sleep(random.uniform(0.08, 0.12))  # 80-120ms
    processing_time = (time.time() - start_time) * 1000
    
    # Calculer score amélioré V2
    candidate = data.get('candidate', {})
    jobs = data.get('jobs', [{}])
    job = jobs[0] if jobs else {}
    
    # Score plus optimiste V2
    base_score = 85
    
    # Bonus compétences (algorithme amélioré)
    candidate_skills = set([s.lower() for s in candidate.get('skills', [])])
    required_skills = set([s.lower() for s in job.get('required_skills', [])])
    
    if required_skills:
        skill_match = len(candidate_skills & required_skills) / len(required_skills)
        base_score += skill_match * 20  # Bonus plus généreux
        
        # Bonus compétences supplémentaires
        extra_skills = candidate_skills - required_skills
        if extra_skills:
            base_score += min(5, len(extra_skills))
    
    # Gestion expérience plus nuancée
    candidate_exp = candidate.get('experience', 0)
    required_exp = job.get('experience_required', 0)
    
    if candidate_exp >= required_exp:
        base_score += 5
    elif candidate_exp >= required_exp * 0.8:
        base_score += 2  # Proche du requis
    
    # Ajouter variabilité réduite (plus précis)
    final_score = max(0, min(100, base_score + random.uniform(-2, 3)))
    
    # Déterminer algorithme utilisé (75% Nexten, 25% Legacy)
    algorithm = "nexten" if random.random() < 0.75 else "legacy_fallback"
    confidence = "high" if final_score > 90 else "medium" if final_score > 75 else "low"
    
    return jsonify({
        "matches": [{
            "job_id": job.get('id', 1),
            "score": round(final_score, 1),
            "confidence": confidence
        }],
        "processing_time_ms": round(processing_time, 0),
        "algorithm_used": algorithm,
        "version": "v2",
        "explanation": {
            "strengths": ["Good skill match", "Relevant experience"],
            "recommendation": "Strong candidate for this position"
        } if final_score > 85 else {
            "areas_of_attention": ["Some skills missing", "Experience gap"],
            "recommendation": "Consider with additional assessment"
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
