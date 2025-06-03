from flask import Flask, jsonify, request
import time
import random

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "service": "SuperSmartMatch V1", "version": "1.0.0"})

@app.route('/api/match', methods=['POST'])
def match():
    data = request.get_json()
    candidate = data.get('candidate', {})
    jobs = data.get('jobs', [])
    
    # Simulation matching V1 (plus simple)
    matches = []
    for job in jobs:
        score = random.randint(60, 85)  # V1 moins précis
        matches.append({
            "job_id": job.get('id'),
            "job_title": job.get('title'),
            "score": score,
            "reasons": ["skills_match", "experience_match"]
        })
    
    # Simulation temps de réponse V1
    time.sleep(random.uniform(0.04, 0.07))  # 40-70ms
    
    return jsonify({
        "matches": matches,
        "processing_time_ms": random.randint(45, 65),
        "algorithm": "basic_matching_v1"
    })

@app.route('/metrics')
def metrics():
    return f"""
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{{method="GET",endpoint="/health"}} {random.randint(100, 500)}
http_requests_total{{method="POST",endpoint="/api/match"}} {random.randint(50, 200)}

# HELP response_time_seconds Response time
# TYPE response_time_seconds histogram
response_time_seconds_sum {random.uniform(0.5, 2.0)}
response_time_seconds_count {random.randint(50, 200)}
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5062, debug=True)
