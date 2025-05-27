#!/usr/bin/env python3
"""
Tests d'intégration pour SuperSmartMatch Unifié
"""

import pytest
import asyncio
import json
import requests
from datetime import datetime

# Configuration pour les tests
TEST_BASE_URL = "http://localhost:5052"
TEST_TIMEOUT = 30

class TestSuperSmartMatchPipeline:
    """Tests du pipeline complet SuperSmartMatch Unifié"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.base_url = TEST_BASE_URL
        self.session_id = f"test_session_{datetime.now().timestamp()}"
    
    def test_health_check(self):
        """Test du health check"""
        response = requests.get(f"{self.base_url}/health", timeout=TEST_TIMEOUT)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "features" in data
    
    def test_pipeline_step1_parsing_only(self):
        """Test de l'étape 1 : parsing uniquement"""
        # Simuler l'upload de fichiers
        files = {
            'cv_file': ('test_cv.txt', 'Test CV content', 'text/plain'),
            'job_file': ('test_job.txt', 'Test Job content', 'text/plain')
        }
        
        data = {
            'session_id': self.session_id
        }
        
        response = requests.post(
            f"{self.base_url}/api/unified-match/start",
            files=files,
            data=data,
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["status"] == "waiting_questionnaire"
        assert result["session_id"] == self.session_id
        assert "parsed_data" in result
    
    def test_pipeline_step2_questionnaire(self):
        """Test de l'étape 2 : ajout du questionnaire"""
        # D'abord, démarrer le parsing
        files = {
            'cv_file': ('test_cv.txt', 'Test CV content', 'text/plain'),
            'job_file': ('test_job.txt', 'Test Job content', 'text/plain')
        }
        
        data = {'session_id': self.session_id}
        
        response = requests.post(
            f"{self.base_url}/api/unified-match/start",
            files=files,
            data=data,
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        
        # Ensuite, compléter avec le questionnaire
        questionnaire_data = {
            "session_id": self.session_id,
            "questionnaire_data": {
                "motivation": 8,
                "disponibilite": 9,
                "mobilite": 6,
                "salaire_souhaite": 50000,
                "experience_specifique": "Développement web avec Python",
                "objectifs_carriere": "Évoluer vers un poste de lead developer"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/unified-match/complete",
            json=questionnaire_data,
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Vérifier la structure du résultat
        assert "matching_score_entreprise" in result
        assert "matching_score_candidat" in result
        assert "detailed_analysis" in result
        assert "recommendations" in result
        
        # Vérifier que les scores sont dans la plage attendue
        assert 0 <= result["matching_score_entreprise"] <= 100
        assert 0 <= result["matching_score_candidat"] <= 100
    
    def test_session_status(self):
        """Test de vérification du statut d'une session"""
        # Créer une session
        files = {
            'cv_file': ('test_cv.txt', 'Test CV content', 'text/plain')
        }
        
        data = {'session_id': self.session_id}
        
        requests.post(
            f"{self.base_url}/api/unified-match/start",
            files=files,
            data=data,
            timeout=TEST_TIMEOUT
        )
        
        # Vérifier le statut
        response = requests.get(
            f"{self.base_url}/api/unified-match/status/{self.session_id}",
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 200
        status = response.json()
        
        assert status["status"] == "ready_for_questionnaire"
        assert "has_cv" in status
        assert "parsing_confidence" in status
    
    def test_invalid_session(self):
        """Test avec une session invalide"""
        response = requests.get(
            f"{self.base_url}/api/unified-match/status/invalid_session",
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 404
        assert response.json()["status"] == "not_found"
    
    def test_missing_questionnaire_data(self):
        """Test avec données questionnaire manquantes"""
        incomplete_data = {
            "session_id": "test_session"
            # questionnaire_data manquant
        }
        
        response = requests.post(
            f"{self.base_url}/api/unified-match/complete",
            json=incomplete_data,
            timeout=TEST_TIMEOUT
        )
        
        assert response.status_code == 400
        assert "error" in response.json()
    
    def test_pipeline_complete_workflow(self):
        """Test du workflow complet"""
        session_id = f"complete_test_{datetime.now().timestamp()}"
        
        # Étape 1: Upload et parsing
        files = {
            'cv_file': ('complete_test_cv.txt', 'Développeur Python avec 3 ans d\'expérience', 'text/plain'),
            'job_file': ('complete_test_job.txt', 'Poste de développeur Python junior', 'text/plain')
        }
        
        data = {'session_id': session_id}
        
        step1_response = requests.post(
            f"{self.base_url}/api/unified-match/start",
            files=files,
            data=data,
            timeout=TEST_TIMEOUT
        )
        
        assert step1_response.status_code == 200
        step1_result = step1_response.json()
        assert step1_result["status"] == "waiting_questionnaire"
        
        # Étape 2: Vérification statut
        status_response = requests.get(
            f"{self.base_url}/api/unified-match/status/{session_id}",
            timeout=TEST_TIMEOUT
        )
        
        assert status_response.status_code == 200
        status_result = status_response.json()
        assert status_result["status"] == "ready_for_questionnaire"
        
        # Étape 3: Completion avec questionnaire
        questionnaire_data = {
            "session_id": session_id,
            "questionnaire_data": {
                "motivation": 7,
                "disponibilite": 8,
                "mobilite": 5,
                "salaire_souhaite": 40000,
                "experience_specifique": "Développement d'applications web",
                "objectifs_carriere": "Devenir expert Python"
            }
        }
        
        final_response = requests.post(
            f"{self.base_url}/api/unified-match/complete",
            json=questionnaire_data,
            timeout=TEST_TIMEOUT
        )
        
        assert final_response.status_code == 200
        final_result = final_response.json()
        
        # Validation du résultat final
        required_fields = [
            "matching_score_entreprise",
            "matching_score_candidat",
            "detailed_analysis",
            "questionnaire_boost",
            "parsing_quality",
            "recommendations",
            "match_id"
        ]
        
        for field in required_fields:
            assert field in final_result, f"Champ manquant: {field}"
        
        # Vérification des scores
        assert 0 <= final_result["matching_score_entreprise"] <= 100
        assert 0 <= final_result["matching_score_candidat"] <= 100
        assert isinstance(final_result["recommendations"], list)
        assert len(final_result["recommendations"]) > 0
        
        print(f"✅ Test complet réussi - Score: {final_result['matching_score_entreprise']:.1f}%")

if __name__ == "__main__":
    # Exécution manuelle des tests
    import sys
    
    print("🧪 Tests SuperSmartMatch Unifié")
    print("=" * 40)
    
    test_instance = TestSuperSmartMatchPipeline()
    
    tests = [
        ("Health Check", test_instance.test_health_check),
        ("Pipeline Step 1", test_instance.test_pipeline_step1_parsing_only),
        ("Session Status", test_instance.test_session_status),
        ("Invalid Session", test_instance.test_invalid_session),
        ("Missing Data", test_instance.test_missing_questionnaire_data),
        ("Complete Workflow", test_instance.test_pipeline_complete_workflow)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🔍 Test: {test_name}")
            test_instance.setup_method()
            test_func()
            print(f"✅ {test_name}: PASSED")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: FAILED - {e}")
            failed += 1
    
    print(f"\n📊 Résultats: {passed} réussis, {failed} échoués")
    
    if failed > 0:
        sys.exit(1)
    else:
        print("🎉 Tous les tests sont passés !")
