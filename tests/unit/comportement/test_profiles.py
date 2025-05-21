import pytest
from datetime import datetime, timedelta
from user_behavior.profiles.profile_builder import UserProfileBuilder


def test_build_user_profiles():
    # Test de la construction des profils utilisateur
    profile_builder = UserProfileBuilder()
    
    # Créer des données de test
    now = datetime.now()
    
    # Actions utilisateur simulées
    user_actions = [
        {'user_id': 'user1', 'action_type': 'login', 'timestamp': (now - timedelta(days=5)).isoformat()},
        {'user_id': 'user1', 'action_type': 'view_job', 'timestamp': (now - timedelta(days=5, hours=1)).isoformat()},
        {'user_id': 'user1', 'action_type': 'apply_job', 'timestamp': (now - timedelta(days=5, hours=2)).isoformat()},
        {'user_id': 'user1', 'action_type': 'logout', 'timestamp': (now - timedelta(days=5, hours=3)).isoformat()},
        
        {'user_id': 'user2', 'action_type': 'login', 'timestamp': (now - timedelta(days=3)).isoformat()},
        {'user_id': 'user2', 'action_type': 'view_job', 'timestamp': (now - timedelta(days=3, hours=1)).isoformat()},
        {'user_id': 'user2', 'action_type': 'logout', 'timestamp': (now - timedelta(days=3, hours=2)).isoformat()}
    ]
    
    # Données utilisateur de base
    user_data = [
        {
            'user_id': 'user1',
            'name': 'User One',
            'email': 'user1@example.com',
            'created_at': (now - timedelta(days=30)).isoformat(),
            'profile_completion': 80
        },
        {
            'user_id': 'user2',
            'name': 'User Two',
            'email': 'user2@example.com',
            'created_at': (now - timedelta(days=20)).isoformat(),
            'profile_completion': 50
        }
    ]
    
    # Construire les profils
    profiles = profile_builder.build_user_profiles(user_actions, user_data)
    
    # Vérifications
    assert len(profiles) == 2
    assert 'user1' in profiles
    assert 'user2' in profiles
    
    # Vérifier le profil de user1
    user1_profile = profiles['user1']
    assert user1_profile['name'] == 'User One'
    assert user1_profile['email'] == 'user1@example.com'
    assert user1_profile['profile_completion'] == 80
    assert user1_profile['action_count'] == 4
    assert user1_profile['job_view_count'] == 1
    assert user1_profile['application_count'] == 1
    assert user1_profile['conversion_rate'] == 1.0  # 1 candidature / 1 vue
    
    # Vérifier le profil de user2
    user2_profile = profiles['user2']
    assert user2_profile['name'] == 'User Two'
    assert user2_profile['email'] == 'user2@example.com'
    assert user2_profile['profile_completion'] == 50
    assert user2_profile['action_count'] == 3
    assert user2_profile['job_view_count'] == 1
    assert user2_profile['application_count'] == 0
    assert user2_profile['conversion_rate'] == 0.0  # 0 candidature / 1 vue


def test_update_profiles():
    # Test de la mise à jour des profils utilisateur
    profile_builder = UserProfileBuilder()
    
    # Créer des données de test
    now = datetime.now()
    
    # Actions utilisateur initiales
    initial_actions = [
        {'user_id': 'user1', 'action_type': 'login', 'timestamp': (now - timedelta(days=5)).isoformat()},
        {'user_id': 'user1', 'action_type': 'view_job', 'timestamp': (now - timedelta(days=5, hours=1)).isoformat()}
    ]
    
    # Construire les profils initiaux
    initial_profiles = profile_builder.build_user_profiles(initial_actions)
    
    # Nouvelles actions
    new_actions = [
        {'user_id': 'user1', 'action_type': 'apply_job', 'timestamp': now.isoformat()},
        {'user_id': 'user2', 'action_type': 'login', 'timestamp': now.isoformat()},
        {'user_id': 'user2', 'action_type': 'view_job', 'timestamp': (now - timedelta(hours=1)).isoformat()}
    ]
    
    # Mettre à jour les profils
    updated_profiles = profile_builder.update_profiles(initial_profiles, new_actions)
    
    # Vérifications
    assert len(updated_profiles) == 2
    assert 'user1' in updated_profiles
    assert 'user2' in updated_profiles
    
    # Vérifier la mise à jour du profil user1
    user1_profile = updated_profiles['user1']
    assert user1_profile['action_count'] == 3  # 2 initiales + 1 nouvelle
    assert user1_profile['job_view_count'] == 1
    assert user1_profile['application_count'] == 1  # Nouvelle action
    assert user1_profile['conversion_rate'] == 1.0  # 1 candidature / 1 vue
    
    # Vérifier le nouveau profil user2
    user2_profile = updated_profiles['user2']
    assert user2_profile['action_count'] == 2
    assert user2_profile['job_view_count'] == 1
    assert user2_profile['application_count'] == 0