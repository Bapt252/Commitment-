import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
import json

from app.main import app
from app.api.endpoints.job_posts import router

client = TestClient(app)

@pytest.fixture
def mock_job_parser():
    """Fixture pour mocker le parser de fiche de poste"""
    with patch("app.ml.job_parser.parse_job_post") as mock:
        mock.return_value = {
            "title": "Développeur Python",
            "description": "Poste de développeur Python expérimenté",
            "company": "TechCorp",
            "location": "Paris",
            "contract_type": "CDI",
            "salary_range": "45K-55K",
            "skills": [
                {"name": "Python", "level": 4},
                {"name": "Django", "level": 3},
                {"name": "SQL", "level": 3}
            ]
        }
        yield mock

def test_parse_job_post_with_file(mock_job_parser):
    """Test du parsing d'une fiche de poste avec un fichier"""
    # Créer un fichier de test
    file_content = b"Contenu de test pour la fiche de poste"
    file = {"file": ("test_job.pdf", io.BytesIO(file_content), "application/pdf")}
    
    # Faire la requête
    response = client.post("/api/v1/job-posts/parse", files=file)
    
    # Vérifier la réponse
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Développeur Python"
    assert len(data["skills"]) == 3
    assert data["skills"][0]["name"] == "Python"
    
    # Vérifier que le mock a été appelé avec les bons arguments
    mock_job_parser.assert_called_once_with(file_content, "test_job.pdf")

def test_create_job_post_with_file(mock_job_parser):
    """Test de la création d'une fiche de poste avec un fichier"""
    # Créer un fichier de test
    file_content = b"Contenu de test pour la fiche de poste"
    file = {"file": ("test_job.pdf", io.BytesIO(file_content), "application/pdf")}
    
    # Faire la requête
    response = client.post("/api/v1/job-posts/", files=file)
    
    # Vérifier la réponse
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Développeur Python"
    assert data["company"] == "TechCorp"
    assert "created_at" in data
    assert "updated_at" in data

def test_create_job_post_with_json(mock_job_parser):
    """Test de la création d'une fiche de poste avec des données JSON"""
    # Créer les données JSON
    job_data = {
        "title": "Développeur Python",
        "description": "Poste de développeur Python expérimenté",
        "company": "TechCorp",
        "location": "Paris",
        "contract_type": "CDI",
        "salary_range": "45K-55K",
        "skills": [
            {"name": "Python", "level": 4},
            {"name": "Django", "level": 3},
            {"name": "SQL", "level": 3}
        ]
    }
    
    # Faire la requête
    response = client.post(
        "/api/v1/job-posts/",
        data={"job_data": json.dumps(job_data)}
    )
    
    # Vérifier la réponse
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Développeur Python"

def test_parse_job_post_without_file():
    """Test du parsing sans fichier (doit échouer)"""
    response = client.post("/api/v1/job-posts/parse")
    assert response.status_code == 422  # ValidationError de FastAPI

def test_get_job_posts():
    """Test de la récupération de la liste des fiches de poste"""
    response = client.get("/api/v1/job-posts/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_job_post():
    """Test de la récupération d'une fiche de poste spécifique"""
    response = client.get("/api/v1/job-posts/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert "title" in data
    assert "skills" in data
