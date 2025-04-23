import pytest
from fastapi.testclient import TestClient
import sys
import os

# Ajouter le répertoire parent au path pour pouvoir importer l'application
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importer l'application après avoir ajusté le path
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
