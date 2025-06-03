from flask import Flask, jsonify, request
import time
import random

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "Nexten Matcher", "version": "nexten"})

@app.route('/api/match', methods=['POST'])
def match():
    # Simulation fallback Nexten (ML avancé mais plus lent)
    time.sleep(random.uniform(0.08, 0.12))  # 80-120ms
    
    data = request.get_json()
    jobs = data.get('jobs', [])
    
    matches = []
    for job in jobs:
        score = random.randint(70, 90)  # Bon mais pas optimal
        matches.append({
            "job_id": job.get('id'),
            "score": score,
            "ml_confidence": random.uniform(0.7, 0.9)
        })
    
    return jsonify({
        "matches": matches,
        "processing_time_ms": random.randint(85, 115),
        "algorithm": "nexten_ml_advanced"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5052, debug=True)
