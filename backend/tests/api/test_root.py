import pytest
from fastapi.testclient import TestClient

def test_read_root(client):
    """
    Test que l'endpoint racine renvoie le message de bienvenue attendu
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bienvenue sur l'API Commitment"}
