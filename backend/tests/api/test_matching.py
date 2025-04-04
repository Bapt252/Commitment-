import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_matching_engine():
    """Fixture pour mocker le moteur de matching"""
    with patch("app.ml.matching_engine.generate_matches") as mock:
        mock.return_value = [
            {
                "job_post_id": 1,
                "candidate_id": 1,
                "overall_score": 0.85,
                "score_details": [
                    {
                        "category": "skills",
                        "score": 0.9,
                        "explanation": "Compétences techniques correspondantes"
                    },
                    {
                        "category": "experience",
                        "score": 0.8,
                        "explanation": "5 ans d'expérience"
                    }
                ],
                "strengths": ["Python", "Machine Learning"],
                "gaps": ["Cloud AWS"],
                "recommendations": ["Formation AWS recommandée"],
                "created_at": "2025-04-01T10:00:00"
            },
            {
                "job_post_id": 1,
                "candidate_id": 2,
                "overall_score": 0.75,
                "score_details": [
                    {
                        "category": "skills",
                        "score": 0.8,
                        "explanation": "Compétences techniques partielles"
                    },
                    {
                        "category": "experience",
                        "score": 0.7,
                        "explanation": "3 ans d'expérience"
                    }
                ],
                "strengths": ["JavaScript", "React"],
                "gaps": ["Python", "Data Science"],
                "recommendations": ["Formation Python recommandée"],
                "created_at": "2025-04-01T10:00:00"
            }
        ]
        yield mock

def test_create_matching(mock_matching_engine):
    """Test de la création d'un matching"""
    # Préparer les données
    matching_request = {
        "job_post_id": 1,
        "candidate_ids": [1, 2, 3],
        "min_score": 0.7
    }
    
    # Faire la requête
    response = client.post("/api/v1/matching/", json=matching_request)
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]["overall_score"] == 0.85
    assert data[1]["overall_score"] == 0.75
    
    # Vérifier que le mock a été appelé avec les bons arguments
    mock_matching_engine.assert_called_once_with(
        job_post_id=1,
        candidate_ids=[1, 2, 3],
        min_score=0.7
    )

def test_create_matching_without_job_post_id():
    """Test de la création d'un matching sans ID de fiche de poste (doit échouer)"""
    matching_request = {
        "candidate_ids": [1, 2, 3],
        "min_score": 0.7
    }
    
    response = client.post("/api/v1/matching/", json=matching_request)
    assert response.status_code == 400
    assert "job_post_id" in response.json()["detail"]

def test_get_matching():
    """Test de la récupération d'un matching spécifique"""
    response = client.get("/api/v1/matching/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "overall_score" in data
    assert "strengths" in data
    assert "gaps" in data

def test_get_matchings_by_job():
    """Test de la récupération des matchings par fiche de poste"""
    response = client.get("/api/v1/matching/job/1?min_score=0.7")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(match["job_post_id"] == 1 for match in data)
    assert all(match["overall_score"] >= 0.7 for match in data)

def test_get_matchings_by_candidate():
    """Test de la récupération des matchings par candidat"""
    response = client.get("/api/v1/matching/candidate/1?min_score=0.6")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert all(match["candidate_id"] == 1 for match in data)
    assert all(match["overall_score"] >= 0.6 for match in data)
