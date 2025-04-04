import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app
from app.core.config import settings

@pytest.fixture
def client():
    """
    Créer un client de test pour l'API FastAPI
    """
    with TestClient(app) as test_client:
        yield test_client

# Si vous avez besoin de mocker la base de données
@pytest.fixture
def mock_db():
    """
    Créer un mock pour la session de base de données
    """
    mock = MagicMock()
    return mock
