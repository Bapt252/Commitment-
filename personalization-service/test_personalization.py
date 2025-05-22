import unittest
import requests
import json
import time

class TestPersonalizationService(unittest.TestCase):
    
    def setUp(self):
        """Configuration des tests"""
        self.base_url = "http://localhost:5060"
        self.test_user_id = f"test_user_{int(time.time())}"
        self.test_job_id = f"test_job_{int(time.time())}"
        
        # Attendre que le service soit prêt
        max_retries = 10
        for i in range(max_retries):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    break
            except:
                pass
            time.sleep(1)
    
    def test_health_check(self):
        """Test du health check"""
        response = requests.get(f"{self.base_url}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['service'], 'personalization-service')
        self.assertEqual(data['status'], 'healthy')
    
    def test_feedback_collection(self):
        """Test de collecte de feedback"""
        feedback_data = {
            "user_id": self.test_user_id,
            "job_id": self.test_job_id, 
            "action": "apply",
            "match_score": 0.85
        }
        
        response = requests.post(f"{self.base_url}/api/feedback", 
                               json=feedback_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
    
    def test_personalized_weights_cold_start(self):
        """Test des poids personnalisés en cold start"""
        response = requests.get(f"{self.base_url}/api/personalized-weights/new_user")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'cold_start')
        self.assertIn('personalized_weights', data)
    
    def test_personalized_weights_with_history(self):
        """Test des poids personnalisés avec historique"""
        # Créer de l'historique
        for i in range(6):
            feedback_data = {
                "user_id": self.test_user_id,
                "job_id": f"job_{i}", 
                "action": "apply" if i % 2 == 0 else "view",
                "match_score": 0.7 + (i * 0.05)
            }
            requests.post(f"{self.base_url}/api/feedback", json=feedback_data)
            time.sleep(0.1)
        
        # Maintenant tester les poids personnalisés
        response = requests.get(f"{self.base_url}/api/personalized-weights/{self.test_user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'personalized')
        self.assertIn('preferences', data)
    
    def test_hybrid_score_calculation(self):
        """Test du calcul de score hybride"""
        # Créer de l'historique
        for i in range(3):
            feedback_data = {
                "user_id": self.test_user_id,
                "job_id": f"job_{i}", 
                "action": "apply",
                "match_score": 0.8
            }
            requests.post(f"{self.base_url}/api/feedback", json=feedback_data)
            time.sleep(0.1)
        
        # Calculer le score hybride
        score_data = {
            "user_id": self.test_user_id,
            "job_id": "new_job",
            "base_match_score": 0.75
        }
        
        response = requests.post(f"{self.base_url}/api/hybrid-score", json=score_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('hybrid_score', data)
        self.assertGreaterEqual(data['hybrid_score'], 0.0)
        self.assertLessEqual(data['hybrid_score'], 1.0)
    
    def test_ab_test_assignment(self):
        """Test de l'assignation A/B"""
        ab_data = {
            "user_id": self.test_user_id,
            "variant": "hybrid"
        }
        
        response = requests.post(f"{self.base_url}/api/ab-test", json=ab_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['assigned_variant'], 'hybrid')
    
    def test_user_stats(self):
        """Test des statistiques utilisateur"""
        # Créer de l'activité
        feedback_data = {
            "user_id": self.test_user_id,
            "job_id": self.test_job_id, 
            "action": "save",
            "match_score": 0.9
        }
        requests.post(f"{self.base_url}/api/feedback", json=feedback_data)
        time.sleep(0.1)
        
        # Récupérer les stats
        response = requests.get(f"{self.base_url}/api/user-stats/{self.test_user_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('stats', data)
    
    def test_collaborative_recommendations(self):
        """Test des recommandations collaboratives"""
        rec_data = {
            "user_id": self.test_user_id,
            "candidate_jobs": ["job1", "job2", "job3"]
        }
        
        response = requests.post(f"{self.base_url}/api/collaborative-recommendations", 
                               json=rec_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('recommendations', data)
        self.assertEqual(len(data['recommendations']), 3)

if __name__ == '__main__':
    unittest.main()