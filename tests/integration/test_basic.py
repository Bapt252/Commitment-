#!/usr/bin/env python3
import requests
import json
import sys

def test_api_health():
    """Test basic health endpoints"""
    base_url = "http://localhost"
    
    endpoints = ["/health", "/health/v1", "/health/v2"]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint} OK")
            else:
                print(f"❌ {endpoint} FAIL ({response.status_code})")
                return False
        except Exception as e:
            print(f"❌ {endpoint} ERROR: {e}")
            return False
    
    return True

def test_api_matching():
    """Test basic matching functionality"""
    base_url = "http://localhost"
    
    payload = {
        "candidate": {
            "name": "Test User",
            "skills": ["Python"],
            "experience": 3
        },
        "jobs": [{
            "id": 1,
            "title": "Python Developer",
            "required_skills": ["Python"],
            "experience_required": 2
        }]
    }
    
    for version in ["v1", "v2"]:
        try:
            response = requests.post(
                f"{base_url}/api/match?version={version}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ API {version} OK (matches: {len(result.get('matches', []))})")
            else:
                print(f"❌ API {version} FAIL ({response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ API {version} ERROR: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("🧪 Tests d'intégration SuperSmartMatch V2")
    
    success = True
    success &= test_api_health()
    success &= test_api_matching()
    
    if success:
        print("🎉 Tous les tests passés!")
        sys.exit(0)
    else:
        print("❌ Certains tests ont échoué")
        sys.exit(1)
