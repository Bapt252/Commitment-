from flask import Flask, jsonify, request
import time
import random

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "SuperSmartMatch V2", "version": "2.0.0"})

@app.route('/api/match', methods=['POST'])
def match():
    data = request.get_json()
    candidate = data.get('candidate', {})
    jobs = data.get('jobs', [])
    
    # Simulation matching V2 (plus intelligent)
    matches = []
    for job in jobs:
        score = random.randint(75, 98)  # V2 plus précis (+13%)
        matches.append({
            "job_id": job.get('id'),
            "job_title": job.get('title'),
            "score": score,
            "reasons": ["ai_skills_match", "experience_perfect", "cultural_fit"],
            "confidence": random.uniform(0.85, 0.98)
        })
    
    # Simulation temps de réponse V2 (meilleur)
    time.sleep(random.uniform(0.03, 0.05))  # 30-50ms
    
    return jsonify({
        "matches": matches,
        "processing_time_ms": random.randint(35, 50),
        "algorithm": "ai_smart_matching_v2",
        "improvement_vs_v1": "+13.2%"
    })

@app.route('/metrics')
def metrics():
    return f"""
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter  
http_requests_total{{method="GET",endpoint="/health"}} {random.randint(100, 500)}
http_requests_total{{method="POST",endpoint="/api/match"}} {random.randint(80, 300)}

# HELP response_time_seconds Response time
# TYPE response_time_seconds histogram
response_time_seconds_sum {random.uniform(0.3, 1.5)}
response_time_seconds_count {random.randint(80, 300)}
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5070, debug=True)
