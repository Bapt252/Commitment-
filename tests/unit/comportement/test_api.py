import pytest
import json
from user_behavior.api.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    # Test du endpoint health
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['service'] == 'user-behavior-api'


def test_create_profile(client):
    # Test de création d'un profil utilisateur
    profile_data = {
        'user_id': 'test123',
        'name': 'Test User',
        'email': 'test@example.com',
        'interactions': [
            {
                'user_id': 'test123',
                'action_type': 'view_job',
                'timestamp': '2025-05-20T10:00:00Z',
                'item_id': 'job-123',
                'job_category': 'Development'
            }
        ]
    }
    
    response = client.post(
        '/api/profiles',
        data=json.dumps(profile_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['user_id'] == 'test123'
    assert data['name'] == 'Test User'
    assert data['job_view_count'] == 1


def test_get_profiles(client):
    # D'abord créer un profil
    test_create_profile(client)
    
    # Tester la récupération de tous les profils
    response = client.get('/api/profiles')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 1
    
    # Tester la récupération d'un profil spécifique
    response = client.get('/api/profiles?user_id=test123')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user_id'] == 'test123'


def test_detect_patterns(client):
    # Test de détection de patterns
    pattern_data = {
        'actions': [
            {
                'user_id': 'test123',
                'action_type': 'login',
                'timestamp': '2025-05-19T09:00:00Z'
            },
            {
                'user_id': 'test123',
                'action_type': 'view_job',
                'timestamp': '2025-05-19T09:05:00Z'
            },
            {
                'user_id': 'test123',
                'action_type': 'login',
                'timestamp': '2025-05-20T09:00:00Z'
            },
            {
                'user_id': 'test123',
                'action_type': 'view_job',
                'timestamp': '2025-05-20T09:05:00Z'
            }
        ]
    }
    
    response = client.post(
        '/api/patterns',
        data=json.dumps(pattern_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'user_patterns' in data
    assert 'common_patterns' in data
    assert 'test123' in data['user_patterns']


def test_calculate_preference_scores(client):
    # Test de calcul des scores de préférence
    score_data = {
        'actions': [
            {
                'user_id': 'test123',
                'action_type': 'view_job',
                'timestamp': '2025-05-20T10:00:00Z',
                'item_id': 'job-123',
                'job_category': 'Development'
            },
            {
                'user_id': 'test123',
                'action_type': 'view_job',
                'timestamp': '2025-05-20T11:00:00Z',
                'item_id': 'job-456',
                'job_category': 'Data Science'
            },
            {
                'user_id': 'test123',
                'action_type': 'apply_job',
                'timestamp': '2025-05-20T11:15:00Z',
                'item_id': 'job-456',
                'job_category': 'Data Science'
            }
        ]
    }
    
    response = client.post(
        '/api/preference-scores',
        data=json.dumps(score_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'test123' in data
    assert 'Development' in data['test123']
    assert 'Data Science' in data['test123']
    assert data['test123']['Data Science'] > data['test123']['Development']  # Plus d'actions en Data Science